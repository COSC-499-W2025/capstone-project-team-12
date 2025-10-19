from anytree import PreOrderIter
#here we would import the getFileType function from its module
from file_classifier import getFileType

def process_file_tree(root):
    for node in PreOrderIter(root):

        # Check for .git, if it is, then it marks the parent folder with the is_repo_head attribute
        if node.name == ".git" and node.parent:
            node.parent.is_repo_head = True

        # Classify files (leaf nodes)
        if len(node.children) == 0: # checks if it's a file or a folder
            # Adds new attribute 'classification' to the node, the value will be the one resulting from the getFileType function
            # getFileType is a temporary name, we will change it to the correct one when it is implemented
            node.classification = getFileType(node.name) 
        else:
            node.classification = None
            if not hasattr(node, 'is_repo_head'):
                node.is_repo_head = False

    return root