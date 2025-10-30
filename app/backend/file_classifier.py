from anytree import Node

def getFileType(node: Node) -> str:
    """Returns file classification string based on file extension"""
    try:
        if not isinstance(node, Node):
            raise TypeError("Input must be a Node")
        
        ext: str = _getExtension(node)
        if not ext:
            return "other"

        if _isCode(ext):
            return "code"
        if _isText(ext):
            return "text"
        return "other"
    
    except Exception as e:
        print(f"An error occurred in getFileType: {e}")
        return "other"

def _getExtension(node: Node) -> str:
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
        

def _isCode(ext: str) -> bool:
    '''Check if extension is a code file extension'''
    code_extensions: set[str] = {'.py', '.java', '.cpp', '.js', '.rb', '.go', '.cs', '.c', '.h', '.php', '.html', '.css', '.htm'}
    return ext in code_extensions

def _isText(ext: str) -> bool:
    '''Check if extension is a text file extension'''
    text_extensions: list[str] = ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx']
    return ext in text_extensions