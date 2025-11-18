import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def create_visualizations():
    print("Creating data quality visualizations...")
    
    # Load data
    df = pd.read_csv("data/cleaned/cleaned_movies.csv")
    
    # Create output directory
    viz_dir = Path("data/cleaned/visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    # 1. Completeness by field
    plt.figure(figsize=(10, 6))
    
    completeness = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            complete = ((df[col].notna()) & (df[col] != '')).sum()
        else:
            complete = df[col].notna().sum()
        
        completeness[col] = (complete / len(df)) * 100
    
    completeness_df = pd.DataFrame.from_dict(
        completeness, 
        orient='index', 
        columns=['Completeness %']
    ).sort_values('Completeness %')
    
    completeness_df.plot(kind='barh', legend=False, color='steelblue')
    plt.xlabel('Completeness (%)')
    plt.title('Data Completeness by Field')
    plt.tight_layout()
    plt.savefig(viz_dir / 'completeness.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'completeness.png'}")
    plt.close()
    
    # 2. Rating distribution
    plt.figure(figsize=(10, 6))
    
    plt.hist(df['vote_average'], bins=20, color='coral', edgecolor='black', alpha=0.7)
    plt.xlabel('Vote Average (0-10)')
    plt.ylabel('Number of Movies')
    plt.title('Distribution of Movie Ratings')
    plt.axvline(df['vote_average'].mean(), color='red', linestyle='--', 
                label=f'Mean: {df["vote_average"].mean():.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(viz_dir / 'rating_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'rating_distribution.png'}")
    plt.close()
    
    # 3. Movies per year
    plt.figure(figsize=(12, 6))
    
    year_counts = df['year'].value_counts().sort_index()
    plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, color='teal')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.title('Movies per Year in Dataset')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(viz_dir / 'movies_per_year.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'movies_per_year.png'}")
    plt.close()
    
    # 4. Top genres
    plt.figure(figsize=(10, 6))
    
    # Extract genres
    all_genres = []
    for genres_str in df['genres'].dropna():
        if genres_str:
            all_genres.extend(genres_str.split())
    
    from collections import Counter
    genre_counts = Counter(all_genres).most_common(10)
    
    genres, counts = zip(*genre_counts)
    plt.barh(genres, counts, color='mediumpurple')
    plt.xlabel('Number of Movies')
    plt.title('Top 10 Genres in Dataset')
    plt.tight_layout()
    plt.savefig(viz_dir / 'top_genres.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'top_genres.png'}")
    plt.close()
    
    # 5. Text length distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # clean_text
    axes[0].hist(df['clean_text'].str.len(), bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Text Length (characters)')
    axes[0].set_ylabel('Number of Movies')
    axes[0].set_title('Distribution of clean_text Length')
    axes[0].axvline(df['clean_text'].str.len().mean(), color='red', linestyle='--',
                    label=f'Mean: {df["clean_text"].str.len().mean():.0f}')
    axes[0].legend()
    
    # clean_overview
    axes[1].hist(df['clean_overview'].str.len(), bins=30, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[1].set_xlabel('Text Length (characters)')
    axes[1].set_ylabel('Number of Movies')
    axes[1].set_title('Distribution of clean_overview Length')
    axes[1].axvline(df['clean_overview'].str.len().mean(), color='red', linestyle='--',
                    label=f'Mean: {df["clean_overview"].str.len().mean():.0f}')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(viz_dir / 'text_length_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'text_length_distribution.png'}")
    plt.close()
    
    # 6. Review count distribution
    plt.figure(figsize=(10, 6))
    
    plt.hist(df['review_count'], bins=20, color='gold', edgecolor='black', alpha=0.7)
    plt.xlabel('Number of Reviews')
    plt.ylabel('Number of Movies')
    plt.title('Distribution of Review Counts')
    plt.axvline(df['review_count'].mean(), color='red', linestyle='--',
                label=f'Mean: {df["review_count"].mean():.1f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(viz_dir / 'review_count_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {viz_dir / 'review_count_distribution.png'}")
    plt.close()
    
    print(f"\n✅ All visualizations created in: {viz_dir}/")

if __name__ == "__main__":
    create_visualizations()