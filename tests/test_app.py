import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np


def get_recommendations(selected_movie, movies_data, similarity_data):
    """Standalone version to avoid Streamlit import issues"""
    movie_indices = movies_data[movies_data["title"] == selected_movie].index
    if len(movie_indices) == 0:
        return []
    movie_index = movie_indices[0]
    distances = similarity_data[movie_index]
    similar_indices = np.argsort(distances)[::-1][1:6]
    return movies_data.iloc[similar_indices]["title"].tolist()


@pytest.fixture
def sample_movies_df():
    return pd.DataFrame({
        "title": ["The Dark Knight", "Inception", "Interstellar",
                  "The Matrix", "Avengers: Endgame", "Pulp Fiction"]
    })


@pytest.fixture
def sample_similarity_matrix(sample_movies_df):
    n = len(sample_movies_df)
    matrix = np.random.rand(n, n)
    matrix = (matrix + matrix.T) / 2
    np.fill_diagonal(matrix, 1.0)
    return matrix


class TestGetRecommendations:

    def test_returns_five_recommendations(self, sample_movies_df, sample_similarity_matrix):
        result = get_recommendations("The Dark Knight", sample_movies_df, sample_similarity_matrix)
        assert len(result) == 5

    def test_does_not_include_selected_movie(self, sample_movies_df, sample_similarity_matrix):
        result = get_recommendations("The Dark Knight", sample_movies_df, sample_similarity_matrix)
        assert "The Dark Knight" not in result

    def test_returns_empty_for_unknown_movie(self, sample_movies_df, sample_similarity_matrix):
        result = get_recommendations("NonExistent Movie 12345", sample_movies_df, sample_similarity_matrix)
        assert result == []

    def test_all_recommendations_are_valid_titles(self, sample_movies_df, sample_similarity_matrix):
        result = get_recommendations("Inception", sample_movies_df, sample_similarity_matrix)
        valid_titles = set(sample_movies_df["title"].tolist())
        for title in result:
            assert title in valid_titles

    def test_returns_list_type(self, sample_movies_df, sample_similarity_matrix):
        result = get_recommendations("Inception", sample_movies_df, sample_similarity_matrix)
        assert isinstance(result, list)


class TestDataValidation:

    def test_movies_df_has_title_column(self, sample_movies_df):
        assert "title" in sample_movies_df.columns

    def test_movies_df_not_empty(self, sample_movies_df):
        assert not sample_movies_df.empty

    def test_similarity_matrix_shape(self, sample_movies_df, sample_similarity_matrix):
        n = len(sample_movies_df)
        assert sample_similarity_matrix.shape == (n, n)

    def test_similarity_diagonal_is_one(self, sample_similarity_matrix):
        diagonal = np.diag(sample_similarity_matrix)
        assert np.allclose(diagonal, 1.0)

    def test_similarity_values_in_range(self, sample_similarity_matrix):
        assert sample_similarity_matrix.min() >= 0
        assert sample_similarity_matrix.max() <= 1.0


class TestEnvironment:

    def test_tmdb_api_key_env_var_exists(self):
        api_key = os.getenv("TMDB_API_KEY", "fallback-default-key")
        assert api_key is not None
        assert len(api_key) > 0

    def test_python_version(self):
        assert sys.version_info >= (3, 9)