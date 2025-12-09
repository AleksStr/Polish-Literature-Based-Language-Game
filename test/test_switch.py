import unittest
from unittest.mock import patch, MagicMock
import random
import sys
from io import StringIO

sys.path.append('.')
import switch

class TestSwitchWordRiddle(unittest.TestCase):
    def test_switch_word_riddle_basic(self):
        page = "To jest przykładowe zdanie testowe."
        with patch('random.choice', side_effect=[0, 1]):
            result = switch.switch_word_riddle(page)
        self.assertIn("\033[91m", result)
        self.assertIn("\033[0m", result)

    def test_switch_word_riddle_empty_page(self):
        page = ""
        result = switch.switch_word_riddle(page)
        self.assertEqual(result, page)

    def test_switch_word_riddle_only_whitespace(self):
        page = "   \n\n   \t\n"
        result = switch.switch_word_riddle(page)
        self.assertEqual(result, page)

    def test_switch_word_riddle_single_word_line(self):
        page = "Word"
        result = switch.switch_word_riddle(page)
        self.assertEqual(result, page)

    def test_switch_word_riddle_two_words(self):
        page = "First Second"
        with patch('random.choice', side_effect=[0, 0]):
            result = switch.switch_word_riddle(page)
        self.assertIn("\033[91mFirst\033[0m", result)
        self.assertIn("\033[91mSecond\033[0m", result)
        words = result.split()
        self.assertEqual(words[0], "\033[91mSecond\033[0m")
        self.assertEqual(words[1], "\033[91mFirst\033[0m")

    def test_switch_word_riddle_multiple_lines(self):
        page = "Line one\nLine two with words\nThird line"
        with patch('random.choice', side_effect=[1, 0]):
            result = switch.switch_word_riddle(page)
        lines = result.split('\n')
        self.assertIn("\033[91m", lines[1])

    def test_switch_word_riddle_empty_lines_between(self):
        page = "First line\n\n\nSecond line with words"
        with patch('random.choice', side_effect=[3, 1]):
            result = switch.switch_word_riddle(page)
        lines = result.split('\n')
        self.assertIn("\033[91m", lines[3])

    def test_switch_word_riddle_special_characters(self):
        page = "Hello, world! How's everything?"
        with patch('random.choice', side_effect=[0, 0]):
            result = switch.switch_word_riddle(page)
        self.assertIn("\033[91m", result)

    def test_switch_word_riddle_with_punctuation(self):
        page = "Hello, world! This is test."
        with patch('random.choice', side_effect=[0, 0]):
            result = switch.switch_word_riddle(page)
        self.assertIn("\033[91m", result)
        self.assertIn("\033[0m", result)

    def test_switch_word_riddle_multiple_valid_pairs(self):
        page = "One two three four five"
        line_idx = 0
        valid_pairs = [0, 1, 2, 3]
        
        def choice_side_effect(args):
            if args == [line_idx]:
                return line_idx
            elif args == valid_pairs:
                return 1
        
        with patch('random.choice', side_effect=choice_side_effect):
            result = switch.switch_word_riddle(page)
        words = result.split()
        self.assertIn("\033[91m", words[1])
        self.assertIn("\033[91m", words[2])

    def test_switch_word_riddle_no_valid_pairs(self):
        page = "Word  \n  \t"
        result = switch.switch_word_riddle(page)
        self.assertEqual(result, page)

class TestGenerateRiddle(unittest.TestCase):
    @patch('switch.switch_word_riddle')
    @patch('random.randint')
    def test_generate_riddle_min_pairs(self, mock_randint, mock_switch):
        mock_randint.return_value = 3
        mock_switch.side_effect = lambda x: f"switched_{x}"
        
        page = "Test page"
        result = switch.generate_riddle(page)
        
        self.assertEqual(mock_randint.call_count, 1)
        self.assertEqual(mock_switch.call_count, 3)
        self.assertEqual(result, "switched_switched_switched_Test page")

    @patch('switch.switch_word_riddle')
    @patch('random.randint')
    def test_generate_riddle_max_pairs(self, mock_randint, mock_switch):
        mock_randint.return_value = 6
        mock_switch.side_effect = lambda x: f"switched_{x}"
        
        page = "Test page"
        result = switch.generate_riddle(page)
        
        self.assertEqual(mock_randint.call_count, 1)
        self.assertEqual(mock_switch.call_count, 6)

    @patch('switch.switch_word_riddle')
    @patch('random.randint')
    def test_generate_riddle_no_changes(self, mock_randint, mock_switch):
        mock_randint.return_value = 3
        mock_switch.side_effect = lambda x: x
        
        page = "Test page"
        result = switch.generate_riddle(page)
        
        self.assertEqual(result, page)

class TestGenerateLevel(unittest.TestCase):
    @patch('switch.read_page')
    @patch('switch.generate_riddle')
    def test_generate_level_multiple_pages(self, mock_generate_riddle, mock_read_page):
        call_count = 0
        def read_page_side_effect(path, count):
            nonlocal call_count
            call_count += 1
            if count > 3:
                return None
            return f"Page {count}"
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.side_effect = ["Riddle1", "Riddle2", "Riddle3"]
        
        result = switch.generate_level("test.txt")
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["Riddle1", "Riddle2", "Riddle3"])

    @patch('switch.read_page')
    def test_generate_level_no_pages(self, mock_read_page):
        mock_read_page.return_value = None
        
        result = switch.generate_level("empty.txt")
        self.assertEqual(result, [])

    @patch('switch.read_page')
    @patch('switch.generate_riddle')
    def test_generate_level_single_page(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count == 1:
                return "Single page"
            return None
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.return_value = "Riddle page"
        
        result = switch.generate_level("single.txt")
        self.assertEqual(result, ["Riddle page"])

class TestIntegration(unittest.TestCase):
    def test_full_integration_small(self):
        page = "This is a test sentence with multiple words."
        
        with patch('random.randint', return_value=3):
            with patch('random.choice', side_effect=[0, 1, 0, 0, 0, 1]):
                result = switch.generate_riddle(page)
        
        self.assertIn("\033[91m", result)
        count_red = result.count("\033[91m")
        self.assertEqual(count_red, 6)

    def test_switch_word_riddle_edge_cases(self):
        test_cases = [
            ("A B", ["\033[91mA\033[0m", "\033[91mB\033[0m"]),
            ("Word1 Word2 Word3", 3),
        ]
        
        for page, expected in test_cases:
            if isinstance(expected, list):
                with patch('random.choice', side_effect=[0, 0]):
                    result = switch.switch_word_riddle(page)
                    for word in expected:
                        self.assertIn(word, result)
            else:
                with patch('random.choice', side_effect=[0, 0]):
                    result = switch.switch_word_riddle(page)
                    self.assertEqual(len(result.split()), expected)

if __name__ == '__main__':
    unittest.main()