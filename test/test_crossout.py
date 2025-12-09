import unittest
from unittest.mock import mock_open, patch, MagicMock
import random
import os
import sys
from io import StringIO

sys.path.append('.')
import crossout

class TestPutExtraLine(unittest.TestCase):
    def test_put_extra_line_middle(self):
        page = "Line 1\nLine 2\nLine 3"
        extra = "Extra line"
        with patch('random.randint', return_value=1):
            result = crossout.put_extra_line(page, extra)
        self.assertIn("\033[91mExtra line\033[0m", result)
        self.assertEqual(len(result.split('\n')), 4)

    def test_put_extra_line_beginning(self):
        page = "Line 1\nLine 2"
        extra = "Extra line"
        with patch('random.randint', return_value=0):
            result = crossout.put_extra_line(page, extra)
        self.assertTrue(result.startswith("\033[91mExtra line\033[0m"))

    def test_put_extra_line_end(self):
        page = "Line 1\nLine 2"
        extra = "Extra line"
        with patch('random.randint', return_value=2):
            result = crossout.put_extra_line(page, extra)
        lines = result.split('\n')
        self.assertTrue(lines[-1].endswith("\033[91mExtra line\033[0m"))

    def test_put_extra_line_with_empty_trailing_line(self):
        page = "Line 1\nLine 2\n"
        extra = "Extra line"
        with patch('random.randint', return_value=1):
            result = crossout.put_extra_line(page, extra)
        lines = [line for line in result.split('\n') if line]
        self.assertEqual(len(lines), 3)

    def test_put_extra_line_warning_for_existing_line(self):
        page = "Line 1\nLine 2\nDuplicate line"
        extra = "Duplicate line"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('random.randint', return_value=1):
                result = crossout.put_extra_line(page, extra)
            output = fake_out.getvalue()
        self.assertIn("Warning: This line exist on this page", output)

    def test_put_extra_line_empty_page(self):
        page = ""
        extra = "Extra line"
        with patch('random.randint', return_value=0):
            result = crossout.put_extra_line(page, extra)
        self.assertEqual(result, "\033[91mExtra line\033[0m")


