# file_name represents the node passed from tree_processor.py 
from anytree import Node

def getFileType(node: Node) -> str:
    if _isCode(node):
        return "code"
    elif _isText(node):
        return "text"
    else:
        return "other"

def _getExtension(node: Node) -> str:
    return node.extension.lower() if node.extension else ''

def _isCode(node: Node) -> bool:
    code_extensions = ['.py', '.java', '.cpp', '.js', '.rb', '.go', '.cs', '.c', '.h', '.php', '.html', '.css', '.htm']
    return _getExtension(node) in code_extensions

def _isText(node: Node) -> bool:
    text_extensions = ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx']
    return _getExtension(node) in text_extensions