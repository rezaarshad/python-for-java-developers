"""Lesson 15 demo: retrieval step by step, then (optionally) a grounded answer from Claude.

Run: uv run python lessons/15_rag/rag_demo.py
Retrieval runs offline. The final answer needs ANTHROPIC_API_KEY.
"""

import os
import re
from collections import Counter
from pathlib import Path

import numpy as np

NOTES = Path(__file__).parent / "data" / "notes"
STOP = {"a", "an", "and", "the", "is", "of", "to", "in", "it", "for", "with", "on", "as", "be", "are", "by",
        "how", "what", "do", "does", "my", "i", "use", "uses", "you", "your", "that", "this", "can", "then", "like"}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP and len(t) > 1]


# 1. Load documents (one chunk per note here; the exercise adds real chunking)
docs = {p.name: p.read_text(encoding="utf-8") for p in sorted(NOTES.glob("*.md"))}
names = list(docs)
print(f"loaded {len(docs)} notes: {names}\n")

# 2. Build a TF-IDF matrix (rows = notes, columns = vocabulary words)
tokenized = [tokenize(t) for t in docs.values()]
vocab = sorted({w for toks in tokenized for w in toks})
col = {w: i for i, w in enumerate(vocab)}
df = Counter(w for toks in tokenized for w in set(toks))
idf = np.array([np.log((1 + len(docs)) / (1 + df[w])) + 1 for w in vocab])


def embed(texts: list[str]) -> np.ndarray:
    m = np.zeros((len(texts), len(vocab)))
    for row, text in enumerate(texts):
        for word, count in Counter(tokenize(text)).items():
            if word in col:
                m[row, col[word]] = count
    m *= idf                                         # broadcasting: scale every column by its idf
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return np.divide(m, norms, out=np.zeros_like(m), where=norms > 0)


matrix = embed(list(docs.values()))
print(f"matrix shape {matrix.shape}  (notes × vocabulary words)")
top_words = sorted(zip(idf, vocab), reverse=True)[:5]
print("rarest (highest idf) words:", [w for _, w in top_words])

# 3. Search = one matrix-vector product
questions = [
    "How do I limit concurrent API calls?",
    "What do I need to pack for the mountains?",
    "How is similarity between texts measured?",
    "What's the capital of Peru?",
]
for q in questions:
    scores = matrix @ embed([q])[0]
    best = np.argsort(-scores)[:3]
    ranked = ", ".join(f"{names[i]} ({scores[i]:.2f})" for i in best if scores[i] > 0) or "nothing relevant"
    print(f"\nQ: {q}\n   → {ranked}")

# 4. Generate: put the best notes into the prompt
question = "How does RAG decide which notes to use, and how is closeness measured?"
scores = matrix @ embed([question])[0]
hits = [names[i] for i in np.argsort(-scores)[:2] if scores[i] > 0.05]
context = "\n".join(f'<note source="{n}">{docs[n]}</note>' for n in hits)
prompt = (f"Answer using ONLY the notes below. Cite sources like [rag.md]. "
          f"If they don't contain the answer, say so.\n\n<notes>\n{context}\n</notes>\n\nQuestion: {question}")
print(f"\n--- prompt sent to Claude ---\n{prompt}\n")

if os.environ.get("ANTHROPIC_API_KEY"):
    import anthropic

    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        max_tokens=2048,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        print("(refused)")
    else:
        print("--- Claude ---\n" + "".join(b.text for b in response.content if b.type == "text"))
else:
    print("(set ANTHROPIC_API_KEY to get Claude's grounded answer)")
