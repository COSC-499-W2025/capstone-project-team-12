import pytest
from anytree import Node, PreOrderIter
# Import your tree_processor function
# Adjust the import path based on where your file is
import sys
sys.path.insert(0, '../../app/backend')  # Go up to reach backend folder
from tree_processor import process_file_tree


class TestTreeProcessor:
    """Tests for tree processor functionality"""
    
    def setup_method(self):
        """Create a fresh test tree before each test"""
        # Simple project structure
        self.root = Node("project")
        self.git = Node(".git", parent=self.root)
        self.src = Node("src", parent=self.root)
        self.app_js = Node("app.js", parent=self.src)
        self.readme = Node("README.md", parent=self.root)
    
    def test_files_get_classified(self):
        """Test that files receive classification attribute"""
        result = process_file_tree(self.root)
        
        # Check that app.js has classification
        for node in PreOrderIter(result):
            if node.name == "app.js":
                assert hasattr(node, 'classification'), "app.js should have classification"
                assert node.classification is not None, "app.js classification shouldn't be None"
                print(f"✓ app.js classification: {node.classification}")
    
    def test_git_marks_parent_as_repo(self):
        """Test that .git marks parent directory as repo head"""
        result = process_file_tree(self.root)
        
        assert hasattr(result, 'is_repo_head'), "Root should have is_repo_head attribute"
        assert result.is_repo_head == True, "Root should be marked as repo head"
        print(f"✓ Root is marked as repo head: {result.is_repo_head}")
    
    def test_directories_not_classified_as_files(self):
        """Test that directories get None classification"""
        result = process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            if node.name == "src":
                assert node.classification is None, "Directories should have None classification"
                print(f"✓ src directory classification: {node.classification}")
    
    def test_all_files_get_classification(self):
        """Test that every file (leaf node) gets classified"""
        result = process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            # If it's a file (no children), it should have classification
            if len(node.children) == 0:
                assert hasattr(node, 'classification'), f"{node.name} should have classification"
                print(f"✓ {node.name} has classification: {node.classification}")
    
    def test_non_repo_directories_marked_false(self):
        """Test that directories without .git get is_repo_head = False"""
        result = process_file_tree(self.root)
        
        for node in PreOrderIter(result):
            if node.name == "src":
                assert hasattr(node, 'is_repo_head'), "All dirs should have is_repo_head"
                assert node.is_repo_head == False, "src should NOT be repo head"
                print(f"✓ src is_repo_head: {node.is_repo_head}")
    
    def test_nested_git_repos(self):
        """Test handling of nested git repositories"""
        # Add nested repo
        subproject = Node("subproject", parent=self.src)
        Node(".git", parent=subproject)
        
        result = process_file_tree(self.root)
        
        # Both root and subproject should be marked as repo heads
        assert self.root.is_repo_head == True, "Root should be repo head"
        assert subproject.is_repo_head == True, "Subproject should be repo head"
        print(f"✓ Root repo head: {self.root.is_repo_head}")
        print(f"✓ Subproject repo head: {subproject.is_repo_head}")
    
    def test_git_without_parent(self):
        """Test .git at root level (no parent to mark)"""
        git_root = Node(".git")
        result = process_file_tree(git_root)
        
        # Should not crash, just shouldn't mark anything
        assert result is not None, "Should handle .git at root"
        print(f"✓ .git at root handled without crash")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])