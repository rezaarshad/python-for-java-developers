"""Lesson 13 exercise: notes analytics with numpy, pandas, matplotlib.

Test: uv run pytest lessons/13_data/exercise -v

Rule: no Python for-loops over rows or vector elements. Use vectorized numpy/pandas operations.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402


# --- NumPy: vector helpers (you'll reuse these for RAG in Lesson 15) --------------------------------
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two 1-D vectors: a·b / (|a| |b|). Return 0.0 if either vector is all zeros."""
    # TODO
    pass


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """Scale every row of a 2-D array to unit length (L2 norm = 1). Leave all-zero rows as zeros.
    Hint: np.linalg.norm(matrix, axis=1, keepdims=True), then broadcasting; np.where avoids divide-by-zero."""
    # TODO
    pass


def top_k(query: np.ndarray, matrix: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Cosine similarity of `query` against EVERY row of `matrix` in one vectorized step
    (normalize, then matrix @ vector). Return the best k as [(row_index, score), ...], best first.
    Scores are Python floats rounded to 4 decimals. Hint: np.argsort(-scores)[:k]."""
    # TODO
    pass


# --- pandas ----------------------------------------------------------------------------------------
def load_notes(path: Path) -> pd.DataFrame:
    """Read the CSV (columns: id,title,created_at,tags,word_count,pinned).
    - created_at parsed as datetime
    - tags: a list of strings per row ("ai;llm" → ["ai", "llm"]); an empty cell → []
    """
    # TODO (hint: .fillna("") then .str.split(";"), then drop empty strings with .apply or a list comprehension)
    pass


def notes_per_month(df: pd.DataFrame) -> pd.Series:
    """Number of notes per month: a Series indexed by "YYYY-MM" strings, sorted by month."""
    # TODO (hint: .dt.strftime("%Y-%m") then groupby/value_counts, then sort_index)
    pass


def tag_counts(df: pd.DataFrame) -> pd.Series:
    """How many notes have each tag: a Series tag → count, most common first, ties broken alphabetically."""
    # TODO (hint: explode; value_counts; sort by count desc then index)
    pass


def words_by_tag(df: pd.DataFrame) -> pd.DataFrame:
    """One row per tag (index = tag, sorted alphabetically) with columns:
    notes (count), avg_words (mean word_count rounded to 1 decimal), max_words."""
    # TODO (hint: explode, then groupby(...).agg(notes=("id", "count"), ...))
    pass


def pinned_share(df: pd.DataFrame) -> float:
    """Fraction of notes that are pinned, rounded to 3 decimals. (Hint: the mean of a bool column.)"""
    # TODO
    pass


# --- matplotlib --------------------------------------------------------------------------------------
def plot_notes_per_month(per_month: pd.Series, path: Path) -> Figure:
    """Bar chart of `per_month`. Title "Notes per month", x label "Month", y label "Notes".
    Save it to `path` (PNG) and return the Figure. Use the OO API: fig, ax = plt.subplots()."""
    # TODO
    pass
