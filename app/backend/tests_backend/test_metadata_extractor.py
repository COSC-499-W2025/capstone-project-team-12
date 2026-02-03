import pytest
from anytree import Node
import tempfile
import os
from metadata_extractor import MetadataExtractor
from pypdf import PdfWriter
from docx import Document

class TestMetadataExtractor:
    def setup_method(self):
        self.metadata_extractor = MetadataExtractor()

    def create_test_node(self, name: str, filepath: str, extension: str, size_bytes: int, binary_index: int = None) -> Node:
        """Helper to create test file nodes with required attributes"""
        node = Node(
            name,
            type="file",
            file_data={
                'filepath': filepath,
                'extension': extension,
                'size_bytes': size_bytes,
                'binary_index': binary_index
            }
        )
        return node

    def test_extract_all_metadata_empty_tree(self):
        """Test extraction with empty tree"""
        result = self.metadata_extractor.extract_all_metadata([])
        
        assert result == {}
        assert self.metadata_extractor.metadata_store == {}
    
    def test_extract_all_metadata_with_files(self):
        """Test metadata extraction for multiple files"""
        # create test files on disk
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f1:
            f1.write("print('hello world')\n# This is a comment")
            test_file1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("This is a text file\nwith multiple lines\nand some words")
            test_file2 = f2.name
        
        try:
            # create list of file nodes
            file_nodes = [self.create_test_node("test_script.py", test_file1, ".py", os.path.getsize(test_file1)),
                          self.create_test_node("document.txt", test_file2, ".txt", os.path.getsize(test_file2))]

            # extract metadata
            result = self.metadata_extractor.extract_all_metadata(file_nodes)
            
            # verify results
            assert len(result) == 2
            assert test_file1 in result
            assert test_file2 in result
            
            # check basic metadata fields
            py_metadata = result[test_file1]
            assert py_metadata['filename'] == "test_script.py"
            assert py_metadata['file_extension'] == ".py"
            assert py_metadata['file_size'] > 0
            assert py_metadata['filepath'] == test_file1
            
            # check content metrics
            assert py_metadata['line_count'] == 2
            assert py_metadata['word_count'] > 0
            assert py_metadata['character_count'] > 0
            
        finally:
            # cleanup
            os.unlink(test_file1)
            os.unlink(test_file2)

    def test_extract_metadata_from_binary_data(self):
        """Test metadata extraction using binary data for zipped files"""
        test_content = b"First line\nSecond line\nThird line"
        binary_data_array = [test_content]
        
        
        file_node = [self.create_test_node("zipped_file.txt",
            "/tmp/nonexistent/zipped_file.txt",  # file doesn't exist on disk
            ".txt", len(test_content),
            binary_index=0  # points to our test content in binary_data_array
        )]
        
        # extract metadata using binary data
        result = self.metadata_extractor.extract_all_metadata(file_node, binary_data_array)

        # verify binary data was used
        metadata = result["/tmp/nonexistent/zipped_file.txt"]
        assert metadata['creation_date'] == 'unknown_date'
        assert metadata['last_modified_date'] == 'unknown_date'
        assert metadata['line_count'] == 3
        assert metadata['word_count'] == 6  # "First", "line", "Second", "Third" - "line" appears once?
        assert metadata['character_count'] == len("First line\nSecond line\nThird line")
        assert metadata['checksum'] != 'unknown_checksum'

    def test_extract_metadata_fallback(self):
        """Test fallback metadata when no file and no binary data"""
        
        file_node = [self.create_test_node("missing_file.txt",
            "/nonexistent/path/missing_file.txt",  # doesn't exist
            ".txt", 0, binary_index=999  # invalid index
        )]
        result = self.metadata_extractor.extract_all_metadata(file_node, [])

        metadata = result["/nonexistent/path/missing_file.txt"]
        assert metadata['creation_date'] == 'unknown_date'
        assert metadata['last_modified_date'] == 'unknown_date'
        assert metadata['checksum'] == 'unknown_checksum'
        assert metadata['line_count'] == 0
        assert metadata['word_count'] == 0
        assert metadata['character_count'] == 0
        assert metadata['encoding'] == 'unknown'

    def test_node_without_file_data(self):
        """Test handling of nodes without file_data attribute"""
        bad_node = Node("bad_file.txt", filepath="/test/path/bad_file.txt", type="file")  # no file_data
        
        with pytest.raises(ValueError, match=r"has no file_data"):
            self.metadata_extractor._extract_single_file_metadata(bad_node)

    def test_content_metrics_calculation(self):
        """Test accurate calculation of line count, word count, character count"""
        test_content = "Hello world!\nThis is a test.\nThird line here."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("test_content.txt", test_file, ".txt", len(test_content))]
            
            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            assert metadata['line_count'] == 3
            assert metadata['word_count'] == 9  # Hello, world, This, is, a, test, Third, line, here
            assert metadata['character_count'] == len(test_content)
            
        finally:
            os.unlink(test_file)

    def test_checksum_calculation(self):
        """Test MD5 checksum calculation"""
        test_content = "Consistent content for checksum"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("checksum_test.txt", test_file, ".txt", len(test_content))]
            
            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            # checksum should be a valid MD5 hash
            assert metadata['checksum'] != 'unknown_checksum'
            assert len(metadata['checksum']) == 32  # MD5 hash length
            assert all(c in '0123456789abcdef' for c in metadata['checksum'])
            
        finally:
            os.unlink(test_file)

    def test_encoding_detection(self):
        """Test encoding detection and fallback"""
        test_content = "Normal ASCII text"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("encoding_test.txt", test_file, ".txt", len(test_content))]

            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            assert metadata['encoding'] == 'UTF-8'
            
        finally:
            os.unlink(test_file)

    def test_mime_type_detection(self):
        """Test MIME type detection for different file extensions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('test')")
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("mime_test.py", test_file, ".py", os.path.getsize(test_file))]
            
            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            # should detect Python MIME type
            assert 'text/x-python' in metadata['mime_type'] or 'application/octet-stream' == metadata['mime_type']
            
        finally:
            os.unlink(test_file)
    
    def test_author_extraction(self):
        """Test author metadata extraction for PDF and DOCX files"""

        # Create a test pdf file with author metadata
        pdf_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata({'/Author': 'Test Author'})
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        # Create a test docx file with author metadata
        docx_path = tempfile.NamedTemporaryFile(suffix='.docx', delete=False).name
        doc = Document()
        doc.core_properties.author = 'Docx Author'
        doc.add_paragraph("Sample content")
        doc.save(docx_path)
        
        try:
            pdf_node = self.create_test_node("test_pdf.pdf", pdf_path, ".pdf", os.path.getsize(pdf_path))
            docx_node = self.create_test_node("test_docx.docx", docx_path, ".docx", os.path.getsize(docx_path))
            file_nodes = [pdf_node, docx_node]
            
            result = self.metadata_extractor.extract_all_metadata(file_nodes)
            
            pdf_metadata = result[pdf_path]
            assert pdf_metadata['author'] == 'Test Author'
            
            docx_metadata = result[docx_path]
            assert docx_metadata['author'] == 'Docx Author'
            
        finally:
            os.unlink(pdf_path)
            os.unlink(docx_path)

    def test_get_metadata_by_filepath(self):
        """Test retrieving metadata for specific filename"""
        # setup  test metadata
        test_metadata = {
            'filename': 'test.py',
            'filepath': '/path/test.py',
            'file_size': 100
        }
        self.metadata_extractor.metadata_store = {'/path/test.py': test_metadata}
        
        result = self.metadata_extractor.get_metadata_by_filepath('/path/test.py')
        assert result == test_metadata
        
        # test non-existent file
        result = self.metadata_extractor.get_metadata_by_filepath('/path/nonexistent.py')
        assert result is None

    def test_get_all_metadata(self):
        """Test retrieving all metadata"""
        test_data = {
            '/path/file1.py': {'filename': 'file1.py', 'size': 100},
            '/path/file2.txt': {'filename': 'file2.txt', 'size': 200}
        }
        self.metadata_extractor.metadata_store = test_data
        
        result = self.metadata_extractor.get_all_metadata()
        assert result == test_data
        
        # verify it returns a copy, not the original
        assert result is not self.metadata_extractor.metadata_store
        result['/path/new_file.py'] = {'filename': 'new_file.py'}  # should not affect internal store
        assert '/path/new_file.py' not in self.metadata_extractor.metadata_store

    def test_empty_file_handling(self):
        """Test metadata extraction for empty files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # create empty file
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("empty.txt", test_file, ".txt", 0)]

            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            assert metadata['line_count'] == 0
            assert metadata['word_count'] == 0
            assert metadata['character_count'] == 0
            assert metadata['file_size'] == 0
            
        finally:
            os.unlink(test_file)

    def test_special_characters_in_content(self):
        """Test files with special characters and encoding edge cases"""
        test_content = "Line with émojis 🚀 and ümlauts\nAnd symbols: ©® and hế lô ngưỡng ổ ộ™"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            file_node = [self.create_test_node("special_chars.txt", test_file, ".txt", len(test_content.encode('utf-8')))]

            result = self.metadata_extractor.extract_all_metadata(file_node)
            metadata = result[test_file]
            
            # should handle special characters without crashing
            assert metadata['line_count'] == 2
            assert metadata['character_count'] > 0
            
        finally:
            os.unlink(test_file)

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])