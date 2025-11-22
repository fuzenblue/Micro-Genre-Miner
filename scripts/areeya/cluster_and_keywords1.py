import os
import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import umap
import warnings

# Optional: HDBSCAN (if installed). If not installed, we'll skip it gracefully.
try:
    import hdbscan
    HAS_HDBSCAN = True
except Exception:
    HAS_HDBSCAN = False

warnings.filterwarnings("ignore", category=FutureWarning)

# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_PKL_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_embeddings.pkl")
EMBEDDING_NPY_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_embeddings.npy")
INPUT_DATA_PATH = os.path.join(BASE_DIR, "../../data/cleaned/cleaned_movies.csv")
OUTPUT_CLUSTER_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../data/processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# K search range for elbow / silhouette (tuned for micro-genre)
N_CLUSTERS_RANGE = range(50, 101, 5)  # 50, 55, 60, ... 100
TFIDF_MAX_FEATURES = 2000
TFIDF_WEIGHT = 2.0

# Feature mode:
# 'emb_only'         -> use only sentence embeddings (default)
# 'emb+tfidf_pca'    -> embeddings + TF-IDF reduced by PCA
# 'full'             -> embeddings + full TF-IDF + numeric
FEATURE_MODE = 'emb_only'
TFIDF_PCA_DIM = 50

# Safety / behavior flags
ALLOW_PADDING = False   # if embeddings shorter than df, whether to pad zeros (unsafe)
FORCE_K = None          # set to an int (e.g., 50) to force chosen_k; set to None to use heuristic

print(f"DEBUG: BASE_DIR = {BASE_DIR}")
print(f"DEBUG: EMBEDDING_PKL exists? {os.path.exists(EMBEDDING_PKL_PATH)}")
print(f"DEBUG: EMBEDDING_NPY exists? {os.path.exists(EMBEDDING_NPY_PATH)}")
print(f"DEBUG: INPUT_DATA_PATH exists? {os.path.exists(INPUT_DATA_PATH)}")

# ----------------------------
# Utility
# ----------------------------
def pretty_print_choice(tested, chosen_name, chosen_k, reason):
    print("Tested: " + ", ".join(tested))
    print(f"Chosen: {chosen_name} (k={chosen_k})")
    print(f"Why K={chosen_k} ?")
    print(reason)

# ----------------------------
# Feature Engineering
# ----------------------------
def build_hybrid_features(df, embeddings, mode='emb_only', tfidf_max_features=2000, tfidf_weight=2.0, tfidf_pca_dim=50):
    """
    Build hybrid features with safety checks.
    embeddings may be: np.ndarray, dict (id->vec), list/tuple
    """
    # 1) normalize embeddings into matrix aligned with df
    emb_matrix = None
    if isinstance(embeddings, dict):
        if 'id' not in df.columns:
            raise ValueError("Embeddings is a dict but dataframe has no 'id' column to align.")
        # align by df['id']
        emb_list = []
        sample_vec = None
        for rid in df['id'].values:
            vec = embeddings.get(rid)
            if vec is None:
                if sample_vec is None:
                    sample_vec = next(iter(embeddings.values()))
                vec = np.zeros_like(sample_vec, dtype=float)
            emb_list.append(vec)
        emb_matrix = np.vstack(emb_list)
    elif isinstance(embeddings, (list, tuple)):
        emb_matrix = np.vstack(embeddings)
    elif isinstance(embeddings, np.ndarray):
        emb_matrix = embeddings
        if emb_matrix.shape[0] != len(df):
            msg = f"Embedding rows ({emb_matrix.shape[0]}) != DF rows ({len(df)})"
            if ALLOW_PADDING and emb_matrix.shape[0] < len(df):
                print("[WARN] " + msg + " -> padding embeddings with zeros (ALLOW_PADDING=True).")
                missing = len(df) - emb_matrix.shape[0]
                pad = np.zeros((missing, emb_matrix.shape[1]), dtype=emb_matrix.dtype)
                emb_matrix = np.vstack([emb_matrix, pad])
            else:
                raise ValueError(msg + ". Regenerate embeddings aligned to dataframe or set ALLOW_PADDING=True (not recommended).")
    else:
        raise ValueError("Unknown embeddings type: {}".format(type(embeddings)))

    print(f"[INFO] Using embeddings matrix with shape = {emb_matrix.shape}")

    if mode == 'emb_only':
        return emb_matrix

    # Build TF-IDF if required
    tfidf = TfidfVectorizer(max_features=tfidf_max_features, stop_words="english")
    tfidf_vec = tfidf.fit_transform(df["clean_text"].fillna("")).toarray()
    print(f"[INFO] TF-IDF raw shape = {tfidf_vec.shape}")

    numeric_vec = df[["desc_length", "num_keywords", "sentiment_score"]].values if {'desc_length','num_keywords','sentiment_score'}.issubset(df.columns) else np.zeros((len(df), 0))

    if mode == 'emb+tfidf_pca':
        print(f"[INFO] Reducing TF-IDF from {tfidf_vec.shape[1]} -> {tfidf_pca_dim} using PCA")
        pca_tfidf = PCA(n_components=tfidf_pca_dim, random_state=42)
        tfidf_reduced = pca_tfidf.fit_transform(tfidf_vec)
        hybrid_vec = np.hstack([emb_matrix, tfidf_reduced * tfidf_weight, numeric_vec])
        print(f"[INFO] Hybrid shape = {hybrid_vec.shape} (emb + tfidf_pca + numeric)")
        return hybrid_vec

    if mode == 'full':
        hybrid_vec = np.hstack([emb_matrix, tfidf_vec * tfidf_weight, numeric_vec])
        print(f"[INFO] Hybrid shape = {hybrid_vec.shape} (emb + full tfidf + numeric)")
        return hybrid_vec

    raise ValueError("Unknown feature mode: " + str(mode))

