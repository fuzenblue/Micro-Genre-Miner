import json
from pathlib import Path

def verify_data():
    print("="*80)
    print("DATA QUALITY VERIFICATION")
    print("="*80)
    
    # Load movies
    movies_file = Path("../../data/raw/raw_movies.json")
    with open(movies_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)
    
    print(f"\n📽️  Movies Dataset:")
    print(f"   Total movies: {len(movies)}")
    
    # Check required fields
    required_fields = ['id', 'title', 'overview', 'genres']
    complete_movies = sum(1 for m in movies if all(f in m for f in required_fields))
    print(f"   Complete records: {complete_movies}/{len(movies)} ({complete_movies/len(movies)*100:.1f}%)")
    
    # Check genres
    all_genres = set()
    for movie in movies:
        for genre in movie.get('genres', []):
            all_genres.add(genre['name'])
    print(f"   Unique genres: {len(all_genres)}")
    print(f"   Genres: {sorted(all_genres)}")
    
    # Load reviews
    reviews_file = Path("../../data/raw/raw_reviews.json")
    with open(reviews_file, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    print(f"\n💬 Reviews Dataset:")
    print(f"   Total reviews: {len(reviews)}")
    
    # Check ratings
    rated_reviews = sum(1 for r in reviews if r.get('author_details', {}).get('rating'))
    print(f"   Reviews with ratings: {rated_reviews}/{len(reviews)} ({rated_reviews/len(reviews)*100:.1f}%)")
    
    # Distribution
    movies_with_reviews = len(set(r['movie_id'] for r in reviews))
    print(f"   Movies with reviews: {movies_with_reviews}/{len(movies)}")
    print(f"   Avg reviews per movie: {len(reviews)/movies_with_reviews:.1f}")
    
    print("\n✅ Data quality check complete")

if __name__ == "__main__":
    verify_data()