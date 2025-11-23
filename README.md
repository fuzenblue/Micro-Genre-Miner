# Micro Genre Miner

A movie recommendation system that analyzes micro-genres using machine learning and data from The Movie Database (TMDB). This project helps discover hidden patterns in movie preferences and provides personalized recommendations.

## 🎬 What This Project Does

- **Data Mining**: Extracts movie data from TMDB API
- **Genre Analysis**: Identifies micro-genres and patterns
- **Recommendation Engine**: Suggests movies based on user preferences
- **Data Visualization**: Creates insights from movie datasets

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

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- Git installed
- Internet connection for API calls

### Step 1: Clone & Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Micro-Genre-Miner.git
cd Micro-Genre-Miner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get TMDB API Key
1. Go to [TMDB](https://www.themoviedb.org/signup) and create account
2. Navigate to Settings → API → Request API Key
3. Choose "Developer" and fill out the form
4. Copy your API key

### Step 3: Configure Environment
```bash
# Create .env file
echo TMDB_API_KEY=your_actual_api_key_here > .env
echo TMDB_BASE_URL=https://api.themoviedb.org/3 >> .env
```

### Step 4: Run the Project
```bash
# Fetch movie data
python scripts/fetch_data.py

# Clean and process data
python scripts/clean_data.py

# Build recommendation model
python scripts/build_model.py
```

---

## 📁 Project Structure
```
Micro-Genre-Miner/
├── 📂 data/
│   ├── 📂 raw/                  # Raw data from TMDB API
│   │   ├── raw_movies.json      # Movie metadata
│   │   └── raw_reviews.json     # User reviews
│   └── 📂 processed/            # Cleaned & processed data
├── 📂 scripts/
│   ├── 🐍 fetch_data.py         # Download data from TMDB
│   ├── 🧹 clean_data.py         # Data preprocessing
│   └── 🤖 build_model.py        # Train ML models
├── 📂 models/                   # Saved ML models
├── 📂 notebooks/                # Jupyter analysis notebooks
├── 📂 docs/                     # Documentation
│   ├── data_dictionary.md       # Data field descriptions
│   └── methodology.md           # Technical methodology
├── 🔐 .env                      # API keys (create this!)
├── 📋 requirements.txt          # Python dependencies
└── 📖 README.md                 # This file
```

## 🔧 Troubleshooting

### Common Issues

**API Key Error:**
```
Error: Invalid API key
```
- Check your `.env` file exists
- Verify API key is correct (no extra spaces)
- Ensure you're using the v3 API key from TMDB

**Module Not Found:**
```
ModuleNotFoundError: No module named 'requests'
```
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**Permission Denied:**
- On Windows: Run terminal as Administrator
- On Mac/Linux: Check file permissions with `ls -la`

### Getting Help
- Check existing [Issues](https://github.com/yourusername/Micro-Genre-Miner/issues)
- Create new issue with error details
- Include your Python version and OS

---

## 📊 Dataset Overview

**Current Dataset Size:**
- 🎬 **Movies**: 5,155 films (~177 MB)
- 📝 **Reviews**: 18,076 reviews (~11 MB)
- 🏷️ **Fields**: 25+ attributes per movie

**Key Data Fields:**
- Movie metadata (title, overview, release date)
- Genre classifications and keywords
- Ratings, popularity scores, revenue
- Cast and crew information
- User reviews and ratings

For complete field descriptions, see [docs/data_dictionary.md](docs/data_dictionary.md)

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
- **Contributors**: Everyone who helps improve this project

---

**Last Updated:** 2025-09-23  
**Version:** 1.0  
**API Version:** TMDB API v3

⭐ **Star this repo if you find it helpful!**
