"""Measured code-mixing level of the query variants (src/mixcheck.py)."""
import pytest

from src.mixcheck import content_tokens, english_share, replaced_share, summarise

LEX = {"congress": {"english": False}, "party": {"english": True}, "leader": {"english": True},
       "dal": {"english": False}, "neta": {"english": False}}


def test_content_tokens_drop_roman_and_english_stopwords_and_numbers():
    assert content_tokens("congress dal ka neta kaun h ? the 1947") == ["congress", "dal", "neta"]


def test_english_share_counts_lexicon_english_over_content_tokens():
    assert english_share("congress party ka leader kaun h", LEX) == pytest.approx(2 / 3)
    assert english_share("congress dal ka neta kaun h", LEX) == 0.0


def test_english_share_ignores_tokens_missing_from_lexicon():
    assert english_share("party xyzzy", LEX) == 1.0
    assert english_share("ka h", LEX) is None  # no content token at all


def test_replaced_share_is_exact_token_diff_against_roman():
    roman = "congress dal ka neta kaun h"
    assert replaced_share(roman, "congress party ka leader kaun h") == pytest.approx(2 / 3)
    assert replaced_share(roman, roman) == 0.0
    assert replaced_share("ka h", "ka h") is None


def test_summarise_reports_mean_median_and_share_with_no_english():
    s = summarise([0.0, 0.5, 1.0, None])
    assert s == {"n": 3, "mean": 0.5, "median": 0.5, "q25": 0.25, "q75": 0.75, "zero": pytest.approx(1 / 3)}
