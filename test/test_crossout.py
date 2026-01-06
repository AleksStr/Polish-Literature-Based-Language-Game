import pytest
from unittest.mock import patch, MagicMock, mock_open
import random
import os
import sys

sys.path.append('.')
import crossout

def test_check_if_allowed_single_item():
    """Test when folder contains only one item."""
    with patch('os.listdir') as mock_listdir:
        with patch('os.path.dirname') as mock_dirname:
            mock_dirname.return_value = "/test/folder"
            mock_listdir.return_value = ["only_file.txt"]
            
            result = crossout.check_if_allowed("/test/folder/file.txt")
            assert result == 0

def test_check_if_allowed_multiple_items():
    """Test when folder contains multiple items."""
    with patch('os.listdir') as mock_listdir:
        with patch('os.path.dirname') as mock_dirname:
            mock_dirname.return_value = "/test/folder"
            mock_listdir.return_value = ["file1.txt", "file2.txt", "file3.txt"]
            
            result = crossout.check_if_allowed("/test/folder/file1.txt")
            assert result == 1

def test_put_extra_line_empty_line():
    """Test adding extra line when page is empty."""
    result = crossout.put_extra_line("", "Test line")
    assert "Test line" in result
    assert crossout.COLOR_START in result
    assert crossout.COLOR_RESET in result

def test_put_extra_line_with_existing_line():
    """Test when extra line already exists in page."""
    page = "Line 1\nLine 2\nLine 3"
    extra = "Line 2"
    
    result = crossout.put_extra_line(page, extra)
    assert result == page  

def test_put_extra_line_random_index():
    """Test adding line at random position."""
    page = "Line 1\nLine 2\nLine 3"
    extra = "Extra Line"
    
    with patch('random.randint') as mock_randint:
        mock_randint.return_value = 1 
        
        result = crossout.put_extra_line(page, extra)
        lines = result.split('\n')
        
        assert "Extra Line" in lines[1]
        assert crossout.COLOR_START in result
        assert crossout.COLOR_RESET in result
        assert len(lines) == 4

def test_put_extra_line_remove_trailing_newline():
    """Test that trailing newline is removed before insertion."""
    page = "Line 1\nLine 2\nLine 3\n"
    extra = "Extra Line"
    
    result = crossout.put_extra_line(page, extra)
    assert not result.endswith('\n\n')

def test_get_random_line_from_extract_skip_empty_lines():
    """Test that empty lines are skipped."""
    mock_lines = ["\n", "", "Valid line\n", "\n\n", "Another valid line\n"]
    
    with patch('builtins.open', mock_open(read_data="".join(mock_lines))):
        with patch('random.choice') as mock_choice:
            mock_choice.side_effect = ["\n", "", "Valid line\n"]
            
            result = crossout.get_random_line_from_extract("dummy_path.txt")
            assert result == "Valid line\n"

def test_get_random_line_from_extract_skip_page_markers():
    """Test that lines with | Page are skipped."""
    mock_lines = ["| Page 1\n", "Normal text\n", "| Page 2\n", "Another line\n"]
    
    with patch('builtins.open', mock_open(read_data="".join(mock_lines))):
        with patch('random.choice') as mock_choice:
            mock_choice.side_effect = ["| Page 1\n", "Normal text\n"]
            
            result = crossout.get_random_line_from_extract("dummy_path.txt")
            assert result == "Normal text\n"

def test_get_random_extract_only_one_file():
    """Test when folder has only one file."""
    with patch('os.listdir') as mock_listdir:
        with patch('os.path.dirname') as mock_dirname:
            mock_dirname.return_value = "/test/folder"
            mock_listdir.return_value = ["file1.txt"]
            
            result = crossout.get_random_extract("/test/folder/file1.txt")
            assert result == os.path.join("/test/folder", "file1.txt")

def test_generate_riddle_single_extra_line():
    """Test generating riddle with one extra line."""
    page = "Line 1\nLine 2"
    extract_path = "/test/file.txt"
    
    with patch('crossout.check_if_allowed', return_value=1):
        with patch('random.randint', return_value=1):  
            with patch('crossout.get_random_extract') as mock_get_extract:
                with patch('crossout.get_random_line_from_extract') as mock_get_line:
                    with patch('crossout.put_extra_line') as mock_put:
                        mock_get_extract.return_value = "/test/other.txt"
                        mock_get_line.return_value = "Extra line\n"
                        mock_put.return_value = "Line 1\nLine 2\nEXTRA"
                        
                        result = crossout.generate_riddle(page, extract_path)
                        
                        assert mock_get_extract.called
                        assert mock_get_line.called
                        assert mock_put.called

def test_generate_riddle_multiple_extra_lines():
    """Test generating riddle with multiple extra lines."""
    page = "Line 1\nLine 2"
    extract_path = "/test/file.txt"
    
    with patch('crossout.check_if_allowed', return_value=1):
        with patch('random.randint', return_value=3):  
            with patch('crossout.get_random_extract') as mock_get_extract:
                with patch('crossout.get_random_line_from_extract') as mock_get_line:
                    with patch('crossout.put_extra_line') as mock_put:
                        mock_get_extract.return_value = "/test/other.txt"
                        mock_get_line.return_value = "Extra line\n"
                        mock_put.side_effect = ["Page1", "Page2", 3]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])