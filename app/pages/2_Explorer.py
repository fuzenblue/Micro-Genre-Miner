import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.title("🔍 Explorer — ค้นหาหนัง")

@st.cache_data
def load_data():
    return pd.read_parquet("movie_clusters_keybert.parquet")

df = load_data()

# Filter
genres = ["All"] + sorted(df["micro_genre_name"].unique())
selected = st.selectbox("Micro-Genre", genres)

keyword = st.text_input("ค้นหาชื่อหนัง")

result = df.copy()
if selected != "All":
    result = result[result["micro_genre_name"] == selected]

if keyword:
    result = result[result["title"].str.contains(keyword, case=False)]

st.subheader("ผลลัพธ์")
st.dataframe(result[["title", "micro_genre_name", "cluster"]])

# Word Cloud
if len(result) > 0:
    text = " ".join(result["description"].dropna().values)
    if text.strip():
        wc = WordCloud(width=800, height=400).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
