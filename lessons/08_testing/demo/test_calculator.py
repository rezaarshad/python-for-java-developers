"""Run: uv run pytest lessons/08_testing/demo -v"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from calculator import History, add, describe, divide


# --- plain asserts -----------------------------------------------------------
def test_add():
    assert add(2, 2) == 4


def test_float_math_needs_approx():
    assert add(0.1, 0.2) == pytest.approx(0.3)


# --- exceptions ---------------------------------------------------------------
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="not allowed"):
        divide(1, 0)


# --- parametrize --------------------------------------------------------------
@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(6, 3, 2), (1, 4, 0.25), (-9, 3, -3)],
    ids=["whole", "fraction", "negative"],
)
def test_divide(a, b, expected):
    assert divide(a, b) == expected


# --- fixtures -------------------------------------------------------------------
FIXED = datetime(2026, 1, 1, 12, 0)


@pytest.fixture
def history():
    return History(clock=lambda: FIXED)       # fake clock instead of datetime.now


def test_history_records_with_timestamp(history):
    history.record("1 + 1")
    assert history.entries == [(FIXED, "1 + 1")]


def test_each_test_gets_a_fresh_fixture(history):
    assert history.entries == []


# --- built-in fixtures ---------------------------------------------------------------
def test_tmp_path(tmp_path):
    f = tmp_path / "out.txt"
    f.write_text("hi", encoding="utf-8")
    assert f.read_text(encoding="utf-8") == "hi"


def test_capsys(capsys):
    print("hello")
    assert capsys.readouterr().out == "hello\n"


def test_monkeypatch_env(monkeypatch):
    import os
    monkeypatch.setenv("MODE", "test")
    assert os.environ["MODE"] == "test"        # undone automatically after the test


# --- mocks & fakes --------------------------------------------------------------------
def test_describe_with_mock():
    formatter = Mock()
    formatter.format.return_value = "4.00"
    assert describe(4, formatter) == "Result: 4.00"
    formatter.format.assert_called_once_with(4)


def test_describe_with_fake():
    class TwoDecimals:                          # a fake: no library needed thanks to duck typing
        def format(self, value: float) -> str:
            return f"{value:.2f}"

    assert describe(4, TwoDecimals()) == "Result: 4.00"


def test_mock_side_effect():
    flaky = Mock(side_effect=[TimeoutError(), "ok"])   # first call raises, second returns
    with pytest.raises(TimeoutError):
        flaky()
    assert flaky() == "ok"
    assert flaky.call_count == 2
