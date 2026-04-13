import pytest
from unittest.mock import patch, mock_open
import os
import sys 
sys.path.append('.')
import crossout


@pytest.fixture
def mock_extract_content():
    return "Line 1\n| Page 1 |\nLine 2\n\n"

def test_load_line_pool_filters_metadata(mock_extract_content):
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_extract_content)):
            pool = crossout.load_line_pool("extracts/book/chapter.txt")
            assert pool == ["Line 1", "Line 2"]

def test_load_line_pool_returns_empty_on_missing_file():
    with patch("os.path.exists", return_value=False):
        pool = crossout.load_line_pool("fake/path.txt")
        assert pool == []

def test_get_lines_from_extract(mock_extract_content):
    with patch("builtins.open", mock_open(read_data=mock_extract_content)):
        lines = crossout.get_lines_from_extract("dummy.txt")
        assert lines == ["Line 1", "Line 2"]

def test_generate_riddle_behavior():
    with patch("crossout.load_line_pool") as mock_pool, \
         patch("crossout.get_lines_from_extract") as mock_ext:
        
        mock_pool.return_value = ["Fake Line A", "Fake Line B", "Story Line 1"]
        mock_ext.return_value = ["Story Line 1"]
        
        page_content = "Story Line 1"
        result = crossout.generate_riddle(page_content, "path")
        result_lines = result.split("\n")
        
        assert len(result_lines) == 3
        assert "Story Line 1" in result_lines
        assert "Fake Line A" in result_lines
        assert "Fake Line B" in result_lines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])