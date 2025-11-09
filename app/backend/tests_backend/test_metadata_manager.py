import pytest
from anytree import Node
import tempfile
import os
from metadata_manager import MetadataManager

class TestMetadataManager:
    def setup_method(self):
        self.metadata_manager = MetadataManager()

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

    def create_test_tree(self) -> Node:
        """Create a test file tree structure"""
        root = Node("root", type="directory")
        
        # Create test files
        file1 = self.create_test_node(
            "test.py", 
            "/fake/path/test.py", 
            ".py", 
            100
        )
        file1.parent = root
        
        file2 = self.create_test_node(
            "document.txt", 
            "/fake/path/document.txt", 
            ".txt", 
            200
        )
        file2.parent = root
        
        return root

    def test_extract_all_metadata_empty_tree(self):
        """Test extraction with empty tree"""
        empty_root = Node("empty", type="directory")
        result = self.metadata_manager.extract_all_metadata(empty_root)
        
        assert result == {}
        assert self.metadata_manager.metadata_store == {}
    
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
            # create test tree with real files
            root = Node("root", type="directory")
            
            file1 = self.create_test_node(
                "test_script.py",
                test_file1,
                ".py",
                os.path.getsize(test_file1)
            )
            file1.parent = root
            
            file2 = self.create_test_node(
                "document.txt", 
                test_file2,
                ".txt", 
                os.path.getsize(test_file2)
            )
            file2.parent = root
            
            # extract metadata
            result = self.metadata_manager.extract_all_metadata(root)
            
            # verify results
            assert len(result) == 2
            assert "test_script.py" in result
            assert "document.txt" in result
            
            # check basic metadata fields
            py_metadata = result["test_script.py"]
            assert py_metadata['filename'] == "test_script.py"
            assert py_metadata['file_extension'] == ".py"
            assert py_metadata['file_size'] > 0
            assert py_metadata['filepath'] == test_file1
            
            # check content metrics
            assert py_metadata['line_count'] == 2
            assert py_metadata['word_count'] > 0
            assert py_metadata['character_count'] > 0
            assert py_metadata['author'] == 'unknown_author'
            
        finally:
            # cleanup
            os.unlink(test_file1)
            os.unlink(test_file2)

    def test_extract_metadata_from_binary_data(self):
        """Test metadata extraction using binary data for zipped files"""
        test_content = b"First line\nSecond line\nThird line"
        binary_data_array = [test_content]
        
        root = Node("root", type="directory")
        
        file_node = self.create_test_node(
            "zipped_file.txt",
            "/tmp/nonexistent/zipped_file.txt",  # file doesn't exist on disk
            ".txt",
            len(test_content),
            binary_index=0  # points to our test content in binary_data_array
        )
        file_node.parent = root
        
        # extract metadata using binary data
        result = self.metadata_manager.extract_all_metadata(root, binary_data_array)
        
        # verify binary data was used
        metadata = result["zipped_file.txt"]
        assert metadata['creation_date'] == 'unknown_date'
        assert metadata['last_modified_date'] == 'unknown_date'
        assert metadata['line_count'] == 3
        assert metadata['word_count'] == 6  # "First", "line", "Second", "Third" - "line" appears once?
        assert metadata['character_count'] == len("First line\nSecond line\nThird line")
        assert metadata['checksum'] != 'unknown_checksum'

    def test_extract_metadata_fallback(self):
        """Test fallback metadata when no file and no binary data"""
        root = Node("root", type="directory")
        
        file_node = self.create_test_node(
            "missing_file.txt",
            "/nonexistent/path/missing_file.txt",  # doesn't exist
            ".txt",
            0,
            binary_index=999  # invalid index
        )
        file_node.parent = root
        
        result = self.metadata_manager.extract_all_metadata(root, [])
        
        metadata = result["missing_file.txt"]
        assert metadata['creation_date'] == 'unknown_date'
        assert metadata['last_modified_date'] == 'unknown_date'
        assert metadata['checksum'] == 'unknown_checksum'
        assert metadata['line_count'] == 0
        assert metadata['word_count'] == 0
        assert metadata['character_count'] == 0
        assert metadata['encoding'] == 'unknown'

    def test_node_without_file_data(self):
        """Test handling of nodes without file_data attribute"""
        root = Node("root", type="directory")
        
        bad_node = Node("bad_file.txt", type="file")  # no file_data
        bad_node.parent = root
        
        result = self.metadata_manager.extract_all_metadata(root)
        
        # should store error information
        assert "bad_file.txt" in result
        assert result["bad_file.txt"]['error'] == 'Metadata extraction failed'

    def test_content_metrics_calculation(self):
        """Test accurate calculation of line count, word count, character count"""
        test_content = "Hello world!\nThis is a test.\nThird line here."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "test_content.txt",
                test_file,
                ".txt",
                len(test_content)
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["test_content.txt"]
            
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
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "checksum_test.txt",
                test_file,
                ".txt",
                len(test_content)
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["checksum_test.txt"]
            
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
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "encoding_test.txt",
                test_file,
                ".txt",
                len(test_content)
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["encoding_test.txt"]
            
            assert metadata['encoding'] == 'UTF-8'
            
        finally:
            os.unlink(test_file)

    def test_mime_type_detection(self):
        """Test MIME type detection for different file extensions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('test')")
            test_file = f.name
        
        try:
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "mime_test.py",
                test_file,
                ".py",
                os.path.getsize(test_file)
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["mime_test.py"]
            
            # should detect Python MIME type
            assert 'text/x-python' in metadata['mime_type'] or 'application/octet-stream' == metadata['mime_type']
            
        finally:
            os.unlink(test_file)

    def test_get_metadata_by_filename(self):
        """Test retrieving metadata for specific filename"""
        # setup  test metadata
        test_metadata = {
            'filename': 'test.py',
            'filepath': '/path/test.py',
            'file_size': 100
        }
        self.metadata_manager.metadata_store = {'test.py': test_metadata}
        
        result = self.metadata_manager.get_metadata_by_filename('test.py')
        assert result == test_metadata
        
        # test non-existent file
        result = self.metadata_manager.get_metadata_by_filename('nonexistent.py')
        assert result is None

    def test_get_all_metadata(self):
        """Test retrieving all metadata"""
        test_data = {
            'file1.py': {'filename': 'file1.py', 'size': 100},
            'file2.txt': {'filename': 'file2.txt', 'size': 200}
        }
        self.metadata_manager.metadata_store = test_data
        
        result = self.metadata_manager.get_all_metadata()
        assert result == test_data
        
        # verify it returns a copy, not the original
        assert result is not self.metadata_manager.metadata_store
        result['new_file.py'] = {'filename': 'new_file.py'}  # should not affect internal store
        assert 'new_file.py' not in self.metadata_manager.metadata_store

    def test_empty_file_handling(self):
        """Test metadata extraction for empty files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # create empty file
            test_file = f.name
        
        try:
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "empty.txt",
                test_file,
                ".txt",
                0
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["empty.txt"]
            
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
            root = Node("root", type="directory")
            file_node = self.create_test_node(
                "special_chars.txt",
                test_file,
                ".txt",
                len(test_content.encode('utf-8'))
            )
            file_node.parent = root
            
            result = self.metadata_manager.extract_all_metadata(root)
            metadata = result["special_chars.txt"]
            
            # should handle special characters without crashing
            assert metadata['line_count'] == 2
            assert metadata['character_count'] > 0
            
        finally:
            os.unlink(test_file)

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])