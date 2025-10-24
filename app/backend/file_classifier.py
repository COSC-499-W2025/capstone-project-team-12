# file_name represents the node passed from tree_processor.py 
def getFileType(node):
    if _isCode(node):
        return "code"
    elif _isText(node):
        return "text"
    else:
        return "other"

def _getExtension(node):
    extension = node.file_data.get('extension', '')
    return extension.lower()

def _isCode(node):
    code_extensions = ['.py', '.java', '.cpp', '.js', '.rb', '.go', '.cs', '.c', '.h', '.php', '.html', '.css', '.htm']
    return _getExtension(node) in code_extensions

def _isText(node):
    text_extensions = ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx']
    return _getExtension(node) in text_extensions