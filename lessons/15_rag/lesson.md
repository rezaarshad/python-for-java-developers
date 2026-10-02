# Lesson 15: Embeddings & RAG ("ask your notes")

LLMs only know their training data. **RAG (Retrieval-Augmented Generation)** lets Claude answer questions
about *your* data: find the relevant pieces, put them in the prompt, and ask Claude to answer **only** from them.

```
                 ┌─────────── indexing (once) ───────────┐
notes ─▶ chunk ─▶ embed ─▶ vectors ─▶ index (matrix / vector DB)
                                            │
question ─▶ embed ─▶ query vector ─▶ top-k similarity search
                                            │
                    prompt = instructions + retrieved chunks + question ─▶ Claude ─▶ grounded answer + citations
```

## 1. Embeddings

An **embedding** maps text to a vector of numbers so that texts with similar meaning point in similar
directions. Closeness is measured with **cosine similarity** (Lesson 13): `a·b / (|a||b|)`. If the vectors are
normalized to length 1 first, it's just a dot product, so searching N notes is a single matrix-vector multiply:
`scores = matrix @ query`.

| Approach                        | Quality | Notes                                              |
|---------------------------------|---------|----------------------------------------------------|
| TF-IDF / bag of words (this lesson) | ok for keywords | no dependencies; matches *words*, not meaning |
| Voyage AI API (`voyageai`)      | great   | Anthropic's recommended embedding provider         |
| `sentence-transformers` (local) | good    | runs on your machine; pulls in PyTorch (large)     |

You'll build TF-IDF yourself so that **nothing is magic**. Because the code depends on an `Embedder`
*protocol*, switching to a real embedding model is a one-class change.

### TF-IDF in one paragraph

Each vocabulary word gets a dimension. A text's value for that word = **term frequency** (how often the word
appears in the text) × **inverse document frequency** (`log((1 + N) / (1 + df)) + 1`, where df = the number of documents
containing the word). Rare words get high weight, while common words like "use" get low weight. Then normalize each row to length 1.

## 2. Chunking

Embed **chunks**, not whole documents. A chunk should cover one topic and fit comfortably in a prompt. A
common simple strategy is fixed-size word windows with **overlap**, so that sentences on a boundary aren't lost:

```
words:   w0 w1 w2 w3 w4 w5 w6 w7 w8 w9
size=4, overlap=1:  [w0..w3] [w3..w6] [w6..w9]
```

Better strategies split on headings and paragraphs first. Keep metadata (note id, title) with each chunk for citations.

## 3. Vector stores

For thousands of chunks, a NumPy matrix is fast enough. Beyond that, use a vector database: **pgvector**
(Postgres extension: great if you already run Postgres), **Qdrant**, **Chroma**, **FAISS** (a library), or a
managed service. They all do the same thing as `matrix @ query` + `argsort`, at scale, with filters.

## 4. The prompt

```text
Answer the question using ONLY the notes below. Cite sources like [rag.md].
If the notes don't contain the answer, say you don't know.

<notes>
<note source="rag.md">RAG answers questions using your own documents...</note>
<note source="embeddings.md">An embedding turns text into...</note>
</notes>

Question: How does RAG find relevant notes?
```

- Delimit retrieved content clearly (XML-style tags work well with Claude).
- Tell the model what to do when the answer isn't there. This is the main defence against hallucination.
- **Don't call the LLM at all** if nothing relevant was retrieved (score below a threshold). That's cheaper and more honest.
- Retrieved text is *data*: a note could contain "ignore previous instructions". Keeping it inside tags, and
  telling the model the notes are reference material, reduces prompt-injection risk.

## 5. Evaluating RAG

Measure the two halves separately:
- **Retrieval:** for a set of questions with known relevant notes, is the right note in the top-k? ("recall@k")
- **Generation:** is the answer correct, grounded in the context, and properly cited? (manual review or an LLM judge)

## 6. Run the example

```bash
uv run python lessons/15_rag/rag_demo.py          # retrieval works offline; the final answer needs ANTHROPIC_API_KEY
```

## 7. Exercise: "ask your notes"

Implement `exercise/rag.py`: tokenizer, chunker, a TF-IDF embedder, a NumPy vector index, prompt building,
and the end-to-end `ask()` that calls Claude, using your Lesson 14 patterns.

```bash
uv run pytest lessons/15_rag/exercise -v
```
