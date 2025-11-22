import os
import pandas as pd
from keybert import KeyBERT

# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CLUSTER_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters.csv")
OUTPUT_KEYBERT_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters_keybert.csv")

TOP_KEYWORDS_PER_CLUSTER = 10  # จะเอา top 10 TF-IDF keywords ต่อ cluster
TOP_KEYWORDS_FOR_LABEL = 3     # จะเอา 1-3 keywords เป็น micro-genre label

# ----------------------------
# 1) Load clustered movie data
# ----------------------------
df = pd.read_csv(INPUT_CLUSTER_PATH)
print(f"[INFO] Loaded clustered movies: {len(df)} rows")

# ----------------------------
# 2) Initialize KeyBERT model
# ----------------------------
kw_model = KeyBERT('all-MiniLM-L6-v2')  # lightweight BERT model

# ----------------------------
# 3) Generate micro-genre labels per cluster
# ----------------------------
cluster_labels = {}

for c in sorted(df['cluster'].unique()):
    cluster_df = df[df['cluster'] == c]
    texts = cluster_df['clean_text'].fillna("").tolist()
    
    # combine all text in cluster
    combined_text = " ".join(texts)
    
    # extract top keywords using KeyBERT
    keywords = kw_model.extract_keywords(combined_text, keyphrase_ngram_range=(1,2),
                                         stop_words='english', top_n=TOP_KEYWORDS_FOR_LABEL)
    
    label = " / ".join([kw[0] for kw in keywords]) if keywords else "Unknown-Genre"
    cluster_labels[c] = label
    print(f"[INFO] Cluster {c}: {label}")

# ----------------------------
# 4) Apply labels to dataframe
# ----------------------------
df['micro_genre_keybert'] = df['cluster'].map(cluster_labels)

# ----------------------------
# 5) Optionally, get representative movies (top 5 by popularity)
# ----------------------------
df['sample_movies'] = df.groupby('cluster')['title'].transform(lambda x: ", ".join(x.head(5)))

# ----------------------------
# 6) Save results
# ----------------------------
df.to_csv(OUTPUT_KEYBERT_PATH, index=False)
print(f"[INFO] Saved KeyBERT-enhanced clusters to {OUTPUT_KEYBERT_PATH}")
