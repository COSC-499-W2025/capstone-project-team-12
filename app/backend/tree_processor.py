from anytree import PreOrderIter

def process_file_tree(root):
    """
    Iterate through tree, classify files, detect .git
    """
    for node in PreOrderIter(root):
        
        # Check for .git
        if node.name == ".git" and node.parent:
            node.parent.is_repo_head = True
        
        # Classify files (leaf nodes)
        if len(node.children) == 0:
            node.classification = getFileType(node.name)
        else:
            node.classification = None
            if not hasattr(node, 'is_repo_head'):
                node.is_repo_head = False
    
    return root