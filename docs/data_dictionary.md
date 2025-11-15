# Data Dictionary - Movie Recommendation System

## Dataset Overview

| File | Description | Records | Size |
|------|-------------|---------|------|
| `raw_movies.json` | Movie details from TMDB | ~200 | ~850 KB |
| `raw_reviews.json` | User reviews from TMDB | ~450 | ~230 KB |

---

## 1. Movies Dataset (`raw_movies.json`)

### Structure
Array of movie objects with detailed information

### Fields

| Field | Type | Description | Example | Nullable |
|-------|------|-------------|---------|----------|
| `id` | Integer | Unique movie ID from TMDB | 550 | No |
| `title` | String | Movie title | "Fight Club" | No |
| `original_title` | String | Original title (if different) | "Fight Club" | No |
| `overview` | String | Movie plot summary | "A ticking-time-bomb..." | Yes |
| `tagline` | String | Movie tagline | "Mischief. Mayhem. Soap." | Yes |
| `release_date` | String (Date) | Release date | "1999-10-15" | Yes |
| `runtime` | Integer | Duration in minutes | 139 | Yes |
| `budget` | Integer | Production budget (USD) | 63000000 | Yes |
| `revenue` | Integer | Box office revenue (USD) | 100853753 | Yes |
| `vote_average` | Float | Average rating (0-10) | 8.4 | No |
| `vote_count` | Integer | Number of votes | 26280 | No |
| `popularity` | Float | Popularity score | 61.416 | No |
| `adult` | Boolean | Adult content flag | false | No |
| `status` | String | Release status | "Released" | Yes |
| `original_language` | String | ISO 639-1 code | "en" | No |

#### Nested Objects

**genres** (Array of Objects)
```json
{
  "id": 18,
  "name": "Drama"
}
```

**keywords.keywords** (Array of Objects)
```json
{
  "id": 825,
  "name": "support group"
}
```

**production_companies** (Array of Objects)
```json
{
  "id": 508,
  "name": "Regency Enterprises",
  "origin_country": "US"
}
```

**credits.cast** (Array of Objects)
```json
{
  "id": 819,
  "name": "Edward Norton",
  "character": "The Narrator",
  "order": 0
}
```

---

## 2. Reviews Dataset (`raw_reviews.json`)

### Structure
Array of review objects

### Fields

| Field | Type | Description | Example | Nullable |
|-------|------|-------------|---------|----------|
| `id` | String | Unique review ID | "5488c29bc3a3686f4a00004a" | No |
| `movie_id` | Integer | TMDB movie ID | 550 | No |
| `movie_title` | String | Movie title (added) | "Fight Club" | No |
| `author` | String | Review author username | "John Doe" | No |
| `content` | String | Full review text | "This movie is amazing..." | No |
| `created_at` | String (ISO 8601) | Review creation date | "2015-06-24T15:45:05.000Z" | No |
| `updated_at` | String (ISO 8601) | Last update date | "2021-06-23T15:58:35.000Z" | No |
| `url` | String | TMDB review URL | "https://www.themoviedb.org/review/..." | No |

#### Nested Object

**author_details** (Object)
```json
{
  "name": "John Doe",
  "username": "johndoe",
  "avatar_path": "/path/to/avatar.jpg",
  "rating": 9.0
}
```

|  Subfield     |  Type  |      Description      | Nullable |
|---------------|--------|-----------------------|----------|
| `name`        | String | Author's display name | Yes      |
| `username`    | String | Author's username     | No       |
| `avatar_path` | String | Avatar image path     | Yes      |
| `rating`      | Float  | User's rating (0-10)  | Yes      |

---

## Data Quality Notes

### Movies Dataset
- **Completeness**: ~95% of records have all core fields filled
- **Missing Data**: 
  - `tagline`: ~30% empty
  - `budget`/`revenue`: ~40% zero or missing
  - `keywords`: ~10% empty
- **Language**: Primarily English (`en`), includes some international films

### Reviews Dataset
- **Completeness**: ~90% have ratings
- **Distribution**: 
  - Average 2-3 reviews per movie
  - Some popular movies have 10+ reviews
- **Text Length**: 50-2000 characters per review

---

## Data Source

**API:** The Movie Database (TMDB) API v3  
**License:** TMDB API Terms of Use  
**Attribution Required:** Yes  
**Commercial Use:** Educational purposes only  

**Fetched Date:** 2025-11-15  
**API Version:** 3  
**Data Freshness:** Real-time from TMDB  

---

## Ethical Considerations

### Data Usage
✅ **Public Data**: All data is publicly available via TMDB API  
✅ **No Personal Data**: No private user information collected  
✅ **Attribution**: TMDB credited as data source  
✅ **Educational Purpose**: Used for learning and research only  

### Limitations
⚠️ Reviews reflect individual opinions and may contain bias  
⚠️ Ratings may not represent all demographics equally  
⚠️ Data skewed toward popular English-language films  

---

## Update History

| Date       | Version |           Changes        |
|------------|---------|--------------------------|
| 2025-01-23 | 1.0     | Initial dataset creation |