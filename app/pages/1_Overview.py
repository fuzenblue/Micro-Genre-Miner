import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

st.title("📊 Overview — ภาพรวมข้อมูล")

@st.cache_data
def load_data():
    return pd.read_parquet("movie_clusters_keybert.parquet")

df = load_data()

# Top-Level Metrics (KPI Cards)
st.markdown("### 📈 สถิติหลัก")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎬 ภาพยนตร์ทั้งหมด",
        value=f"{len(df):,}",
        help="จำนวนหนังทั้งหมดในฐานข้อมูล"
    )

with col2:
    st.metric(
        label="🎭 Micro-Genres",
        value=f"{df['micro_genre_keybert'].nunique()}",
        help="จำนวนกลุ่มย่อยที่ระบบจัดแบ่ง"
    )

with col3:
    avg_rating = df['vote_average'].mean() if 'vote_average' in df.columns else 0
    st.metric(
        label="⭐ คะแนนเฉลี่ย",
        value=f"{avg_rating:.1f}/10" if avg_rating > 0 else "N/A",
        help="คะแนนเฉลี่ยของหนังทั้งหมด"
    )

with col4:
    year_span = df['year'].max() - df['year'].min() if 'year' in df.columns else 0
    st.metric(
        label="📅 ช่วงเวลา",
        value=f"{year_span:.0f} ปี" if year_span > 0 else "N/A",
        help=f"ตั้งแต่ปี {df['year'].min():.0f} ถึง {df['year'].max():.0f}"
    )

st.markdown("---")

# Micro-Genre Distribution (Treemap)
st.markdown("### 🗺️ การกระจายตัวของ Micro-Genres")

# Prepare data for treemap
genre_counts = df['micro_genre_keybert'].value_counts().head(20)
genre_data = pd.DataFrame({
    'genre': genre_counts.index,
    'count': genre_counts.values,
    'percentage': (genre_counts.values / len(df) * 100).round(1)
})

# Create treemap
fig_treemap = px.treemap(
    genre_data,
    path=['genre'],
    values='count',
    title="Top 20 Micro-Genres (ขนาดกล่อง = จำนวนหนัง)",
    hover_data={'percentage': True},
    color='count',
    color_continuous_scale='Viridis'
)

fig_treemap.update_traces(
    textinfo="label+value",
    textfont_size=12,
    hovertemplate='<b>%{label}</b><br>จำนวน: %{value} เรื่อง<br>สัดส่วน: %{customdata[0]}%<extra></extra>'
)

fig_treemap.update_layout(
    height=500,
    font=dict(size=14)
)

st.plotly_chart(fig_treemap, use_container_width=True)

# Insights box
st.info("""
💡 **Insight:** กล่องใหญ่แสดงถึง Micro-Genre ที่มีหนังเยอะ (แนวหลัก) 
ส่วนกล่องเล็กๆ คือกลุ่มเฉพาะ (Niche) ที่แสดงความละเอียดของระบบ AI
""")

st.markdown("---")

# Top Rankings
st.markdown("### 🏆 Top 10 Micro-Genres ยอดนิยม")

top_genres = df['micro_genre_keybert'].value_counts().head(10)

fig_bar = px.bar(
    x=top_genres.values,
    y=top_genres.index,
    orientation='h',
    title="จำนวนหนังในแต่ละ Micro-Genre",
    labels={'x': 'จำนวนหนัง', 'y': 'Micro-Genre'},
    color=top_genres.values,
    color_continuous_scale='Blues'
)

fig_bar.update_layout(
    height=400,
    yaxis={'categoryorder': 'total ascending'},
    showlegend=False
)

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("### ⭐ Top 10 Micro-Genres คุณภาพสูง")

