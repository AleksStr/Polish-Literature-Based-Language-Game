import string
import sys
sys.path.append('.')
from helpers import read_page, get_token_info, get_token_info2, is_punctuation

import pytest


def test_read_page():
    expected1 = 'Gospodarstwo\nPowrót panicza — Spotkanie się pierwsze w pokoiku, drugie\nu stołu — Ważna Sędziego nauka o grzeczności — Podkomorzego\nuwagi polityczne nad modami — Początek sporu o Kusego\ni Sokoła — Żale Wojskiego — Ostatni Woźny Trybunału — Rzut\n'
    result1 = read_page("test/books_for_tests/Pan_Tadeusz/Księga pierwsza_part_1.txt", 1)
    expected2 = 'Tymczasem przenoś moją duszę utęsknioną\nDo tych pagórków leśnych, do tych łąk zielonych,\n'
    result2 = read_page("test/books_for_tests/Pan_Tadeusz/Księga pierwsza_part_1.txt", 2)
    expected10= 'Już konie w stajnią wzięto, już im hojnie dano,\nJako w porządnym domu, i obrok, i siano:\nBo Sędzia nigdy nie chciał, według nowej mody,\n'
    result10 = read_page("test/books_for_tests/Pan_Tadeusz/Księga pierwsza_part_1.txt", 10)
    assert result1 == expected1
    assert result2 == expected2
    assert result10 == expected10

def test_get_token_info2():
    word_tokens = get_token_info2("Litwo, Ojczyzno ty Moja!")
    assert len(word_tokens) == 4
    assert word_tokens[1].original_text == "Ojczyzno"
    assert word_tokens[1].start == 7
    assert word_tokens[1].finish== 15
    assert word_tokens[1].display_word == "ojczyzno"
    assert word_tokens[1].i == 2

def test_get_token_info():

    word_tokens = get_token_info("Litwo, Ojczyzno ty Moja!")
    '''
    print(f"Number of tokens: {len(word_tokens)}")
    for i, token in enumerate(word_tokens):
        print(f"Token {i}: '{token.original_text}'")
        print(f"  POS: {token.pos}")
        print(f"  Morph str: {str(token.morph)}")
        print(f"  Morph dict: {token.morph.to_dict()}")
        print(f"  Case from morph: {token.morph.get('Case')}")
        print("---")
    '''
    assert len(word_tokens) == 4
    assert word_tokens[1].original_text == "Ojczyzno"
    assert word_tokens[1].start == 7
    assert word_tokens[1].finish== 15
    assert word_tokens[1].display_word == "ojczyzno"

def test_is_punctuation_edge_cases():


    for punct in string.punctuation:
        assert is_punctuation(punct) == True

    assert is_punctuation("-") == True
    assert is_punctuation("–") == True 
    assert is_punctuation("—") == True 
    assert is_punctuation("?!") == True
    assert is_punctuation("---") == True
    assert is_punctuation(" ") == False  
    assert is_punctuation("\n") == False  
    assert is_punctuation("\t") == False
    assert is_punctuation("a") == False
    assert is_punctuation("word") == False
    assert is_punctuation("a.") == False  


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
