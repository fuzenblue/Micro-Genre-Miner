# 🎬 Micro-Genre Miner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Discover hidden movie patterns with AI-powered micro-genre classification**

An intelligent movie recommendation system that uses machine learning to identify nuanced movie categories beyond traditional genres. Built with Python, Streamlit, and modern NLP techniques.

![Demo](https://via.placeholder.com/800x400/1f1f1f/ffffff?text=Micro-Genre+Miner+Demo)

## ✨ Features

- 🤖 **AI-Powered Classification**: 150+ micro-genres discovered using KeyBERT and clustering
- 📊 **Interactive Analytics**: Real-time visualizations with Plotly and word clouds  
- 🔍 **Smart Search**: Filter by micro-genres, keywords, and traditional categories
- 📈 **Trend Analysis**: Explore genre evolution over 130+ years of cinema
- 🚀 **Production Ready**: Docker deployment with <2s load times

## 🎯 What Makes This Special?

Instead of broad categories like "Action" or "Comedy", discover specific themes like:
- *Psychological Thriller Mind* (45 movies, 8.1★)
- *Zombie Apocalypse Survival* (34 movies, 6.4★)  
- *Superhero Action Marvel* (73 movies, 7.2★)
- *Historical War Drama* (52 movies, 7.8★)

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/yourusername/Micro-Genre-Miner.git
cd Micro-Genre-Miner/app
docker build -t micro-genre-miner .
docker run -p 8501:8501 micro-genre-miner
```
**Access**: http://localhost:8501

### Option 2: Local Installation
```bash
git clone https://github.com/yourusername/Micro-Genre-Miner.git
cd Micro-Genre-Miner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
cd app
streamlit run app.py
```

### Option 3: Streamlit Cloud
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## 📊 Dataset Overview

- **Movies**: 4,968 films from TMDB API
- **Time Range**: 1900-2030 (130+ years)
- **Micro-Genres**: 150+ AI-generated categories
- **Languages**: 85 languages (67% English)
- **Data Quality**: 96.37% retention rate

## 🏗️ Architecture

```
TMDB API → Data Pipeline → ML Processing → Streamlit App
    ↓           ↓              ↓             ↓
Raw Data → Clean Data → Embeddings → Micro-Genres → Web UI
```

### Tech Stack
- **Backend**: Python, Pandas, Scikit-learn, SentenceTransformers
- **ML/NLP**: KeyBERT, K-Means Clustering, TF-IDF
- **Frontend**: Streamlit, Plotly, Matplotlib, WordCloud
- **Deployment**: Docker, Parquet storage

## 📱 Application Pages

### 🏠 Landing Page
- Value proposition and concept explanation
- Live dataset statistics
- Navigation guidance

### 📊 Overview Dashboard  
- KPI metrics and treemap visualizations
- Top micro-genres by popularity and quality
- Statistical insights and patterns

### 🔍 Movie Explorer
- Interactive search and filtering
- Visual poster grid with detailed modals
- Cross-genre navigation

### 📈 Trends Analysis
- Time-series genre evolution
- Dynamic word clouds
- Comparative analytics and insights

## 🔬 Machine Learning Pipeline

### 1. Data Collection
```bash
python scripts/fetch_data.py        # Collect from TMDB API
```

### 2. Data Cleaning  
```bash
python scripts/clean_data.py        # Clean and validate data
```

### 3. Feature Engineering
```bash
python scripts/vectorize_cluster.py # Generate embeddings
```

### 4. Clustering & Labeling
```bash
python scripts/areeya/cluster_and_keywords1.py  # ML clustering
python scripts/areeya/label_microgenres.py      # Generate labels
```

### 5. Package for Deployment
```bash
python scripts/make_parquet.py      # Create optimized dataset
```

## 📈 Performance Metrics

- **Clustering Quality**: 0.342 silhouette score
- **Processing Time**: ~55 minutes for full pipeline
- **Storage Efficiency**: 73% compression with Parquet
- **Application Speed**: <2 second load times
- **Semantic Quality**: 84% keyword relevance

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker Production
```bash
docker-compose up -d
```

### Cloud Platforms
- **Streamlit Cloud**: One-click deployment
- **Heroku**: `git push heroku main`
- **AWS EC2**: Full production setup
- **Google Cloud Run**: Serverless containers

See [Deployment Guide](docs/deployment_guide.md) for detailed instructions.

## 📚 Documentation

- 📖 [Project Summary](docs/project_summary.md) - Complete project overview
- 🤖 [Model Report](docs/model_report.md) - ML methodology and results  
- 🔄 [Data Pipeline](docs/data_pipeline_report.md) - Processing workflow
- 💻 [Streamlit Report](docs/streamlit_report.md) - Application analysis
- 🚀 [Deployment Guide](docs/deployment_guide.md) - Setup instructions
- 📊 [Data Dictionary](docs/data_dictionary.md) - Field descriptions

## 🔧 Configuration

### Environment Variables
```bash
# Required for data collection (optional for demo)
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_BASE_URL=https://api.themoviedb.org/3

# Optional Streamlit configuration  
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Custom Configuration
```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false

[theme]  
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/Micro-Genre-Miner.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python -m pytest tests/

# Submit pull request
```

### Areas for Contribution
- 🌍 Multi-language support
- 🎨 UI/UX improvements  
- 🤖 Advanced ML models
- 📊 New visualization types
- 🐛 Bug fixes and optimizations

## 📊 Project Stats

```
📈 Repository Metrics:
- Lines of Code: ~3,500
- Documentation: 6 comprehensive reports
- Processing Pipeline: 7 automated scripts
- Web Application: 4 interactive pages
- Docker Ready: Production deployment
- Test Coverage: Core functionality tested
```

## 🏆 Key Achievements

- ✅ **96.37% data retention** from raw to clean dataset
- ✅ **150+ micro-genres** automatically discovered
- ✅ **0.342 silhouette score** for clustering quality
- ✅ **<2 second load times** for web application
- ✅ **73% storage compression** with optimized format
- ✅ **Production ready** with Docker deployment

## 🔮 Roadmap

### Short-term (3-6 months)
- [ ] User rating and review system
- [ ] Personalized recommendations  
- [ ] Advanced filtering options
- [ ] Mobile app development
- [ ] A/B testing framework

### Long-term (6-12 months)  
- [ ] Real-time learning capabilities
- [ ] Multi-modal analysis (text + images)
- [ ] Social features and community
- [ ] Cross-platform recommendation engine
- [ ] Advanced AI models (GPT, BERT)

## 🙏 Acknowledgments

- **TMDB** - For comprehensive movie database API
- **Streamlit** - For excellent web framework
- **Hugging Face** - For pre-trained transformer models  
- **Open Source Community** - For amazing libraries and tools