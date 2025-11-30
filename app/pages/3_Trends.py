import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import re

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

st.title("📈 Trends — วิเคราะห์เทรนด์เชิงลึก")

@st.cache_data
def load_data():
    return pd.read_parquet("movie_clusters_keybert.parquet")

df = load_data()

# Ensure we have year data
if 'year' not in df.columns:
    st.error("ไม่พบข้อมูลปีในฐานข้อมูล")
    st.stop()

st.markdown("---")

# 1. Time-Series Analysis
st.markdown("## 📊 1. การวิเคราะห์ตามกาลเวลา")

st.markdown("### 🎬 The Rise and Fall of Micro-Genres")

# Get individual genres (split by /)
all_genres = []
for genre_str in df['micro_genre_keybert'].dropna():
    genres = [g.strip() for g in str(genre_str).split('/')]
    all_genres.extend(genres)

top_genres = pd.Series(all_genres).value_counts().head(15).index.tolist()

# Multi-select for genre comparison
selected_genres = st.multiselect(
    "เลือก Micro-Genres ที่ต้องการเปรียบเทียบ (สูงสุด 5 กลุ่ม):",
    options=top_genres,
    default=top_genres[:3],
    max_selections=5,
    help="เลือกกลุ่มที่สนใจเพื่อดูเทรนด์การเปลี่ยนแปลงตามเวลา"
)

if selected_genres:
    # Create time series data
    time_series_data = []
    
    for genre in selected_genres:
        genre_df = df[df['micro_genre_keybert'].str.contains(genre, case=False, na=False)]
        yearly_counts = genre_df.groupby('year').size().reset_index(name='count')
        yearly_counts['genre'] = genre
        time_series_data.append(yearly_counts)
    
    combined_data = pd.concat(time_series_data, ignore_index=True)
    
    # Create multi-line chart
    fig_timeline = px.line(
        combined_data,
        x='year',
        y='count',
        color='genre',
        title="จำนวนหนังที่ผลิตในแต่ละปี",
        labels={'year': 'ปี', 'count': 'จำนวนหนัง', 'genre': 'Micro-Genre'},
        markers=True
    )
    
    fig_timeline.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Insights
    st.info("""
    💡 **Insight:** เส้นกราฟแสดงให้เห็นการเปลี่ยนแปลงความนิยมของแต่ละ Micro-Genre ตามยุคสมัย 
    เช่น หนัง Superhero อาจพุ่งสูงในช่วง 2010s หรือ Horror Slasher ได้รับความนิยมในยุค 80s
    """)

# Heatmap Calendar
st.markdown("### 🗓️ ความหนาแน่นการผลิตหนังตามปี")

