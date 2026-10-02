"""Lesson 01 exercise. Fill in the TODOs, then run:

    uv run python lessons/01_hello/exercise.py

Don't use anything we haven't covered yet. Simple is fine.
"""


def fizzbuzz(n: int) -> str:
    """Return "Fizz" if n is divisible by 3, "Buzz" if by 5, "FizzBuzz" if by both,
    otherwise the number as a string (hint: str(n))."""
    if n % 3 == 0 and n % 5 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:   
        return str(n)


def describe(name: str, language: str, years: int) -> str:
    """Return e.g. 'Reza has written Java for 10 years (that's 120 months).'
    Use an f-string. If years == 1, say 'year' instead of 'years' (use a ternary)."""
    years_word = "year" if years == 1 else "years"
    months = years * 12
    return f"{name} has written {language} for {years} {years_word} (that's {months} months)."

def count_vowels(text: str) -> int:
    """Count the vowels (a, e, i, o, u, upper or lower case) in text.
    Hint: loop over the string with `for ch in text:`, and use `in` and .lower()."""
    vowel_count = 0
    for ch in text:
        if ch.lower() in "aeiouAEIOU":
            vowel_count += 1
    return vowel_count


def main() -> None:
    for i in range(1, 16):
        print(fizzbuzz(i))
    print(describe("Reza", "Java", 10))
    print(describe("Reza", "Python", 1))
    print(count_vowels("Hello Python World"))  # expected: 4


if __name__ == "__main__":
    main()