# ----------------------------
# Numeric Feature Engineering
# ----------------------------
def extract_basic_features(df):
    print("[INFO] Extracting basic numeric features...")
    df["clean_text"] = df["clean_text"].fillna("")
    df["desc_length"] = df["clean_text"].str.len()
    df["num_keywords"] = df["clean_text"].str.split().apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["sentiment_score"] = df["clean_text"].apply(lambda x: TextBlob(x).sentiment.polarity if x else 0.0)
    return df

# ----------------------------
# 1) Load Data & Embedding
# ----------------------------
def load_embeddings(prefer_npy=True):
    """
    Try to load .npy first (prefer_npy=True), otherwise .pkl.
    Returns numpy array or dict/list depending on file contents.
    """
    # try npy
    if prefer_npy and os.path.exists(EMBEDDING_NPY_PATH):
        print(f"[INFO] Loading embeddings from npy: {EMBEDDING_NPY_PATH}")
        emb = np.load(EMBEDDING_NPY_PATH, allow_pickle=False)
        print(f"[INFO] Embeddings loaded (npy), shape = {emb.shape}")
        return emb

    # try pkl
    if os.path.exists(EMBEDDING_PKL_PATH):
        print(f"[INFO] Loading embeddings from pkl: {EMBEDDING_PKL_PATH}")
        with open(EMBEDDING_PKL_PATH, "rb") as f:
            emb = pickle.load(f)
        if isinstance(emb, np.ndarray):
            print(f"[INFO] Embeddings loaded (pkl->ndarray), shape = {emb.shape}")
        elif isinstance(emb, dict):
            sample = next(iter(emb.items()))
            print(f"[INFO] Embeddings loaded as dict, sample key = {sample[0]}, dim = {len(sample[1])}")
        else:
            try:
                arr = np.vstack(emb)
                print(f"[INFO] Embeddings loaded as list/tuple, converted to array shape = {arr.shape}")
                emb = arr
            except Exception:
                print("[WARN] Embeddings loaded from pkl but type is unexpected:", type(emb))
        return emb

    raise FileNotFoundError("No embeddings file found. Please generate embeddings and save to .npy or .pkl paths.")

def load_data(path):
    print(f"[INFO] Loading cleaned data from: {path}")
    df = pd.read_csv(path)
    if "clean_text" not in df.columns:
        raise ValueError("ERROR: ต้องมี column clean_text")
    print(f"[INFO] Data loaded, rows = {len(df)}")
    return df.copy()

