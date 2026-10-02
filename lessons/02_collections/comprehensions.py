"""Lesson 02: comprehensions, Python's answer to the Streams API.

Run: uv run python lessons/02_collections/comprehensions.py
"""

users = [
    {"name": "Reza", "lang": "Java", "years": 10},
    {"name": "Ana", "lang": "Python", "years": 3},
    {"name": "Bob", "lang": "Java", "years": 1},
    {"name": "Kim", "lang": "Go", "years": 5},
]

# filter + map → list
# Java: users.stream().filter(u -> u.years() > 2).map(User::name).toList()
seniors = [u["name"] for u in users if u["years"] > 2]
print(seniors)

# map → dict   (Collectors.toMap)
years_by_name = {u["name"]: u["years"] for u in users}
print(years_by_name)

# → set   (Collectors.toSet)
languages = {u["lang"] for u in users}
print(languages)

# Generator expression: lazy, like a Stream that hasn't been collected.
# Pass it straight into sum/min/max/any/all; no intermediate list is built.
total_years = sum(u["years"] for u in users)
print(total_years)

# Conditional expression inside the comprehension (map with if/else)
labels = ["senior" if u["years"] >= 5 else "junior" for u in users]
print(labels)

# Sorting with key (Comparator.comparing(...).reversed())
by_experience = sorted(users, key=lambda u: u["years"], reverse=True)
print([u["name"] for u in by_experience])

# Sort by multiple keys: return a tuple (thenComparing)
by_lang_then_name = sorted(users, key=lambda u: (u["lang"], u["name"]))
print([(u["lang"], u["name"]) for u in by_lang_then_name])

# max with key
most_experienced = max(users, key=lambda u: u["years"])
print(most_experienced["name"])

# groupingBy, done with a dict comprehension over a set of keys
names_by_lang = {
    lang: [u["name"] for u in users if u["lang"] == lang]
    for lang in sorted(languages)
}
print(names_by_lang)
# (This is O(n * groups). For big data, use defaultdict(list) with a loop, see collections_demo.py.)

# Flatten a list of lists (flatMap)
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [x for row in matrix for x in row]   # read the fors left to right, like nested loops
print(flat)

# Invert a dict
name_by_years = {v: k for k, v in years_by_name.items()}
print(name_by_years)
