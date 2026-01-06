import pytest
import sys
from unittest.mock import patch, MagicMock

sys.path.append('.')
import anagram

def test_get_anagram():
    with patch('random.shuffle') as mock_shuffle:
        def mock_shuffle_impl(lst):
            if len(lst) > 1:
                lst[0], lst[-1] = lst[-1], lst[0]
        mock_shuffle.side_effect = mock_shuffle_impl
        
        new_anagram = anagram.get_anagram("ziemia")
        assert sorted(new_anagram.lower()) == sorted("ziemia".lower())
        assert new_anagram != "ziemia"
        
        new_anagram2 = anagram.get_anagram("miłość")
        assert sorted(new_anagram2.lower()) == sorted("miłość".lower())
        assert new_anagram2 != "miłość"

def test_generate_riddle_has_no_switches(monkeypatch):
    monkeypatch.setattr('anagram.MIN_WORDS', 1)
    monkeypatch.setattr('anagram.MAX_WORDS', 3)
    monkeypatch.setattr('anagram.COLOR_START', "")
    monkeypatch.setattr('anagram.COLOR_RESET', "")
    
    mock_page = "Fraszki to wszytko, cokolwiek myślemy, Fraszki to wszytko, cokolwiek czyniemy;"
    
    mock_tokens = []
    class MockToken:
        def __init__(self, text, idx, start_pos):
            self.original_text = text
            self.display_word = text
            self.i = idx
            self.start = start_pos
            self.finish = start_pos + len(text)
    
    current_pos = 0
    words = mock_page.replace(",", " ,").replace(";", " ;").split()
    for idx, word in enumerate(words):
        token = MockToken(word, idx, current_pos)
        mock_tokens.append(token)
        current_pos += len(word) + 1
    
    with patch('anagram.get_token_info2', return_value=mock_tokens):
        with patch('anagram.get_anagram') as mock_anagram:
            def mock_get_anagram(word):
                if len(word) <= 1:
                    return word
                chars = list(word)
                chars[0], chars[-1] = chars[-1], chars[0]
                return ''.join(chars)
            
            mock_anagram.side_effect = mock_get_anagram
            
            with patch('random.randint', return_value=2):
                with patch('random.sample', return_value=[0, 2]):
                    
                    result_page, changed_words = anagram.generate_riddle(mock_page)
                    result_words = result_page.split()
                    
                    original_words = mock_page.split()
                    for orig, res in zip(original_words, result_words):
                        if res.strip(",;") != orig.strip(",;"):
                            assert sorted(orig.strip(",;").lower()) == sorted(res.strip(",;").lower())

def test_generate_riddle_makes_correct_anagrams(monkeypatch):
    monkeypatch.setattr('anagram.MIN_WORDS', 1)
    monkeypatch.setattr('anagram.MAX_WORDS', 3)
    monkeypatch.setattr('anagram.COLOR_START', "")
    monkeypatch.setattr('anagram.COLOR_RESET', "")
    
    mock_page = "Fraszki to wszytko"
    
    mock_tokens = []
    class MockToken:
        def __init__(self, text, idx, start_pos):
            self.original_text = text
            self.display_word = text
            self.i = idx
            self.start = start_pos
            self.finish = start_pos + len(text)
    
    current_pos = 0
    words = mock_page.split()
    for idx, word in enumerate(words):
        token = MockToken(word, idx, current_pos)
        mock_tokens.append(token)
        current_pos += len(word) + 1
    
    with patch('anagram.get_token_info2', return_value=mock_tokens):
        with patch('anagram.get_anagram') as mock_anagram:
            def mock_get_anagram(word):
                return word[::-1]
            
            mock_anagram.side_effect = mock_get_anagram
            
            with patch('random.randint', return_value=2):
                with patch('random.sample', return_value=[0, 2]):
                    
                    result_page, changed_words = anagram.generate_riddle(mock_page)
                    
                    result_words = result_page.split()
                    
                    changed_indices = [t.i for t in changed_words]
                    
                    for idx, (orig, res) in enumerate(zip(mock_page.split(), result_words)):
                        if idx in changed_indices:
                            assert sorted(orig.lower()) == sorted(res.lower())
                            assert orig != res
                        else:
                            assert orig == res

if __name__ == "__main__":
    pytest.main([__file__, "-v"])