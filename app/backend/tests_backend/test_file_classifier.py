import pytest
from file_classifier import getFileType, _getExtension, _isCode, _isText
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
        assert _isCode(".py") == True
        assert _isCode(".html") == True
        assert _isCode(".cpp") == True
        
    def test_isCode_edge_cases(self):
        node = MockNode("script.JAVA", ".JAVA")
        ext = _getExtension(node)
        assert _isCode(ext) == True # Case insensitivity
        assert _isCode(".h") == True
        assert _isCode(".txt") == False
        assert _isCode(".py") == True

    def test_isText_function(self):
        assert _isText(".md") == True
        assert _isText(".txt") == True
        assert _isText(".rtf") == True
        assert _isText(".pdf") == True
        assert _isText(".doc") == True

    def test_isText_edge_cases(self):
        node1 = MockNode("notes.TXT", ".TXT")
        ext1 = _getExtension(node1)
        assert _isText(ext1) == True # Case insensitivity
        node2 = MockNode("document.PDF", ".PDF")
        ext2 = _getExtension(node2)
        assert _isText(ext2) == True # Case insensitivity
        assert _isText(".docx") == True
        assert _isText(".py") == False
    
    def test_empty_extension_handling(self):
        node = MockNode("noextension", "")
        ext = _getExtension(node)
        assert getFileType(node) == "other"
        assert _isCode(ext) is False
        assert _isText(ext) is False

    def test_no_extension_handling(self):
        node = MockNode("filewithnoext")
        ext = _getExtension(node)
        assert getFileType(node) == "other"
        assert _isCode(ext) is False
        assert _isText(ext) is False

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])