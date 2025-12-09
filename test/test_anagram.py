import unittest
from unittest.mock import patch, MagicMock, call
import random
import sys

sys.path.append('.')
import anagram

class TestGetAnagram(unittest.TestCase):
    def test_get_anagram_basic(self):
        with patch('random.shuffle') as mock_shuffle:
            def shuffle_side_effect(lst):
                if lst == list("test"):
                    lst[:] = ['t', 's', 'e', 't']
            
            mock_shuffle.side_effect = shuffle_side_effect
            result = anagram.get_anagram("test")
            self.assertEqual(result, "tset")
    
    def test_get_anagram_different_result(self):
        word = "abc"
        result = anagram.get_anagram(word)
        self.assertNotEqual(result, word)
        self.assertEqual(sorted(result), sorted(word))
        self.assertEqual(len(result), len(word))
    
    def test_get_anagram_single_letter(self):
        word = "a"
        result = anagram.get_anagram(word)
        self.assertEqual(result, "a")
    
    def test_get_anagram_empty(self):
        word = ""
        result = anagram.get_anagram(word)
        self.assertEqual(result, "")
    
    def test_get_anagram_repeated_letters(self):
        word = "aa"
        with patch('random.shuffle') as mock_shuffle:
            def shuffle_side_effect(lst):
                if lst == ['a', 'a']:
                    lst[:] = ['a', 'a']
            
            mock_shuffle.side_effect = shuffle_side_effect
            result = anagram.get_anagram(word)
            self.assertEqual(result, "aa")

class TestGenerateRiddle(unittest.TestCase):
    @patch('anagram.get_token_info')
    @patch('random.randint')
    @patch('random.sample')
    def test_generate_riddle_basic(self, mock_sample, mock_randint, mock_token_info):
        page = "To jest przykładowe zdanie testowe."
        mock_token_info.return_value = [
            {'text': 'To', 'start': 0, 'end': 2},
            {'text': 'jest', 'start': 3, 'end': 7},
            {'text': 'przykładowe', 'start': 8, 'end': 19},
            {'text': 'zdanie', 'start': 20, 'end': 26},
            {'text': 'testowe', 'start': 27, 'end': 34}
        ]
        
        mock_randint.return_value = 3
        mock_sample.return_value = [0, 2, 4]
        
        with patch('anagram.get_anagram') as mock_anagram:
            mock_anagram.side_effect = ['oT', 'ekadowyrzpł', 'ewotset']
            
            result_page, result_words = anagram.generate_riddle(page)
        
        self.assertIn("\033[91m", result_page)
        self.assertIn("\033[0m", result_page)
        self.assertEqual(len(result_words), 3)
        self.assertEqual(result_words, ['To', 'przykładowe', 'testowe'])
        mock_anagram.assert_has_calls([call('To'), call('przykładowe'), call('testowe')])
    
    @patch('anagram.get_token_info')
    def test_generate_riddle_no_words(self, mock_token_info):
        page = ""
        mock_token_info.return_value = []
        
        result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(result_page, page)
        self.assertEqual(result_words, [])
    
    @patch('anagram.get_token_info')
    @patch('random.randint')
    def test_generate_riddle_few_words_than_min(self, mock_randint, mock_token_info):
        page = "One two"
        mock_token_info.return_value = [
            {'text': 'One', 'start': 0, 'end': 3},
            {'text': 'two', 'start': 4, 'end': 7}
        ]
        
        mock_randint.return_value = 2
        
        with patch('random.sample', return_value=[0, 1]):
            with patch('anagram.get_anagram') as mock_anagram:
                mock_anagram.side_effect = ['enO', 'owt']
                
                result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(len(result_words), 2)
        self.assertEqual(result_words, ['One', 'two'])
    
    @patch('anagram.get_token_info')
    @patch('random.randint')
    @patch('random.sample')
    def test_generate_riddle_max_words(self, mock_sample, mock_randint, mock_token_info):
        page = " ".join([f"word{i}" for i in range(10)])
        mock_token_info.return_value = [
            {'text': f'word{i}', 'start': i*6, 'end': i*6+5} for i in range(10)
        ]
        
        mock_randint.return_value = 8
        mock_sample.return_value = list(range(8))
        
        with patch('anagram.get_anagram') as mock_anagram:
            mock_anagram.side_effect = [f'drow{i}' for i in range(8)]
            
            result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(len(result_words), 8)
    
    @patch('anagram.get_token_info')
    def test_generate_riddle_single_word(self, mock_token_info):
        page = "Single"
        mock_token_info.return_value = [
            {'text': 'Single', 'start': 0, 'end': 6}
        ]
        
        with patch('random.randint', return_value=1):
            with patch('random.sample', return_value=[0]):
                with patch('anagram.get_anagram', return_value='elngiS'):
                    result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(result_words, ['Single'])
        self.assertIn("\033[91melngiS\033[0m", result_page)

    
    def test_generate_riddle_real_example(self):
        page = "Hello world"
        with patch('anagram.get_token_info') as mock_token_info:
            mock_token_info.return_value = [
                {'text': 'Hello', 'start': 0, 'end': 5},
                {'text': 'world', 'start': 6, 'end': 11}
            ]
            
            with patch('random.randint', return_value=1):
                with patch('random.sample', return_value=[0]):
                    with patch('anagram.get_anagram', return_value='olleH'):
                        result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(result_page, "\033[91molleH\033[0m world")
        self.assertEqual(result_words, ['Hello'])

