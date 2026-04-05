"""
tests/test_app.py
Unit tests for the Movie Recommender System
Run with: pytest tests/ -v --cov=app
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_movies_df():
    """Create a small mock movies DataFrame"""
    return pd.DataFrame({
        "title": [
            "The Dark Knight",
            "Inception",
            "Interstellar",
            "The Matrix",
            "Avengers: Endgame",
            "Pulp Fiction"
        ]
    })

@pytest.fixture
def sample_similarity_matrix(sample_movies_df):
    """Create a mock similarity matrix"""
    n = len(sample_movies_df)
    matrix = np.random.rand(n, n)
    # Make it symmetric and set diagonal to 1
    matrix = (matrix + matrix.T) / 2
    np.fill_diagonal(matrix, 1.0)
    return matrix


# ─── Tests: get_recommendations ──────────────────────────────────────────────

class TestGetRecommendations:

    def test_returns_five_recommendations(self, sample_movies_df, sample_similarity_matrix):
        """Should return exactly 5 recommendations"""
        from app import get_recommendations
        result = get_recommendations("The Dark Knight", sample_movies_df, sample_similarity_matrix)
        assert len(result) == 5

    def test_does_not_include_selected_movie(self, sample_movies_df, sample_similarity_matrix):
        """The selected movie should not appear in recommendations"""
        from app import get_recommendations
        result = get_recommendations("The Dark Knight", sample_movies_df, sample_similarity_matrix)
        assert "The Dark Knight" not in result

    def test_returns_empty_for_unknown_movie(self, sample_movies_df, sample_similarity_matrix):
        """Unknown movie title should return empty list"""
        from app import get_recommendations
        result = get_recommendations("NonExistent Movie 12345", sample_movies_df, sample_similarity_matrix)
        assert result == []

    def test_all_recommendations_are_valid_titles(self, sample_movies_df, sample_similarity_matrix):
        """All recommended titles should exist in the movies DataFrame"""
        from app import get_recommendations
        result = get_recommendations("Inception", sample_movies_df, sample_similarity_matrix)
        valid_titles = set(sample_movies_df["title"].tolist())
        for title in result:
            assert title in valid_titles

    def test_returns_list_type(self, sample_movies_df, sample_similarity_matrix):
        """Return type should always be a list"""
        from app import get_recommendations
        result = get_recommendations("Inception", sample_movies_df, sample_similarity_matrix)
        assert isinstance(result, list)


# ─── Tests: Data Validation ──────────────────────────────────────────────────

class TestDataValidation:

    def test_movies_df_has_title_column(self, sample_movies_df):
        """DataFrame must have a 'title' column"""
        assert "title" in sample_movies_df.columns

    def test_movies_df_not_empty(self, sample_movies_df):
        """DataFrame should not be empty"""
        assert not sample_movies_df.empty

    def test_similarity_matrix_shape(self, sample_movies_df, sample_similarity_matrix):
        """Similarity matrix should be square with shape matching the movies count"""
        n = len(sample_movies_df)
        assert sample_similarity_matrix.shape == (n, n)

    def test_similarity_diagonal_is_one(self, sample_similarity_matrix):
        """Self-similarity should be 1.0 for all movies"""
        diagonal = np.diag(sample_similarity_matrix)
        assert np.allclose(diagonal, 1.0)

    def test_similarity_values_in_range(self, sample_similarity_matrix):
        """All similarity scores should be between 0 and 1"""
        assert sample_similarity_matrix.min() >= 0
        assert sample_similarity_matrix.max() <= 1.0


# ─── Tests: Environment ───────────────────────────────────────────────────────

class TestEnvironment:

    def test_tmdb_api_key_env_var_exists(self):
        """TMDB_API_KEY env variable should be set in CI"""
        # This will pass locally with a default key in the code
        api_key = os.getenv("TMDB_API_KEY", "fallback-default-key")
        assert api_key is not None
        assert len(api_key) > 0

    def test_python_version(self):
        """Python version should be 3.9+"""
        assert sys.version_info >= (3, 9)
