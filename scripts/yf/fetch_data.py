import requests
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL')

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")

# Output paths
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

MOVIES_FILE = DATA_DIR / "raw_movies.json"
REVIEWS_FILE = DATA_DIR / "raw_reviews.json"
MOVIE_JSONL = DATA_DIR / "raw_movies.jsonl"
REVIEWS_JSONL = DATA_DIR / "raw_reviews.jsonl"

# API rate limiting
REQUEST_DELAY = 0.20  # 5 requests/second


def append_jsonl(path, record):
    """Append record to JSONL file"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_processed_ids(path):
    """Load processed movie IDs from JSONL file"""
    ids = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    ids.add(obj["id"])
                except:
                    continue
    return ids 


class TMDBFetcher:
    """Class สำหรับดึงข้อมูลจาก TMDB API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = TMDB_BASE_URL
        self.session = requests.Session()
        
    def safe_get(self, endpoint, params=None, retries=5):
        """Safe HTTP request with retry logic and exponential backoff"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(retries):
            try:
                r = self.session.get(url, params=params, timeout=15)
                if r.status_code == 200:
                    time.sleep(REQUEST_DELAY)
                    return r.json()
                else:
                    print(f"{endpoint} status {r.status_code}, retry {attempt+1}/{retries}")
            except Exception as e:
                print(f"{endpoint} error: {e}, retry {attempt+1}/{retries}")
            time.sleep(1 + attempt * 1.5)  # exponential backoff

        return None
    
    def fetch_popular_movies(self, num_pages=20):
        """
        ดึงรายการภาพยนตร์ยอดนิยม
        
        Args:
            num_pages (int): จำนวนหน้าที่จะดึง (20 movies/page)
        
        Returns:
            list: รายการภาพยนตร์
        """
        movies = []
        
        print(f"Fetching popular movies ({num_pages} pages)...")
        
        for page in tqdm(range(1, num_pages + 1)):
            data = self.safe_get('movie/popular', {'page': page, 'language': 'en-US'})
            
            if data and 'results' in data:
                movies.extend(data['results'])
            else:
                print(f"Failed to fetch page {page}")
        
        return movies
    
    def fetch_movie_details(self, movie_id):
        """
        ดึงรายละเอียดภาพยนตร์
        
        Args:
            movie_id (int): TMDB movie ID
        
        Returns:
            dict: ข้อมูลภาพยนตร์ครบถ้วน
        """
        details = self.safe_get(
            f'movie/{movie_id}',
            {'append_to_response': 'keywords,credits'}
        )
        
        return details
    
    def fetch_movie_reviews(self, movie_id):
        """
        ดึง reviews ของภาพยนตร์
        
        Args:
            movie_id (int): TMDB movie ID
        
        Returns:
            list: รายการ reviews
        """
        data = self.safe_get(f'movie/{movie_id}/reviews', {'page': 1})
        
        if data and 'results' in data:
            return data['results']
        
        return []
    
    def fetch_complete_dataset(self, num_movies=5000):
        """
        ดึงข้อมูลภาพยนตร์ครบชุด (resumable mode)
        
        Args:
            num_movies (int): จำนวนภาพยนตร์ที่ต้องการ
        """
        # Load checkpoint
        processed_ids = load_processed_ids(MOVIE_JSONL)

        print("="*80)
        print("TMDB DATA FETCHING (RESUMABLE MODE)")
        print("="*80)

        num_pages = (num_movies // 20) + 1
        popular_movies = self.fetch_popular_movies(num_pages)

        print(f"\nFetched {len(popular_movies)} popular movies\n")

        # Loop
        for movie in tqdm(popular_movies[:num_movies]):

            movie_id = movie["id"]

            # Skip if already done
            if movie_id in processed_ids:
                continue

            # Fetch details
            details = self.fetch_movie_details(movie_id)
            if not details:
                print(f"❌ Skip details for {movie_id}")
                continue

            # Save movie details
            append_jsonl(MOVIE_JSONL, details)

            # Fetch reviews
            reviews = self.fetch_movie_reviews(movie_id)
            if reviews:
                for r in reviews:
                    r["movie_id"] = movie_id
                    r["movie_title"] = details.get("title", "")
                    append_jsonl(REVIEWS_JSONL, r)

            # Mark as done
            processed_ids.add(movie_id)

        print("\n⭐ Fetching complete (safe mode)")
        print(f"Movies saved to: {MOVIE_JSONL}")
        print(f"Reviews saved to: {REVIEWS_JSONL}")

def save_data(movies, reviews):
    """บันทึกข้อมูลเป็น JSON files"""
    
    print("\nSaving data...")
    
    # Save movies
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved: {MOVIES_FILE}")
    print(f"   Size: {MOVIES_FILE.stat().st_size / 1024:.2f} KB")
    
    # Save reviews
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved: {REVIEWS_FILE}")
    print(f"   Size: {REVIEWS_FILE.stat().st_size / 1024:.2f} KB")


def print_sample_data(movies, reviews):
    """แสดงตัวอย่างข้อมูล"""
    
    print("\n" + "="*80)
    print("SAMPLE DATA")
    print("="*80)
    
    if movies:
        print("\n📽️  Sample Movie:")
        sample_movie = movies[0]
        print(f"   Title: {sample_movie.get('title')}")
        print(f"   Overview: {sample_movie.get('overview', '')[:100]}...")
        print(f"   Genres: {[g['name'] for g in sample_movie.get('genres', [])]}")
        print(f"   Release Date: {sample_movie.get('release_date')}")
        print(f"   Rating: {sample_movie.get('vote_average')}/10")
        
        if 'keywords' in sample_movie:
            keywords = [k['name'] for k in sample_movie.get('keywords', {}).get('keywords', [])]
            print(f"   Keywords: {keywords[:5]}")
    
    if reviews:
        print("\n💬 Sample Review:")
        sample_review = reviews[0]
        print(f"   Movie: {sample_review.get('movie_title')}")
        print(f"   Author: {sample_review.get('author')}")
        print(f"   Rating: {sample_review.get('author_details', {}).get('rating', 'N/A')}/10")
        print(f"   Content: {sample_review.get('content', '')[:150]}...")


def main():
    """Main execution"""
    
    # Initialize fetcher
    fetcher = TMDBFetcher(TMDB_API_KEY)
    
    # Fetch data (5000 movies by default)
    fetcher.fetch_complete_dataset(num_movies=5000)
    
    print("\n" + "="*80)
    print("✅ DATA FETCHING COMPLETE")
    print("="*80)
    print(f"\nNext steps:")
    print(f"1. Check data/raw/raw_movies.jsonl")
    print(f"2. Check data/raw/raw_reviews.jsonl")
    print(f"3. Run data quality checks")


if __name__ == "__main__":
    main()