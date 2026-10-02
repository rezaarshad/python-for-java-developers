"""Lesson 15 exercise: "ask your notes", a RAG pipeline built from scratch.

Test: uv run pytest lessons/15_rag/exercise -v
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np

MODEL = "claude-opus-5-5"
LLM_OPTIONS = {"model": MODEL, "betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how", "in", "is", "it", "its",
    "like", "of", "on", "or", "so", "that", "the", "then", "this", "to", "use", "uses", "what", "when",
    "which", "with", "you", "your", "do", "does", "i", "my", "me",
}

NO_ANSWER = "I couldn't find anything relevant in your notes."


@dataclass(frozen=True)
class Chunk:
    source: str      # e.g. "rag.md"
    index: int       # position of this chunk within its source: 0, 1, 2, ...
    text: str


# --- 1. Text processing -------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    """Lowercase, extract words with re.findall(r"[a-z0-9]+", ...), drop STOPWORDS and 1-character tokens."""
    # TODO
    pass


def chunk_words(text: str, size: int = 40, overlap: int = 10) -> list[str]:
    """Split text into windows of `size` words (str.split), each starting `size - overlap` words after
    the previous one. Stop once a window reaches the end of the text. Join each window with spaces.
    Raise ValueError unless 0 <= overlap < size. Empty text → []."""
    # TODO
    pass


def load_chunks(folder: Path, size: int = 40, overlap: int = 10) -> list[Chunk]:
    """One Chunk per window, for every *.md file in `folder` sorted by file name. Chunk.source = file name."""
    # TODO
    pass


# --- 2. Embeddings ----------------------------------------------------------------------------------
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...   # shape (len(texts), dim), rows L2-normalized


class TfidfEmbedder:
    """Fit on a corpus, then embed any text into the corpus vocabulary space."""

    def __init__(self) -> None:
        self.vocabulary: dict[str, int] = {}      # word → column index
        self.idf: np.ndarray = np.array([])

    def fit(self, corpus: list[str]) -> "TfidfEmbedder":
        """- vocabulary: every token in the corpus, sorted alphabetically, mapped to 0, 1, 2, ...
        - document frequency df[word] = number of corpus texts containing the word (count once per text)
        - idf = log((1 + N) / (1 + df)) + 1 (natural log), as a float array ordered by column
        Return self (so you can write TfidfEmbedder().fit(corpus))."""
        # TODO
        pass

    def embed(self, texts: list[str]) -> np.ndarray:
        """For each text: term counts (Counter of tokens) for known words only, multiplied by idf,
        then L2-normalize each row (all-zero rows stay zero). Shape (len(texts), len(vocabulary))."""
        # TODO
        pass


# --- 3. Vector index ----------------------------------------------------------------------------------
@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class VectorIndex:
    def __init__(self, embedder: Embedder) -> None:
        self.embedder = embedder
        self.chunks: list[Chunk] = []
        self.matrix: np.ndarray | None = None

    def add(self, chunks: list[Chunk]) -> None:
        """Embed the chunk texts and store them. Calling add() again appends (np.vstack)."""
        # TODO
        pass

    def __len__(self) -> int:
        # TODO
        pass

    def search(self, query: str, k: int = 3, min_score: float = 0.0) -> list[Hit]:
        """Embed the query, score = matrix @ query_vector (rows are normalized → cosine similarity).
        Return up to k Hits with score > min_score, best first, scores rounded to 4 decimals (Python float).
        An empty index → []."""
        # TODO
        pass


# --- 4. Prompt + answer ------------------------------------------------------------------------------------
def build_prompt(question: str, hits: list[Hit]) -> str:
    """Exactly this format (one <note> line per hit, in order):

    Answer the question using ONLY the notes below. Cite sources like [rag.md].
    If the notes don't contain the answer, say you don't know.

    <notes>
    <note source="rag.md">chunk text</note>
    <note source="embeddings.md">chunk text</note>
    </notes>

    Question: <question>
    """
    # TODO
    pass


@dataclass
class Answer:
    text: str
    sources: list[str]          # distinct sources of the retrieved hits, in hit order


def ask(client, index: VectorIndex, question: str, k: int = 3, min_score: float = 0.05) -> Answer:
    """1. hits = index.search(question, k, min_score)
    2. No hits → Answer(NO_ANSWER, []) WITHOUT calling the client (cheaper and more honest)
    3. Otherwise client.beta.messages.create(**LLM_OPTIONS, max_tokens=2048, output_config={"effort": "low"},
       messages=[{"role": "user", "content": build_prompt(question, hits)}])
    4. If stop_reason == "refusal" → raise RuntimeError("refused"). Else join the text blocks.
    """
    # TODO
    pass


def recall_at_k(index: VectorIndex, labeled: dict[str, str], k: int = 3) -> float:
    """Retrieval eval: `labeled` maps question → the source that should be retrieved.
    Return the fraction of questions whose expected source appears in the top-k hits."""
    # TODO
    pass
