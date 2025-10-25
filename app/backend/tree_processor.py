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
            if node.name == ".git" and node.parent:
                node.parent.is_repo_head = True  # Update existing attribute
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
            #note that directories keep their default classification=None from FileManager
        return root
    
    def _drop_invalid_node(node):
    # detaching the node from the tree by removing its parent reference
        if node.parent:
            node.parent = None
    # TODO: drop the binary data once binary data list is implemented
    # set binarydata[index of node] = None

    #get text and get
    def get_text_files(self):
        return self.text_files
    
    def get_code_files(self):
        return self.code_files
    
    def get_git_repos(self): #returns only root paths of repos
        return self.git_repos