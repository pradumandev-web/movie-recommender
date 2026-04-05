# IMPORTANT: set_page_config must be the very first Streamlit command
import streamlit as st

st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other libraries
import pickle
import pandas as pd
import requests
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time

# Simple logging setup
import logging
import sys
import tempfile


def setup_logging():
    log_dir = os.path.join(tempfile.gettempdir(), 'movie_recommender_logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()

# Get TMDB API key - simple version without st.secrets
TMDB_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_KEY:
    st.error("🔑 TMDB API key not found.")
    st.stop()

logger.info("TMDB API key loaded successfully")


# Cache data loading with performance monitoring
@st.cache_resource
@st.cache_resource
def load_data():
    """Load pickle files - download from S3 if not present locally"""
    try:
        import boto3

        start_time = time.time()
        logger.info("Checking for data files...")

        bucket_name = os.getenv("S3_BUCKET_NAME", "movie-recommender-praduman")

        # Download from S3 if files don't exist locally
        if not os.path.exists("movie_dict.pkl") or not os.path.exists("similarity.pkl"):
            logger.info("Downloading data files from S3...")
            s3 = boto3.client("s3")

            with st.spinner("📥 Downloading movie database from S3... (first run only)"):
                s3.download_file(bucket_name, "movie_dict.pkl", "movie_dict.pkl")
                logger.info("Downloaded movie_dict.pkl")

                s3.download_file(bucket_name, "similarity.pkl", "similarity.pkl")
                logger.info("Downloaded similarity.pkl")
        else:
            logger.info("Data files found locally, skipping download")

        # Load into memory
        movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
        movies_df = pd.DataFrame(movies_dict)
        similarity_matrix = pickle.load(open("similarity.pkl", "rb"))

        if movies_df.empty:
            raise ValueError("Movies data is empty")
        if similarity_matrix is None or len(similarity_matrix) == 0:
            raise ValueError("Similarity matrix is empty")

        load_time = time.time() - start_time
        logger.info(f"Loaded {len(movies_df)} movies in {load_time:.2f}s")

        return movies_df, similarity_matrix

    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        st.error(f"❌ Failed to load movie database: {str(e)}")
        st.stop()

# Cache API calls with TTL
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_movie_info(movie_title, retry_count=2):
    """Fetch movie info from TMDB with retry logic"""
    for attempt in range(retry_count):
        try:
            logger.info(f"Fetching info for: {movie_title} (attempt {attempt + 1})")

            # Search for movie
            search_url = f"https://api.themoviedb.org/3/search/movie"
            params = {
                "api_key": TMDB_KEY,
                "query": movie_title,
                "language": "en-US"
            }

            res = requests.get(search_url, params=params, timeout=10)
            res.raise_for_status()
            search_data = res.json()

            if "results" not in search_data or len(search_data["results"]) == 0:
                logger.warning(f"No results found for: {movie_title}")
                return None

            movie_result = search_data["results"][0]
            movie_id = movie_result["id"]

            # Get detailed info
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            detail_params = {"api_key": TMDB_KEY, "language": "en-US"}
            details_response = requests.get(detail_url, params=detail_params, timeout=10)
            details_response.raise_for_status()
            movie_details = details_response.json()

            poster_url = (
                f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path')}"
                if movie_details.get("poster_path")
                else None
            )

            return {
                "title": movie_details.get("title"),
                "year": movie_details.get("release_date", "")[:4] if movie_details.get("release_date") else "N/A",
                "genres": ", ".join([genre["name"] for genre in movie_details.get("genres", [])]),
                "overview": movie_details.get("overview", "No overview available."),
                "poster": poster_url,
                "rating": movie_details.get("vote_average", 0),
                "vote_count": movie_details.get("vote_count", 0),
                "runtime": movie_details.get("runtime"),
                "status": movie_details.get("status", "Released")
            }

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {movie_title}, attempt {attempt + 1}")
            if attempt == retry_count - 1:
                return None
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {movie_title}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {movie_title}: {e}")
            return None

    return None


def get_recommendations(selected_movie, movies_data, similarity_data):
    """Get movie recommendations using similarity matrix"""
    try:
        # Find movie index
        movie_indices = movies_data[movies_data["title"] == selected_movie].index
        if len(movie_indices) == 0:
            logger.error(f"Movie not found: {selected_movie}")
            return []

        movie_index = movie_indices[0]

        # Get similarity scores
        distances = similarity_data[movie_index]

        # Sort and get top 5 recommendations (excluding the movie itself)
        similar_indices = np.argsort(distances)[::-1][1:6]

        # Get recommended movie titles
        recommended_movies = movies_data.iloc[similar_indices]["title"].tolist()

        logger.info(f"Generated {len(recommended_movies)} recommendations for {selected_movie}")
        return recommended_movies

    except IndexError as e:
        logger.error(f"Index error in recommendation: {e}")
        return []
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return []


# Load data
movies_df, similarity_matrix = load_data()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .movie-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .rating {
        color: #ffb400;
        font-weight: bold;
    }
    .genre-tag {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 2px;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This intelligent recommendation system suggests movies based on content similarity.

    **Features:**
    - 🎯 Content-based filtering
    - 🎨 Movie posters from TMDB
    - ⭐ Ratings and runtime
    - 📖 Detailed overviews
    """)

    st.metric("📊 Database Size", f"{len(movies_df):,} movies")

    st.header("🎯 How it works")
    st.markdown("""
    1. Select a movie you like
    2. Click "Recommend"
    3. Get 5 similar movies based on:
       - Genre similarity
       - Cast & crew
       - Plot keywords
       - User ratings patterns
    """)

    st.header("🔑 API Status")
    st.success("✅ TMDB API Connected")

    # Add some stats
    st.header("📈 Stats")
    if st.button("Show Sample Movies"):
        st.write(movies_df.sample(5)["title"].tolist())

    # Show log location for debugging
    with st.expander("Debug Info"):
        log_path = os.path.join(tempfile.gettempdir(), 'movie_recommender_logs', 'app.log')
        st.write(f"Log file location: {log_path}")

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Select a movie you've enjoyed")
    selected_movie_name = st.selectbox(
        "Choose a movie:",
        movies_df["title"].values,
        label_visibility="collapsed"
    )

    if st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
        with st.spinner("🤔 Finding the best recommendations for you..."):
            recommendations_list = get_recommendations(selected_movie_name, movies_df, similarity_matrix)

            if recommendations_list:
                st.success(f"✨ Found {len(recommendations_list)} great recommendations!")

                # Display recommendations in a grid
                for idx, movie_name in enumerate(recommendations_list):
                    with st.container():
                        col_img, col_info = st.columns([1, 2])

                        with col_img:
                            # Fetch movie info
                            movie_info = fetch_movie_info(movie_name)
                            if movie_info and movie_info["poster"]:
                                # Fixed: use use_column_width instead of use_container_width
                                st.image(movie_info["poster"], use_column_width=True)
                            else:
                                # Fixed: use use_column_width instead of use_container_width
                                st.image("https://via.placeholder.com/300x450?text=No+Poster", use_column_width=True)

                        with col_info:
                            if movie_info:
                                st.markdown(f"### {idx + 1}. {movie_info['title']} ({movie_info['year']})")

                                # Rating with stars
                                rating_value = movie_info['rating'] or 0
                                stars = "⭐" * int(rating_value / 2) + "☆" * (5 - int(rating_value / 2))
                                st.markdown(f"**Rating:** {stars} {rating_value}/10")

                                # Genres as tags
                                if movie_info['genres']:
                                    genres_html = " ".join(
                                        [f'<span class="genre-tag">{genre.strip()}</span>' for genre in
                                         movie_info['genres'].split(',')[:3]])
                                    st.markdown(f"**Genres:** {genres_html}", unsafe_allow_html=True)

                                # Runtime formatting
                                if movie_info['runtime']:
                                    hours = movie_info['runtime'] // 60
                                    minutes = movie_info['runtime'] % 60
                                    runtime_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                                    st.markdown(f"**⏱️ Runtime:** {runtime_str}")

                                # Vote count
                                if movie_info.get('vote_count', 0) > 0:
                                    st.markdown(f"**👥 Votes:** {movie_info['vote_count']:,}")

                                # Overview with expander
                                with st.expander("📖 Click for synopsis"):
                                    st.write(movie_info['overview'])

                                # Add a separator
                                st.markdown("---")
                            else:
                                st.markdown(f"### {idx + 1}. {movie_name}")
                                st.warning("Movie details temporarily unavailable")
                                st.markdown("---")
            else:
                st.error("❌ No recommendations found. Please try another movie.")

        # Log the recommendation activity
        logger.info(f"Recommendations generated for: {selected_movie_name}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        <p>🎬 Powered by TMDB API | 🤖 Content-based filtering with scikit-learn</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)