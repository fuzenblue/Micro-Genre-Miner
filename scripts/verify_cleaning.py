import pandas as pd
from pathlib import Path

def verify_cleaned_data():
    print("="*80)
    print("CLEANED DATA VERIFICATION")
    print("="*80)
    
    # Load cleaned data
    file_path = Path("data/cleaned/cleaned_movies.csv")
    
    if not file_path.exists():
        print("❌ Error: cleaned_movies.csv not found!")
        print("   Run: python scripts/clean_data.py")
        return False
    
    df = pd.read_csv(file_path)
    
    print(f"\n📊 Dataset Info:")
    print(f"   Total records: {len(df)}")
    print(f"   Total columns: {len(df.columns)}")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Check required columns
    required_cols = [
        'movie_id', 'title', 'year', 'genres', 
        'overview', 'clean_text', 'vote_average'
    ]
    
    print(f"\n✓ Checking required columns...")
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"   ❌ Missing columns: {missing_cols}")
        return False
    else:
        print(f"   ✅ All required columns present")
    
    # Check for nulls
    print(f"\n✓ Checking for null values...")
    critical_cols = ['movie_id', 'title', 'overview', 'clean_text', 'year']
    
    nulls_found = False
    for col in critical_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f"   ❌ {col}: {null_count} nulls")
            nulls_found = True
    
    if not nulls_found:
        print(f"   ✅ No nulls in critical columns")
    
    # Check clean_text
    print(f"\n✓ Checking clean_text field...")
    empty_text = (df['clean_text'].str.len() == 0).sum()
    
    if empty_text > 0:
        print(f"   ⚠️  {empty_text} records with empty clean_text")
    else:
        print(f"   ✅ All records have clean_text")
    
    # Text length stats
    text_lengths = df['clean_text'].str.len()
    print(f"\n   Text length stats:")
    print(f"   - Min: {text_lengths.min()} chars")
    print(f"   - Mean: {text_lengths.mean():.0f} chars")
    print(f"   - Max: {text_lengths.max()} chars")
    
    # Check year range
    print(f"\n✓ Checking year validity...")
    year_min = df['year'].min()
    year_max = df['year'].max()
    
    print(f"   Year range: {year_min} - {year_max}")
    
    if year_min < 1900 or year_max > 2030:
        print(f"   ⚠️  Suspicious year range")
    else:
        print(f"   ✅ Year range valid")
    
    # Check ratings
    print(f"\n✓ Checking ratings...")
    rating_min = df['vote_average'].min()
    rating_max = df['vote_average'].max()
    
    print(f"   Rating range: {rating_min} - {rating_max}")
    
    if rating_min < 0 or rating_max > 10:
        print(f"   ❌ Invalid rating range")
        return False
    else:
        print(f"   ✅ Rating range valid")
    
    # Show sample
    print(f"\n📄 Sample records:")
    print("-" * 80)
    
    for i, row in df.head(3).iterrows():
        print(f"\n{i+1}. {row['title']} ({row['year']})")
        print(f"   Genres: {row['genres'][:50]}...")
        print(f"   Rating: {row['vote_average']}/10")
        print(f"   Clean text: {len(row['clean_text'])} chars")
        print(f"   Review count: {row['review_count']}")
    
    print("\n" + "="*80)
    print("✅ VERIFICATION PASSED")
    print("="*80)
    print("\nDataset is ready for Phase 3 (Model Building)")
    
    return True

if __name__ == "__main__":
    verify_cleaned_data()