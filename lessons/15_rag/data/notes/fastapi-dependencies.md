# FastAPI dependency injection

FastAPI uses Depends() for dependency injection, similar to constructor injection in Spring.
A database session dependency yields a SQLAlchemy Session per request. In tests, override dependencies with
app.dependency_overrides to swap in an in-memory SQLite database.
