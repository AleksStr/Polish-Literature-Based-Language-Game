import pytest
from unittest.mock import patch
import sys

sys.path.append('.')
import spellcheck

def test_swap_adjecet_letters():
    for i in range(3):
        assert spellcheck.swap_adjacent_letters("kot") in ["okt", "kto"]

def test_change_u():
    for i in range(3):
        assert spellcheck.change_u("Ustrój") in ["Óstrój", "Ustruj"]

def test_change_rz():
    for i in range(3): 
        assert spellcheck.change_rz("Rzerzucha") in ["Żerzucha", "Rzeżucha"]
    assert spellcheck.change_rz("ŻEBY") == "RZEBY"
    assert spellcheck.change_rz("Żeby") == "Rzeby"

def test_generate_typo_distractor_short_word():
    result = spellcheck.generate_typo_distractor("ab")
    assert result == "ba"

def test_generate_typo_distractor_no_special_chars():
    result = spellcheck.generate_typo_distractor("pomatka")
    assert sorted(result) == sorted("pomatka")
    assert result != "pomatka"

def test_generate_typo_distractor_u_o_logic():
    valid_results = "órangutan" 
    result = spellcheck.generate_typo_distractor("orangutan")
    assert (result == "orangótan") or (sorted(result) == sorted("orangutan"))

def test_generate_typo_distractor_rz_z_logic():
    result = spellcheck.generate_typo_distractor("morze")
    assert (result == "może") or (sorted(result) == sorted("morze"))

def test_generate_typo_distractor_ch_h_logic():
    result = spellcheck.generate_typo_distractor("chata")
    assert (result == "hata") or (sorted(result) == sorted("chata"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])