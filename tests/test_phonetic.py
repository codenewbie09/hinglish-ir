from src.phonetic import phonetic_key


def test_nasal_variants_match():
    assert phonetic_key("हिन्दी") == phonetic_key("हिंदी")
    assert phonetic_key("में") == phonetic_key("मे")


def test_vowel_length_merged():
    assert phonetic_key("किताब") == phonetic_key("कीताब")
    assert phonetic_key("पुस्तक") == phonetic_key("पूस्तक")


def test_aspiration_merged():
    assert phonetic_key("भारत") == phonetic_key("बारत")
    assert phonetic_key("धर्म") == phonetic_key("दर्म")


def test_different_words_differ():
    assert phonetic_key("कमल") != phonetic_key("कलम")
    assert phonetic_key("राजा") != phonetic_key("रानी")


def test_latin_tokens_get_a_key():
    assert phonetic_key("google") == phonetic_key("gooogle")
