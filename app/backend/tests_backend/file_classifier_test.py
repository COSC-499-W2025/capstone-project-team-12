import pytest
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)  # Go up to reach backend folder
from file_classifier import getFileType, _isCode, _isText

class MockNode:
    # A simple mock class to simulate file nodes from file manager
    def __init__(self, name, extension=''):
        self.name = name
        self.extension = extension

class TestFileClassifier:

    def test_getFileType_function(self):
        # Code files returns "code" label
        assert getFileType(MockNode("script.py", ".py")) == "code"
        assert getFileType(MockNode("program.cs", ".cs")) == "code"
        assert getFileType(MockNode("index.html", ".html")) == "code"
        # Text files returns "text" label
        assert getFileType(MockNode("readme.txt", ".txt")) == "text"
        assert getFileType(MockNode("notes.docx", ".docx")) == "text"
        # Non-conforming files returns "other" label
        assert getFileType(MockNode("data.json", ".json")) == "other"
        assert getFileType(MockNode("notes.tex", ".tex")) == "other"
        assert getFileType(MockNode("data.csv", ".csv")) == "other"

    def test_getFileType_edge_cases(self):
        assert getFileType(MockNode("SCRIPT.JS", ".JS")) == "code"  # Case insensitivity
        assert getFileType(MockNode("readme.MD", ".MD")) == "text"
        assert getFileType(MockNode("unknownfile.xyz", ".xyz")) == "other"
        assert getFileType(MockNode("noextension", "")) == "other"
    
    def test_isCode_function(self):
        assert _isCode(MockNode("script.py", ".py")) == True
        assert _isCode(MockNode("index.html", ".html")) == True
        assert _isCode(MockNode("program.cpp", ".cpp")) == True
        
    def test_isCode_edge_cases(self):
        assert _isCode(MockNode("script.JAVA", ".JAVA")) == True  # Case insensitivity
        assert _isCode(MockNode("header.h", ".h")) == True
        assert _isCode(MockNode("document.txt", ".txt")) == False
        assert _isCode(MockNode("config.test.py", ".py")) == True  
    
    def test_isText_function(self):
        assert _isText(MockNode("readme.md", ".md")) == True
        assert _isText(MockNode("notes.txt", ".txt")) == True
        assert _isText(MockNode("document.rtf", ".rtf")) == True
        assert _isText(MockNode("report.pdf", ".pdf")) == True
        assert _isText(MockNode("document.doc", ".doc")) == True

    def test_isText_edge_cases(self):
        assert _isText(MockNode("notes.TXT", ".TXT")) == True  # Case insensitivity
        assert _isText(MockNode("report.Pdf", ".PDF")) == True
        assert _isText(MockNode("archive.docx", ".docx")) == True
        assert _isText(MockNode("script.py", ".py")) == False

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])