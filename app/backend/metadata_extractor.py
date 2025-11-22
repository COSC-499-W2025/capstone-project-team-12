import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import datetime
import hashlib
import mimetypes
import tempfile
import re
from anytree import Node
from pypdf import PdfReader 
from docx import Document
from io import BytesIO


class MetadataExtractor:
    """
    Manages metadata extraction for file nodes in a directory tree
    """
    
    def __init__(self) -> None:
        mimetypes.init()

        self.metadata_store: Dict[str, Dict[str, Any]] = {} # filepath -> metadata
        
    
    def extract_all_metadata(self, file_tree: Node, binary_data_array: List[bytes] = None) -> Dict[str, Dict[str, Any]]:
        """
        Extract metadata for all file nodes in the tree
        Uses binary_data_array for files that don't exist on filesystem  (zipped files)
        """
        self.metadata_store = {}
        
        try:
            # get all file nodes from tree
            file_nodes: List[Node] = self._get_all_file_nodes(file_tree)
            
            # extract metadata for each file node
            for node in file_nodes:
                try:
                    filepath: str = node.file_data['filepath']
                    metadata: Dict[str, Any] = self._extract_single_file_metadata(node, binary_data_array)
                    self.metadata_store[filepath] = metadata
                except Exception:
                    # if extraction fails, store error info in metadata store but continue processing
                    self.metadata_store[filepath] = {
                        'error': 'Metadata extraction failed',
                        'filename': node.name,
                        'filepath': filepath
                    }
                    
        except Exception:
            # if tree processing fails, return empty metadata store
            pass
            
        return self.metadata_store
    
    def _get_all_file_nodes(self, node: Node) -> List[Node]:
        """
        Recursively get all file nodes from the tree
        """
        file_nodes: List[Node] = []
        
        # check that the node is a file
        if hasattr(node, 'type') and node.type == "file":
            file_nodes.append(node)
        
        for child in node.children:
            file_nodes.extend(self._get_all_file_nodes(child))
            
        return file_nodes
    
    def _extract_single_file_metadata(self, node: Node, binary_data_array: List[bytes] = None) -> Dict[str, Any]:
        """
        Extract metadata using binary data when files don't exist on filesystem (zipped files)
        """
        if not hasattr(node, 'file_data'):
            raise ValueError(f"Node {node.name} has no file_data")
            
        file_data: Dict[str, Any] = node.file_data
        filepath: str = file_data['filepath']
        path: Path = Path(filepath)
        binary_index: Optional[int] = file_data.get('binary_index')
        
        # init metadata with basic info from file manager
        metadata: Dict[str, Any] = {
            'filename': node.name,
            'filepath': filepath,
            'file_extension': file_data.get('extension', ''),
            'file_size': file_data.get('size_bytes', 0),
            'binary_index': binary_index
        }
        
        # Check if file exists on filesystem or if we need to use binary data
        file_exists: bool = path.exists()
        binary_data: Optional[bytes] = None
        
        if binary_data_array and binary_index is not None and binary_index < len(binary_data_array):
            binary_data = binary_data_array[binary_index]
        
        if file_exists:
            # file ecists on filesystem
            self._extract_filesystem_metadata(path, metadata)
            self._extract_content_metrics(path, metadata)
        elif binary_data is not None:
            # file doesn't exist on filesystem - use binary data
            self._extract_metadata_from_binary_data(binary_data, filepath, metadata)
        else:
            # no file and no binary data
            self._extract_fallback_metadata(metadata)
        
        # Extract author metadata (PDF, DOCX)
        metadata['author'] = self._extract_author_metadata(
            filepath=path if file_exists else None,
            binary_data=binary_data,
            ext=file_data.get('extension', '')
        )
        return metadata
    
    def _extract_author_metadata(self, filepath: Optional[Path], binary_data: Optional[bytes], ext: str) -> str:
        """
        Extract author metadata from PDF or DOCX.
        """
        try:
            # for pdf
            if ext == ".pdf":
                if filepath and filepath.exists():
                    reader = PdfReader(str(filepath))
                elif binary_data:
                    reader = PdfReader(BytesIO(binary_data))
                else:
                    return "unknown_author"

                info = reader.metadata or {}
                author = getattr(info, "author", None) or info.get("/Author")
                return author or "unknown_author"

            # for docx
            if ext == ".docx":
                if filepath and filepath.exists():
                    doc = Document(str(filepath))
                elif binary_data:
                    doc = Document(BytesIO(binary_data))
                else:
                    return "unknown_author"

                core = doc.core_properties
                author = core.author
                return author if author else "unknown_author"

        except Exception:
            print(f"Error extracting author metadata for {filepath}: {e}")
            return "unknown_author"

        return "unknown_author"

    
    def _extract_metadata_from_binary_data(self, binary_data: bytes, filepath: str, metadata: Dict[str, Any]) -> None:
        """
        Extract metadata from binary data for zipped files
        """
        metadata.update({
            'creation_date': 'unknown_date',
            'last_modified_date': 'unknown_date',
            'checksum': hashlib.md5(binary_data).hexdigest(),
            'mime_type': mimetypes.guess_type(filepath)[0] or "application/octet-stream",
            'author': 'unknown_author'
        })
        
        # Extract content metrics from binary data
        self._extract_content_metrics_from_binary_data(binary_data, metadata)
    
    def _extract_content_metrics_from_binary_data(self, binary_data: bytes, metadata: Dict[str, Any]) -> None:
        """
        Extract content metrics from binary data
        """
        try:
            content: str = binary_data.decode('utf-8', errors='ignore')
            
            if content:
                lines: List[str] = content.splitlines()
                
                metadata.update({
                    'line_count': len(lines),
                    'character_count': len(content),
                    'word_count': self._count_words(content),
                    'encoding': 'UTF-8'
                })
            else:
                metadata.update({
                    'line_count': 0,
                    'character_count': 0,
                    'word_count': 0,
                    'encoding': 'unknown'
                })
                
        except Exception:
            metadata.update({
                'line_count': 0,
                'character_count': 0,
                'word_count': 0,
                'encoding': 'unknown'
            })
    
    def _extract_filesystem_metadata(self, path: Path, metadata: Dict[str, Any]) -> None:
        """
        Extract filesystem-related metadata
        """
        try:
            # get file stats from filesystem
            stat = path.stat()
            
            metadata['creation_date'] = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%m/%d/%Y')
            metadata['last_modified_date'] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%m/%d/%Y')
            
            metadata['checksum'] = self._calculate_checksum(path)
            
            mime_type, encoding = mimetypes.guess_type(str(path))
            metadata['mime_type'] = mime_type or "application/octet-stream"
            
        except (OSError, AttributeError):
            metadata.update({
                'creation_date': 'unknown_date',
                'last_modified_date': 'unknown_date',
                'checksum': 'unknown_checksum',
                'mime_type': 'application/octet-stream'
            })
    
    def _extract_content_metrics(self, path: Path, metadata: Dict[str, Any]) -> None:
        """
        Extract line count, word count, character count from file content
        """
        try:
            content: str = self._read_file_with_fallback_encoding(path)
            
            if content:
                lines: List[str] = content.splitlines()
                
                metadata.update({
                    'line_count': len(lines),
                    'character_count': len(content),
                    'word_count': self._count_words(content),
                    'encoding': 'UTF-8'
                })
            else:
                metadata.update({
                    'line_count': 0,
                    'character_count': 0,
                    'word_count': 0,
                    'encoding': 'unknown'
                })
                
        except Exception:
            metadata.update({
                'line_count': 0,
                'character_count': 0,
                'word_count': 0,
                'encoding': 'unknown'
            })
        
        
    
    def _extract_fallback_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Fallback when no file and no binary data available
        """
        metadata.update({
            'creation_date': 'unknown_date',
            'last_modified_date': 'unknown_date',
            'checksum': 'unknown_checksum',
            'mime_type': 'application/octet-stream',
            'author': 'unknown_author',
            'line_count': 0,
            'character_count': 0,
            'word_count': 0,
            'encoding': 'unknown'
        })
    
    def _read_file_with_fallback_encoding(self, path: Path) -> str:
        """
        Read file content with encoding fallback and tries different encodings
        """
        encodings: List[str] = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding, errors='ignore') as f:
                    return f.read()
            except (UnicodeDecodeError, OSError):
                # try next encoding
                continue
                
        return ""
    
    def _count_words(self, text: str) -> int:
        """
        Count words in text using regex
        """
        words: List[str] = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _calculate_checksum(self, path: Path) -> str:
        """
        Calculate MD5 checksum of file
        """
        try:
            hasher = hashlib.md5()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError):
            return "unknown_checksum"
    
    def get_metadata_by_filepath(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific filename
        """
        return self.metadata_store.get(filepath)
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all extracted metadata
        Returns a copy to prevent external modification of internal state
        """
        return self.metadata_store.copy()

# Manual testing
if __name__ == "__main__":
    # create a test file to demonstrate metadata extraction
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello world\nThis is a test file\nWith three lines of text")
        test_file = f.name
    
    try:
        # Create a simple node structure for testing
        class TestNode:
            def __init__(self, name, file_data):
                self.name = name
                self.file_data = file_data
                self.type = "file"
                self.children = []
        
        # create test node
        test_node = TestNode(
            name="test_file.txt",
            file_data={
                'filepath': test_file,
                'extension': '.txt',
                'size_bytes': os.path.getsize(test_file),
                'binary_index': None
            }
        )
        
        # test metadata extraction
        metadata_extractor = MetadataExtractor()
        metadata = metadata_extractor._extract_single_file_metadata(test_node)
        
        print("Metadata Extraction Test")
        for key, value in metadata.items():
            print(f"{key}: {value}")
            
    finally:
        # Clean up test file
        os.unlink(test_file)