class TestGetRandomLineFromExtract(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_get_random_line_success(self, mock_file):
        mock_content = [
            "| Page 1 |\n",
            "\n",
            "First line\n",
            "Second line\n",
            "\n",
            "Third line\n",
            "| Page 2 |\n",
        ]
        mock_file.return_value.readlines.return_value = mock_content
        
        with patch('random.choice', side_effect=["| Page 1 |\n", "First line\n"]):
            result = crossout.get_random_line_from_extract("dummy.txt")
            self.assertEqual(result, "First line\n")

    @patch('builtins.open', new_callable=mock_open)
    def test_skip_empty_lines_and_page_markers(self, mock_file):
        mock_content = ["\n", "| Page 1 |\n", "Valid line\n"]
        mock_file.return_value.readlines.return_value = mock_content
        
        with patch('random.choice', side_effect=["\n", "| Page 1 |\n", "Valid line\n"]):
            result = crossout.get_random_line_from_extract("dummy.txt")
            self.assertEqual(result, "Valid line\n")


class TestGetRandomExtract(unittest.TestCase):
    @patch('os.path.dirname')
    @patch('os.listdir')
    @patch('os.path.join')
    def test_get_random_extract_different_file(self, mock_join, mock_listdir, mock_dirname):
        mock_dirname.return_value = "/test/extracts"
        mock_listdir.return_value = ["file1.txt", "file2.txt", "file3.txt"]
        mock_join.side_effect = lambda x, y: f"{x}/{y}"
        
        with patch('random.choice', side_effect=["file2.txt"]):
            result = crossout.get_random_extract("/test/extracts/file1.txt")
            self.assertEqual(result, "/test/extracts/file2.txt")


class TestGenerateRiddle(unittest.TestCase):
    @patch('crossout.get_random_extract')
    @patch('crossout.get_random_line_from_extract')
    @patch('crossout.put_extra_line')
    @patch('random.randint')
    def test_generate_riddle_basic(self, mock_randint, mock_put_extra_line, 
                                  mock_get_random_line, mock_get_random_extract):
        mock_randint.return_value = 3
        mock_get_random_extract.side_effect = ["path2.txt", "path3.txt", "path1.txt"]
        mock_get_random_line.side_effect = ["Line 1", "Line 2", "Line 3"]
        mock_put_extra_line.side_effect = ["Page1", "Page2", "Page3"]
        
        result = crossout.generate_riddle("Original", "path1.txt")
        
        self.assertEqual(mock_randint.call_count, 1)
        self.assertEqual(mock_get_random_extract.call_count, 3)
        self.assertEqual(mock_get_random_line.call_count, 3)
        self.assertEqual(mock_put_extra_line.call_count, 3)
        self.assertEqual(result, "Page3")

    @patch('crossout.get_random_extract')
    @patch('crossout.get_random_line_from_extract')
    @patch('crossout.put_extra_line')
    @patch('random.randint')
    def test_generate_riddle_min_lines(self, mock_randint, mock_put_extra_line,
                                      mock_get_random_line, mock_get_random_extract):
        mock_randint.return_value = 2
        mock_get_random_extract.return_value = "path2.txt"
        mock_get_random_line.return_value = "Extra"
        mock_put_extra_line.side_effect = lambda p, e: f"{p}\n{e}"
        
        result = crossout.generate_riddle("Original", "path1.txt")
        self.assertEqual(mock_put_extra_line.call_count, 2)


class TestGenerateLevel(unittest.TestCase):
    @patch('crossout.read_page')
    @patch('crossout.generate_riddle')
    def test_generate_level_multiple_pages(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count > 3:
                return None
            return f"Page{count}"
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.side_effect = ["Riddle1", "Riddle2", "Riddle3"]
        
        result = crossout.generate_level("book.txt")
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["Riddle1", "Riddle2", "Riddle3"])

    @patch('crossout.read_page')
    def test_generate_level_no_pages(self, mock_read_page):
        mock_read_page.return_value = None
        
        result = crossout.generate_level("empty.txt")
        self.assertEqual(result, [])

    @patch('crossout.read_page')
    @patch('crossout.generate_riddle')
    def test_generate_level_single_page(self, mock_generate_riddle, mock_read_page):
        def read_page_side_effect(path, count):
            if count == 1:
                return "Single"
            return None
        
        mock_read_page.side_effect = read_page_side_effect
        mock_generate_riddle.return_value = "Riddle"
        
        result = crossout.generate_level("single.txt")
        self.assertEqual(result, ["Riddle"])


class TestIntegration(unittest.TestCase):
    @patch('builtins.open')
    @patch('os.path.dirname')
    @patch('os.listdir')
    @patch('os.path.join')
    @patch('random.choice')
    @patch('random.randint')
    def test_complete_flow(self, mock_randint, mock_choice, mock_join, 
                          mock_listdir, mock_dirname, mock_open):
        mock_dirname.return_value = "/extracts"
        mock_listdir.return_value = ["book1.txt", "book2.txt"]
        mock_join.side_effect = lambda x, y: f"{x}/{y}"
        
        mock_file = MagicMock()
        mock_file.readlines.return_value = ["| Page 1 |\n", "Extra line\n"]
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_randint.side_effect = [2, 1, 0, 1, 0, 1]
        mock_choice.side_effect = [
            "book2.txt", 
            "Extra line\n", 
            "book1.txt", 
            "Extra line\n",
            "book2.txt",
            "Extra line\n"
        ]
        
        with patch('crossout.read_page', return_value="Line1\nLine2"):
            result = crossout.generate_riddle("Page", "/extracts/book1.txt")
            self.assertIn("\033[91m", result)
            self.assertIn("\033[0m", result)


if __name__ == '__main__':
    unittest.main()