from typing import List, Tuple, Any, Dict
from anytree import Node, Resolver
from datetime import datetime

class TreeManager:
    """
    Manages tree operations including merging incremental updates.
    """
    def __init__(self):
        self.resolver = Resolver('name')

    def merge_trees(
        self, 
        old_tree: Node, 
        old_binary_data: List[bytes], 
        new_tree: Node, 
        new_binary_data: List[bytes]
    ) -> Tuple[Node, List[bytes]]:
        """
        Merges a new file tree (from a fresh input) into an old file tree.
        
        Preserves metadata like classifications from the old tree if the file 
        has not been modified (based on timestamp).
        
        Returns:
            Tuple[Node, List[bytes]]: The updated tree and a combined binary 
            data array.
        """
        
        merged_binary_data: List[bytes] = []
        
        # We traverse the new tree because it represents the current context of the file system.
        #We want to carry over metadata from the old tree where applicable.
        
        self._process_merge_node(new_tree, old_tree, old_binary_data, new_binary_data, merged_binary_data)
        
        return new_tree, merged_binary_data

    def _process_merge_node(
        self,
        new_node: Node,
        old_node_context: Node,
        old_binary_data: List[bytes],
        new_binary_data: List[bytes],
        merged_binary_data: List[bytes]
    ) -> None:
        """
        Recursive helper to process nodes.
        Mutates new_node in place to update binary_index and metadata.
        Appends data to merged_binary_data.
        """
        
        # Try to find the corresponding node in the old tree context
        # old_node_context is the generic 'root' or 'parent' in the old tree to search from.
        # Since we are traversing recursively, we can usually just look at children of the matched parent.
        # But for the root call, we pass the old_root.
        
        matched_old_node = None
        
        # If both are roots or we are at the start
        if new_node.is_root and old_node_context.is_root and new_node.name == old_node_context.name:
            matched_old_node = old_node_context
        else:
            # Try to find child with same name in old_node_context
            # Note: This logic assumes we pass the corresponding match of the parent as context
            if old_node_context:
                matched_old_node = next(
                    (child for child in old_node_context.children if child.name == new_node.name), 
                    None
                )

        if new_node.type == "file":
            self._merge_file_node(
                new_node, 
                matched_old_node, 
                old_binary_data, 
                new_binary_data, 
                merged_binary_data
            )
        
        # Process children
        for child in new_node.children:
            self._process_merge_node(
                child, 
                matched_old_node, # Pass the matched old node as the parent scope for the next step
                old_binary_data, 
                new_binary_data, 
                merged_binary_data
            )

    def _merge_file_node(
        self,
        new_node: Node,
        old_node: Node | None,
        old_binary_data: List[bytes],
        new_binary_data: List[bytes],
        merged_binary_data: List[bytes]
    ) -> None:
        
        is_unchanged = False
        
        # Check if file is unchanged
        if old_node and hasattr(old_node, 'last_modified') and hasattr(new_node, 'last_modified'):
            if old_node.last_modified == new_node.last_modified:
                is_unchanged = True

        if is_unchanged:
            # CASE 1: UNCHANGED
            # Reuse data from old binary array
            original_index = old_node.binary_index
            data = old_binary_data[original_index]
            
            # Preserve metadata from old node
            if hasattr(old_node, 'classification'):
                new_node.classification = old_node.classification
            
            # Check for other custom attributes to preserve here if needed
             
        else:
            # CASE 2: CHANGED or NEW
            # Use data from new binary array (freshly loaded)
            original_index = new_node.binary_index
            data = new_binary_data[original_index]
            
            # Classification remains None (or whatever fresh load default is)

        # Update the binary index to point to the new consolidated list
        new_index = len(merged_binary_data)
        merged_binary_data.append(data)
        
        new_node.binary_index = new_index
        
        # Also update the file_data dictionary attached to the node to keep it consistent
        if hasattr(new_node, 'file_data'):
            new_node.file_data['binary_index'] = new_index