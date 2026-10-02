# Python generators

A generator is a function that uses `yield`. It produces values lazily, one at a time, which keeps memory low
when reading huge files. Generators can only be consumed once, like a Java Stream.
Use `yield from` to delegate to another iterable.
