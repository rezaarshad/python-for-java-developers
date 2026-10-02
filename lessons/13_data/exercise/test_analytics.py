"""Provided tests. Run: uv run pytest lessons/13_data/exercise -v"""

import numpy as np
import pandas as pd
import pytest

from analytics import (
    cosine_similarity,
    load_notes,
    normalize_rows,
    notes_per_month,
    pinned_share,
    plot_notes_per_month,
    tag_counts,
    top_k,
    words_by_tag,
)

CSV = """id,title,created_at,tags,word_count,pinned
1,RAG,2026-01-05T10:00,ai;llm,300,True
2,Pandas,2026-01-20T11:30,python;data,120,False
3,Groceries,2026-02-02T09:00,,10,False
4,Claude tools,2026-02-14T16:45,ai;llm;python,450,True
5,NumPy,2026-03-01T08:15,python;data,200,False
"""


@pytest.fixture
def df(tmp_path):
    path = tmp_path / "notes.csv"
    path.write_text(CSV, encoding="utf-8")
    return load_notes(path)


# --- numpy -----------------------------------------------------------------------------------
def test_cosine_similarity():
    assert cosine_similarity(np.array([1.0, 0]), np.array([1.0, 0])) == pytest.approx(1.0)
    assert cosine_similarity(np.array([1.0, 0]), np.array([0, 1.0])) == pytest.approx(0.0)
    assert cosine_similarity(np.array([1.0, 1]), np.array([-1.0, -1])) == pytest.approx(-1.0)
    assert cosine_similarity(np.array([3.0, 4]), np.array([6.0, 8])) == pytest.approx(1.0)
    assert cosine_similarity(np.array([0.0, 0]), np.array([1.0, 2])) == 0.0
    assert isinstance(cosine_similarity(np.array([1.0]), np.array([2.0])), float)


def test_normalize_rows():
    m = np.array([[3.0, 4.0], [0.0, 0.0], [0.0, 2.0]])
    out = normalize_rows(m)
    assert np.allclose(out, [[0.6, 0.8], [0, 0], [0, 1]])
    assert np.allclose(m, [[3.0, 4.0], [0.0, 0.0], [0.0, 2.0]]), "don't modify the input"


def test_top_k():
    matrix = np.array([[1.0, 0, 0], [0.9, 0.1, 0], [0, 1.0, 0], [0, 0, 1.0], [0.5, 0.5, 0]])
    result = top_k(np.array([1.0, 0.05, 0]), matrix, k=3)
    assert [i for i, _ in result] == [0, 1, 4]
    assert result[0][1] == pytest.approx(0.9988, abs=1e-4)
    assert all(isinstance(i, int) and isinstance(s, float) for i, s in result)


# --- pandas -------------------------------------------------------------------------------------
def test_load_notes(df):
    assert list(df["id"]) == [1, 2, 3, 4, 5]
    assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
    assert df.loc[0, "tags"] == ["ai", "llm"]
    assert df.loc[2, "tags"] == [], "an empty tags cell must become []"
    assert df["pinned"].dtype == bool


def test_notes_per_month(df):
    s = notes_per_month(df)
    assert s.to_dict() == {"2026-01": 2, "2026-02": 2, "2026-03": 1}
    assert list(s.index) == ["2026-01", "2026-02", "2026-03"]


def test_tag_counts(df):
    s = tag_counts(df)
    assert list(s.items()) == [("python", 3), ("ai", 2), ("data", 2), ("llm", 2)]


def test_words_by_tag(df):
    t = words_by_tag(df)
    assert list(t.index) == ["ai", "data", "llm", "python"]
    assert list(t.columns) == ["notes", "avg_words", "max_words"]
    assert t.loc["ai"].to_dict() == {"notes": 2, "avg_words": 375.0, "max_words": 450}
    assert t.loc["python", "avg_words"] == pytest.approx(256.7)


def test_pinned_share(df):
    assert pinned_share(df) == 0.4


# --- matplotlib -----------------------------------------------------------------------------------
def test_plot_notes_per_month(df, tmp_path):
    out = tmp_path / "chart.png"
    fig = plot_notes_per_month(notes_per_month(df), out)
    assert out.exists() and out.stat().st_size > 1000
    assert out.read_bytes()[:4] == b"\x89PNG"
    ax = fig.axes[0]
    assert ax.get_title() == "Notes per month"
    assert ax.get_xlabel() == "Month" and ax.get_ylabel() == "Notes"
    assert [round(p.get_height()) for p in ax.patches] == [2, 2, 1]
