import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Overview")

@st.cache_data
def load_data():
    return pd.read_parquet("micro_genre.parquet")

df = load_data()

st.subheader("จำนวนหนังในแต่ละ Micro-Genre")
genre_count = df['micro_genre'].value_counts()

fig, ax = plt.subplots()
genre_count.head(20).plot(kind='bar', ax=ax)
st.pyplot(fig)
