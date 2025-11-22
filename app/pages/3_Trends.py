import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Trends")

@st.cache_data
def load_data():
    return pd.read_parquet("micro_genre.parquet")

df = load_data()

st.subheader("จำนวนหนังตามปี")
year_count = df["year"].value_counts().sort_index()

fig, ax = plt.subplots()
year_count.plot(kind="line", marker="o", ax=ax)
st.pyplot(fig)
