import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.title("Explorer — ค้นหาหนัง")

@st.cache_data
def load_data():
    # Load movie clusters
    clusters_df = pd.read_parquet("movie_clusters_keybert.parquet")
    
    # Load raw movies for poster_path and genres
    movies_file = Path("../data/raw/raw_movies.json")
    with open(movies_file, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
    
    movies_df = pd.DataFrame(movies_data)[['title', 'poster_path', 'genres']]
    
    # Load cleaned movies for additional details
    cleaned_file = Path("../data/processed/cleaned_movies.csv")
    if cleaned_file.exists():
        cleaned_df = pd.read_csv(cleaned_file)
        # Merge all data
        merged_df = clusters_df.merge(movies_df, on='title', how='left')
        merged_df = merged_df.merge(cleaned_df, on='title', how='left', suffixes=('', '_cleaned'))
    else:
        merged_df = clusters_df.merge(movies_df, on='title', how='left')
    
    return merged_df

def split_micro_genres(micro_genre_text):
    """Split micro genres by / and return as list"""
    if pd.isna(micro_genre_text) or not micro_genre_text:
        return []
    return [genre.strip() for genre in str(micro_genre_text).split('/')]

df = load_data()

# Get all unique micro genres
all_micro_genres = []
for micro_genre in df['micro_genre_keybert'].dropna():
    all_micro_genres.extend(split_micro_genres(micro_genre))
unique_micro_genres = ["All"] + sorted(set(all_micro_genres))

# Filter
col1, col2 = st.columns(2)
with col1:
    selected = st.selectbox("Micro-Genre", unique_micro_genres)
with col2:
    keyword = st.text_input("ค้นหาชื่อหนัง")

result = df.copy()

# Apply session state filters
if 'filter_genre' in st.session_state:
    result = result[result['genres'].fillna('').str.contains(st.session_state['filter_genre'], case=False, na=False)]
    st.info(f"Filtered by genre: {st.session_state['filter_genre']}")
    if st.button("Clear genre filter"):
        del st.session_state['filter_genre']
        st.rerun()

if 'filter_micro_genre' in st.session_state:
    result = result[result['micro_genre_keybert'].fillna('').str.contains(st.session_state['filter_micro_genre'], case=False, na=False)]
    st.info(f"Filtered by micro genre: {st.session_state['filter_micro_genre']}")
    if st.button("Clear micro genre filter"):
        del st.session_state['filter_micro_genre']
        st.rerun()

if selected != "All":
    result = result[result['micro_genre_keybert'].fillna('').str.contains(selected, case=False, na=False)]

if keyword:
    result = result[result['title'].fillna('').str.contains(keyword, case=False, na=False)]

# Limit to first 10 results if no search
if not keyword and selected == "All" and 'filter_genre' not in st.session_state and 'filter_micro_genre' not in st.session_state:
    result = result.head(10)

st.subheader(f"ผลลัพธ์ ({len(result)} เรื่อง)")

# Display results as poster grid
cols = st.columns(4)
for idx, (_, row) in enumerate(result.iterrows()):
    col = cols[idx % 4]
    
    with col:
        if pd.notna(row.get('poster_path')):
            poster_url = f"https://image.tmdb.org/t/p/w300{row['poster_path']}"
            
            # Display poster
            st.image(poster_url, use_container_width=True)
            
            # Clickable title
            if st.button(
                row['title'][:30] + "..." if len(row['title']) > 30 else row['title'],
                key=f"title_{idx}",
                use_container_width=True
            ):
                @st.dialog(f"🎬 {row['title']}", width="large")
                def show_movie_details():
                    col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])
                    
                    with col1:
                        st.image(poster_url, width=300)
                        
                        # Overview
                        if pd.notna(row.get('overview')):
                            st.write("**เรื่องย่อ:**")
                            st.write(row['overview'])
                    
                    with col2:
                        # Movie details
                        st.write(f"**คะแนน:** {row.get('vote_average', 'N/A')}/10")
                        st.write(f"**ความนิยม:** {row.get('popularity', 'N/A')}")
                        st.write(f"**วันที่ออกฉาย:** {row.get('release_date', 'N/A')}")
                        st.write(f"**ภาษา:** {row.get('original_language', 'N/A')}")
                        st.write(f"**รายได้:** {row.get('revenue', 'N/A')}")
                        st.write(f"**งบประมาณ:** {row.get('budget', 'N/A')}")
                        st.write(f"**สถานะ:** {row.get('status', 'N/A')}")
                        
                        # Original genres
                        if pd.notna(row.get('genres')):
                            st.write("**Original Genres:**")
                            for genre in str(row['genres']).split('/'):
                                if st.button(genre.strip(), key=f"dialog_orig_{idx}_{genre.strip()}"):
                                    st.session_state['filter_genre'] = genre.strip()
                                    st.rerun()
                        
                        # Show genre from parquet file if available
                        if pd.notna(row.get('genre')):
                            st.write("**Genres:**")
                            st.write(row['genre'])
                    
                    with col3:
                        st.write(f"**Movie ID:** {row.get('movie_id', 'N/A')}")
                        st.write(f"**Cluster:** {row.get('cluster', 'N/A')}")
                        st.write(f"**Micro Genre Name:** {row.get('micro_genre_name', 'N/A')}")
                    
                    with col4:
                        # Micro genres
                        micro_genres = split_micro_genres(row.get('micro_genre_keybert', ''))
                        if micro_genres:
                            st.write("**Micro Genres:**")
                            for genre in micro_genres:
                                if st.button(genre, key=f"dialog_micro_{idx}_{genre}"):
                                    st.session_state['filter_micro_genre'] = genre
                                    st.rerun()
                
                show_movie_details()
        else:
            if st.button(f"🎬 {row['title']}", key=f"no_poster_{idx}"):
                @st.dialog(f"🎬 {row['title']}", width="large")
                def show_movie_details_no_poster():
                    col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])
                    
                    with col1:
                        # Overview
                        if pd.notna(row.get('overview')):
                            st.write("**เรื่องย่อ:**")
                            st.write(row['overview'])
                    
                    with col2:
                        # Movie details
                        st.write(f"**คะแนน:** {row.get('vote_average', 'N/A')}/10")
                        st.write(f"**ความนิยม:** {row.get('popularity', 'N/A')}")
                        st.write(f"**วันที่ออกฉาย:** {row.get('release_date', 'N/A')}")
                        st.write(f"**ภาษา:** {row.get('original_language', 'N/A')}")
                        
                        # Original genres
                        if pd.notna(row.get('genres')):
                            st.write("**Original Genres:**")
                            for genre in str(row['genres']).split('/'):
                                if st.button(genre.strip(), key=f"dialog_np_orig_{idx}_{genre}"):
                                    st.session_state['filter_genre'] = genre.strip()
                                    st.rerun()
                        
                        # Show genre from parquet file if available
                        if pd.notna(row.get('genre')):
                            st.write("**Genres:**")
                            st.write(row['genre'])
                    
                    with col3:
                        st.write(f"**Movie ID:** {row.get('movie_id', 'N/A')}")
                        st.write(f"**Cluster:** {row.get('cluster', 'N/A')}")
                        st.write(f"**Micro Genre Name:** {row.get('micro_genre_name', 'N/A')}")
                    
                    with col4:
                        # Micro genres
                        micro_genres = split_micro_genres(row.get('micro_genre_keybert', ''))
                        if micro_genres:
                            st.write("**Micro Genres:**")
                            for genre in micro_genres:
                                if st.button(genre, key=f"dialog_np_micro_{idx}_{genre}"):
                                    st.session_state['filter_micro_genre'] = genre
                                    st.rerun()
                
                show_movie_details_no_poster()