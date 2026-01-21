from anytree import Node, PreOrderIter
import pygments.util
import pygments.lexers
from typing import Tuple, List

class FileClassifier:
    def __init__(self) -> None:
        self.text_files: List[Node] = []
        self.code_files: List[Node] = []

    def classify_files(self, unprocessed_tree: Node, binary_data: List[bytes]) -> Node:
        '''
        Takes an unprocessed file tree and traverses it to classify files into text and code categories.
        Takes binary_data list to set binary data to None for detached nodes.
        '''
        if unprocessed_tree is None:
            raise ValueError("Unprocessed tree cannot be None")

        if not isinstance(unprocessed_tree, Node):
            raise TypeError(f"Expected Node object, got {type(unprocessed_tree).__name__}")

        # clear previous data
        self.text_files.clear()
        self.code_files.clear()

        # classify text files first, then code files to prevent pygments from misclassifying text files as code
        self.text_files, remaining_tree = self._filter_tree(unprocessed_tree, "text", binary_data)
        self.code_files, remaining_tree = self._filter_tree(remaining_tree, "code", binary_data)

        return self.text_files, self.code_files, binary_data


    def _filter_tree(self, root: Node, mode: str, binary_data: List[bytes]) -> Tuple[List[Node], Node]:
        """
        Classify and filter the tree nodes based on the mode ('text' or 'code')
        """
        classified_files: List[Node] = []

        for node in PreOrderIter(root):
            try:
                # skip non-file nodes
                if not hasattr(node, "type") or node.type != "file":
                    continue

                # skip all files inside .git directories
                if ".git" in [ancestor.name for ancestor in node.ancestors]:
                    node.classification = "git"
                    continue
                    
                is_text = self._is_text(node)
                is_code = self._is_code(node)

                # classify node as text or code and add to respective list
                if mode == "text" and is_text:
                    node.classification = "text"
                    classified_files.append(node)
                    # detach from tree
                    if node.parent:
                        node.parent = None
                elif mode == "code" and is_code:
                    node.classification = "code"
                    classified_files.append(node)
                    # detach from tree
                    if node.parent:
                        node.parent = None
                else:
                    # detach from tree if it doesn't match either category
                    if not is_text and not is_code:
                        self._detach_node(node, binary_data)
                name = getattr(node, "name", "unnamed")
                classification = getattr(node, "classification", "unclassified")
                print(f"{name} classified as {classification}")
            except Exception as e:
                print(f"An error occurred while classifying node {node.name}: {e}")
                continue

        return classified_files, root

    def _is_text(self, node: Node) -> bool:
        """Check if the node is a text file"""
        ext = self._getExtension(node)
        text_extensions: set[str] = {'.txt', '.md', '.rtf', '.pdf', '.doc', '.docx'}
        return ext in text_extensions

    def _is_code(self, node: Node) -> bool:
        """Check if the node is a code file using Pygments"""
        try:
            filename: str = node.name
            pygments.lexers.get_lexer_for_filename(filename)
            return True
        except pygments.util.ClassNotFound:
            return False

    def _getExtension(self, node: Node) -> str:
        """Get file extension from node"""
        try: 
            ext: str = node.extension
            return ext.lower() if isinstance(ext, str) else ''
        except AttributeError:
            print("Node does not have 'extension' attribute")
            return ''
        except Exception as e:
            print(f"An error occurred in _getExtension: {e}")
            return ''

    def _detach_node(self, node: Node, binary_data: List[bytes]) -> None:
        """Detach node from its parent and set binary data to None"""
        if node.parent:
            node.parent = None
        if binary_data and hasattr(node, "binary_data_index"):
            index = node.binary_data_index
            if 0 <= index < len(binary_data):
                binary_data[index] = None
        

