import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import umap
import matplotlib.pyplot as plt
from textblob import TextBlob


# ----------------------------
# CONFIG
# ----------------------------
INPUT_PATH = "data/cleaned/cleaned_movies.csv"
OUTPUT_PATH = "data/processed/movie_embeddings.pkl"
USE_EMBEDDING = True         # False = TF-IDF, True = SentenceTransformers
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ----------------------------
# 1) Load Cleaned Data
# ----------------------------
def load_data(path):
    df = pd.read_csv(path)
    if "clean_text" not in df.columns:
        raise ValueError("ERROR: ต้องมี column clean_text ในไฟล์ cleaned data")
    return df


# ----------------------------
# 2) Basic Feature Engineering
# ----------------------------
def extract_basic_features(df):
    df["desc_length"] = df["clean_text"].str.len()
    df["num_keywords"] = df["clean_text"].str.split().apply(len)
    df["sentiment_score"] = df["clean_text"].apply(lambda x: TextBlob(x).sentiment.polarity)
    return df


# ----------------------------
# 3) Embedding (TF-IDF หรือ Sentence Embedding)
# ----------------------------
def vectorize_text(df):
    texts = df["clean_text"].tolist()

    if USE_EMBEDDING:
        print(">> Using Sentence Embedding:", EMBED_MODEL)
        model = SentenceTransformer(EMBED_MODEL)
        vectors = model.encode(texts, show_progress_bar=True)
    else:
        print(">> Using TF-IDF Vectorizer")
        vectorizer = TfidfVectorizer(max_features=2000)
        vectors = vectorizer.fit_transform(texts).toarray()

    return vectors


# ----------------------------
# 4) Combine vectors + basic features
# ----------------------------
def combine_features(text_vec, df):
    numeric = df[["desc_length", "num_keywords", "sentiment_score"]].values
    return np.hstack([text_vec, numeric])


# ----------------------------
# 5) PCA / UMAP Visualization
# ----------------------------
def plot_distribution(vectors, output_dir="data/processed"):
    os.makedirs(output_dir, exist_ok=True)

    print(">> Running PCA...")
    pca = PCA(n_components=2)
    pca_vec = pca.fit_transform(vectors)

    plt.figure(figsize=(6, 6))
    plt.scatter(pca_vec[:,0], pca_vec[:,1], s=4)
    plt.title("PCA Distribution")
    plt.savefig(os.path.join(output_dir, "pca_distribution.png"))
    plt.close()

    print(">> Running UMAP...")
    reducer = umap.UMAP(n_components=2)
    umap_vec = reducer.fit_transform(vectors)

    plt.figure(figsize=(6, 6))
    plt.scatter(umap_vec[:,0], umap_vec[:,1], s=4)
    plt.title("UMAP Distribution")
    plt.savefig(os.path.join(output_dir, "umap_distribution.png"))
    plt.close()

    print(">> Saved PCA & UMAP distribution plots")


# ----------------------------
# 6) Save Output
# ----------------------------
def save_pickle(data, path):
    with open(path, "wb") as f:
        pickle.dump(data, f)
    print(f">> Saved: {path}")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("=== Phase 3: Feature Engineering & Vectorization ===")

    df = load_data(INPUT_PATH)
    df = extract_basic_features(df)

    vec = vectorize_text(df)
    combined = combine_features(vec, df)

    save_pickle(combined, OUTPUT_PATH)

    plot_distribution(combined)

    print("=== DONE ===")
