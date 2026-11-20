from src.normalise import detect_script
from src.text import tokenize


def test_detect_script():
    assert detect_script("भारत") == "deva"
    assert detect_script("bharat") == "latin"
    assert detect_script("1947") == "other"


def test_tokenize_keeps_matras_together():
    assert tokenize("भारत की राजधानी।") == ["भारत", "की", "राजधानी"]


def test_tokenize_mixed():
    assert tokenize("Roth IRA पे tax कितना?") == ["roth", "ira", "पे", "tax", "कितना"]
