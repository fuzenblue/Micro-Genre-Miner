# llm_workflow.py
import os
import pandas as pd
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CLUSTER_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters.csv")
OUTPUT_LLM_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters_llm.csv")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable.")

openai.api_key = OPENAI_API_KEY

# ----------------------------
# 1) Load cluster data
# ----------------------------
df = pd.read_csv(INPUT_CLUSTER_PATH)
print(f"[INFO] Loaded clustered movies: {len(df)} rows")

# ----------------------------
# 2) Helper: LLM micro-genre suggestion
# ----------------------------
def suggest_micro_genre(movie_title, description, current_micro_genre):
    """
    ส่ง prompt ไป LLM เพื่อให้ generate concise micro-genre
    """
    prompt = f"""
Movie Title: "{movie_title}"
Description: "{description}"
Current micro-genre: "{current_micro_genre}"

Suggest a concise, meaningful micro-genre (1-3 words) for this movie:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            mmessages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarize Frankenstein in one sentence."}
            ],
            temperature=0.5,
            max_tokens=20
        )
        suggested = response.choices[0].message.content.strip()
        return suggested
    except Exception as e:
        print(f"[ERROR] LLM failed for '{movie_title}': {e}")
        return current_micro_genre  # fallback

# ----------------------------
# 3) Apply LLM to dataset (example: first 50 movies)
# ----------------------------
df["micro_genre_llm"] = df.apply(
    lambda row: suggest_micro_genre(row["title"], row["clean_text"], row["micro_genre_name"]),
    axis=1
)

# ----------------------------
# 4) Save results
# ----------------------------
df.to_csv(OUTPUT_LLM_PATH, index=False)
print(f"[INFO] Saved LLM-enhanced clusters to {OUTPUT_LLM_PATH}")

# ----------------------------
# 5) Optional: Semantic similarity recommendation
# ----------------------------
# Example: find top 5 similar movies based on cluster embedding
# Assuming df has "embedding" column (numpy array saved as string)
def recommend_similar_movies(target_index, top_k=5):
    embeddings = np.vstack(df["embedding"].apply(lambda x: np.fromstring(x[1:-1], sep=' ')))
    sim = cosine_similarity([embeddings[target_index]], embeddings)[0]
    top_idx = sim.argsort()[::-1][1:top_k+1]  # skip self
    return df.iloc[top_idx][["title", "micro_genre_llm"]].to_dict(orient="records")

# Example usage
print(recommend_similar_movies(target_index=0, top_k=5))