# Create decade-based heatmap
df_heatmap = df.copy()
df_heatmap['decade'] = (df_heatmap['year'] // 10) * 10

# Get top 10 genres for heatmap
top_10_genres = df['micro_genre_keybert'].value_counts().head(10).index

heatmap_data = df_heatmap[df_heatmap['micro_genre_keybert'].isin(top_10_genres)]
heatmap_pivot = heatmap_data.groupby(['decade', 'micro_genre_keybert']).size().unstack(fill_value=0)

fig_heatmap = px.imshow(
    heatmap_pivot.T,
    title="ความหนาแน่นของ Micro-Genres ในแต่ละทศวรรษ",
    labels={'x': 'ทศวรรษ', 'y': 'Micro-Genre', 'color': 'จำนวนหนัง'},
    aspect='auto',
    color_continuous_scale='YlOrRd'
)

fig_heatmap.update_layout(height=400)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# 2. Semantic Analysis
st.markdown("## ☁️ 2. การวิเคราะห์ความหมาย (Semantic Analysis)")

st.markdown("### 🔤 Dynamic Word Cloud")

# Genre selection for word cloud
selected_genre_wc = st.selectbox(
    "เลือก Micro-Genre เพื่อดู Word Cloud:",
    options=top_genres,
    help="เลือกกลุ่มที่สนใจเพื่อดูคำสำคัญที่ปรากฏบ่อยใน Plot"
)

if selected_genre_wc:
    # Get movies from selected genre (contains the selected genre)
    genre_movies = df[df['micro_genre_keybert'].str.contains(selected_genre_wc, case=False, na=False)]
    
    # Create word cloud from overview/plot text if available
    if 'overview' in df.columns:
        # Combine all overviews from the selected genre
        text_data = ' '.join(genre_movies['overview'].dropna().astype(str))
        
        # Clean text (basic preprocessing)
        text_data = re.sub(r'[^\w\s]', ' ', text_data.lower())
        text_data = re.sub(r'\s+', ' ', text_data)
        
        # Enhanced stop words list
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'his', 'their', 'one', 'two', 'three', 'who', 'what', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'get', 'gets', 'got', 'make', 'makes', 'made', 'take', 'takes', 'took', 'come', 'comes', 'came', 'go', 'goes', 'went', 'see', 'sees', 'saw', 'know', 'knows', 'knew', 'think', 'thinks', 'thought', 'say', 'says', 'said', 'tell', 'tells', 'told', 'ask', 'asks', 'asked', 'work', 'works', 'worked', 'seem', 'seems', 'seemed', 'feel', 'feels', 'felt', 'try', 'tries', 'tried', 'leave', 'leaves', 'left', 'put', 'puts', 'end', 'ends', 'ended', 'find', 'finds', 'found', 'give', 'gives', 'gave', 'turn', 'turns', 'turned', 'start', 'starts', 'started', 'show', 'shows', 'showed', 'hear', 'hears', 'heard', 'play', 'plays', 'played', 'run', 'runs', 'ran', 'move', 'moves', 'moved', 'live', 'lives', 'lived', 'believe', 'believes', 'believed', 'hold', 'holds', 'held', 'bring', 'brings', 'brought', 'happen', 'happens', 'happened', 'write', 'writes', 'wrote', 'sit', 'sits', 'sat', 'stand', 'stands', 'stood', 'lose', 'loses', 'lost', 'pay', 'pays', 'paid', 'meet', 'meets', 'met', 'include', 'includes', 'included', 'continue', 'continues', 'continued', 'set', 'sets', 'follow', 'follows', 'followed', 'stop', 'stops', 'stopped', 'create', 'creates', 'created', 'speak', 'speaks', 'spoke', 'read', 'reads', 'allow', 'allows', 'allowed', 'add', 'adds', 'added', 'spend', 'spends', 'spent', 'grow', 'grows', 'grew', 'open', 'opens', 'opened', 'walk', 'walks', 'walked', 'win', 'wins', 'won', 'offer', 'offers', 'offered', 'remember', 'remembers', 'remembered', 'love', 'loves', 'loved', 'consider', 'considers', 'considered', 'appear', 'appears', 'appeared', 'buy', 'buys', 'bought', 'wait', 'waits', 'waited', 'serve', 'serves', 'served', 'die', 'dies', 'died', 'send', 'sends', 'sent', 'expect', 'expects', 'expected', 'build', 'builds', 'built', 'stay', 'stays', 'stayed', 'fall', 'falls', 'fell', 'cut', 'cuts', 'reach', 'reaches', 'reached', 'kill', 'kills', 'killed', 'remain', 'remains', 'remained', 'suggest', 'suggests', 'suggested', 'raise', 'raises', 'raised', 'pass', 'passes', 'passed', 'sell', 'sells', 'sold', 'require', 'requires', 'required', 'report', 'reports', 'reported', 'decide', 'decides', 'decided', 'pull', 'pulls', 'pulled', 'movie', 'film', 'cinema', 'story', 'character', 'plot', 'scene', 'director', 'actor', 'actress', 'cast', 'role', 'performance', 'drama', 'action', 'comedy', 'horror', 'thriller', 'romance', 'adventure', 'fantasy', 'fiction', 'documentary', 'animation', 'musical', 'western', 'crime', 'mystery', 'war', 'biography', 'history', 'family', 'sport', 'music', 'dance', 'art', 'culture', 'society', 'politics', 'religion', 'science', 'technology', 'nature', 'animal', 'human', 'man', 'woman', 'child', 'boy', 'girl', 'father', 'mother', 'son', 'daughter', 'brother', 'sister', 'friend', 'enemy', 'hero', 'villain', 'good', 'bad', 'evil', 'dark', 'light', 'black', 'white', 'red', 'blue', 'green', 'yellow', 'big', 'small', 'long', 'short', 'high', 'low', 'fast', 'slow', 'old', 'new', 'young', 'beautiful', 'ugly', 'strong', 'weak', 'rich', 'poor', 'happy', 'sad', 'angry', 'afraid', 'surprised', 'excited', 'bored', 'tired', 'hungry', 'thirsty', 'hot', 'cold', 'warm', 'cool', 'wet', 'dry', 'clean', 'dirty', 'easy', 'hard', 'simple', 'complex', 'clear', 'unclear', 'true', 'false', 'right', 'wrong', 'correct', 'incorrect', 'real', 'fake', 'natural', 'artificial', 'normal', 'strange', 'weird', 'funny', 'serious', 'important', 'unimportant', 'necessary', 'unnecessary', 'possible', 'impossible', 'probable', 'improbable', 'certain', 'uncertain', 'sure', 'unsure', 'safe', 'dangerous', 'risky', 'secure', 'insecure', 'public', 'private', 'personal', 'professional', 'official', 'unofficial', 'formal', 'informal', 'legal', 'illegal', 'moral', 'immoral', 'ethical', 'unethical', 'fair', 'unfair', 'equal', 'unequal', 'similar', 'different', 'same', 'opposite', 'near', 'far', 'close', 'distant', 'inside', 'outside', 'above', 'below', 'over', 'under', 'before', 'after', 'during', 'while', 'until', 'since', 'from', 'into', 'onto', 'off', 'out', 'up', 'down', 'left', 'right', 'north', 'south', 'east', 'west', 'here', 'there', 'everywhere', 'nowhere', 'somewhere', 'anywhere', 'always', 'never', 'sometimes', 'often', 'rarely', 'seldom', 'usually', 'normally', 'generally', 'specifically', 'particularly', 'especially', 'mainly', 'mostly', 'partly', 'completely', 'totally', 'fully', 'entirely', 'absolutely', 'relatively', 'approximately', 'exactly', 'precisely', 'roughly', 'about', 'around', 'nearly', 'almost', 'quite', 'rather', 'pretty', 'fairly', 'somewhat', 'slightly', 'barely', 'hardly', 'scarcely', 'extremely', 'very', 'really', 'truly', 'actually', 'indeed', 'certainly', 'definitely', 'probably', 'maybe', 'perhaps', 'possibly', 'likely', 'unlikely', 'obviously', 'clearly', 'apparently', 'seemingly', 'supposedly', 'allegedly', 'reportedly', 'according', 'based', 'depending', 'regarding', 'concerning', 'involving', 'including', 'excluding', 'except', 'besides', 'apart', 'aside', 'along', 'across', 'through', 'throughout', 'within', 'without', 'against', 'towards', 'between', 'among', 'amongst', 'beyond', 'beneath', 'beside', 'behind', 'ahead', 'forward', 'backward', 'upward', 'downward', 'inward', 'outward', 'toward', 'away', 'together', 'apart', 'alone', 'single', 'double', 'triple', 'multiple', 'several', 'many', 'much', 'little', 'less', 'least', 'more', 'most', 'enough', 'too', 'also', 'either', 'neither', 'both', 'all', 'none', 'some', 'any', 'every', 'each', 'another', 'other', 'others', 'else', 'otherwise', 'however', 'therefore', 'thus', 'hence', 'consequently', 'accordingly', 'meanwhile', 'nevertheless', 'nonetheless', 'furthermore', 'moreover', 'additionally', 'besides', 'instead', 'rather', 'alternatively', 'similarly', 'likewise', 'equally', 'comparatively', 'relatively', 'respectively', 'particularly', 'especially', 'specifically', 'generally', 'usually', 'normally', 'typically', 'commonly', 'frequently', 'regularly', 'occasionally', 'sometimes', 'rarely', 'seldom', 'never', 'always', 'constantly', 'continuously', 'permanently', 'temporarily', 'briefly', 'shortly', 'quickly', 'slowly', 'gradually', 'suddenly', 'immediately', 'instantly', 'eventually', 'finally', 'ultimately', 'originally', 'initially', 'firstly', 'secondly', 'thirdly', 'lastly', 'previously', 'formerly', 'recently', 'currently', 'presently', 'nowadays', 'today', 'tomorrow', 'yesterday', 'earlier', 'later', 'sooner', 'longer', 'shorter', 'better', 'worse', 'best', 'worst', 'greater', 'lesser', 'higher', 'lower', 'larger', 'smaller', 'bigger', 'littler', 'older', 'newer', 'younger', 'elder', 'latest', 'earliest', 'first', 'second', 'third', 'last', 'next', 'previous', 'following', 'preceding', 'subsequent', 'prior', 'former', 'latter', 'current', 'present', 'past', 'future', 'modern', 'ancient', 'recent', 'old', 'new', 'fresh', 'stale', 'original', 'copy', 'duplicate', 'unique', 'common', 'rare', 'unusual', 'typical', 'atypical', 'standard', 'nonstandard', 'regular', 'irregular', 'normal', 'abnormal', 'average', 'median', 'mean', 'mode', 'range', 'minimum', 'maximum', 'total', 'sum', 'difference', 'product', 'quotient', 'ratio', 'proportion', 'percentage', 'fraction', 'decimal', 'number', 'figure', 'digit', 'amount', 'quantity', 'volume', 'size', 'length', 'width', 'height', 'depth', 'area', 'perimeter', 'circumference', 'diameter', 'radius', 'angle', 'degree', 'temperature', 'pressure', 'weight', 'mass', 'density', 'speed', 'velocity', 'acceleration', 'force', 'energy', 'power', 'frequency', 'wavelength', 'amplitude', 'phase', 'period', 'cycle', 'rhythm', 'pattern', 'sequence', 'series', 'order', 'arrangement', 'organization', 'structure', 'system', 'method', 'process', 'procedure', 'technique', 'approach', 'strategy', 'plan', 'scheme', 'design', 'model', 'framework', 'concept', 'idea', 'notion', 'thought', 'opinion', 'view', 'perspective', 'viewpoint', 'standpoint', 'position', 'stance', 'attitude', 'belief', 'conviction', 'faith', 'trust', 'confidence', 'doubt', 'uncertainty', 'confusion', 'clarity', 'understanding', 'comprehension', 'knowledge', 'information', 'data', 'facts', 'details', 'specifics', 'particulars', 'features', 'characteristics', 'properties', 'qualities', 'attributes', 'aspects', 'elements', 'components', 'parts', 'pieces', 'sections', 'segments', 'portions', 'fractions', 'fragments', 'bits', 'chunks', 'blocks', 'units', 'items', 'objects', 'things', 'stuff', 'material', 'substance', 'matter', 'content', 'subject', 'topic', 'theme', 'issue', 'problem', 'question', 'answer', 'solution', 'result', 'outcome', 'consequence', 'effect', 'impact', 'influence', 'cause', 'reason', 'purpose', 'goal', 'objective', 'aim', 'target', 'intention', 'plan', 'desire', 'wish', 'want', 'need', 'requirement', 'demand', 'request', 'order', 'command', 'instruction', 'direction', 'guidance', 'advice', 'suggestion', 'recommendation', 'proposal', 'offer', 'invitation', 'welcome', 'greeting', 'farewell', 'goodbye', 'hello', 'hi', 'hey', 'yes', 'no', 'okay', 'alright', 'fine', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic', 'incredible', 'unbelievable', 'impossible', 'possible', 'probable', 'likely', 'unlikely', 'certain', 'uncertain', 'sure', 'unsure', 'maybe', 'perhaps', 'possibly', 'definitely', 'absolutely', 'certainly', 'probably', 'apparently', 'obviously', 'clearly', 'evidently', 'supposedly', 'allegedly', 'reportedly', 'according', 'based', 'depending', 'regarding', 'concerning', 'involving', 'including', 'excluding', 'except', 'besides', 'apart', 'aside', 'along', 'across', 'through', 'throughout', 'within', 'without', 'against', 'towards', 'between', 'among', 'amongst', 'beyond', 'beneath', 'beside', 'behind', 'ahead', 'forward', 'backward', 'upward', 'downward', 'inward', 'outward', 'toward', 'away', 'together', 'apart', 'alone'}
        
        if text_data.strip():
            try:
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    max_words=50,
                    stopwords=stop_words,
                    colormap='viridis'
                ).generate(text_data)
                
                fig_wc, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title(f'Word Cloud: {selected_genre_wc}', fontsize=16, pad=20)
                
                st.pyplot(fig_wc)
                
            except Exception as e:
                st.warning("ไม่สามารถสร้าง Word Cloud ได้ อาจเป็นเพราะข้อมูลไม่เพียงพอ")
        else:
            st.warning("ไม่มีข้อมูล overview สำหรับกลุ่มนี้")
    else:
        # Use keywords if available
        if 'micro_genre_keybert' in df.columns:
            # Extract only the selected genre keywords
            selected_keywords = []
            for genre_str in genre_movies['micro_genre_keybert'].dropna():
                genres = [g.strip() for g in str(genre_str).split('/')]
                if selected_genre_wc in genres:
                    selected_keywords.append(selected_genre_wc)
            
            keywords_data = ' '.join(selected_keywords)
            
            if keywords_data.strip():
                try:
                    # Enhanced stop words for keywords
                    keyword_stop_words = {'genre', 'micro', 'keybert', 'movie', 'film', 'cinema'}
                    
                    wordcloud = WordCloud(
                        width=800, 
                        height=400, 
                        background_color='white',
                        max_words=30,
                        colormap='plasma',
                        stopwords=keyword_stop_words
                    ).generate(keywords_data)
                    
                    fig_wc, ax = plt.subplots(figsize=(12, 6))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    ax.set_title(f'Keywords Cloud: {selected_genre_wc}', fontsize=16, pad=20)
                    
                    st.pyplot(fig_wc)
                    
                except Exception as e:
                    st.warning("ไม่สามารถสร้าง Word Cloud ได้")
            else:
                st.warning("ไม่มีข้อมูล keywords สำหรับกลุ่มนี้")
        else:
            st.info("ไม่มีข้อมูลข้อความสำหรับสร้าง Word Cloud")
    
    # Statistics below the image
    st.markdown("#### 📊 สถิติของกลุ่มนี้")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("จำนวนหนัง", len(genre_movies))
    
    with col2:
        if 'vote_average' in df.columns:
            avg_rating = genre_movies['vote_average'].mean()
            st.metric("คะแนนเฉลี่ย", f"{avg_rating:.1f}/10")
    
    with col3:
        if 'year' in df.columns:
            year_range = f"{genre_movies['year'].min():.0f} - {genre_movies['year'].max():.0f}"
            st.metric("ช่วงปี", year_range)
    
    # Top movies in this genre
    if 'vote_average' in df.columns:
        st.markdown("**หนังคะแนนสูงสุด:**")
        top_movies = genre_movies.nlargest(3, 'vote_average')[['title', 'vote_average']]
        for _, movie in top_movies.iterrows():
            st.write(f"• {movie['title']} ({movie['vote_average']:.1f})")

    st.info("""
    💡 **Insight:** Word Cloud ช่วยยืนยันว่าทำไม AI ถึงจัดกลุ่มหนังเหล่านี้มาอยู่ด้วยกัน 
    คำที่ปรากฏบ่อยจะสะท้อนธีม อารมณ์ และเนื้อหาหลักของ Micro-Genre นั้นๆ
    """)

