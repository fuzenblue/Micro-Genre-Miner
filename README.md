# Movie Recommendation System

## Project Overview

ระบบแนะนำภาพยนตร์โดยใช้ Machine Learning วิเคราะห์จากเนื้อหา (Content-Based Filtering) และความคิดเห็นผู้ใช้ (Collaborative Filtering)

---

## 📊 Data Source

### The Movie Database (TMDB)

**API Endpoint:** https://api.themoviedb.org/3  
**Documentation:** https://developers.themoviedb.org/3  
**License:** [TMDB API Terms of Use](https://www.themoviedb.org/documentation/api/terms-of-use)  

#### Data Collected:
- ✅ Movie metadata (title, overview, genres, keywords)
- ✅ Movie statistics (ratings, popularity, revenue)
- ✅ Cast and crew information
- ✅ User reviews and ratings

#### Data NOT Collected:
- ❌ Personal user information
- ❌ User viewing history
- ❌ Email addresses or contact details
- ❌ Payment information

---

## 🔐 API Key Setup

1. Register at [TMDB](https://www.themoviedb.org/signup)
2. Request API key: Settings → API → Request API Key
3. Create `.env` file:
```bash
   TMDB_API_KEY=your_api_key_here
   TMDB_BASE_URL=https://api.themoviedb.org/3
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip
- TMDB API Key

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your TMDB_API_KEY
```

---

## 📁 Project Structure
```
movie-recommendation-system/
├── data/
│   ├── raw/                  # Raw data from TMDB
│   │   ├── raw_movies.json
│   │   └── raw_reviews.json
│   └── processed/            # Cleaned data
├── scripts/
│   ├── fetch_data.py         # Data fetching script
│   ├── clean_data.py         # Data cleaning (Phase 2)
│   └── build_model.py        # Model building (Phase 3)
├── models/                   # Trained models
├── notebooks/                # Jupyter notebooks (analysis)
├── docs/
│   ├── data_dictionary.md    # Data field descriptions
│   └── methodology.md        # Technical approach
├── .env                      # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📖 Data Dictionary

See [docs/data_dictionary.md](docs/data_dictionary.md) for detailed field descriptions.

**Quick Summary:**
- **Movies Dataset**: 5155 movies, ~177,390 KB, 25+ fields per movie
- **Reviews Dataset**: ~18076 reviews, ~11,733 KB, user ratings and text

---

## 🎯 Ethical Considerations

### Data Collection Ethics

✅ **Publicly Available Data**
- All data sourced from TMDB public API
- No web scraping or unauthorized access
- Compliance with TMDB Terms of Service

✅ **Privacy Protection**
- No collection of personal identifiable information (PII)
- Reviews are public submissions by users who agreed to TMDB terms
- Usernames kept but no contact information collected

✅ **Attribution**
- TMDB credited as primary data source
- API usage follows attribution requirements
- Dataset marked as "Educational Use Only"

### Usage Limitations

⚠️ **This Dataset Should NOT Be Used For:**
- Commercial applications without proper licensing
- Training models that identify or track individuals
- Creating competing services to TMDB
- Redistribution without attribution

✅ **Appropriate Uses:**
- Educational projects and learning
- Academic research
- Portfolio demonstrations
- Non-commercial recommendation systems

### Bias Considerations

📊 **Known Biases in Dataset:**
- **Geographic Bias**: Primarily US/Western films
- **Language Bias**: Predominantly English-language content
- **Popularity Bias**: Sample includes only popular films
- **Recency Bias**: More recent films have more reviews

**Mitigation Strategies:**
- Acknowledge limitations in model documentation
- Do not claim universal applicability
- Consider diversity metrics when evaluating model

---

## 🙏 Acknowledgments

- **TMDB**: For providing comprehensive movie database API
- **Open Source Community**: For libraries and tools used

---

**Last Updated:** 2025-11-15  
**Dataset Version:** 1.0  
**API Version:** TMDB API v3