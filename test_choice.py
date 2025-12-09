import unittest
from unittest.mock import patch, MagicMock
import random
import sys

sys.path.append('.')
import choice

class TestFindSameFormCandidates(unittest.TestCase):
    def test_find_same_form_noun_matching(self):
        word_token = {"text": "kot", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Nom", "Number": "Sing"})}
        
        all_tokens = [
            {"text": "kot", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Nom", "Number": "Sing"})},
            {"text": "pies", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Nom", "Number": "Sing"})},
            {"text": "kota", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Gen", "Number": "Sing"})},
        ]
        
        result = choice.find_same_form_candidates(word_token, all_tokens)
        self.assertIn("pies", result)
        self.assertNotIn("kot", result)
        self.assertNotIn("kota", result)

    def test_find_same_form_adverb(self):
        word_token = {"text": "szybko", "pos": "ADV", "morph": MagicMock(to_dict=lambda: {})}
        
        all_tokens = [
            {"text": "szybko", "pos": "ADV", "morph": MagicMock(to_dict=lambda: {})},
            {"text": "wolno", "pos": "ADV", "morph": MagicMock(to_dict=lambda: {})},
            {"text": "kot", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Nom", "Number": "Sing"})},
        ]
        
        result = choice.find_same_form_candidates(word_token, all_tokens)
        self.assertIn("wolno", result)
        self.assertNotIn("szybko", result)
        self.assertNotIn("kot", result)

class TestGenerateRiddle(unittest.TestCase):
    @patch('choice.get_token_info')
    def test_generate_riddle_basic(self, mock_token_info):
        page = "To jest test."
        
        mock_tokens = [
            {"text": "To", "pos": "PRON", "morph": MagicMock(to_dict=lambda: {}), "start": 0, "end": 2},
            {"text": "jest", "pos": "VERB", "morph": MagicMock(to_dict=lambda: {}), "start": 3, "end": 7},
            {"text": "test", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {}), "start": 8, "end": 12},
        ]
        
        mock_token_info.return_value = mock_tokens
        
        with patch('random.randint', return_value=2):
            with patch('random.sample', return_value=[0, 2]):
                result_page, result_tokens = choice.generate_riddle(page)
        
        self.assertIn("\033[91m[x]\033[0m", result_page)
        self.assertEqual(len(result_tokens), 2)
        self.assertEqual(result_tokens[0]["text"], "To")
        self.assertEqual(result_tokens[1]["text"], "test")

    @patch('choice.get_token_info')
    def test_generate_riddle_no_words(self, mock_token_info):
        page = ""
        mock_token_info.return_value = []
        
        result_page, result_tokens = choice.generate_riddle(page)
        
        self.assertEqual(result_page, "")
        self.assertEqual(result_tokens, [])

class TestGenerateOptionsForMasked(unittest.TestCase):
    @patch('random.sample')
    @patch('random.shuffle')
    def test_generate_options_with_candidates(self, mock_shuffle, mock_sample):
        masked_tokens = [
            {"text": "kot", "pos": "NOUN", "morph": MagicMock()},
        ]
        
        all_tokens = [
            {"text": "kot", "pos": "NOUN", "morph": MagicMock()},
            {"text": "pies", "pos": "NOUN", "morph": MagicMock()},
            {"text": "ptak", "pos": "NOUN", "morph": MagicMock()},
            {"text": "ryba", "pos": "NOUN", "morph": MagicMock()},
        ]
        
        with patch('choice.find_same_form_candidates', return_value=["pies", "ptak", "ryba"]):
            mock_sample.return_value = ["pies", "ptak"]
            
            result = choice.generate_options_for_masked(masked_tokens, all_tokens)
        
        self.assertIn("kot", result)
        self.assertEqual(len(result["kot"]), 3)
        self.assertIn("kot", result["kot"])
        self.assertIn("pies", result["kot"])
        self.assertIn("ptak", result["kot"])

    @patch('random.sample')
    @patch('random.shuffle')
    def test_generate_options_few_fillers(self, mock_shuffle, mock_sample):
        masked_tokens = [
            {"text": "biega", "pos": "VERB", "morph": MagicMock()},
        ]
        
        all_tokens = [
            {"text": "biega", "pos": "VERB", "morph": MagicMock()},
            {"text": "kot", "pos": "NOUN", "morph": MagicMock()},
            {"text": "pies", "pos": "NOUN", "morph": MagicMock()},
        ]
        
        with patch('choice.find_same_form_candidates', return_value=[]):
            mock_sample.return_value = ["kot", "pies"]
            
            result = choice.generate_options_for_masked(masked_tokens, all_tokens)
        
        self.assertIn("biega", result)
        self.assertEqual(len(result["biega"]), 3)

class TestGenerateLevel(unittest.TestCase):
    @patch('choice.read_page')
    @patch('choice.generate_riddle')
    @patch('choice.get_token_info')
    @patch('choice.generate_options_for_masked')
    def test_generate_level_basic(self, mock_options, mock_get_token, mock_generate_riddle, mock_read_page):
        mock_read_page.side_effect = ["Page 1", None]
        
        masked_tokens = [{"text": "word1", "pos": "NOUN", "morph": MagicMock(), "start": 0, "end": 5}]
        mock_generate_riddle.return_value = ("Masked1", masked_tokens)
        mock_get_token.return_value = [{"text": "word1", "pos": "NOUN", "morph": MagicMock()}, {"text": "other", "pos": "NOUN", "morph": MagicMock()}]
        mock_options.return_value = {"word1": ["word1", "opt1", "opt2"]}
        
        result = choice.generate_level("test.txt")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "Masked1")
        self.assertEqual(result[0][1][0]["text"], "word1")
        self.assertEqual(result[0][2], {"word1": ["word1", "opt1", "opt2"]})

    @patch('choice.read_page')
    def test_generate_level_no_pages(self, mock_read_page):
        mock_read_page.return_value = None
        
        result = choice.generate_level("empty.txt")
        self.assertEqual(result, [])

class TestIntegration(unittest.TestCase):
    @patch('choice.read_page')
    @patch('choice.get_token_info')
    def test_full_flow_simple(self, mock_get_token, mock_read_page):
        page = "Kot biega."
        mock_read_page.side_effect = [page, None]
        
        all_tokens = [
            {"text": "Kot", "pos": "NOUN", "morph": MagicMock(to_dict=lambda: {"Case": "Nom", "Number": "Sing"}), "start": 0, "end": 3},
            {"text": "biega", "pos": "VERB", "morph": MagicMock(to_dict=lambda: {"Mood": "Ind", "Tense": "Pres", "Person": "3", "Number": "Sing"}), "start": 4, "end": 9},
        ]
        
        mock_get_token.return_value = all_tokens
        
        def mock_generate_riddle(p):
            return "\033[91m[x]\033[0m \033[91m[x]\033[0m", all_tokens
        
        def mock_generate_options(masked_tokens, all_t):
            return {
                "Kot": ["Kot", "Pies", "Ptak"],
                "biega": ["biega", "chodzi", "pływa"]
            }
        
        with patch('choice.generate_riddle', side_effect=mock_generate_riddle):
            with patch('choice.generate_options_for_masked', side_effect=mock_generate_options):
                result = choice.generate_level("test.txt")
        
        self.assertEqual(len(result), 1)
        masked_page, masked_tokens, options = result[0]
        self.assertEqual(len(masked_tokens), 2)
        self.assertEqual(len(options), 2)
        self.assertIn("Kot", options)
        self.assertIn("biega", options)

class TestConstants(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(choice.MIN_WORDS, 3)
        self.assertEqual(choice.MAX_WORDS, 8)
        self.assertEqual(choice.COLOR_START, "\033[91m")
        self.assertEqual(choice.COLOR_RESET, "\033[0m")

if __name__ == '__main__':
    unittest.main