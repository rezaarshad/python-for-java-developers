# Lesson 13: Data Essentials: NumPy, pandas, matplotlib

This is the "scientific Python" stack that the whole AI/ML ecosystem sits on: PyTorch tensors mimic NumPy,
datasets arrive as DataFrames, and every notebook ends with a chart.

| Library      | What it is                                    | Java-ish analogue                       |
|--------------|-----------------------------------------------|-----------------------------------------|
| `numpy`      | fast n-dimensional arrays, vectorized math     | primitive arrays + a BLAS library (ND4J) |
| `pandas`     | tables (DataFrame) with labelled columns      | an in-memory SQL table + Streams; Tablesaw |
| `matplotlib` | plotting                                      | JFreeChart                              |

Convention: `import numpy as np`, `import pandas as pd`, `import matplotlib.pyplot as plt`.

> 💡 This is a great lesson to work through in a **notebook** (see the Jupyter side lesson): open `explore.ipynb`.

## 1. NumPy: vectorization

Python loops are slow (~50× slower than Java). NumPy runs the loop in C:

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
a * 2              # array([2., 4., 6.])   no loop: "vectorized"
a + np.array([10, 20, 30])
a.sum(), a.mean(), a.max(), a.argmax()
np.sqrt(a), np.exp(a)

m = np.arange(6).reshape(2, 3)   # 2×3 matrix
m.shape, m.dtype                  # (2, 3), int64
m[0], m[:, 1], m[m > 2]           # row, column, boolean mask (filter)
m.T, m @ m.T                      # transpose, matrix multiply
m.sum(axis=0), m.sum(axis=1)      # column sums, row sums
```

**Broadcasting:** shapes are stretched to match automatically. `matrix - matrix.mean(axis=0)` centres every column.

The one formula you need for AI: **cosine similarity** (how "close" two embedding vectors are):

```python
def cosine(a, b):
    return a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
```

## 2. pandas: DataFrames

```python
import pandas as pd

df = pd.read_csv("notes.csv", parse_dates=["created_at"])   # also read_json, read_parquet, read_sql, read_excel
df.head(), df.info(), df.describe(), df.shape, df.columns, df.dtypes

df["word_count"]                          # a column = Series
df[["title", "word_count"]]               # several columns = DataFrame
df[df["word_count"] > 300]                # filter rows (boolean mask)    ≈ WHERE
df.query("word_count > 300 and pinned")   # same, as a string expression
df.loc[df["pinned"], "title"]             # rows by mask/label, then a column
df.iloc[0]                                # row by position
df.sort_values("word_count", ascending=False).head(5)   # ≈ ORDER BY ... LIMIT
df.nlargest(5, "word_count")

df["minutes"] = df["word_count"] / 200    # new column (vectorized)
df["month"] = df["created_at"].dt.to_period("M")          # .dt = datetime accessor
df["title"].str.lower().str.contains("rag")               # .str = string accessor

df.groupby("month")["word_count"].agg(["count", "mean", "max"])   # ≈ GROUP BY
df["tags"].str.split(";").explode().value_counts()               # one row per tag, then count
df.merge(other, on="id", how="left")      # ≈ JOIN
df.pivot_table(index="month", columns="pinned", values="id", aggfunc="count")
df.to_csv("out.csv", index=False); df.to_dict("records")
```

Mental model: a DataFrame is a dict of equally long columns (Series) sharing one **index** (row labels).
**Avoid row-by-row loops** (`iterrows`): think in whole-column operations, like SQL.

## 3. matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 4))   # the object-oriented API: prefer this over plt.plot(...)
ax.bar(series.index.astype(str), series.values)
ax.set(title="Notes per month", xlabel="Month", ylabel="Notes")
fig.tight_layout()
fig.savefig("notes_per_month.png", dpi=150)
plt.close(fig)
```

`series.plot(kind="bar")` / `df.plot(...)` are pandas shortcuts that use matplotlib under the hood. In
notebooks, charts render inline automatically. Also worth knowing: `seaborn` (statistical charts) and `plotly` (interactive charts).

## 4. Run the examples

```bash
uv run python lessons/13_data/data_demo.py        # writes charts into lessons/13_data/output/
```

Or open `lessons/13_data/explore.ipynb` and run the cells.

## 5. Exercise: notes analytics

Implement `exercise/analytics.py`: vector helpers in NumPy (you'll reuse them for RAG in Lesson 15),
note statistics in pandas, and a chart.

```bash
uv run pytest lessons/13_data/exercise -v
```
