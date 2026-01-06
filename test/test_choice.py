import pytest
from unittest.mock import patch, MagicMock, mock_open
import random
import sys
import io

sys.path.append('.')
import choice  

def test_find_same_form_candidates_noun():
    """Test noun with matching case and number."""
    mock_word_token = MagicMock()
    mock_word_token.display_word = "kot"
    mock_word_token.pos = "NOUN"
    mock_word_token.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
    
    mock_other1 = MagicMock()
    mock_other1.display_word = "pies"
    mock_other1.pos = "NOUN"
    mock_other1.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
    
    mock_other2 = MagicMock()
    mock_other2.display_word = "psa"
    mock_other2.pos = "NOUN"
    mock_other2.morph.to_dict.return_value = {"Case": "Gen", "Number": "Sing"}
    
    mock_other3 = MagicMock()
    mock_other3.display_word = "kot" 
    mock_other3.pos = "NOUN"
    mock_other3.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
    
    all_tokens = [mock_word_token, mock_other1, mock_other2, mock_other3]
    
    result = choice.find_same_form_candidates(mock_word_token, all_tokens)
    assert "pies" in result
    assert "psa" not in result
    assert "kot" not in result

def test_find_same_form_candidates_verb():
    """Test verb with sufficient shared features."""
    mock_word_token = MagicMock()
    mock_word_token.display_word = "czytał"
    mock_word_token.pos = "VERB"
    mock_word_token.morph.to_dict.return_value = {"Mood": "Ind", "Tense": "Past", "Person": "3", "Number": "Sing", "Aspect": "Imp"}
    
    mock_other1 = MagicMock()
    mock_other1.display_word = "pisał"
    mock_other1.pos = "VERB"
    mock_other1.morph.to_dict.return_value = {"Mood": "Ind", "Tense": "Past", "Person": "3", "Number": "Sing", "Aspect": "Imp"}
    
    mock_other2 = MagicMock()
    mock_other2.display_word = "czyta"
    mock_other2.pos = "VERB"
    mock_other2.morph.to_dict.return_value = {"Mood": "Ind", "Tense": "Pres", "Person": "3", "Number": "Sing", "Aspect": "Imp"}
    
    all_tokens = [mock_word_token, mock_other1, mock_other2]
    
    result = choice.find_same_form_candidates(mock_word_token, all_tokens)
    assert "pisał" in result 

def test_find_same_form_candidates_adjective():
    """Test adjective with matching case, number and gender."""
    mock_word_token = MagicMock()
    mock_word_token.display_word = "duży"
    mock_word_token.pos = "ADJ"
    mock_word_token.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}
    
    mock_other1 = MagicMock()
    mock_other1.display_word = "mały"
    mock_other1.pos = "ADJ"
    mock_other1.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}
    
    mock_other2 = MagicMock()
    mock_other2.display_word = "duża"
    mock_other2.pos = "ADJ"
    mock_other2.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing", "Gender": "Fem"}
    
    all_tokens = [mock_word_token, mock_other1, mock_other2]
    
    result = choice.find_same_form_candidates(mock_word_token, all_tokens)
    assert "mały" in result
    assert "duża" not in result

def test_find_same_form_candidates_adverb():
    """Test adverb - all adverbs should be candidates."""
    mock_word_token = MagicMock()
    mock_word_token.display_word = "szybko"
    mock_word_token.pos = "ADV"
    mock_word_token.morph.to_dict.return_value = {}
    
    mock_other1 = MagicMock()
    mock_other1.display_word = "wolno"
    mock_other1.pos = "ADV"
    mock_other1.morph.to_dict.return_value = {}
    
    mock_other2 = MagicMock()
    mock_other2.display_word = "ładnie"
    mock_other2.pos = "ADJ"  
    
    all_tokens = [mock_word_token, mock_other1, mock_other2]
    
    result = choice.find_same_form_candidates(mock_word_token, all_tokens)
    assert "wolno" in result
    assert "ładnie" not in result

def test_generate_riddle_empty_page():
    """Test with empty page."""
    result_page, result_tokens = choice.generate_riddle("")
    assert result_page == ""
    assert result_tokens == []

def test_generate_riddle_with_mock_tokens(monkeypatch):
    """Test riddle generation with mocked get_token_info."""
    page_text = "To jest testowy tekst."
    monkeypatch.setattr('anagram.COLOR_START', "")
    monkeypatch.setattr('anagram.COLOR_RESET', "")
    
    mock_tokens = []
    for i, word in enumerate(["To", "jest", "testowy", "tekst"]):
        mock_token = MagicMock()
        mock_token.display_word = word
        mock_token.start = i * 3
        mock_token.finish = i * 3 + len(word)
        mock_tokens.append(mock_token)
    
    with patch('choice.get_token_info') as mock_get_tokens:
        mock_get_tokens.return_value = mock_tokens
        
        with patch('random.randint') as mock_randint:
            with patch('random.sample') as mock_sample:
                mock_randint.return_value = 3
                mock_sample.return_value = [0, 1, 2]
                
                result_page, result_tokens = choice.generate_riddle(page_text)
                
                assert len(result_tokens) == 3

def test_generate_options_for_masked_few_candidates():
    """Test when there are few candidates."""
    mock_masked_token = MagicMock()
    mock_masked_token.display_word = "kot"
    mock_masked_token.pos = "NOUN"
    mock_masked_token.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
    
    mock_all_token1 = MagicMock()
    mock_all_token1.display_word = "kot"
    mock_all_token1.pos = "NOUN"
    
    mock_all_token2 = MagicMock()
    mock_all_token2.display_word = "pies"
    mock_all_token2.pos = "NOUN"
    
    mock_all_token3 = MagicMock()
    mock_all_token3.display_word = "dom"
    mock_all_token3.pos = "NOUN"
    
    mock_all_token4 = MagicMock()
    mock_all_token4.display_word = "stół"
    mock_all_token4.pos = "NOUN"
    
    masked_tokens = [mock_masked_token]
    all_tokens = [mock_all_token1, mock_all_token2, mock_all_token3, mock_all_token4]
    
    with patch('random.sample') as mock_sample:
        mock_sample.return_value = ["pies", "dom"]
        
        result = choice.generate_options_for_masked(masked_tokens, all_tokens)
        
        assert "kot" in result
        assert len(result["kot"]) == 3
        assert "kot" in result["kot"]
        assert "pies" in result["kot"]
        assert "dom" in result["kot"]

def test_generate_options_for_masked_many_candidates():
    """Test when there are many candidates."""
    mock_masked_token = MagicMock()
    mock_masked_token.display_word = "kot"
    mock_masked_token.pos = "NOUN"
    mock_masked_token.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
    

    mock_candidates = []
    for i in range(10):
        mock_tok = MagicMock()
        mock_tok.display_word = f"word{i}"
        mock_tok.pos = "NOUN"
        mock_tok.morph.to_dict.return_value = {"Case": "Nom", "Number": "Sing"}
        mock_candidates.append(mock_tok)
    
    all_tokens = [mock_masked_token] + mock_candidates
    
    with patch('random.sample') as mock_sample:
        mock_sample.return_value = ["word0", "word1"]
        
        result = choice.generate_options_for_masked([mock_masked_token], all_tokens)
        
        assert "kot" in result
        assert len(result["kot"]) == 3
        assert "word0" in result["kot"]
        assert "word1" in result["kot"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])