if 'vote_average' in df.columns:
    # Calculate average rating per genre (only genres with 5+ movies)
    genre_ratings = df.groupby('micro_genre_keybert').agg({
        'vote_average': 'mean',
        'title': 'count'
    }).rename(columns={'title': 'movie_count'})
    
    # Filter genres with at least 5 movies
    quality_genres = genre_ratings[genre_ratings['movie_count'] >= 5].sort_values('vote_average', ascending=False).head(10)
    
    fig_quality = px.bar(
        quality_genres,
        x='vote_average',
        y=quality_genres.index,
        orientation='h',
        title="คะแนนเฉลี่ยของแต่ละ Micro-Genre",
        labels={'vote_average': 'คะแนนเฉลี่ย', 'y': 'Micro-Genre'},
        color='vote_average',
        color_continuous_scale='Reds',
        hover_data=['movie_count']
    )
    
    fig_quality.update_layout(
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    fig_quality.update_traces(
        hovertemplate='<b>%{y}</b><br>คะแนนเฉลี่ย: %{x:.1f}<br>จำนวนหนัง: %{customdata[0]}<extra></extra>'
    )
    
    st.plotly_chart(fig_quality, use_container_width=True)
else:
    st.info("ไม่มีข้อมูลคะแนนในฐานข้อมูล")

st.markdown("---")

# Additional Statistics
st.markdown("### 📊 สถิติเพิ่มเติม")

st.markdown("#### 🎯 ความหลากหลาย")

# Calculate diversity metrics
total_genres = df['micro_genre_keybert'].nunique()
avg_movies_per_genre = len(df) / total_genres

st.write(f"**Micro-Genres ทั้งหมด:** {total_genres}")
st.write(f"**หนังเฉลี่ยต่อกลุ่ม:** {avg_movies_per_genre:.1f} เรื่อง")

# Genre with most/least movies
genre_counts = df['micro_genre_keybert'].value_counts()
st.write(f"**กลุ่มใหญ่สุด:** {genre_counts.index[0]} ({genre_counts.iloc[0]} เรื่อง)")
st.write(f"**กลุ่มเล็กสุด:** {genre_counts.index[-1]} ({genre_counts.iloc[-1]} เรื่อง)")

st.markdown("#### 📅 การกระจายตามเวลา")

if 'year' in df.columns:
    year_stats = df['year'].describe()
    st.write(f"**ปีเก่าสุด:** {year_stats['min']:.0f}")
    st.write(f"**ปีใหม่สุด:** {year_stats['max']:.0f}")
    st.write(f"**ปีเฉลี่ย:** {year_stats['mean']:.0f}")
    
    # Decade distribution
    df_temp = df.copy()
    df_temp['decade'] = (df_temp['year'] // 10) * 10
    decade_counts = df_temp['decade'].value_counts().sort_index()
    peak_decade = decade_counts.idxmax()
    st.write(f"**ทศวรรษที่มีหนังมากสุด:** {peak_decade:.0f}s ({decade_counts[peak_decade]} เรื่อง)")

st.markdown("#### ⭐ คุณภาพ")

if 'vote_average' in df.columns:
    rating_stats = df['vote_average'].describe()
    st.write(f"**คะแนนเฉลี่ย:** {rating_stats['mean']:.1f}/10")
    st.write(f"**คะแนนสูงสุด:** {rating_stats['max']:.1f}/10")
    st.write(f"**คะแนนต่ำสุด:** {rating_stats['min']:.1f}/10")
    
    # High quality movies (8.0+)
    high_quality = len(df[df['vote_average'] >= 8.0])
    st.write(f"**หนังคุณภาพสูง (8.0+):** {high_quality} เรื่อง ({high_quality/len(df)*100:.1f}%)")

# Navigation hint
st.markdown("---")
st.markdown("""
### 🧭 ขั้นตอนถัดไป

🎯 **พร้อมแล้ว?** ลองไปหาหนังที่ชอบใน **Explorer** หรือดูเทรนด์เชิงลึกใน **Trends**

💡 **เคล็ดลับ:** ใช้เมนูด้านซ้ายเพื่อนำทางไปหน้าอื่นๆ
""")