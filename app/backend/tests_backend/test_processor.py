import pytest
from anytree import Node, PreOrderIter
from tree_processor import TreeProcessor

class TestTreeProcessor:
    """Tests for tree processor functionality"""
    
    def setup_method(self):
        """Create a fresh test tree before each test"""
        # Simple project structure with all required attributes
        self.root = Node(
            "project", 
            type="directory", 
            path="/project",
            classification=None,
            is_repo_head=False
        )
        self.git = Node(
            ".git", 
            type="directory", 
            path="/project/.git",
            classification=None,
            is_repo_head=False,
            parent=self.root
        )
        self.src = Node(
            "src", 
            type="directory", 
            path="/project/src",
            classification=None,
            is_repo_head=False,
            parent=self.root
        )
        self.app_js = Node(
            "app.js", 
            type="file", 
            path="/project/src/app.js",
            classification=None,
            is_repo_head=False,
            parent=self.src,
            extension='.js'
        )
        self.readme = Node(
            "README.md", 
            type="file", 
            path="/project/README.md",
            classification=None,
            is_repo_head=False,
            parent=self.root,
            extension ='.md'
        )
        self.config = Node(
            "config.json",
            type="file",
            path="/project/config.json",
            classification=None,
            is_repo_head=False,
            parent=self.root,
            extension='.json'
        )
    
    def test_files_get_classified(self):
        """Test that files receive classification attribute"""
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        # Check that app.js has classification
        for node in PreOrderIter(result):
            if node.name == "app.js":
                assert hasattr(node, 'classification'), "app.js should have classification"
                assert node.classification is not None, "app.js classification shouldn't be None"
                print(f"✓ app.js classification: {node.classification}")
    
    def test_git_marks_parent_as_repo(self):
        """Test that .git marks parent directory as repo head"""
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        assert hasattr(result, 'is_repo_head'), "Root should have is_repo_head attribute"
        assert result.is_repo_head == True, "Root should be marked as repo head"
        print(f"✓ Root is marked as repo head: {result.is_repo_head}")
    
    def test_directories_not_classified_as_files(self):
        """Test that directories keep None classification"""
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            if node.name == "src":
                assert node.classification is None, "Directories should have None classification"
                print(f"✓ src directory classification: {node.classification}")
    
    def test_all_files_get_classification(self):
        """Test that every file gets classified"""
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            # Check files by type attribute
            if hasattr(node, 'type') and node.type == "file":
                assert hasattr(node, 'classification'), f"{node.name} should have classification"
                assert node.classification is not None, f"{node.name} should be classified"
                print(f"✓ {node.name} has classification: {node.classification}")
    
    def test_non_repo_directories_marked_false(self):
        """Test that directories without .git get is_repo_head = False"""
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            if node.name == "src":
                assert hasattr(node, 'is_repo_head'), "All dirs should have is_repo_head"
                assert node.is_repo_head == False, "src should NOT be repo head"
                print(f"✓ src is_repo_head: {node.is_repo_head}")
    
    def test_nested_git_repos(self):
        """Test handling of nested git repositories"""
        # Add nested repo
        subproject = Node(
            "subproject", 
            type="directory",
            path="/project/src/subproject",
            classification=None,
            is_repo_head=False,
            parent=self.src
        )
        Node(
            ".git", 
            type="directory",
            path="/project/src/subproject/.git",
            classification=None,
            is_repo_head=False,
            parent=subproject
        )
        
        processor = TreeProcessor()
        result = processor.process_file_tree(self.root)
        
        # Both root and subproject should be marked as repo heads
        assert self.root.is_repo_head == True, "Root should be repo head"
        assert subproject.is_repo_head == True, "Subproject should be repo head"
        print(f"✓ Root repo head: {self.root.is_repo_head}")
        print(f"✓ Subproject repo head: {subproject.is_repo_head}")
    
    def test_git_without_parent(self):
        """Test .git at root level (no parent to mark)"""
        git_root = Node(
            ".git", 
            type="directory",
            path="/.git",
            classification=None,
            is_repo_head=False
        )
        processor = TreeProcessor()
        result = processor.process_file_tree(git_root)
        
        # Should not crash, just shouldn't mark anything
        assert result is not None, "Should handle .git at root"
        print(f"✓ .git at root handled without crash")

    def test_drop_invalid_node(self):
        """Test that invalid file is dropped from tree"""
        # Create an invalid file node
        invalid_file = Node(
            "invalid.png",
            type="file",
            path="/project/src/invalid.png",
            classification=None,
            is_repo_head=False,
            parent=self.src
        )
        assert invalid_file.parent == self.src
        assert invalid_file in self.src.children

        # Drop the node
        processor = TreeProcessor()
        processor._drop_invalid_node(invalid_file)
        
        # Verify it's removed
        assert invalid_file.parent is None
        assert invalid_file not in self.src.children

    def test_drop_invalid_node_no_parent(self):
        """test that dropping a node with no parent does not raise error"""
        # Create orphan node (no parent)
        orphan_node = Node("orphan_file", type="file")
        assert orphan_node.parent is None
        
        # Try to drop it (should not crash)
        processor = TreeProcessor()
        processor._drop_invalid_node(orphan_node)
        
        
        assert orphan_node.parent is None # Still no parent

class TestTreeProcessorErrorHandling:
    """Tests for error handling in tree_processor.py"""

    def test_none_root_raises_error(self):
        """Tests that passing None as root raises error"""
        processor = TreeProcessor()
        with pytest.raises(ValueError, match = "Root node cannot be None"):
            processor.process_file_tree(None)


    def test_invalid_root_type_raises_error(self):
        """Tests that passing an non object arigument raises typeError"""
        processor = TreeProcessor()
        with pytest.raises(TypeError, match = "Expected Node object"):
            processor.process_file_tree("WAAAAAA")
        with pytest.raises(TypeError, match = "Expected Node object"):
            processor.process_file_tree(2412412414241241)
        with pytest.raises(TypeError, match = "Expected Node object"):
            processor.process_file_tree([])
        with pytest.raises(TypeError, match = "Expected Node object"):
            processor.process_file_tree({'Key': 'valeu'})

    def test_multiple_bad_nodes_keep_processing(self):
        """tests that problematic nodes wont stop the tree from being processed"""
        
        #create mock tree for test
        root = Node(
            "root",
            type="directory",
            path="/root",
            classification=None,
            is_repo_head=False
        )
        Node(".git", type="directory", path="/root/.git",
             classification=None, is_repo_head=False, parent=root)
        #good file
        Node("file1.js", type="file", path="/root/file1.js",
             classification=None, is_repo_head=False, parent=root, extension='.js')
        #bad file
        Node("bad.txt", type="file", path="/root/bad.txt",
             classification=None, is_repo_head=False, parent=root)
        #good file
        Node("file2.py", type="file", path="/root/file2.py",
             classification=None, is_repo_head=False, parent=root, extension='.py')
        processor = TreeProcessor()
        result = processor.process_file_tree(root)
        
        assert len(processor.get_code_files()) >= 2
        assert len(processor.get_git_repos()) >= 1

        


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])