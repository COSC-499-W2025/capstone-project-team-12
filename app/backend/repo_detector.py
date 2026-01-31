from anytree import PreOrderIter, Node
from typing import List, Optional

class RepoDetector:
    def __init__(self) -> None:
        self.git_repos: List[Node] = []

    def process_git_repos(self, root: Node) -> None:
        """
        Traverses the file tree to detect .git repositories
        """
        if root is None:
            raise ValueError("Root node cannot be None")
        
        if not isinstance(root, Node):
            raise TypeError(f"Expected Node object, got {type(root).__name__}")

        self.git_repos.clear()
        
        try:
            for node in PreOrderIter(root):
                if node.name == ".git" and node.parent:
                    node.parent.is_repo_head = True
                    self.git_repos.append(node.parent)
        except Exception as e:
            raise RuntimeError(f"Failed to process git repositories: {e}")


    def get_git_repos(self) -> List[Node]:
        """Returns list of git repository nodes"""
        return self.git_repos