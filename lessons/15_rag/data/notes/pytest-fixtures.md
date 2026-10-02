# pytest fixtures

Fixtures replace JUnit's @BeforeEach. A test requests a fixture by naming it as a parameter.
Use `tmp_path` for temporary files and `monkeypatch` for environment variables. Shared fixtures live in conftest.py.
Parametrize replaces @ParameterizedTest.
