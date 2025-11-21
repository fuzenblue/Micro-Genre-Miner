import os
import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import umap


# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_embeddings.pkl")
INPUT_DATA_PATH = os.path.join(BASE_DIR, "../../data/cleaned/cleaned_movies.csv")
OUTPUT_CLUSTER_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters.csv")
N_CLUSTERS_RANGE = range(5, 16)  # ทดลองตั้งแต่ 5 - 15 cluster
TFIDF_MAX_FEATURES = 2000
TFIDF_WEIGHT = 2.0

print(f"DEBUG: BASE_DIR = {BASE_DIR}")
print(f"DEBUG: EMBEDDING_PATH exists? {os.path.exists(EMBEDDING_PATH)}")
print(f"DEBUG: INPUT_DATA_PATH exists? {os.path.exists(INPUT_DATA_PATH)}")

# ----------------------------
# Feature Engineering
# ----------------------------
def build_hybrid_features(df, embeddings, tfidf_max_features=2000, tfidf_weight=2.0):
    """
    สร้าง hybrid feature vector สำหรับ clustering
    -------------------------------------------------
    df: pandas DataFrame ที่มีคอลัมน์ 'clean_text' + numeric features
    embeddings: numpy array ของ sentence embeddings
    tfidf_max_features: จำนวน feature ของ TF-IDF
    tfidf_weight: น้ำหนักของ TF-IDF เทียบกับ embedding
    """
    # 1) TF-IDF
    tfidf = TfidfVectorizer(max_features=tfidf_max_features, stop_words="english")
    tfidf_vec = tfidf.fit_transform(df["clean_text"]).toarray()
    
    # 2) Numeric features
    numeric_vec = df[["desc_length", "num_keywords", "sentiment_score"]].values
    
    # 3) รวมเข้าด้วยกัน
    hybrid_vec = np.hstack([
        embeddings,                   # sentence embeddings
        tfidf_vec * tfidf_weight,     # TF-IDF (เพิ่มน้ำหนัก)
        numeric_vec                   # numeric features
    ])
    
    return hybrid_vec
# ----------------------------
# Numeric Feature Engineering
# ----------------------------
def extract_basic_features(df):
    """
    สร้าง numeric features: desc_length, num_keywords, sentiment_score
    """
    print("[INFO] Extracting basic numeric features...")
    df["desc_length"] = df["clean_text"].str.len()
    df["num_keywords"] = df["clean_text"].str.split().apply(len)
    df["sentiment_score"] = df["clean_text"].apply(lambda x: TextBlob(x).sentiment.polarity)
    return df

# ----------------------------
# 1) Load Data & Embedding
# ----------------------------
def load_embeddings(path):
    print(f"[INFO] Loading embeddings from: {path}")
    with open(path, "rb") as f:
        emb = pickle.load(f)
    print(f"[INFO] Embeddings loaded, shape = {emb.shape}")
    return emb

def load_data(path):
    print(f"[INFO] Loading cleaned data from: {path}")
    df = pd.read_csv(path)
    if "clean_text" not in df.columns:
        raise ValueError("ERROR: ต้องมี column clean_text")
    print(f"[INFO] Data loaded, rows = {len(df)}")
    return df.copy()

# ----------------------------
# 2) Find Optimal K (Silhouette Score)
# ----------------------------
def find_optimal_k(vectors):
    best_k = None
    best_score = -1

    for k in N_CLUSTERS_RANGE:
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(vectors)
            score = silhouette_score(vectors, labels)
            print(f"k = {k}, silhouette_score = {score:.4f}")
            if score > best_score:
                best_score = score
                best_k = k
        except Exception as e:
            print(f"[ERROR] silhouette_score failed for k={k}: {e}")
            continue

    print(f"\n>> Optimal K = {best_k} (Silhouette = {best_score:.4f})")
    return best_k

# ----------------------------
# 3) Cluster
# ----------------------------
def perform_clustering(vectors, k):
    print(f"[INFO] Clustering using K = {k}")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(vectors)
    print(f"[INFO] Clustering completed")
    return labels

# ----------------------------
# 4) Extract Micro-Genre Name
# ----------------------------
def extract_cluster_keywords(df, labels):
    print("[INFO] Extracting micro-genre keywords")
    df["cluster"] = labels
    cluster_names = {}

    for c in sorted(df["cluster"].unique()):
        cluster_df = df[df["cluster"] == c]

        # ใช้ TF-IDF เพื่อ extract คำเด่น
        tfidf = TfidfVectorizer(max_features=50, stop_words="english")
        tfidf_matrix = tfidf.fit_transform(cluster_df["clean_text"])
        keywords = tfidf.get_feature_names_out()[:5]  # เลือก top 5

        # representative movies
        top_movies = cluster_df.nlargest(3, "popularity")["title"].tolist()

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
    df["micro_genre_name"] = df["cluster"].apply(lambda x: cluster_names[x]["micro_genre"])
    df["sample_movies"] = df["cluster"].apply(lambda x: ", ".join(cluster_names[x]["sample_movies"]))
    df.to_csv(path, index=False)
    print(f"\n>> Saved final clustering result to {path}")

# ----------------------------
# 6) Visualization
# ----------------------------
def visualize_clusters(hybrid_vec, labels, df, output_dir="../../data/processed"):
    
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "../../data/processed")
    os.makedirs(output_dir, exist_ok=True)
    # ----------------------------
    # PCA
    # ----------------------------
    print("[INFO] Running PCA for visualization...")
    pca = PCA(n_components=2)
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

    # ----------------------------
    # UMAP
    # ----------------------------
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
    print("=== Phase 4: Clustering and Micro-Genre Naming ===")

    embeddings = load_embeddings(EMBEDDING_PATH)
    df = load_data(INPUT_DATA_PATH)
    df = extract_basic_features(df)
    # ใช้ hybrid feature vector
    print("[INFO] Building hybrid feature vectors...")
    hybrid_vec = build_hybrid_features(df, embeddings, tfidf_max_features=TFIDF_MAX_FEATURES, tfidf_weight=TFIDF_WEIGHT)
    print(f"[INFO] Hybrid feature vector shape = {hybrid_vec.shape}")
    

    optimal_k = find_optimal_k(hybrid_vec)
    labels = perform_clustering(hybrid_vec, optimal_k)
    # เรียกใช้งาน visualization
    visualize_clusters(hybrid_vec, labels, df)

    print("\n=== Cluster Distribution ===")
    print(pd.Series(labels).value_counts())

    cluster_names = extract_cluster_keywords(df, labels)
    save_clusters(df, cluster_names, OUTPUT_CLUSTER_PATH)

    print("=== DONE ===")
