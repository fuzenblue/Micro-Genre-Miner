import pandas as pd
import os

# ----------------------------
# CONFIG
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "../../data/processed/movie_clusters_keybert.csv")  # ไฟล์ output ปัจจุบัน
OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "movie_clusters_keybert.csv")  # เซฟลง Downloads

# ----------------------------
# LOAD CSV
# ----------------------------
df = pd.read_csv(INPUT_PATH)
print(f"[INFO] Loaded CSV, shape = {df.shape}")

# ----------------------------
# SAVE TO LOCAL PC
# ----------------------------
df.to_csv(OUTPUT_PATH, index=False)
print(f">> CSV saved to: {OUTPUT_PATH}")
print("[INFO] Download complete.")