# ----------------------------
# 2) Find K using Elbow method (inertia) with heuristic
# ----------------------------
def find_k_elbow(vectors, k_range=range(5,101), rel_improve_threshold=0.03):
    """
    Compute inertia for KMeans over k_range, then choose elbow where relative improvement < threshold.
    Implementation detail:
      - rel_improv[i] = (inertia[i-1] - inertia[i]) / inertia[i-1]
      - find first i>=1 where rel_improv[i] < threshold -> choose k = ks[i]
    Returns chosen_k, ks, inertias, reason
    """
    ks = list(k_range)
    inertias = []
    print("[INFO] Computing inertia for K in:", ks)
    for k in ks:
        if k >= len(vectors):
            print(f"[WARN] k={k} >= n_samples ({len(vectors)}), skipping")
            inertias.append(np.nan)
            continue
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(vectors)
        inertias.append(kmeans.inertia_)
        print(f"  k={k}, inertia={kmeans.inertia_:.2f}")

    inertias = np.array(inertias, dtype=float)
    # compute relative improvements
    rel_improv = np.full_like(inertias, np.nan)
    for i in range(1, len(inertias)):
        if np.isnan(inertias[i-1]) or np.isnan(inertias[i]):
            continue
        rel_improv[i] = (inertias[i-1] - inertias[i]) / (inertias[i-1] + 1e-12)

    # find first i where rel_improv[i] < threshold
    chosen_k = None
    reason = ""
    for i in range(1, len(ks)):
        if np.isnan(rel_improv[i]):
            continue
        if rel_improv[i] < rel_improve_threshold:
            chosen_k = ks[i]
            reason = f"Elbow method: relative inertia improvement fell below {rel_improve_threshold*100:.1f}% at k={chosen_k}."
            break

    if chosen_k is None:
        # fallback to silhouette best within ks (excluding nan and k>=n_samples)
        best_k = None
        best_score = -1
        for k, inertia_val in zip(ks, inertias):
            if np.isnan(inertia_val) or k >= len(vectors):
                continue
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(vectors)
                score = silhouette_score(vectors, labels)
                print(f"  silhouette k={k}: score={score:.4f}")
                if score > best_score:
                    best_score = score
                    best_k = k
            except Exception as e:
                print(f"  silhouette failed for k={k}: {e}")
                continue
        if best_k is not None:
            chosen_k = best_k
            reason = f"No clear elbow found; fallback to silhouette best k={chosen_k} (score={best_score:.4f})."
        else:
            chosen_k = ks[len(ks)//2]
            reason = "Fallback: choose mid-point of k range."

    return chosen_k, ks, inertias, reason

# ----------------------------
# 3) Cluster
# ----------------------------
def perform_kmeans(vectors, k):
    print(f"[INFO] Clustering using KMeans with K={k}")
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(vectors)
    return labels, km

def perform_agglomerative(vectors, k):
    print(f"[INFO] Clustering using Agglomerative with K={k}")
    agg = AgglomerativeClustering(n_clusters=k)
    labels = agg.fit_predict(vectors)
    return labels, agg

def perform_hdbscan(vectors, min_cluster_size=15):
    if not HAS_HDBSCAN:
        raise ImportError("hdbscan not installed")
    print(f"[INFO] Clustering using HDBSCAN (min_cluster_size={min_cluster_size})")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    labels = clusterer.fit_predict(vectors)
    return labels, clusterer

# ----------------------------
# 4) Extract Micro-Genre Name
# ----------------------------
def extract_cluster_keywords(df, labels, top_n=5):
    print("[INFO] Extracting micro-genre keywords")
    df = df.copy()
    df["cluster"] = labels
    cluster_names = {}

    for c in sorted(df["cluster"].unique()):
        cluster_df = df[df["cluster"] == c]
        if len(cluster_df) == 0:
            continue
        tfidf = TfidfVectorizer(max_features=50, stop_words="english")
        tfidf_matrix = tfidf.fit_transform(cluster_df["clean_text"].fillna(""))
        keywords = tfidf.get_feature_names_out()[:top_n]
        top_movies = cluster_df.nlargest(3, "popularity")["title"].tolist() if "popularity" in cluster_df.columns else cluster_df["title"].head(3).tolist()

        cluster_names[c] = {
            "micro_genre": " / ".join(keywords),
            "sample_movies": top_movies
        }
        print(f" - Cluster {c}: {cluster_names[c]}")

    return cluster_names

# ----------------------------
# 5) Save Results
# ----------------------------
def save_clusters(df, cluster_names, path):
    df_out = df.copy()
    df_out["micro_genre_name"] = df_out["cluster"].apply(lambda x: cluster_names.get(x, {}).get("micro_genre", ""))
    df_out["sample_movies"] = df_out["cluster"].apply(lambda x: ", ".join(cluster_names.get(x, {}).get("sample_movies", [])))
    df_out.to_csv(path, index=False)
    print(f"\n>> Saved final clustering result to {path}")

# ----------------------------
# 6) Visualization
# ----------------------------
def visualize_clusters(hybrid_vec, labels, df, output_dir=OUTPUT_DIR):
    print("[INFO] Running PCA for visualization...")
    pca = PCA(n_components=2, random_state=42)
    pca_vec = pca.fit_transform(hybrid_vec)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(pca_vec[:, 0], pca_vec[:, 1], c=labels, cmap='tab10', s=10, alpha=0.7)
    plt.legend(*scatter.legend_elements(), title="Cluster")
    plt.title("PCA of Movie Hybrid Features")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    pca_path = os.path.join(output_dir, "pca_clusters.png")
    plt.savefig(pca_path, dpi=150)
    plt.close()
    print(f"[INFO] PCA plot saved to {pca_path}")

    print("[INFO] Running UMAP for visualization...")
    reducer = umap.UMAP(n_components=2, random_state=42)
    umap_vec = reducer.fit_transform(hybrid_vec)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(umap_vec[:, 0], umap_vec[:, 1], c=labels, cmap='tab10', s=10, alpha=0.7)
    plt.legend(*scatter.legend_elements(), title="Cluster")
    plt.title("UMAP of Movie Hybrid Features")
    plt.xlabel("UMAP1")
    plt.ylabel("UMAP2")
    plt.tight_layout()
    umap_path = os.path.join(output_dir, "umap_clusters.png")
    plt.savefig(umap_path, dpi=150)
    plt.close()
    print(f"[INFO] UMAP plot saved to {umap_path}")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("=== Phase 4: Clustering and Micro-Genre Naming (Fixed) ===")

    embeddings = load_embeddings(prefer_npy=True)
    df = load_data(INPUT_DATA_PATH)
    df = extract_basic_features(df)

    # Build features according to mode
    print("[INFO] Building hybrid feature vectors...")
    hybrid_vec = build_hybrid_features(df, embeddings,
                                       mode=FEATURE_MODE,
                                       tfidf_max_features=TFIDF_MAX_FEATURES,
                                       tfidf_weight=TFIDF_WEIGHT,
                                       tfidf_pca_dim=TFIDF_PCA_DIM)
    print(f"[INFO] Hybrid feature vector shape = {hybrid_vec.shape}")

    # Determine K using elbow heuristic
    print("[INFO] Searching for optimal K using Elbow heuristic (and fallback to silhouette)...")
    chosen_k, ks, inertias, reason = find_k_elbow(hybrid_vec, k_range=N_CLUSTERS_RANGE, rel_improve_threshold=0.03)

    # Force k if requested
    if FORCE_K is not None:
        chosen_k = int(FORCE_K)
        reason = f"Forced to k={chosen_k} by config."

    # For reproducibility set default if chosen_k is None
    if chosen_k is None:
        chosen_k = 50
        reason = "Fallback to default k=50"

    # Try KMeans first
    tested = ["K-Means", "HDBSCAN" if HAS_HDBSCAN else "HDBSCAN(not_installed)", "Agglomerative"]
    labels_km, km_model = perform_kmeans(hybrid_vec, chosen_k)

    # Optionally try other algorithms for diagnostics (do not override chosen result)
    labels_agg, agg_model = perform_agglomerative(hybrid_vec, chosen_k)
    labels_hdb = None
    if HAS_HDBSCAN:
        try:
            labels_hdb, hdb_model = perform_hdbscan(hybrid_vec, min_cluster_size=15)
        except Exception as e:
            print(f"[WARN] HDBSCAN failed: {e}")

    # Visualization and outputs based on KMeans labels
    visualize_clusters(hybrid_vec, labels_km, df, output_dir=OUTPUT_DIR)

    print("\n=== Cluster Distribution (KMeans) ===")
    print(pd.Series(labels_km).value_counts())

    df["cluster"] = labels_km
    cluster_names = extract_cluster_keywords(df, labels_km)
    save_clusters(df, cluster_names, OUTPUT_CLUSTER_PATH)

    # Print summary in requested format
    pretty_print_choice(tested=tested, chosen_name="K-Means", chosen_k=chosen_k, reason=reason)

    print("=== DONE ===")
