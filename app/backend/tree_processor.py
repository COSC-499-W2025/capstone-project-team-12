from anytree import PreOrderIter, Node
from typing import List, Optional
from file_classifier import getFileType

class TreeProcessor:
    def __init__(self) -> None:
        self.text_files: List[Node] = []
        self.code_files: List[Node] = []
        self.git_repos: List[Node] = []

    def process_file_tree(self, root: Node) -> Node:
        #clear previous data
        self.text_files = []
        self.code_files = []
        self.git_repos = []
        
        for node in PreOrderIter(root):
            if node.name == ".git" and node.parent:
                node.parent.is_repo_head = True  # Update existing attribute
                self.git_repos.append(node.parent)  # Store the node, not the path
            
            # Classify files (update the existing classification attribute)
            if hasattr(node, 'type') and node.type == "file":
                classification: str = getFileType(node)
                if classification == "other": #drop if invalid file type
                    self._drop_invalid_node(node)
                    continue
                node.classification = classification
                
                # Add to appropriate array based on classification - store nodes
                if classification == "text":
                    self.text_files.append(node)
                elif classification == "code":
                    self.code_files.append(node)
            #note that directories keep their default classification=None from FileManager
        return root
    
    def _drop_invalid_node(self, node: Node) -> None:
        # detaching the node from the tree by removing its parent reference
        if node.parent:
            node.parent = None
        # TODO: drop the binary data once binary data list is implemented
        # set binarydata[index of node] = None

    def get_text_files(self) -> List[Node]:
        """Returns list of text file nodes"""
        return self.text_files

    def get_code_files(self) -> List[Node]:
        """Returns list of code file nodes"""
        return self.code_files
    
    def get_git_repos(self) -> List[Node]:
        """Returns list of git repository nodes"""
        return self.git_repos