class TestGenerateLevel(unittest.TestCase):
    @patch('anagram.read_page')
    @patch('anagram.generate_riddle')
    def test_generate_level_multiple_pages(self, mock_generate_riddle, mock_read_page):
        call_count = 0
        def read_page_side_effect(path, count):
            nonlocal call_count
            call_count += 1
            if count > 3:
                return None
            return f"Page {count}"
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.side_effect = [
            ("Page1_anagram", ["word1", "word2"]),
            ("Page2_anagram", ["word3"]),
            ("Page3_anagram", ["word4", "word5", "word6"])
        ]
        
        result = anagram.generate_level("test.txt")
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("Page1_anagram", ["word1", "word2"]))
        self.assertEqual(result[1], ("Page2_anagram", ["word3"]))
        self.assertEqual(result[2], ("Page3_anagram", ["word4", "word5", "word6"]))
    
    @patch('anagram.read_page')
    def test_generate_level_no_pages(self, mock_read_page):
        mock_read_page.return_value = None
        
        result = anagram.generate_level("empty.txt")
        self.assertEqual(result, [])
    
    @patch('anagram.read_page')
    @patch('anagram.generate_riddle')
    def test_generate_level_single_page(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count == 1:
                return "Single page"
            return None
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.return_value = ("Anagrammed", ["words"])
        
        result = anagram.generate_level("single.txt")
        self.assertEqual(result, [("Anagrammed", ["words"])])

class TestIntegration(unittest.TestCase):
    @patch('anagram.get_token_info')
    def test_full_flow(self, mock_token_info):
        page = "Test sentence with words"
        mock_token_info.return_value = [
            {'text': 'Test', 'start': 0, 'end': 4},
            {'text': 'sentence', 'start': 5, 'end': 13},
            {'text': 'with', 'start': 14, 'end': 18},
            {'text': 'words', 'start': 19, 'end': 24}
        ]
        
        with patch('random.randint', return_value=3):
            with patch('random.sample', return_value=[0, 1, 3]):
                with patch('anagram.get_anagram') as mock_anagram:
                    mock_anagram.side_effect = ['tseT', 'ecnetnes', 'sdrow']
                    
                    result_page, result_words = anagram.generate_riddle(page)
        
        self.assertEqual(result_words, ['Test', 'sentence', 'words'])
        self.assertIn("\033[91mtseT\033[0m", result_page)
        self.assertIn("\033[91mecnetnes\033[0m", result_page)
        self.assertIn("\033[91msdrow\033[0m", result_page)
        self.assertIn("with", result_page)
    
    def test_anagram_always_different(self):
        for word in ["test", "hello", "python", "example"]:
            result = anagram.get_anagram(word)
            self.assertNotEqual(result, word)
            self.assertEqual(sorted(result), sorted(word))
            self.assertEqual(len(result), len(word))

if __name__ == '__main__':
    unittest.main()