import pytest
from anytree import Node, PreOrderIter
from repo_detector import RepoDetector

@pytest.fixture
def repo_detector():
    return RepoDetector()

@pytest.fixture
def git_tree():
    """
    Create a file tree with 2 git repositories
    """
    root = Node(
        "project", 
        type="directory", 
        path="/project",
        classification=None,
        is_repo_head=False
    )
    git1 = Node(".git", 
        type="directory", 
        path="/project/.git",
        classification=None,
        is_repo_head=False,
        parent=root
    )
    src = Node("src", 
        type="directory", 
        path="/project/src",
        classification=None,
        is_repo_head=False,
        parent=root
    )
    git2 = Node(".git", 
        type="directory", 
        path="/project/src/.git",
        classification=None,
        is_repo_head=False,
        parent=src
    )
    return root

@pytest.fixture
def nested_git_tree():
    """Create a tree with nested git repositories"""
    root = Node(
        "root", 
        type="directory", 
        path="/root",
        classification=None,
        is_repo_head=False
    )
    outer_git = Node(".git", 
        type="directory", 
        path="/root/.git",
        classification=None,
        is_repo_head=False,
        parent=root
    )
    inner = Node("inner", 
        type="directory", 
        path="/root/inner",
        classification=None,
        is_repo_head=False,
        parent=root
    )
    inner_git = Node(".git", 
        type="directory", 
        path="/root/inner/.git",
        classification=None,
        is_repo_head=False,
        parent=inner
    )
    inner_inner = Node("inner_inner", 
        type="directory", 
        path="/root/inner/inner_inner",
        classification=None,
        is_repo_head=False,
        parent=inner
    )
    inner_inner_git = Node(".git", 
        type="directory", 
        path="/root/inner/inner_inner/.git",
        classification=None,
        is_repo_head=False,
        parent=inner_inner
    )

    return root

@pytest.fixture
def tree_with_no_git():
    """Create a tree with no git repo"""
    root = Node(
        "project", 
        type="directory", 
        path="/project",
        classification=None,
        is_repo_head=False
    )
    docs = Node("docs", 
        type="directory", 
        path="/project/docs",
        classification=None,
        is_repo_head=False,
        parent=root
    )
    readme = Node("readme.md", 
        type="file", 
        path="/project/docs/readme.md",
        classification=None,
        is_repo_head=False,
        parent=docs,
        extension='.md',
        binary_data_index=1
    )
    return root

def test_process_git_repos(repo_detector, git_tree):
    """Test process_git_repos with simple git_tree"""
    repo_detector.process_git_repos(git_tree)
    git_repos = repo_detector.get_git_repos()

    assert len(git_repos) == 2
    assert git_tree in git_repos # verify git repo detected and returned
    assert git_tree.is_repo_head == True

def test_process_nested_git_repos(repo_detector, nested_git_tree):
    """Test process_git_repos with nested git repositories"""
    repo_detector.process_git_repos(nested_git_tree)
    git_repos = repo_detector.get_git_repos()

    assert len(git_repos) == 3
    assert nested_git_tree in git_repos
    
    # verify all 3 git repos detected
    repo_names = {repo.name for repo in git_repos}
    assert "root" in repo_names
    assert "inner" in repo_names
    assert "inner_inner" in repo_names

    # verify is_repo_head is set correctly
    for node in PreOrderIter(nested_git_tree):
        if node.name in ["root", "inner", "inner_inner"]:
            assert node.is_repo_head == True
        elif node.type == "directory":
            assert not hasattr(node, 'is_repo_head') or node.is_repo_head == False

def test_process_git_repos_no_git(repo_detector, tree_with_no_git):
    """Test process_git_repos with tree that has no git repos"""
    repo_detector.process_git_repos(tree_with_no_git)
    git_repos = repo_detector.get_git_repos()

    assert len(git_repos) == 0

def test_process_git_repos_with_none_root(repo_detector):
    """Test process_git_repos raises ValueError with None root"""
    with pytest.raises(ValueError, match="Root node cannot be None"):
        repo_detector.process_git_repos(None)

def test_process_git_repos_with_invalid_root(repo_detector):
    """Test process_git_repos raises TypeError with invalid root type"""
    with pytest.raises(TypeError, match="Expected Node object, got str"):
        repo_detector.process_git_repos("not_a_node")

def test_process_git_repos_empty_tree(repo_detector):
    """Test with single node tree (just one file))"""
    root = Node("empty.txt", type="file")
    
    repo_detector.process_git_repos(root)
    git_repos = repo_detector.get_git_repos()
    
    assert len(git_repos) == 0

def test_get_git_repos_returns_list(repo_detector, git_tree):
    """Test that get_git_repos returns a list"""
    repo_detector.process_git_repos(git_tree)
    git_repos = repo_detector.get_git_repos()
    
    assert all(isinstance(node, Node) for node in git_repos)
    assert isinstance(git_repos, list)
    assert len(git_repos) == 2
    assert git_tree in git_repos



if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])