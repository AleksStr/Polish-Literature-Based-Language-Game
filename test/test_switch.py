import pytest
import sys
from unittest.mock import patch

sys.path.append('.')
import switch


def test_select_swap_index_empty_valid_pairs():
    """Test basic case - empty input."""
    result = switch.select_swap_index([], 0, set())
    assert result is None


def test_select_swap_index_adjacent_restricted():
    """Test when only some positions are restricted."""
    valid_pairs = [0, 1, 2]
    line_index = 5
    swapped_word = {(5, 0)}  
    with patch('random.choice', side_effect=[0, 2]):
        result = switch.select_swap_index(valid_pairs, line_index, swapped_word)
        assert result == 2


def test_generate_riddle(monkeypatch):
    monkeypatch.setattr('switch.COLOR_START', "")
    monkeypatch.setattr('switch.COLOR_RESET', "")
    monkeypatch.setattr('switch.MIN_PAIRS', 1)
    monkeypatch.setattr('switch.MAX_PAIRS', 1)
    assert switch.generate_riddle("Życie mnie mnie") == "mnie Życie mnie"
    possible_results = ["trzech Test słów!", "Test słów! trzech"]
    assert switch.generate_riddle("Test trzech słów!") in possible_results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])