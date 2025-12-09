import unittest
from unittest.mock import patch, mock_open
from helpers import read_page, get_token_info
from typing import List, Dict, Any



MOCK_FILE_CONTENT = """
| Title |
Some introductory text.
| Page 1 |
<-- START PAGE 1 -->
Page content line 1.
Page content line 2.
<-- END PAGE 1 -->
| Page 2 |
<-- START PAGE 2 -->
Page content line 3.
Page content line 4.
<-- END PAGE 2 -->
| Page 3 |
<-- START PAGE 3 -->
Final line.
<-- END PAGE 3 -->
"""

class TestFileHelpers(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_FILE_CONTENT)
    def test_read_page_first_page(self, mock_file):
        extract_path = "extracts/test/mock_file.txt"

        expected_content = "Page content line 1.\nPage content line 2.\n"
        
        content = read_page(extract_path, 1)
        self.assertEqual(content, expected_content)
        mock_file.assert_called_once_with(extract_path, 'r', encoding='utf-8')

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_FILE_CONTENT)
    def test_read_page_middle_page(self, mock_file):
        expected_content = "Page content line 3.\nPage content line 4.\n"
        content = read_page("dummy_path", 2)
        self.assertEqual(content, expected_content)

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_FILE_CONTENT)
    def test_read_page_last_page(self, mock_file):
        expected_content = "Final line.\n"
        content = read_page("dummy_path", 3)
        self.assertEqual(content, expected_content)

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_FILE_CONTENT)
    def test_read_page_non_existent_page(self, mock_file):
        content = read_page("dummy_path", 4)
        self.assertIsNone(content)
        
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_page_empty_file(self, mock_file):
        content = read_page("dummy_path", 1)
        self.assertIsNone(content)


class MockToken:
    def __init__(self, text, idx, is_punct=False, is_space=False):
        self.text = text
        self.idx = idx
        self.is_punct = is_punct
        self.is_space = is_space
        
    def __len__(self):
        return len(self.text)

class MockDoc:
    def __init__(self, tokens):
        self.tokens = tokens
        
    def __iter__(self):
        return iter(self.tokens)

class TestTokenHelpers(unittest.TestCase):

    @patch("helpers.NLP")
    def test_get_token_info_standard_sentence(self, mock_nlp):

        mock_tokens = [
            MockToken(text='The', idx=0),
            MockToken(text=' ', idx=3, is_space=True),
            MockToken(text='red', idx=4),
            MockToken(text='.', idx=7, is_punct=True),
            MockToken(text=' ', idx=8, is_space=True),
            MockToken(text='ball', idx=9),
            MockToken(text='!', idx=13, is_punct=True),
        ]
        mock_nlp.return_value = MockDoc(mock_tokens)
        
        text = "The red. ball!"
        tokens = get_token_info(text)
        
        expected_tokens = [
            {'text': 'The', 'start': 0, 'end': 3},
            {'text': 'red', 'start': 4, 'end': 7},
            {'text': 'ball', 'start': 9, 'end': 13}
        ]
        
        self.assertEqual(tokens, expected_tokens)

    @patch("helpers.NLP")
    def test_get_token_info_short_tokens(self, mock_nlp):
        
        mock_tokens = [
            MockToken(text='A', idx=0),
            MockToken(text=' ', idx=1, is_space=True),
            MockToken(text='big', idx=2),
            MockToken(text=' ', idx=5, is_space=True),
            MockToken(text='eye', idx=6),
        ]
        mock_nlp.return_value = MockDoc(mock_tokens)
        
        text = "A big eye"
        tokens = get_token_info(text)

        expected_tokens = [
            {'text': 'big', 'start': 2, 'end': 5},
            {'text': 'eye', 'start': 6, 'end': 9}
        ]
        
        self.assertEqual(tokens, expected_tokens)

    @patch("helpers.NLP")
    def test_get_token_info_empty_input(self, mock_nlp):
        mock_nlp.return_value = MockDoc([])
        tokens = get_token_info("")
        self.assertEqual(tokens, [])

    @patch("helpers.NLP")
    def test_get_token_info_only_junk(self, mock_nlp):
        
        mock_tokens = [
            MockToken(text=' ', idx=0, is_space=True),
            MockToken(text='...', idx=1, is_punct=True),
            MockToken(text='\n', idx=4, is_space=True),
        ]
        mock_nlp.return_value = MockDoc(mock_tokens)
        
        tokens = get_token_info(" ...\n")
        self.assertEqual(tokens, [])


if __name__ == '__main__':
    unittest.main()