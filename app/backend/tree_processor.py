from anytree import PreOrderIter
#here we would import the getFileType function from its module
from file_classifier import getFileType
class TreeProcessor:
    def __init__(self):
        self.text_files = []
        self.code_files = []
        self.git_repos = []

    def process_file_tree(self, root):
        #clear previous data
        self.text_files = []
        self.code_files = []
        self.git_repos = []
        
        for node in PreOrderIter(root):
            # Check for .git and mark parent as repo head
            if node.name == ".git" and node.parent:
                node.parent.is_repo_head = True  # Update existing attribute
                # Add the repo root path to git_repos array
                if hasattr(node.parent, 'path'):
                    self.git_repos.append(node.parent.path)
            
            # Classify files (update the existing classification attribute)
            if hasattr(node, 'type') and node.type == "file":
                classification = getFileType(node.name)
                node.classification = classification  # Update existing attribute
                
                # Add to appropriate array based on classification
                if classification == "TEXT" and hasattr(node, 'path'):
                    self.text_files.append(node.path)
                elif classification == "CODE" and hasattr(node, 'path'):
                    self.code_files.append(node.path)
            # Note: directories keep their default classification=None from FileManager
        return root
    
    def get_text_files(self):
        return self.text_files
    
    def get_code_files(self):
        return self.code_files
    
    def get_git_repos(self):
        return self.git_repos