st.markdown("---")

# 3. Comparative Analysis
st.markdown("## 🔬 3. การวิเคราะห์เชิงเปรียบเทียบ")

st.markdown("### 📊 Scatter Plot: ปี vs คะแนน vs Micro-Genre")

if 'vote_average' in df.columns:
    # Sample data for better performance if dataset is large
    sample_size = min(1000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    
    # Get top 8 genres for color coding
    top_8_genres = df['micro_genre_keybert'].value_counts().head(8).index
    df_sample_filtered = df_sample[df_sample['micro_genre_keybert'].isin(top_8_genres)]
    
    fig_scatter = px.scatter(
        df_sample_filtered,
        x='year',
        y='vote_average',
        color='micro_genre_keybert',
        title=f"การกระจายตัวของหนัง: ปี vs คะแนน (ตัวอย่าง {len(df_sample_filtered)} เรื่อง)",
        labels={'year': 'ปีที่ฉาย', 'vote_average': 'คะแนน IMDB', 'micro_genre_keybert': 'Micro-Genre'},
        hover_data=['title'] if 'title' in df.columns else None,
        opacity=0.7
    )
    
    fig_scatter.update_layout(
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.info("""
    💡 **Insight:** กราฟจุดแสดงให้เห็น "Cluster" ของแต่ละ Micro-Genre 
    - **แกน X (ปี):** บางกลุ่มอาจกระจุกตัวในยุคใดยุคหนึ่ง
    - **แกน Y (คะแนน):** บางกลุ่มอาจมีคุณภาพสม่ำเสมอสูง/ต่ำ
    - **สี:** แยกแยะ Micro-Genre ต่างๆ
    """)
    
    # Genre performance over time
    st.markdown("### 📈 ประสิทธิภาพของ Micro-Genres ตามเวลา")
    
    # Calculate average rating by decade for top genres
    df_decade = df.copy()
    df_decade['decade'] = (df_decade['year'] // 10) * 10
    
    decade_performance = df_decade[df_decade['micro_genre_keybert'].isin(top_8_genres)].groupby(['decade', 'micro_genre_keybert'])['vote_average'].mean().reset_index()
    
    fig_performance = px.line(
        decade_performance,
        x='decade',
        y='vote_average',
        color='micro_genre_keybert',
        title="คะแนนเฉลี่ยของ Micro-Genres ในแต่ละทศวรรษ",
        labels={'decade': 'ทศวรรษ', 'vote_average': 'คะแนนเฉลี่ย', 'micro_genre_keybert': 'Micro-Genre'},
        markers=True
    )
    
    fig_performance.update_layout(height=400)
    st.plotly_chart(fig_performance, use_container_width=True)

else:
    st.warning("ไม่มีข้อมูลคะแนนสำหรับการวิเคราะห์เชิงเปรียบเทียบ")

# Summary Statistics
st.markdown("---")
st.markdown("## 📋 สรุปข้อมูลเชิงลึก")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🎯 Micro-Genre ที่โดดเด่น")
    
    # Most consistent genre (lowest std deviation in ratings)
    if 'vote_average' in df.columns:
        genre_consistency = df.groupby('micro_genre_keybert')['vote_average'].agg(['mean', 'std', 'count']).reset_index()
        genre_consistency = genre_consistency[genre_consistency['count'] >= 5]  # At least 5 movies
        most_consistent = genre_consistency.loc[genre_consistency['std'].idxmin()]
        
        st.write(f"**คุณภาพสม่ำเสมอ:** {most_consistent['micro_genre_keybert']}")
        st.write(f"คะแนนเฉลี่ย: {most_consistent['mean']:.1f} (±{most_consistent['std']:.1f})")

with col2:
    st.markdown("#### 📅 เทรนด์ตามเวลา")
    
    # Fastest growing genre in recent years
    recent_years = df[df['year'] >= 2010]
    if len(recent_years) > 0:
        recent_growth = recent_years['micro_genre_keybert'].value_counts().head(1)
        st.write(f"**เติบโตเร็วสุด (2010+):** {recent_growth.index[0]}")
        st.write(f"จำนวน: {recent_growth.iloc[0]} เรื่อง")

with col3:
    st.markdown("#### 🏆 ความหลากหลาย")
    
    # Genre diversity index
    total_genres = df['micro_genre_keybert'].nunique()
    movies_per_genre = len(df) / total_genres
    
    st.write(f"**ดัชนีความหลากหลาย:** {total_genres} กลุ่ม")
    st.write(f"เฉลี่ย: {movies_per_genre:.1f} เรื่อง/กลุ่ม")

# Navigation
st.markdown("---")
st.markdown("""
### 🧭 สำรวจต่อ

🎬 **ลองไปหาหนังที่ชอบ:** ใช้ข้อมูลที่ได้จากการวิเคราะห์นี้ไปค้นหาในหน้า **Explorer**

📊 **ดูภาพรวม:** กลับไปดูสถิติโดยรวมในหน้า **Overview**
""")