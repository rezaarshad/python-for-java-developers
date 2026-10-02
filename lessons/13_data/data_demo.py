"""Lesson 13 demo: numpy, pandas, matplotlib on the sample notes dataset.

Run: uv run python lessons/13_data/data_demo.py
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                      # render to files, no GUI window (set before importing pyplot)
import matplotlib.pyplot as plt            # noqa: E402
import numpy as np                         # noqa: E402
import pandas as pd                        # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# --- NumPy -----------------------------------------------------------------------
print("=== numpy ===")
values = list(range(1_000_000))
start = time.perf_counter()
py_total = sum(v * v for v in values)
py_time = time.perf_counter() - start
arr = np.arange(1_000_000, dtype=np.int64)
start = time.perf_counter()
np_total = int((arr * arr).sum())
np_time = time.perf_counter() - start
print(f"sum of squares: python {py_time * 1000:.1f} ms vs numpy {np_time * 1000:.1f} ms (same result: {py_total == np_total})")

m = np.arange(12).reshape(3, 4)
print(m, m.shape, sep="\n")
print("column means:", m.mean(axis=0), "| row sums:", m.sum(axis=1))
print("mask m > 6:", m[m > 6])
print("broadcast (centre columns):\n", m - m.mean(axis=0))

# Cosine similarity between toy "embeddings"
emb = {
    "cat":    np.array([0.9, 0.1, 0.0]),
    "kitten": np.array([0.85, 0.2, 0.05]),
    "car":    np.array([0.1, 0.0, 0.95]),
}


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


print({f"cat~{k}": round(cosine(emb["cat"], v), 3) for k, v in emb.items()})

rng = np.random.default_rng(seed=0)        # modern random API: seeded and reproducible
print("random normal sample:", rng.normal(size=3).round(3))

# --- pandas ----------------------------------------------------------------------------
print("\n=== pandas ===")
df = pd.read_csv(HERE / "data" / "notes.csv", parse_dates=["created_at"])
print(df.head())
print(df.dtypes)
print(df.describe())

df["tags"] = df["tags"].str.split(";")
df["month"] = df["created_at"].dt.to_period("M")
df["reading_min"] = (df["word_count"] / 200).round(1)

print("\nlongest notes:\n", df.nlargest(3, "word_count")[["title", "word_count", "reading_min"]])
print("\npinned:\n", df.loc[df["pinned"], ["id", "title"]])
print("\nper month:\n", df.groupby("month").agg(notes=("id", "count"), words=("word_count", "sum")))

tags = df.explode("tags")
print("\ntag counts:\n", tags["tags"].value_counts())
print("\navg words per tag:\n", tags.groupby("tags")["word_count"].mean().round(0).sort_values(ascending=False))
print("\nweekday × pinned:\n", df.pivot_table(index=df["created_at"].dt.day_name(), columns="pinned",
                                                values="id", aggfunc="count", fill_value=0))

# --- matplotlib -------------------------------------------------------------------------------
per_month = df.groupby("month").size()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(per_month.index.astype(str), per_month.values, color="#4C72B0")
ax.set(title="Notes per month", xlabel="Month", ylabel="Notes")
fig.tight_layout()
fig.savefig(OUT / "notes_per_month.png", dpi=120)
plt.close(fig)

fig, (left, right) = plt.subplots(1, 2, figsize=(10, 4))
tags["tags"].value_counts().plot(kind="barh", ax=left, title="Tags")       # pandas → matplotlib
left.invert_yaxis()
right.hist(df["word_count"], bins=15, color="#55A868")
right.set(title="Word count distribution", xlabel="words")
fig.tight_layout()
fig.savefig(OUT / "tags_and_words.png", dpi=120)
plt.close(fig)
print(f"\ncharts written to {OUT}")
