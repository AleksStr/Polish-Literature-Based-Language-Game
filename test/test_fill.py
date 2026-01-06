import pytest
import sys

sys.path.append('.')
import fill
import helpers

def test_pick_words_to_remove():
    #does it pick good amount of words and are they all tokens from passed lists
    tokens = helpers.get_token_info2("Król Karol kupił Królowej Karolinie korale koloru koralowego")
    chosen = fill.pick_words_to_remove(tokens,3)
    for i in range(2):
        assert chosen[i] in tokens

def test_pick_words_to_remove_wont_double_words():
    tokens = helpers.get_token_info2("Test test1 Test2 test1 Test Test1")
    for i in range(3):
        chosen = fill.pick_words_to_remove(tokens,2)
        if len(chosen)>= 2:
            assert chosen[0].original_text.lower() != chosen[1].original_text.lower()


def test_replace_word_token(monkeypatch):
    monkeypatch.setattr('fill.COLOR_START', "")
    monkeypatch.setattr('fill.COLOR_RESET', "")
    page = "Test page"
    tokens = helpers.get_token_info2(page)
    assert fill.replace_word_token(page, tokens[0]) == "[x] page"
    assert fill.replace_word_token(page, tokens[1]) == "Test [x]"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])