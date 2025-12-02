from anytree import PreOrderIter, Node
from typing import List, Optional
from file_classifier import getFileType

class TreeProcessor:
    def __init__(self) -> None:
        self.text_files: List[Node] = []
        self.code_files: List[Node] = []
        self.git_repos: List[Node] = []

    def process_file_tree(self, root: Node) -> Node:
        if root is None:
            raise ValueError("Root node cannot be None")
        
        if not isinstance(root, Node):
            raise TypeError(f"Expected Node object, got {type(root).__name__}")
        

        #clear previous data
        self.text_files = []
        self.code_files = []
        self.git_repos = []
        
        try:
            for node in PreOrderIter(root):
                try:
                    if node.name == ".git" and node.parent:
                        print(f"TREEPROCESSOR: Marking {node.parent.name} as repo_head", flush=True)
                        print(f"  .git node has {len(node.children)} children", flush=True)
                        node.parent.is_repo_head = True
                        self.git_repos.append(node.parent)
                    
                    # Classify files (update the existing classification attribute)
                    if hasattr(node, 'type') and node.type == "file":
                        try:
                            # SKIP CLASSIFICATION OF GIT FILES -> this takes place here to follow SRP
                            if '.git' in [ancestor.name for ancestor in node.ancestors]:
                                node.classification = "git"
                                continue

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
                        except AttributeError as e:
                            print(f"Node missing required attribute: {e}")
                            continue
                        except Exception as e:
                            print(f"Failed to classify file {node.name}: {e}")
                            continue
                    #note that directories keep their default classification=None from FileManager
                except Exception as e:
                    print(f"Error processing node {getattr(node, 'name', 'unknown')}: {e}")
                    continue
        except Exception as e:
            raise RuntimeError(f"Failed to process file tree: {e}")
        return root
    
    def _drop_invalid_node(self, node: Node) -> None:
        if node is None:
            print("No node to drop")
            return
        if not isinstance(node, Node):
            print(f"Expected Node object, got {type(node).__name__}")
            return
        try:
            # detaching the node from the tree by removing its parent reference
            if node.parent:
                node.parent = None
            # TODO: drop the binary data once binary data list is implemented
            # set binarydata[index of node] = None
        except Exception as e:
            print(f"Failed to drop node {getattr(node, 'name', 'unknown')}: {e}")

    def get_text_files(self) -> List[Node]:
        """Returns list of text file nodes"""
        return self.text_files

    def get_code_files(self) -> List[Node]:
        """Returns list of code file nodes"""
        return self.code_files
    
    def get_git_repos(self) -> List[Node]:
        """Returns list of git repository nodes"""
        return self.git_repos