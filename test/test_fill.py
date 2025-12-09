import unittest
from unittest.mock import patch, MagicMock
import random
import sys

sys.path.append('.')
import fill

class TestGenerateRiddle(unittest.TestCase):
    @patch('fill.get_token_info')
    def test_generate_riddle_basic(self, mock_token_info):
        page = "To jest przykładowe zdanie testowe."
        mock_token_info.return_value = [
            {'text': 'To', 'start': 0, 'end': 2},
            {'text': 'jest', 'start': 3, 'end': 7},
            {'text': 'przykładowe', 'start': 8, 'end': 19},
            {'text': 'zdanie', 'start': 20, 'end': 26},
            {'text': 'testowe', 'start': 27, 'end': 34}
        ]
        
        with patch('random.randint', return_value=3):
            with patch('random.sample', return_value=[0, 2, 4]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertIn("\033[91m[x]\033[0m", result_page)
        self.assertEqual(len(result_words), 3)
        self.assertEqual(result_words, ['To', 'przykładowe', 'testowe'])
    
    @patch('fill.get_token_info')
    def test_generate_riddle_no_words(self, mock_token_info):
        page = ""
        mock_token_info.return_value = []
        
        result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(result_page, page)
        self.assertEqual(result_words, [])
    
    @patch('fill.get_token_info')
    def test_generate_riddle_min_words(self, mock_token_info):
        page = "One two three four five"
        mock_token_info.return_value = [
            {'text': f'word{i}', 'start': i*5, 'end': i*5+4} for i in range(5)
        ]
        
        with patch('random.randint', return_value=3):
            with patch('random.sample', return_value=[0, 1, 2]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(len(result_words), 3)
        self.assertEqual(result_words, ['word0', 'word1', 'word2'])
    
    @patch('fill.get_token_info')
    def test_generate_riddle_max_words(self, mock_token_info):
        page = " ".join([f"word{i}" for i in range(10)])
        mock_token_info.return_value = [
            {'text': f'word{i}', 'start': i*6, 'end': i*6+5} for i in range(10)
        ]
        
        with patch('random.randint', return_value=8):
            with patch('random.sample', return_value=list(range(8))):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(len(result_words), 8)
    
    @patch('fill.get_token_info')
    def test_generate_riddle_all_words_masked(self, mock_token_info):
        page = "Hello world"
        mock_token_info.return_value = [
            {'text': 'Hello', 'start': 0, 'end': 5},
            {'text': 'world', 'start': 6, 'end': 11}
        ]
        
        with patch('random.randint', return_value=2):
            with patch('random.sample', return_value=[0, 1]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(result_words, ['Hello', 'world'])
        self.assertEqual(result_page.count("[x]"), 2)
        self.assertNotIn("Hello", result_page)
        self.assertNotIn("world", result_page)
    
    
    @patch('fill.get_token_info')
    def test_generate_riddle_single_word(self, mock_token_info):
        page = "Single"
        mock_token_info.return_value = [
            {'text': 'Single', 'start': 0, 'end': 6}
        ]
        
        with patch('random.randint', return_value=1):
            with patch('random.sample', return_value=[0]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(result_words, ['Single'])
        self.assertEqual(result_page, "\033[91m[x]\033[0m")
    
    @patch('fill.get_token_info')
    def test_generate_riddle_words_shorter_than_min(self, mock_token_info):
        page = "A B"
        mock_token_info.return_value = [
            {'text': 'A', 'start': 0, 'end': 1},
            {'text': 'B', 'start': 2, 'end': 3}
        ]
        
        with patch('random.randint', return_value=2):
            with patch('random.sample', return_value=[0, 1]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(len(result_words), 2)
        self.assertEqual(result_words, ['A', 'B'])

class TestGenerateLevel(unittest.TestCase):
    @patch('fill.read_page')
    @patch('fill.generate_riddle')
    def test_generate_level_multiple_pages(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count > 3:
                return None
            return f"Page {count}"
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.side_effect = [
            ("Page1_masked", ["word1", "word2"]),
            ("Page2_masked", ["word3"]),
            ("Page3_masked", ["word4", "word5", "word6"])
        ]
        
        result = fill.generate_level("test.txt")
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("Page1_masked", ["word1", "word2"]))
        self.assertEqual(result[1], ("Page2_masked", ["word3"]))
        self.assertEqual(result[2], ("Page3_masked", ["word4", "word5", "word6"]))
    
    @patch('fill.read_page')
    def test_generate_level_no_pages(self, mock_read_page):
        mock_read_page.return_value = None
        
        result = fill.generate_level("empty.txt")
        self.assertEqual(result, [])
    
    @patch('fill.read_page')
    @patch('fill.generate_riddle')
    def test_generate_level_single_page(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count == 1:
                return "Single page"
            return None
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.return_value = ("Masked page", ["word"])
        
        result = fill.generate_level("single.txt")
        self.assertEqual(result, [("Masked page", ["word"])])

class TestIntegration(unittest.TestCase):
    @patch('fill.get_token_info')
    def test_full_flow_with_real_page(self, mock_token_info):
        page = "To jest testowe zdanie z kilkoma słowami."
        mock_token_info.return_value = [
            {'text': 'To', 'start': 0, 'end': 2},
            {'text': 'jest', 'start': 3, 'end': 7},
            {'text': 'testowe', 'start': 8, 'end': 15},
            {'text': 'zdanie', 'start': 16, 'end': 22},
            {'text': 'z', 'start': 23, 'end': 24},
            {'text': 'kilkoma', 'start': 25, 'end': 32},
            {'text': 'słowami', 'start': 33, 'end': 40}
        ]
        
        with patch('random.randint', return_value=4):
            with patch('random.sample', return_value=[0, 2, 3, 6]):
                result_page, result_words = fill.generate_riddle(page)
        
        self.assertEqual(len(result_words), 4)
        self.assertEqual(result_words, ['To', 'testowe', 'zdanie', 'słowami'])
        self.assertEqual(result_page.count("[x]"), 4)
        self.assertIn("jest", result_page)
        self.assertIn("z", result_page)
        self.assertIn("kilkoma", result_page)
    
    def test_constants(self):
        self.assertEqual(fill.MIN_WORDS, 3)
        self.assertEqual(fill.MAX_WORDS, 8)
        self.assertEqual(fill.COLOR_START, "\033[91m")
        self.assertEqual(fill.COLOR_RESET, "\033[0m")

if __name__ == '__main__':
    unittest.main()