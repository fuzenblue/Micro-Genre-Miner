import json
import pandas as pd
import numpy as np
import re
from pathlib import Path
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Paths
RAW_MOVIES = Path("data/raw/raw_movies.json")
RAW_REVIEWS = Path("data/raw/raw_reviews.json")
OUTPUT_DIR = Path("data/cleaned")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "cleaned_movies.csv"
REPORT_FILE = OUTPUT_DIR / "data_quality_report.txt"

# NLTK stopwords
STOP_WORDS = set(stopwords.words('english'))


def normalize_genres(genres):
    """Normalize genres into a list of strings."""
    if genres is None:
        return []

    # Convert numpy array to list
    if hasattr(genres, "__array__"):
        genres = genres.tolist()

    # Only accept list/tuple
    if not isinstance(genres, (list, tuple)):
        return []

    cleaned = []
    for g in genres:
        if isinstance(g, dict) and "name" in g:
            cleaned.append(g["name"])
    return cleaned


class DataCleaner:
    """Class สำหรับทำความสะอาดข้อมูล"""
    
    def __init__(self):
        self.cleaning_log = []
        self.stats = {
            'initial_movies': 0,
            'initial_reviews': 0,
            'final_records': 0,
            'removed_duplicates': 0,
            'removed_null_overview': 0,
            'removed_invalid_year': 0,
            'filled_missing_values': 0
        }
    
    def log(self, message):
        """บันทึก log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.cleaning_log.append(log_entry)
        print(log_entry)
    
    def load_data(self):
        """โหลดข้อมูลจากไฟล์ JSON"""
        self.log("Loading raw data...")
        
        # Load movies
        with open(RAW_MOVIES, 'r', encoding='utf-8') as f:
            movies = json.load(f)
        
        self.stats['initial_movies'] = len(movies)
        self.log(f"Loaded {len(movies)} movies")
        
        # Load reviews
        with open(RAW_REVIEWS, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        self.stats['initial_reviews'] = len(reviews)
        self.log(f"Loaded {len(reviews)} reviews")
        
        return movies, reviews
    
    def clean_html(self, text):
        """ลบ HTML tags"""
        if pd.isna(text) or text == '':
            return ''
        
        # Parse HTML
        soup = BeautifulSoup(str(text), 'html.parser')
        
        # Get text only
        clean_text = soup.get_text()
        
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        
        return clean_text
    
    def remove_special_chars(self, text):
        """ลบ special characters ที่ไม่จำเป็น"""
        if pd.isna(text) or text == '':
            return ''
        
        # Keep letters, numbers, spaces, and basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', ' ', str(text))
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def remove_stopwords(self, text):
        """ลบ stopwords"""
        if pd.isna(text) or text == '':
            return ''
        
        # Tokenize
        words = word_tokenize(str(text).lower())
        
        # Remove stopwords and punctuation
        filtered = [w for w in words if w not in STOP_WORDS and w not in string.punctuation]
        
        return ' '.join(filtered)
    
    def clean_text_field(self, text, remove_stops=False):
        """ทำความสะอาดข้อความ (pipeline)"""
        # Step 1: Clean HTML
        text = self.clean_html(text)
        
        # Step 2: Remove special characters
        text = self.remove_special_chars(text)
        
        # Step 3: Remove stopwords (optional)
        if remove_stops:
            text = self.remove_stopwords(text)
        
        # Step 4: Lowercase
        text = text.lower()
        
        return text.strip()
    
    def extract_year(self, date_str):
        """แยกปีจาก release_date"""
        if pd.isna(date_str) or date_str == '':
            return None
        
        try:
            # Format: YYYY-MM-DD
            year = int(str(date_str).split('-')[0])
            
            # Validate year range
            if 1800 <= year <= 2030:
                return year
            else:
                return None
        except:
            return None
    
    def process_movies(self, movies_raw):
        """ประมวลผลข้อมูลภาพยนตร์"""
        self.log("\nProcessing movies...")
        
        # Convert to DataFrame
        df = pd.DataFrame(movies_raw)
        
        self.log(f"Initial shape: {df.shape}")
        
        # ===== EXTRACT BASIC FIELDS =====
        
        movies_clean = pd.DataFrame()
        
        movies_clean['movie_id'] = df['id']
        movies_clean['title'] = df['title']
        movies_clean['original_title'] = df['original_title']
        movies_clean['overview'] = df['overview']
        movies_clean['tagline'] = df['tagline']
        movies_clean['release_date'] = df['release_date']
        movies_clean['runtime'] = df['runtime']
        movies_clean['budget'] = df['budget']
        movies_clean['revenue'] = df['revenue']
        movies_clean['vote_average'] = df['vote_average']
        movies_clean['vote_count'] = df['vote_count']
        movies_clean['popularity'] = df['popularity']
        movies_clean['status'] = df['status']
        movies_clean['original_language'] = df['original_language']
        
        # ===== EXTRACT YEAR =====
        
        movies_clean['year'] = df['release_date'].apply(self.extract_year)
        
        # ===== EXTRACT GENRES =====
        
        movies_clean['genres'] = df['genres'].apply(normalize_genres)
        
        # ===== EXTRACT KEYWORDS =====
        
        def extract_keywords(keywords_obj):
            if pd.isna(keywords_obj) or not keywords_obj:
                return []
            
            keywords_list = keywords_obj.get('keywords', [])
            return [k['name'] for k in keywords_list]
        
        movies_clean['keywords'] = df['keywords'].apply(extract_keywords)
        
        # ===== EXTRACT CAST (TOP 5) =====
        
        def extract_cast(credits_obj):
            if pd.isna(credits_obj) or not credits_obj:
                return ''
            
            cast_list = credits_obj.get('cast', [])
            top_cast = [c['name'] for c in cast_list[:5]]
            return ' '.join(top_cast)
        
        movies_clean['cast'] = df['credits'].apply(extract_cast)
        
        # ===== EXTRACT DIRECTOR =====
        
        def extract_director(credits_obj):
            if pd.isna(credits_obj) or not credits_obj:
                return ''
            
            crew_list = credits_obj.get('crew', [])
            directors = [c['name'] for c in crew_list if c.get('job') == 'Director']
            return directors[0] if directors else ''
        
        movies_clean['director'] = df['credits'].apply(extract_director)
        
        self.log(f"Extracted fields. Shape: {movies_clean.shape}")
        
        return movies_clean
    
    def aggregate_reviews(self, reviews_raw):
        """รวม reviews ของแต่ละภาพยนตร์"""
        self.log("\nAggregating reviews...")
        
        df_reviews = pd.DataFrame(reviews_raw)
        
        # Group by movie_id
        reviews_agg = df_reviews.groupby('movie_id').agg({
            'content': lambda x: ' '.join(x.astype(str)),  # รวมเนื้อหา
            'id': 'count'  # นับจำนวน reviews
        }).rename(columns={'content': 'reviews_text', 'id': 'review_count'})
        
        self.log(f"Aggregated reviews for {len(reviews_agg)} movies")
        
        return reviews_agg
    
    def merge_data(self, movies_df, reviews_df):
        """รวม movies และ reviews"""
        self.log("\nMerging movies and reviews...")
        
        # Left join
        merged = movies_df.merge(
            reviews_df,
            left_on='movie_id',
            right_index=True,
            how='left'
        )
        
        # Fill missing reviews
        merged['reviews_text'] = merged['reviews_text'].fillna('')
        merged['review_count'] = merged['review_count'].fillna(0).astype(int)
        
        self.log(f"Merged data shape: {merged.shape}")
        
        return merged
    
    def create_clean_text(self, df):
        """สร้าง clean_text จาก overview + genres + keywords + reviews"""
        self.log("\nCreating clean_text field...")
        
        def combine_text(row):
            parts = []

            # overview
            if pd.notna(row.get("overview")):
                parts.append(str(row["overview"]))

            # genres
            genres = row.get("genres", [])
            if isinstance(genres, (list, tuple)) and len(genres) > 0:
                parts.append(" ".join(genres))

            # keywords
            keywords = row.get("keywords", [])
            if isinstance(keywords, (list, tuple)) and len(keywords) > 0:
                parts.append(" ".join(keywords))

            # reviews
            review_texts = row.get("review_texts", [])
            if isinstance(review_texts, (list, tuple)) and len(review_texts) > 0:
                parts.append(" ".join(review_texts))

            return " ".join(parts)
        
        # Combine all text
        df['raw_text'] = df.apply(combine_text, axis=1)
        
        # Clean text
        df['clean_text'] = df['raw_text'].apply(
            lambda x: self.clean_text_field(x, remove_stops=True)
        )
        
        # Clean overview separately (without removing stopwords)
        df['clean_overview'] = df['overview'].apply(
            lambda x: self.clean_text_field(x, remove_stops=False)
        )
        
        self.log(f"Created clean_text for {len(df)} records")
        
        # Drop raw_text (intermediate)
        df = df.drop('raw_text', axis=1)
        
        return df
    
    def handle_missing_values(self, df):
        """จัดการ missing values"""
        self.log("\nHandling missing values...")
        
        initial_nulls = df.isnull().sum().sum()
        
        # ===== CRITICAL FIELDS (ห้ามเป็น null) =====
        
        # Remove rows with null overview
        before = len(df)
        df = df[df['overview'].notna() & (df['overview'] != '')]
        removed = before - len(df)
        self.stats['removed_null_overview'] = removed
        self.log(f"Removed {removed} rows with null overview")
        
        # Remove rows with null clean_text
        before = len(df)
        df = df[df['clean_text'].notna() & (df['clean_text'] != '')]
        removed = before - len(df)
        self.log(f"Removed {removed} rows with null clean_text")
        
        # ===== NUMERIC FIELDS =====
        
        # Fill numeric fields with 0
        numeric_fields = ['runtime', 'budget', 'revenue', 'vote_count', 'popularity']
        for field in numeric_fields:
            filled = df[field].isnull().sum()
            df[field] = df[field].fillna(0)
            if filled > 0:
                self.log(f"Filled {filled} missing values in {field} with 0")
        
        # Fill vote_average with median
        if df['vote_average'].isnull().sum() > 0:
            median_rating = df['vote_average'].median()
            filled = df['vote_average'].isnull().sum()
            df['vote_average'] = df['vote_average'].fillna(median_rating)
            self.log(f"Filled {filled} missing vote_average with median: {median_rating:.2f}")
        
        # ===== TEXT FIELDS =====
        
        text_fields = ['tagline', 'genres', 'keywords', 'cast', 'director', 'status']
        for field in text_fields:
            filled = df[field].isnull().sum()
            df[field] = df[field].fillna('')
            if filled > 0:
                self.log(f"Filled {filled} missing values in {field} with empty string")
        
        final_nulls = df.isnull().sum().sum()
        self.stats['filled_missing_values'] = initial_nulls - final_nulls
        
        self.log(f"Remaining nulls: {final_nulls}")
        
        return df
    
    def validate_data(self, df):
        """ตรวจสอบและแก้ไขค่าที่ผิดปกติ"""
        self.log("\nValidating data...")
        
        # ===== YEAR VALIDATION =====
        
        before = len(df)
        df = df[df['year'].notna() & (df['year'] >= 1900) & (df['year'] <= 2030)]
        removed = before - len(df)
        self.stats['removed_invalid_year'] = removed
        self.log(f"Removed {removed} rows with invalid year")
        
        # ===== RATING VALIDATION =====
        
        # vote_average should be 0-10
        df.loc[df['vote_average'] < 0, 'vote_average'] = 0
        df.loc[df['vote_average'] > 10, 'vote_average'] = 10
        
        # ===== RUNTIME VALIDATION =====
        
        # Runtime should be positive and reasonable
        df.loc[df['runtime'] < 0, 'runtime'] = 0
        df.loc[df['runtime'] > 500, 'runtime'] = 500  # Cap at 500 minutes
        
        # ===== BUDGET/REVENUE VALIDATION =====
        
        df.loc[df['budget'] < 0, 'budget'] = 0
        df.loc[df['revenue'] < 0, 'revenue'] = 0
        
        self.log(f"Data validation complete")
        
        return df
    
    def remove_duplicates(self, df):
        """ลบข้อมูลซ้ำ"""
        self.log("\nRemoving duplicates...")
        
        before = len(df)
        
        # Remove based on movie_id
        df = df.drop_duplicates(subset=['movie_id'], keep='first')
        
        removed = before - len(df)
        self.stats['removed_duplicates'] = removed
        self.log(f"Removed {removed} duplicate records")
        
        return df
    
    def finalize_dataset(self, df):
        """จัดเรียงและเลือก columns สุดท้าย"""
        self.log("\nFinalizing dataset...")
        
        # Select and reorder columns
        final_columns = [
            'movie_id',
            'title',
            'original_title',
            'year',
            'runtime',
            'genres',
            'director',
            'cast',
            'overview',
            'clean_overview',
            'tagline',
            'keywords',
            'clean_text',
            'vote_average',
            'vote_count',
            'popularity',
            'budget',
            'revenue',
            'review_count',
            'status',
            'original_language',
            'release_date'
        ]
        
        df = df[final_columns]
        
        # Sort by popularity
        df = df.sort_values('popularity', ascending=False)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        self.stats['final_records'] = len(df)
        
        self.log(f"Final dataset: {df.shape}")
        
        return df
    
    def generate_report(self, df):
        """สร้าง data quality report"""
        self.log("\nGenerating data quality report...")
        
        report = []
        report.append("="*80)
        report.append("DATA QUALITY REPORT")
        report.append("="*80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ===== SUMMARY STATISTICS =====
        
        report.append("\n" + "="*80)
        report.append("SUMMARY STATISTICS")
        report.append("="*80)
        
        report.append(f"\nInitial movies: {self.stats['initial_movies']}")
        report.append(f"Initial reviews: {self.stats['initial_reviews']}")
        report.append(f"Final records: {self.stats['final_records']}")
        report.append(f"\nData Retention Rate: {self.stats['final_records']/self.stats['initial_movies']*100:.2f}%")
        
        # ===== CLEANING OPERATIONS =====
        
        report.append("\n" + "="*80)
        report.append("CLEANING OPERATIONS")
        report.append("="*80)
        
        report.append(f"\nRemoved duplicates: {self.stats['removed_duplicates']}")
        report.append(f"Removed null overview: {self.stats['removed_null_overview']}")
        report.append(f"Removed invalid year: {self.stats['removed_invalid_year']}")
        report.append(f"Filled missing values: {self.stats['filled_missing_values']}")
        
        # ===== COMPLETENESS ANALYSIS =====
        
        report.append("\n" + "="*80)
        report.append("COMPLETENESS ANALYSIS")
        report.append("="*80)
        
        total_records = len(df)
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_pct = (null_count / total_records) * 100
            
            empty_count = (df[col] == '').sum() if df[col].dtype == 'object' else 0
            empty_pct = (empty_count / total_records) * 100
            
            report.append(f"\n{col}:")
            report.append(f"  Null: {null_count} ({null_pct:.2f}%)")
            if df[col].dtype == 'object':
                report.append(f"  Empty: {empty_count} ({empty_pct:.2f}%)")
        
        # ===== DESCRIPTIVE STATISTICS =====
        
        report.append("\n" + "="*80)
        report.append("NUMERIC FIELDS - DESCRIPTIVE STATISTICS")
        report.append("="*80)
        
        numeric_cols = ['year', 'runtime', 'vote_average', 'vote_count', 
                       'popularity', 'budget', 'revenue', 'review_count']
        
        desc = df[numeric_cols].describe()
        report.append("\n" + desc.to_string())
        
        # ===== CATEGORICAL FIELDS =====
        
        report.append("\n" + "="*80)
        report.append("CATEGORICAL FIELDS - VALUE COUNTS")
        report.append("="*80)
        
        # Top languages
        report.append("\nTop 10 Languages:")
        lang_counts = df['original_language'].value_counts().head(10)
        for lang, count in lang_counts.items():
            report.append(f"  {lang}: {count} ({count/total_records*100:.2f}%)")
        
        # Status distribution
        report.append("\nStatus Distribution:")
        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            report.append(f"  {status}: {count} ({count/total_records*100:.2f}%)")
        
        # ===== TEXT FIELDS ANALYSIS =====
        
        report.append("\n" + "="*80)
        report.append("TEXT FIELDS ANALYSIS")
        report.append("="*80)
        
        report.append(f"\nclean_text:")
        report.append(f"  Avg length: {df['clean_text'].str.len().mean():.0f} characters")
        report.append(f"  Min length: {df['clean_text'].str.len().min():.0f}")
        report.append(f"  Max length: {df['clean_text'].str.len().max():.0f}")
        
        report.append(f"\nclean_overview:")
        report.append(f"  Avg length: {df['clean_overview'].str.len().mean():.0f} characters")
        report.append(f"  Min length: {df['clean_overview'].str.len().min():.0f}")
        report.append(f"  Max length: {df['clean_overview'].str.len().max():.0f}")
        
        # ===== DATA QUALITY ISSUES =====
        
        report.append("\n" + "="*80)
        report.append("POTENTIAL DATA QUALITY ISSUES")
        report.append("="*80)
        
        # Movies with no reviews
        no_reviews = (df['review_count'] == 0).sum()
        report.append(f"\nMovies with no reviews: {no_reviews} ({no_reviews/total_records*100:.2f}%)")
        
        # Movies with no budget info
        no_budget = (df['budget'] == 0).sum()
        report.append(f"Movies with no budget info: {no_budget} ({no_budget/total_records*100:.2f}%)")
        
        # Movies with no revenue info
        no_revenue = (df['revenue'] == 0).sum()
        report.append(f"Movies with no revenue info: {no_revenue} ({no_revenue/total_records*100:.2f}%)")
        
        # Movies with low vote count
        low_votes = (df['vote_count'] < 10).sum()
        report.append(f"Movies with <10 votes: {low_votes} ({low_votes/total_records*100:.2f}%)")
        
        # ===== RECOMMENDATIONS =====
        
        report.append("\n" + "="*80)
        report.append("RECOMMENDATIONS")
        report.append("="*80)
        
        if no_reviews > total_records * 0.3:
            report.append("\n⚠️  HIGH: >30% movies have no reviews")
            report.append("   → Consider filtering or using only movies with reviews for collaborative filtering")
        
        if low_votes > total_records * 0.2:
            report.append("\n⚠️  MEDIUM: >20% movies have <10 votes")
            report.append("   → Consider filtering low-vote movies or using popularity weighting")
        
        if no_budget > total_records * 0.5:
            report.append("\n⚠️  INFO: >50% movies missing budget data")
            report.append("   → Budget may not be reliable feature for modeling")
        
        report.append("\n✅ Data is ready for modeling")
        
        report.append("\n" + "="*80)
        
        return '\n'.join(report)
    
    def save_results(self, df, report):
        """บันทึกผลลัพธ์"""
        self.log("\nSaving results...")
        
        # Save CSV
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        self.log(f"✅ Saved: {OUTPUT_FILE}")
        self.log(f"   Size: {OUTPUT_FILE.stat().st_size / 1024:.2f} KB")
        
        # Save report
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"✅ Saved: {REPORT_FILE}")
        
        # Save cleaning log
        log_file = OUTPUT_DIR / "cleaning_log.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.cleaning_log))
        
        self.log(f"✅ Saved: {log_file}")
    
    def run(self):
        """รัน cleaning pipeline ทั้งหมด"""
        
        print("="*80)
        print("DATA CLEANING & INTEGRATION PIPELINE")
        print("="*80)
        
        # Load data
        movies_raw, reviews_raw = self.load_data()
        
        # Process movies
        movies_df = self.process_movies(movies_raw)
        
        # Aggregate reviews
        reviews_df = self.aggregate_reviews(reviews_raw)
        
        # Merge
        merged_df = self.merge_data(movies_df, reviews_df)
        
        # Create clean_text
        merged_df = self.create_clean_text(merged_df)
        
        # Handle missing values
        merged_df = self.handle_missing_values(merged_df)
        
        # Validate data
        merged_df = self.validate_data(merged_df)
        
        # Remove duplicates
        merged_df = self.remove_duplicates(merged_df)
        
        # Finalize
        final_df = self.finalize_dataset(merged_df)
        
        # Generate report
        report = self.generate_report(final_df)
        
        # Save
        self.save_results(final_df, report)
        
        print("\n" + "="*80)
        print("✅ DATA CLEANING COMPLETE")
        print("="*80)
        print(f"\nOutput files:")
        print(f"1. {OUTPUT_FILE}")
        print(f"2. {REPORT_FILE}")
        print(f"3. {OUTPUT_DIR / 'cleaning_log.txt'}")
        
        return final_df


def main():
    """Main execution"""
    cleaner = DataCleaner()
    df = cleaner.run()
    
    # Show sample
    print("\n📄 Sample Records (first 3):")
    print("-" * 80)
    for i, row in df.head(3).iterrows():
        print(f"\n{i+1}. {row['title']} ({row['year']})")
        print(f"   Genres: {row['genres']}")
        print(f"   Rating: {row['vote_average']}/10 ({row['vote_count']} votes)")
        print(f"   Clean text length: {len(row['clean_text'])} chars")


if __name__ == "__main__":
    main()