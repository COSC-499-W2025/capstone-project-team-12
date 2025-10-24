from anytree import PreOrderIter
#here we would import the getFileType function from its module
from file_classifier import getFileType

def process_file_tree(root):
    for node in PreOrderIter(root):

        # Check for .git, if it is, then it marks the parent folder with the is_repo_head attribute
        if node.name == ".git" and node.parent:
            node.parent.is_repo_head = True

        # Classify files (leaf nodes)
        if hasattr(node, 'type') and node.type == "file": # checks if it's a file or a folder
            # Adds new attribute 'classification' to the node, the value will be the one resulting from the getFileType function
            node.classification = getFileType(node)
            if node.classification == "other":
                # Drop invalid files
                _drop_invalid_node(node) 
        else:
            node.classification = None
            if not hasattr(node, 'is_repo_head'):
                node.is_repo_head = False

    return root

def _drop_invalid_node(node):
    # detaching the node from the tree by removing its parent reference
    if node.parent:
        node.parent = None
    # TODO: drop the binary data once binary data list is implemented
    # set binarydata[index of node] = None