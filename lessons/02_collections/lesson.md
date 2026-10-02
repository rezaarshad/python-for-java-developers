# Lesson 02: Collections & Comprehensions

In Java you have `ArrayList`, `HashMap`, `HashSet`, records, plus the Streams API to process them.
Python builds the equivalents into the language with literal syntax. The real superpower is
**comprehensions**, which replace most `stream().filter().map().collect()` chains.

## 1. The four built-in collections

| Python  | Literal             | Java equivalent                | Mutable? | Ordered?           |
|---------|---------------------|--------------------------------|----------|--------------------|
| `list`  | `[1, 2, 3]`         | `ArrayList<Object>`            | yes      | yes                |
| `tuple` | `(1, 2, 3)`         | immutable `List.of(...)` / a record | no  | yes                |
| `dict`  | `{"a": 1, "b": 2}`  | `LinkedHashMap<K, V>`          | yes      | insertion order    |
| `set`   | `{1, 2, 3}`         | `HashSet<E>`                   | yes      | no                 |

Gotcha: `{}` is an empty **dict**, not a set. An empty set is `set()`.

Collections can hold mixed types (`[1, "two", 3.0]`), but in real code keep them uniform and
say so with type hints: `list[str]`, `dict[str, int]`, `set[int]`, `tuple[str, int]`.

## 2. Indexing & slicing (lists, tuples, strings)

```python
nums = [10, 20, 30, 40, 50]
nums[0]      # 10
nums[-1]     # 50        last element, no nums.get(nums.size() - 1)
nums[1:3]    # [20, 30]  start inclusive, end exclusive (like subList)
nums[:2]     # [10, 20]
nums[::2]    # [10, 30, 50]  step
nums[::-1]   # reversed copy
```

## 3. Unpacking

```python
x, y = 1, 2               # multiple assignment
x, y = y, x               # swap, no temp variable
first, *rest = [1, 2, 3, 4]    # first=1, rest=[2, 3, 4]
name, age = ("Reza", 30)  # works on any iterable
for key, value in my_dict.items(): ...
```

Functions return several values by returning a tuple: `return min_val, max_val`.

## 4. Comprehensions ≈ Streams

```java
List<String> result = names.stream()
    .filter(n -> n.length() > 3)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

```python
result = [n.upper() for n in names if len(n) > 3]
```

Read it as: **[ expression  for item in iterable  if condition ]**

```python
squares   = [x * x for x in range(10)]                  # list
lengths   = {name: len(name) for name in names}          # dict
initials  = {name[0] for name in names}                  # set
total     = sum(x * x for x in range(10))                # generator: lazy, no list built
pairs     = [(x, y) for x in range(3) for y in range(3)] # nested loops (keep them short!)
```

If a comprehension needs more than one `for` and one `if`, write a normal loop instead.

## 5. Built-ins you'll use daily

| Python                          | Java-ish                                          |
|---------------------------------|---------------------------------------------------|
| `len(x)`                        | `.size()` / `.length()`                           |
| `sorted(xs, key=..., reverse=True)` | `stream().sorted(Comparator...)`: returns a new list |
| `xs.sort(key=...)`              | `Collections.sort`: in place, returns `None`!     |
| `min(xs, key=...)`, `max(...)`  | `Collections.min/max` with a comparator           |
| `sum(xs)`                       | `mapToInt(...).sum()`                             |
| `any(...)`, `all(...)`          | `anyMatch`, `allMatch`                            |
| `zip(a, b)`                     | no built-in equivalent; pairs elements up         |
| `enumerate(xs)`                 | index + value                                     |
| `reversed(xs)`                  | reversed iterator                                 |

`key=` takes a function: `sorted(users, key=lambda u: u["age"])`. That one argument replaces a whole `Comparator`.

## 6. The `collections` module

```python
from collections import Counter, defaultdict, deque

Counter("mississippi").most_common(2)   # [('i', 4), ('s', 4)]   word counts in one line
groups = defaultdict(list)              # ≈ map.computeIfAbsent(k, k -> new ArrayList<>())
groups["java"].append("Reza")
queue = deque([1, 2, 3])                # ArrayDeque: fast appends/pops at both ends
```

## 7. References & mutability (same as Java, but easier to trip on)

Variables are references, exactly like Java objects. There are no primitives.

```python
a = [1, 2, 3]
b = a           # same list!
b.append(4)     # a is now [1, 2, 3, 4]
c = a.copy()    # shallow copy (also: list(a), a[:])
```

Only immutable types (`int`, `str`, `tuple`, `frozenset`) can be dict keys or set members,
the equivalent of "must have a stable `hashCode()`".

## 8. Run the examples

```bash
uv run python lessons/02_collections/collections_demo.py
uv run python lessons/02_collections/comprehensions.py
```

## 9. Exercise: notes app v0.1

Open `exercise.py`. You'll build the first version of **the notes app**: an in-memory note store
using only lists, dicts, and sets. The `main()` function has `assert` checks, so when every one
passes it prints `All checks passed ✅`.
