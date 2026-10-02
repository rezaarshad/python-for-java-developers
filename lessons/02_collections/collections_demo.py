"""Lesson 02: list, tuple, dict, set, with Java comparisons.

Run: uv run python lessons/02_collections/collections_demo.py
"""

from collections import Counter, defaultdict, deque

# --- list ≈ ArrayList -----------------------------------------------------
langs: list[str] = ["Java", "Python", "Go"]
langs.append("Rust")             # add
langs.insert(0, "C")             # add(0, ...)
langs.extend(["Kotlin", "Zig"])  # addAll
print(langs)
print(langs.pop())               # removes and returns the last item → Zig
langs.remove("C")                # remove by value (ValueError if missing)
print(len(langs), "Python" in langs)   # size(), contains()
print(langs.index("Go"))         # indexOf (ValueError if missing, not -1!)

print(langs[0], langs[-1], langs[1:3])  # Java Python... slicing: start inclusive, end exclusive

nums = [5, 2, 9, 1]
print(sorted(nums))              # NEW sorted list; nums unchanged
nums.sort(reverse=True)          # in place, returns None (a classic bug: x = nums.sort())
print(nums)
print(sorted(langs, key=len))    # key function replaces Comparator.comparing(String::length)
print(sorted(langs, key=str.lower))

print([0] * 5)                   # [0, 0, 0, 0, 0]
print([1, 2] + [3, 4])           # concatenation → new list

# --- tuple ≈ immutable list / lightweight record ---------------------------
point: tuple[int, int] = (3, 4)
x, y = point                     # unpacking
print(f"x={x}, y={y}")
single = (42,)                   # one-element tuple needs a trailing comma
# point[0] = 10                  # TypeError: tuples are immutable


def min_max(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)   # "returning two values" = returning a tuple


lo, hi = min_max([4, 8, 1, 7])
print(lo, hi)

first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)       # 1 [2, 3, 4] 5

# --- dict ≈ LinkedHashMap (keeps insertion order) ---------------------------
ages: dict[str, int] = {"Reza": 30, "Ana": 25}
ages["Bob"] = 40                 # put
print(ages["Reza"])              # get (KeyError if missing!)
print(ages.get("Zoe"))           # None if missing ≈ map.get()
print(ages.get("Zoe", 0))        # getOrDefault
print("Ana" in ages)             # containsKey
del ages["Bob"]                  # remove

for name, age in ages.items():   # entrySet()
    print(f"{name} is {age}")

print(list(ages.keys()), list(ages.values()))
ages.setdefault("Kim", 22)       # putIfAbsent
merged = ages | {"Lee": 50}      # merge into a new dict (Python 3.9+)
print(merged)

# --- set ≈ HashSet -----------------------------------------------------------
backend = {"Java", "Python", "Go"}
ai = {"Python", "Julia", "R"}
print(backend & ai)              # intersection → {'Python'}
print(backend | ai)              # union
print(backend - ai)              # difference
print(backend ^ ai)              # symmetric difference
print(set([1, 1, 2, 3, 3]))      # dedupe → {1, 2, 3}
empty = set()                    # NOT {} (that's an empty dict)

# --- collections module --------------------------------------------------------
words = "the cat and the hat and the bat".split()
counts = Counter(words)
print(counts.most_common(2))     # [('the', 3), ('and', 2)]

by_length: defaultdict[int, list[str]] = defaultdict(list)
for w in words:
    by_length[len(w)].append(w)  # no "if key not in map: put new list" dance
print(dict(by_length))

q = deque([1, 2, 3])
q.appendleft(0)
q.append(4)
print(q.popleft(), q.pop(), q)   # 0 4 deque([1, 2, 3])

# --- references & copying ---------------------------------------------------------
a = [1, 2, 3]
b = a                            # alias: same object, like Java references
b.append(4)
print(a)                         # [1, 2, 3, 4]
c = a.copy()                     # shallow copy
c.append(5)
print(a, c)

# --- zip / enumerate / any / all ------------------------------------------------
names = ["Reza", "Ana", "Bob"]
scores = [90, 85, 70]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
print(dict(zip(names, scores)))  # build a dict from two lists
print(any(s > 88 for s in scores), all(s > 60 for s in scores))
