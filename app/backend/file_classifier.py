def getFileType(file_name):
    if isCode(file_name):
        return "code"
    elif isText(file_name):
        return "text"
    elif file_name.lower().endswith('.zip'):
        return "zipped"
    else:
        return "other"
    
def isCode(file_name):
    code_extensions = ['.py', '.java', '.cpp', '.js', '.rb', '.go', '.cs', '.c', '.h', '.php', '.html', '.css', '.htm']
    for ext in code_extensions:
        if file_name.lower().endswith(ext):
            return True
    return False

def isText(file_name):
    text_extensions = ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx']
    for ext in text_extensions:
        if file_name.lower().endswith(ext):
            return True
    return False