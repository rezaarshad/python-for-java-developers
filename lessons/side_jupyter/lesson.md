# Side Lesson: Jupyter Notebooks

A side lesson isn't part of the main track. It's a tool you'll keep using,
and from Lesson 13 onward (data and AI) you'll use it a lot.

## 1. What a notebook is

A notebook (`.ipynb`) is a document made of **cells**:

- **Code cells** run Python and show the output right below: text, tables, charts.
- **Markdown cells** hold notes, headings, and formulas.

A background Python process called the **kernel** runs the code and **keeps state in memory
between cells**. Load a big dataset once, then re-run the analysis cell as often as you like.

> **Java analogy:** `jshell` with saved history, inline charts, and notes.
> Java has nothing in common use like it, which is a big part of why Python dominates data science and AI.

## 2. Setup (already done for this project)

```bash
uv add --dev ipykernel     # lets VS Code run notebooks with the project's .venv
```

- [`.vscode/settings.json`](../../.vscode/settings.json) points VS Code at `.venv/bin/python`.
- Open a `.ipynb` file → **Select Kernel** (top right) → **Python Environments** → **.venv**.

Other ways to run notebooks:

| Tool             | Command / link              | When to use it                       |
|------------------|-----------------------------|--------------------------------------|
| VS Code          | open the `.ipynb` file      | everyday use (what we'll use)        |
| JupyterLab       | `uvx jupyter lab`           | the classic browser interface        |
| Google Colab     | colab.research.google.com   | free GPUs for ML/AI experiments      |

## 3. Keyboard shortcuts worth learning

| Key            | Action                                   |
|----------------|------------------------------------------|
| `Shift+Enter`  | run cell, move to next                   |
| `Ctrl+Enter`   | run cell, stay                           |
| `Esc` then `A` / `B` | insert cell above / below          |
| `Esc` then `M` / `Y` | switch cell to Markdown / code     |
| `Esc` then `DD`      | delete cell                        |

## 4. Gotchas

1. **Out-of-order execution.** Cells can run in any order, so the notebook's state can stop
   matching what's on screen. When things get weird: **Restart Kernel → Run All**.
2. **Hidden state.** Deleting a cell doesn't delete its variables from memory.
3. **Git diffs are ugly.** Notebooks are JSON and include their outputs. Clear outputs before committing
   (`...` menu → **Clear All Outputs**).
4. **Not for production.** Explore in notebooks, then move working code into `.py` modules
   that you can test and import.

## 5. Importing your own code into a notebook

Notebooks can import regular `.py` files. That's the healthy workflow: logic in modules,
experimenting in the notebook.

```python
import sys
sys.path.append("../01_hello")      # make that folder importable (we'll do this properly in Lesson 05)

from exercise import fizzbuzz, count_vowels
[fizzbuzz(i) for i in range(1, 16)]
```

If you edit `exercise.py`, the notebook won't see the change until you restart the kernel, or run this
once at the top of the notebook:

```python
%load_ext autoreload
%autoreload 2
```

## 6. Exercise

Open [`playground.ipynb`](playground.ipynb):

1. Run every cell top to bottom.
2. Change `n` in the "state" cell to `5`, then re-run **only** the `squares` display cell. What do you see, and why?
3. In the last cell, import your Lesson 01 functions (section 5) and display `count_vowels("Jupyter Notebook")`.
