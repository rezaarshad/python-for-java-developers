"""Write the tests! Run: uv run pytest lessons/08_testing/exercise -v

One test is written for you as an example. Replace each pytest.fail("TODO") with a real test.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from note_service import (
    DuplicateNoteError,
    InMemoryNoteRepository,
    NoteNotFoundError,
    NoteService,
    parse_tags,
    slugify,
)


class FakeClock:
    """Returns 2026-01-01 00:00, 00:01, 00:02, ... on successive calls."""

    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1)

    def __call__(self) -> datetime:
        current = self.now
        self.now += timedelta(minutes=1)
        return current


@pytest.fixture
def service() -> NoteService:
    return NoteService(InMemoryNoteRepository(), clock=FakeClock())


# --- Example (done for you) ----------------------------------------------------------
def test_create_returns_note_with_slug(service):
    note = service.create("Python Testing", body="pytest rocks", tags="python, testing")
    assert note.slug == "python-testing"
    assert note.tags == ["python", "testing"]
    assert note.created_at == datetime(2026, 1, 1)


# --- slugify ------------------------------------------------------------------------
# TODO: use @pytest.mark.parametrize with at least 5 cases, including:
#   "Hello, World!", "  lots   of   spaces  ", "C++ & Java", "already-a-slug", "Ünïcode 2026!"
#   Read the docstring of slugify carefully. One of these cases exposes the bug.
def test_slugify():
    pytest.fail("TODO")


def test_slugify_rejects_titles_with_no_letters_or_digits():
    pytest.fail("TODO: pytest.raises(ValueError) for something like '!!!'")


# --- parse_tags -----------------------------------------------------------------------
def test_parse_tags_normalizes_dedupes_and_keeps_order():
    pytest.fail("TODO")


def test_parse_tags_empty_string():
    pytest.fail("TODO")


# --- NoteService ------------------------------------------------------------------------
def test_create_duplicate_title_raises(service):
    pytest.fail("TODO: two titles that slugify to the same slug")


def test_get_missing_raises(service):
    pytest.fail("TODO")


def test_search_is_case_insensitive_and_oldest_first(service):
    pytest.fail("TODO: create 3 notes, search, check the order (the FakeClock gives increasing times)")


def test_summarize_calls_summarizer_and_caches(service):
    pytest.fail("TODO: use Mock(); call summarize twice; assert summarizer.summarize called ONCE with the body")


def test_summarize_missing_note_raises_without_calling_summarizer(service):
    pytest.fail("TODO")
