import pandas as pd

df = pd.read_csv("data/cleaned/cleaned_movies.csv")

df.to_parquet("app/micro_genre.parquet")
print("✔ Parquet saved to app/micro_genre.parquet")
