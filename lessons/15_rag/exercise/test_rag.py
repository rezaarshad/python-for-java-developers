"""Provided tests. Run: uv run pytest lessons/15_rag/exercise -v"""

import math
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from rag import (
    LLM_OPTIONS,
    NO_ANSWER,
    Chunk,
    Hit,
    TfidfEmbedder,
    VectorIndex,
    ask,
    build_prompt,
    chunk_words,
    load_chunks,
    recall_at_k,
    tokenize,
)

NOTES_DIR = Path(__file__).parent.parent / "data" / "notes"


# --- Text processing ----------------------------------------------------------------------------
def test_tokenize():
    assert tokenize("The RAG pipeline uses Claude, and it's GREAT! v2") == ["rag", "pipeline", "claude", "great", "v2"]


@pytest.mark.parametrize(("size", "overlap", "expected"), [
    (4, 1, ["w0 w1 w2 w3", "w3 w4 w5 w6", "w6 w7 w8 w9"]),
    (5, 0, ["w0 w1 w2 w3 w4", "w5 w6 w7 w8 w9"]),
    (20, 5, ["w0 w1 w2 w3 w4 w5 w6 w7 w8 w9"]),
    (4, 2, ["w0 w1 w2 w3", "w2 w3 w4 w5", "w4 w5 w6 w7", "w6 w7 w8 w9"]),
])
def test_chunk_words(size, overlap, expected):
    text = " ".join(f"w{i}" for i in range(10))
    assert chunk_words(text, size, overlap) == expected


def test_chunk_words_edge_cases():
    assert chunk_words("", 4, 1) == []
    assert chunk_words("a b c", 4, 1) == ["a b c"]
    with pytest.raises(ValueError):
        chunk_words("a b", 3, 3)


def test_load_chunks():
    chunks = load_chunks(NOTES_DIR, size=40, overlap=10)
    sources = [c.source for c in chunks]
    assert sources == sorted(sources), "files sorted by name"
    assert {"rag.md", "groceries.md"} <= set(sources)
    rag = [c for c in chunks if c.source == "rag.md"]
    assert [c.index for c in rag] == list(range(len(rag)))
    assert all(isinstance(c, Chunk) for c in chunks)


# --- TF-IDF ------------------------------------------------------------------------------------------
CORPUS = ["python generators yield values", "python async coroutines", "coffee and bananas"]


def test_fit_vocabulary_and_idf():
    e = TfidfEmbedder().fit(CORPUS)
    assert list(e.vocabulary) == sorted(e.vocabulary)
    assert e.vocabulary["async"] == 0
    python_idf = e.idf[e.vocabulary["python"]]
    coffee_idf = e.idf[e.vocabulary["coffee"]]
    assert python_idf == pytest.approx(math.log(4 / 3) + 1)
    assert coffee_idf == pytest.approx(math.log(4 / 2) + 1)
    assert coffee_idf > python_idf, "rarer words weigh more"


def test_embed_shape_and_normalization():
    e = TfidfEmbedder().fit(CORPUS)
    m = e.embed(["python yield", "unknown words only"])
    assert m.shape == (2, len(e.vocabulary))
    assert np.linalg.norm(m[0]) == pytest.approx(1.0)
    assert np.allclose(m[1], 0), "texts with no known words embed to zeros"


def test_embed_similar_texts_are_closer():
    e = TfidfEmbedder().fit(CORPUS)
    q, gen, coffee = e.embed(["python generators", CORPUS[0], CORPUS[2]])
    assert q @ gen > q @ coffee


# --- Index ------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def index():
    chunks = load_chunks(NOTES_DIR)
    idx = VectorIndex(TfidfEmbedder().fit([c.text for c in chunks]))
    idx.add(chunks)
    return idx


def test_index_len(index):
    assert len(index) == len(load_chunks(NOTES_DIR))


@pytest.mark.parametrize(("question", "expected_source"), [
    ("How do fixtures replace BeforeEach?", "pytest-fixtures.md"),
    ("What should I buy, oat milk or coffee?", "groceries.md"),
    ("How does dependency injection work with Depends?", "fastapi-dependencies.md"),
    ("What is cosine similarity between embeddings?", "embeddings.md"),
])
def test_search_finds_the_right_note(index, question, expected_source):
    hits = index.search(question, k=3)
    assert hits[0].chunk.source == expected_source
    assert all(isinstance(h.score, float) for h in hits)
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_search_min_score_and_unknown_words(index):
    assert index.search("zzz qqq xyzzy", k=3) == []
    assert all(h.score > 0.3 for h in index.search("generators yield", k=5, min_score=0.3))


def test_search_empty_index():
    assert VectorIndex(TfidfEmbedder().fit(CORPUS)).search("python") == []


def test_add_appends():
    e = TfidfEmbedder().fit(CORPUS)
    idx = VectorIndex(e)
    idx.add([Chunk("a.md", 0, CORPUS[0])])
    idx.add([Chunk("b.md", 0, CORPUS[2])])
    assert len(idx) == 2 and idx.search("coffee")[0].chunk.source == "b.md"


# --- Prompt + answer --------------------------------------------------------------------------------
HITS = [Hit(Chunk("rag.md", 0, "RAG retrieves chunks."), 0.9), Hit(Chunk("embeddings.md", 1, "Vectors."), 0.5)]


def test_build_prompt():
    assert build_prompt("What is RAG?", HITS) == (
        "Answer the question using ONLY the notes below. Cite sources like [rag.md].\n"
        "If the notes don't contain the answer, say you don't know.\n"
        "\n"
        "<notes>\n"
        '<note source="rag.md">RAG retrieves chunks.</note>\n'
        '<note source="embeddings.md">Vectors.</note>\n'
        "</notes>\n"
        "\n"
        "Question: What is RAG?"
    )


class FakeClient:
    def __init__(self, reply="It retrieves notes [rag.md].", stop_reason="end_turn"):
        self.calls = []
        self.reply, self.stop_reason = reply, stop_reason
        self.beta = NS(messages=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(content=[NS(type="text", text=self.reply)], stop_reason=self.stop_reason, stop_details=None)


def test_ask_calls_claude_with_retrieved_context(index):
    client = FakeClient()
    answer = ask(client, index, "How does retrieval augmented generation use my documents?")
    assert answer.text == "It retrieves notes [rag.md]."
    assert answer.sources[0] == "rag.md"
    assert len(answer.sources) == len(set(answer.sources)), "sources must be distinct"
    [call] = client.calls
    for key, value in LLM_OPTIONS.items():
        assert call[key] == value
    prompt = call["messages"][0]["content"]
    assert '<note source="rag.md">' in prompt and prompt.endswith("documents?")


def test_ask_skips_llm_when_nothing_relevant(index):
    client = FakeClient()
    assert ask(client, index, "xyzzy plugh") == ask(client, index, "qqq")
    assert ask(client, index, "xyzzy plugh").text == NO_ANSWER
    assert client.calls == [], "don't pay for an LLM call with no context"


def test_ask_refusal(index):
    with pytest.raises(RuntimeError):
        ask(FakeClient(stop_reason="refusal"), index, "pytest fixtures")


def test_recall_at_k(index):
    labeled = {
        "fixtures and monkeypatch in tests": "pytest-fixtures.md",
        "hiking boots for the cabin": "trip-planning.md",
        "semaphore for rate limits": "asyncio-basics.md",
        "this question matches nothing at all": "rag.md",
    }
    assert recall_at_k(index, labeled, k=3) == 0.75
