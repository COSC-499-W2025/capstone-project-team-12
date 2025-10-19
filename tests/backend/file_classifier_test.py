import pytest
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','app','backend'))
sys.path.insert(0, backend_path)  # Go up to reach backend folder
from file_classifier import getFileType, isCode, isText

class TestFileClassifier:

    def test_getFileType_function(self):
        # Code files returns "code" label
        assert getFileType("script.py") == "code"
        assert getFileType("program.cs") == "code"
        assert getFileType("index.html") == "code"
        # Text files returns "text" label
        assert getFileType("readme.txt") == "text"
        assert getFileType("notes.docx") == "text"
        # Zip files returns "zipped" label
        assert getFileType("archive.zip") == "zipped"
        # Non-conforming files returns "other" label
        assert getFileType("data.json") == "other"
        assert getFileType("notes.tex") == "other"
        assert getFileType("data.csv") == "other"

    def test_getFileType_edge_cases(self):
        assert getFileType("SCRIPT.JS") == "code"  # Case insensitivity
        assert getFileType("readme.MD") == "text"
        assert getFileType("compressed.ZIP") == "zipped"
        assert getFileType("unknownfile.xyz") == "other"
        assert getFileType("noextension") == "other"
    
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