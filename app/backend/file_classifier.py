# file_name represents the node passed from tree_processor.py 
def getFileType(file_name):
    if _isCode(file_name):
        return "code"
    elif _isText(file_name):
        return "text"
    elif file_name.name.lower().endswith('.zip'):
        return "zipped"
    else:
        return "other"

def _getExtension(file_name):
    extension = file_name.file_data.get('extension', '')
    return extension.lower()

def _isCode(file_name):
    code_extensions = ['.py', '.java', '.cpp', '.js', '.rb', '.go', '.cs', '.c', '.h', '.php', '.html', '.css', '.htm']
    return _getExtension(file_name) in code_extensions

def _isText(file_name):
    text_extensions = ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx']
    return _getExtension(file_name) in text_extensions