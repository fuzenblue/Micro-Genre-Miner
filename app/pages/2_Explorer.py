import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Custom CSS for Mitr font
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    html, body, [class*="css"] {
        font-family: "Mitr", sans-serif !important;
    }
    
    .stApp * {
        font-family: "Mitr", sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: "Mitr", sans-serif !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown, .stMarkdown * {
        font-family: "Mitr", sans-serif !important;
    }
    
    .stSelectbox, .stTextInput, .stButton, .stMetric {
        font-family: "Mitr", sans-serif !important;
    }
    
    div[data-testid="metric-container"] {
        font-family: "Mitr", sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Explorer — ค้นหาหนัง")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init_state("open_dialog", False)
init_state("dialog_row", None)
init_state("dialog_poster", None)
init_state("selected_micro", "All")
init_state("filter_genre", None)
init_state("dialog_key", None)
init_state("last_filters", {"micro": "All", "keyword": "", "genre": None})

# -----------------------------
# RESET DIALOG
# -----------------------------
def reset_dialog():
    st.session_state.open_dialog = False
    st.session_state.dialog_row = None
    st.session_state.dialog_poster = None
    st.session_state.dialog_key = None


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    clusters_df = pd.read_parquet("movie_clusters_keybert.parquet")
    
    movies_file = Path("../data/raw/raw_movies.json")
    with open(movies_file, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)

    movies_df = pd.DataFrame(movies_data)[['title', 'poster_path', 'genres']]
    
    cleaned_file = Path("../data/processed/cleaned_movies.csv")
    if cleaned_file.exists():
        cleaned_df = pd.read_csv(cleaned_file)
        merged_df = clusters_df.merge(movies_df, on='title', how='left')
        merged_df = merged_df.merge(cleaned_df, on='title', how='left', suffixes=('', '_cleaned'))
    else:
        merged_df = clusters_df.merge(movies_df, on='title', how='left')

    return merged_df


def split_micro_genres(txt):
    if pd.isna(txt) or not txt:
        return []
    return [g.strip() for g in str(txt).split('/')]


df = load_data()


# -----------------------------
# MICRO GENRE FILTER OPTIONS
# -----------------------------
all_micro = []
for mg in df['micro_genre_keybert'].dropna():
    all_micro.extend(split_micro_genres(mg))

unique_micro_genres = ["All"] + sorted(set(all_micro))


# -----------------------------
# FILTER UI
# -----------------------------
col1, col2 = st.columns(2)

def reset_micro_filter():
    st.session_state.selected_micro = "All"
    reset_dialog()

def reset_genre_filter():
    st.session_state.filter_genre = None
    reset_dialog()

with col1:
    selected = st.selectbox(
        "Micro-Genre",
        unique_micro_genres,
        key="selected_micro"
    )
    
    if selected != "All":
        st.button("❌ ล้าง Filter Micro-Genre", on_click=reset_micro_filter)

with col2:
    keyword = st.text_input("ค้นหาชื่อหนัง")


# -----------------------------
# FILTER LOGIC
# -----------------------------
result = df.copy()

# Micro-genre filter
if selected != "All":
    result = result[result['micro_genre_keybert'].fillna('').str.contains(
        selected, case=False, na=False)]

# Keyword search
if keyword:
    result = result[result['title'].fillna('').str.contains(keyword, case=False, na=False)]

# Genre filter
if st.session_state.filter_genre:
    result = result[result['genres'].fillna('').str.contains(
        st.session_state.filter_genre, case=False, na=False)]
    st.info(f"Filtered by genre: {st.session_state.filter_genre}")
    st.button("❌ ล้าง Filter Genre", on_click=reset_genre_filter)

# Default show first 12 movies
if selected == "All" and not keyword and not st.session_state.filter_genre:
    result = result.head(100)

st.subheader(f"ผลลัพธ์ ({len(result)} เรื่อง)")


# -----------------------------
# DISPLAY POSTER GRID
# -----------------------------
cols = st.columns(4)
for idx, (_, row) in enumerate(result.iterrows()):
    col = cols[idx % 4]
    with col:
        poster_url = None
        if pd.notna(row.get("poster_path")):
            poster_url = f"https://image.tmdb.org/t/p/w300{row['poster_path']}"

        if poster_url:
            st.image(poster_url, width=250)
        else:
            st.write("📦 ไม่มีโปสเตอร์")

        btn_key = f"open_dialog_{idx}"
        title_lower = row['title']
        label = title_lower[:30] + "..." if len(title_lower) > 30 else title_lower

        if st.button(label, key=btn_key):
            st.session_state.open_dialog = True
            st.session_state.dialog_row = row.to_dict()
            st.session_state.dialog_poster = poster_url
            st.session_state.dialog_key = btn_key
            st.rerun()


# -----------------------------
# MOVIE DIALOG
# -----------------------------
def show_movie_dialog(row, poster_url):

    @st.dialog(f"🎬 {row['title']}", width="large")
    def _dialog():

        col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])

        # COLUMN 1 — Poster & Overview
        with col1:
            if poster_url:
                st.image(poster_url, width=300)
            if pd.notna(row.get("overview")):
                st.write("### เรื่องย่อ")
                st.write(row["overview"])

        # COLUMN 2 — Original Genres
        with col2:
            st.write("### รายละเอียด")
            st.write(f"คะแนน: {row.get('vote_average', 'N/A')}/10")
            st.write(f"ความนิยม: {row.get('popularity', 'N/A')}")
            st.write(f"วันที่ออกฉาย: {row.get('release_date', 'N/A')}")
            st.write(f"ภาษา: {row.get('original_language', 'N/A')}")

            if pd.notna(row.get("genres")):
                st.write("### Original Genres")
                for idx_g, g in enumerate(str(row["genres"]).split('/')):
                    if st.button(g.strip(), key=f"genre_btn_{row['movie_id']}_{idx_g}"):
                        st.session_state.filter_genre = g.strip()
                        reset_dialog()
                        st.rerun()

        # COLUMN 3 — Cluster Info
        with col3:
            st.write("### ข้อมูลระบบ")
            st.write(f"Movie ID: {row.get('movie_id', 'N/A')}")
            st.write(f"Cluster: {row.get('cluster', 'N/A')}")
            st.write(f"Micro Genre Name: {row.get('micro_genre_name', 'N/A')}")

        # COLUMN 4 — Micro Genres
        with col4:
            mg_list = split_micro_genres(row.get("micro_genre_keybert"))
            st.write("### Micro Genres")
            for idx_mg, mg in enumerate(mg_list):
                if st.button(mg, key=f"micro_btn_{row['movie_id']}_{idx_mg}"):
                    st.session_state.selected_micro = mg
                    reset_dialog()
                    st.rerun()

        st.write("---")
        if st.button("❌ ปิดหน้าต่าง"):
            reset_dialog()
            st.rerun()

    _dialog()

# -----------------------------
# AUTO CLOSE DIALOG WHEN FILTER CHANGES
# -----------------------------
current_filters = {
    "micro": st.session_state.selected_micro,
    "keyword": keyword,
    "genre": st.session_state.filter_genre,
}

# ถ้า filter เปลี่ยนจากรอบก่อนหน้า → ต้องปิด dialog
if current_filters != st.session_state.last_filters:
    reset_dialog()
    st.session_state.last_filters = current_filters

# แสดง dialog
if st.session_state.open_dialog and st.session_state.dialog_row:
    show_movie_dialog(
        st.session_state.dialog_row,
        st.session_state.dialog_poster
    )
