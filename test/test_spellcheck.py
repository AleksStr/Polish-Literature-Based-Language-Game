import pytest
from unittest.mock import patch, MagicMock, mock_open
import random
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

def test_generate_typo_dystractor_word_less_than_5_always_swap():
    for i in range(3):
        assert spellcheck.generate_typo_distractor("kot") in ["okt", "kto"]

def test_generate_typo_distractor_short_word():
    """Test with short word - should always swap adjacent letters."""
    with patch('random.random') as mock_random:
        mock_random.return_value = 0.9
        result = spellcheck.generate_typo_distractor("ab")
        assert result == "ba"

def test_generate_typo_distractor_no_special_chars():
    """Test word without u/o or rz/z - should swap adjacent letters."""
    with patch('random.random') as mock_random:
        mock_random.return_value = 0.9 
        result = spellcheck.generate_typo_distractor("pomatka")
        assert sorted(result) == sorted("pomatka")

def test_generate_typo_distractor_only_u_o_roll_low():
    """Test word with only u/o and roll < 0.5 - should swap letters."""
    with patch('random.random', return_value=0.3):
        result = spellcheck.generate_typo_distractor("orangutan")
        assert sorted(result) == sorted("orangutan")



def test_generate_typo_distractor_only_u_o_roll_high():
    """Test word with only u/o and roll >= 0.5 - should change u."""
    with patch('random.random', return_value=0.7):
        result = spellcheck.generate_typo_distractor("orangutan")
        assert result=="orangótan"


def test_generate_typo_distractor_only_rz_z_roll_low():
    """Test word with only rz/z and roll < 0.5 - should swap letters."""
    with patch('random.random', return_value=0.3):
        result = spellcheck.generate_typo_distractor("morze")
        assert sorted(result) == sorted("morze")

def test_generate_typo_distractor_only_rz_z_roll_high():
    """Test word with only rz/z and roll >= 0.5 - should change rz."""
    with patch('random.random', return_value=0.7):
        result = spellcheck.generate_typo_distractor("morze")
        assert result=="może"


def test_generate_typo_distractor_both_special_roll_low():
    """Test word with both u/o and rz/z, roll < 0.2 - swap letters."""
    with patch('random.random', return_value=0.1):
        result = spellcheck.generate_typo_distractor("burza")
        assert sorted(result) == sorted("burza")

def test_generate_typo_distractor_both_special_roll_mid():
    """Test word with both, 0.2 <= roll < 0.6 - change u."""
    with patch('random.random', return_value=0.4):
        result = spellcheck.generate_typo_distractor("burza")
        assert result == "bórza"


def test_generate_typo_distractor_both_special_roll_high():
    """Test word with both, roll >= 0.6 - change rz."""
    with patch('random.random', return_value=0.8):
        result = spellcheck.generate_typo_distractor("burza")
        assert result == "buża"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])