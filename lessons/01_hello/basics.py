"""Lesson 01: Python basics for Java developers.

A triple-quoted string at the top of a file is a *docstring*, Python's Javadoc.
Run: uv run python lessons/01_hello/basics.py
"""

# --- Variables & dynamic typing -------------------------------------------
# No type declaration needed. The *value* has a type; the *name* doesn't.
x = 42
print(type(x))          # <class 'int'>
x = "now I'm a string"  # legal! (a type checker like mypy would warn if you annotated x: int)
print(type(x))          # <class 'str'>

# Type hints: documentation + tooling, NOT enforced at runtime.
name: str = "Reza"
years_of_java: int = 10
pi: float = 3.14159
is_learning: bool = True
nothing: None = None    # Java's null

# --- Strings ---------------------------------------------------------------
# Single or double quotes are equivalent.
greeting = f"Hi {name}, {years_of_java} years of Java!"   # f-string ≈ String.format, but readable
print(greeting)
print(f"{pi:.2f}")            # format spec: 3.14
print(f"{years_of_java=}")    # debug shortcut: prints years_of_java=10

multiline = """Text blocks
exist too, like Java 15's \"\"\" blocks."""
print(multiline)

print(name.upper(), name.lower(), len(name))   # len() is a built-in function, not .length()
print("py" in "python")                        # True, like .contains()
print("a,b,c".split(","))                      # ['a', 'b', 'c']
print("-".join(["a", "b", "c"]))               # 'a-b-c'  (String.join reversed)
print(name[0], name[-1], name[1:3])            # indexing, negative index, slicing → R a ez

# --- Numbers ---------------------------------------------------------------
print(7 / 2)     # 3.5  ← true division, even with ints (Java gives 3)
print(7 // 2)    # 3    ← floor division (Java's int division)
print(7 % 2)     # 1
print(2 ** 10)   # 1024 ← power operator
print(2 ** 100)  # no overflow: ints are arbitrary precision (like BigInteger, built in)
print(1_000_000) # underscores allowed in literals, like Java

# --- Booleans & truthiness -------------------------------------------------
# Empty things are "falsy": 0, 0.0, "", [], {}, None. Everything else is truthy.
items = []
if not items:              # idiomatic; instead of `if (items.isEmpty())`
    print("list is empty")

age = 30
if 18 <= age < 65:         # chained comparisons
    print("working age")
elif age >= 65:            # `elif`, not `else if`
    print("retired")
else:
    print("minor")

# Ternary: Java's `cond ? a : b`
status = "adult" if age >= 18 else "minor"
print(status)

# --- == vs is --------------------------------------------------------------
a = [1, 2]
b = [1, 2]
print(a == b)   # True:  value equality (Java's .equals())
print(a is b)   # False: identity (Java's ==)
print(nothing is None)   # always compare to None with `is`

# --- Loops -----------------------------------------------------------------
for i in range(3):              # 0, 1, 2
    print("i =", i)

for lang in ["Java", "Python", "Go"]:   # like for-each
    print(lang)

for index, lang in enumerate(["Java", "Python"]):   # index + value, no counter variable
    print(index, lang)

count = 0
while count < 3:
    count += 1                  # no ++ operator in Python!
print("count:", count)


# --- Functions (full lesson later) ----------------------------------------
def greet(person: str, punctuation: str = "!") -> str:   # default args replace overloading
    return f"Hello, {person}{punctuation}"


print(greet("Reza"))
print(greet("Reza", punctuation="?"))   # keyword arguments


# --- The "main" idiom ------------------------------------------------------
# __name__ is "__main__" when the file is run directly, and the module name when imported.
# This keeps code from running on import, similar to having a dedicated main().
def main() -> None:
    print("Running as a script")


if __name__ == "__main__":
    main()
