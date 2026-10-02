# Lesson 01: Setup & Hello World

## 1. Install the toolchain

Java has `sdkman` + Maven/Gradle. The modern Python equivalent is **`uv`**: one fast tool
that installs Python versions, creates virtual environments, and manages dependencies.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # official installer (or: brew install uv on Apple Silicon)
uv python install 3.13        # installs Python 3.13 (doesn't touch macOS's /usr/bin/python3)
uv init --name python-for-java-developers --python 3.13 .   # creates pyproject.toml (≈ pom.xml); already done in this repo
uv run python --version       # runs inside the project's virtual env (.venv/)
```

In VS Code, install the **Python** extension (Microsoft). Then run `Python: Select Interpreter`
and pick `.venv/bin/python`.

> **Virtual env ≈ a per-project classpath.** Every project gets its own isolated `.venv/` folder
> with its own packages. Never `pip install` into the system Python.

## 2. Hello World

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

```python
print("Hello, World!")
```

There is no class, no `main`, no semicolons, and no compile step. A `.py` file is a script that runs top to bottom.

## 3. The 10 biggest mindset shifts from Java

| Java                                   | Python                                                    |
|----------------------------------------|-----------------------------------------------------------|
| `{ }` blocks                           | **indentation** is syntax (4 spaces)                      |
| static types, checked at compile time  | dynamic types; optional **type hints** checked by tools   |
| `String name = "Reza";`                | `name = "Reza"` (or `name: str = "Reza"`)                  |
| `"Hi " + name + "!"`                    | `f"Hi {name}!"` (f-strings)                               |
| `true / false / null`                  | `True / False / None`                                     |
| `&& \|\| !`                             | `and or not`                                              |
| `==` is identity for objects           | `==` is equality (calls `__eq__`); `is` is identity       |
| `for (int i=0; i<n; i++)`              | `for i in range(n):`                                      |
| `int` overflows at 2^31                | `int` is arbitrary precision: `2**1000` works            |
| `public static void main`              | `if __name__ == "__main__":`                              |

## 4. The REPL (like `jshell`, but you'll actually use it)

```bash
uv run python
>>> 2 ** 100
>>> type(3.14)
>>> help(str.split)
>>> dir("hello")      # list every method on a string
```

Use the REPL constantly for quick experiments.

## 5. Run the examples

```bash
uv run python lessons/01_hello/hello.py
uv run python lessons/01_hello/basics.py
```

Read `basics.py` top to bottom. Every block has a Java comparison in its comments.

## 6. Exercise

Open `exercise.py`, fill in the TODOs, and run it. Tell me when you're done and I'll review it.
