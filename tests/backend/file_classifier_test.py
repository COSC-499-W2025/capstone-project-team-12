import pytest
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','app','backend'))
sys.path.insert(0, backend_path)  # Go up to reach backend folder
from file_classifier import getFileType, isCode, isText

class TestFileClassifier:
    
    def test_isCode_function(self):
        assert isCode("script.py") == True
        assert isCode("index.html") == True
        assert isCode("program.cpp") == True
        
    def test_isCode_edge_cases(self):
        assert isCode("script.JAVA") == True  # Case insensitivity
        assert isCode("header.h") == True
        assert isCode("document.txt") == False
        assert isCode("config.test.py") == True  
    
    def test_isText_function(self):
        assert isText("readme.md") == True
        assert isText("notes.txt") == True
        assert isText("document.rtf") == True
        assert isText("report.pdf") == True
        assert isText("document.doc") == True

    def test_isText_edge_cases(self):
        assert isText("notes.TXT") == True  # Case insensitivity
        assert isText("report.Pdf") == True
        assert isText("archive.docx") == True
        assert isText("script.py") == False

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])