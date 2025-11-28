from typing import List
from anytree import Node
from text_preprocessor import text_preprocess
from code_preprocessor import code_preprocess

def combined_preprocess(text_nodes: List[Node], text_data: List[str], code_nodes: List[Node], code_data: List[str], normalize:bool = True) -> List[List[str]]:
    """ 
    Combined preprocessing function for both text files and code files.
    Params:
        text_nodes: List[Node] = List of anytree Nodes corresponding to text files
        text_data: List[str] = List of strings corresponding to text file data
        code_nodes: List[Node] = List of anytree Nodes corresponding to code files
        code_data: List[str] = List of strings corresponding to code file data
        normalize: bool = Whether to apply normalization (so snake_case and camelCase is removed) to code files

    Returns: List[List[str]] = tokens from both text and code files ready for BoW analysis
    """
    # Extract and normalize code file tokens
    code_tokens_by_file: List[List[str]] = []
    if code_nodes and code_data:
        code_tokens_by_file = code_preprocess(code_nodes, code_data, True)

    # Join code tokens into strings for text preprocessing
    code_as_text_data: List[str] = [' '.join(tokens) for tokens in code_tokens_by_file]

    # Combine text file data and code file data as text
    combined_text_data: List[str] = text_data + code_as_text_data
    combined_text_nodes: List[Node] = text_nodes + code_nodes

    # Preprocess combined data
    combined_preprocessed_tokens: List[List[str]] = text_preprocess(combined_text_nodes, combined_text_data)
    return combined_preprocessed_tokens