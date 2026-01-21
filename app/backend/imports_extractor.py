import ast
import re
from typing import List, Dict, Any, Set
from datetime import datetime

class ImportsExtractor:
    def __init__(self):
        # Common false positives to filter out
        self.likely_noise = {
            'utils', 'helper', 'helpers', 'common', 'shared', 'lib', 'libs',
            'models', 'views', 'controllers', 'components', 'services',
            'types', 'interfaces', 'constants', 'config', 'test', 'tests',
            'base', 'core', 'main', 'index', 'app'
        }
    
    def extract_python_imports(self, source_code: str) -> Set[str]:
        """Extract Python imports using AST parsing."""
        imports = set()
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        package = alias.name.split('.')[0]
                        imports.add(package)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        imports.add(package)
        except SyntaxError:
            imports = self._extract_python_imports_regex(source_code)
        return imports
    
    def _extract_python_imports_regex(self, source_code: str) -> Set[str]:
        """Fallback regex-based Python import extraction."""
        imports = set()
        pattern = re.compile(r'^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))', re.MULTILINE)
        for m_from, m_imp in pattern.findall(source_code):
            if m_from:
                imports.add(m_from.split('.')[0])
            elif m_imp:
                imports.add(m_imp.split('.')[0])
        return imports
    
    def extract_java_imports(self, source_code: str) -> Set[str]:
        """Extract Java imports with smart package name extraction."""
        imports = set()
        pattern = re.compile(r'^\s*import\s+(?:static\s+)?([\w\.]+)(?:\.\*)?;', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            parts = match.split('.')
            
            if len(parts) >= 3:
                if parts[0] in ('com', 'org', 'net', 'io', 'dev'):
                    if parts[1] in ('google', 'android', 'github', 'apache', 'jetbrains', 'springframework', 'hibernate'):
                        imports.add(parts[2])
                    else:
                        imports.add('.'.join(parts[1:3]))
                elif parts[0] in ('androidx', 'android', 'javax', 'java'):
                    imports.add('.'.join(parts[:2]))
                else:
                    imports.add(parts[0])
            else:
                imports.add(parts[0])
        
        return imports
    
    def extract_csharp_imports(self, source_code: str) -> Set[str]:
        """Extract C# using statements."""
        imports = set()
        pattern = re.compile(r'^\s*using\s+(?:static\s+)?([\w\.]+)\s*;', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            parts = match.split('.')
            
            if len(parts) >= 2:
                if parts[0] == 'System':
                    imports.add('.'.join(parts[:2]))
                elif parts[0] == 'Microsoft':
                    imports.add(parts[1])
                else:
                    imports.add('.'.join(parts[:2]) if len(parts) > 2 else parts[0])
            else:
                imports.add(parts[0])
        
        return imports
    
    def extract_go_imports(self, source_code: str) -> Set[str]:
        """Extract Go imports."""
        imports = set()
        
        single_pattern = re.compile(r'^\s*import\s+"([^"]+)"', re.MULTILINE)
        block_pattern = re.compile(r'import\s*\((.*?)\)', re.DOTALL)
        import_line_pattern = re.compile(r'"([^"]+)"')
        
        for match in single_pattern.findall(source_code):
            imports.add(self._normalize_go_import(match))
        
        for block in block_pattern.findall(source_code):
            for match in import_line_pattern.findall(block):
                imports.add(self._normalize_go_import(match))
        
        return {imp for imp in imports if imp}
    
    def _normalize_go_import(self, import_path: str) -> str:
        """Normalize Go import paths."""
        if import_path.startswith('github.com/'):
            parts = import_path.split('/')
            if len(parts) >= 3:
                return '/'.join(parts[1:3])
        elif import_path.startswith('golang.org/x/'):
            return import_path.split('/')[-1]
        elif '/' in import_path:
            return import_path.split('/')[-1]
        
        return import_path
    
    def extract_rust_imports(self, source_code: str) -> Set[str]:
        """Extract Rust use statements."""
        imports = set()
        pattern = re.compile(r'^\s*use\s+([\w:]+)', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            parts = match.split('::')
            if len(parts) >= 2 and parts[0] in ('std', 'core', 'alloc'):
                imports.add('::'.join(parts[:2]))
            else:
                imports.add(parts[0])
        
        return imports
    
    def extract_ruby_imports(self, source_code: str) -> Set[str]:
        """Extract Ruby require statements."""
        imports = set()
        pattern = re.compile(r'^\s*require\s+["\']([^"\']+)["\']', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            if match.startswith('.'):
                continue
            package = match.split('/')[0]
            imports.add(package)
        
        return imports
    
    def extract_php_imports(self, source_code: str) -> Set[str]:
        """Extract PHP use statements."""
        imports = set()
        pattern = re.compile(r'^\s*use\s+([\w\\]+)', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            parts = match.split('\\')
            
            if len(parts) >= 2:
                if parts[0] in ('Illuminate', 'Laravel'):
                    imports.add(parts[0])
                else:
                    imports.add(parts[0])
            else:
                imports.add(parts[0])
        
        return imports
    
    def extract_swift_imports(self, source_code: str) -> Set[str]:
        """Extract Swift imports."""
        imports = set()
        pattern = re.compile(r'^\s*import\s+(\w+)', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            imports.add(match)
        
        return imports
    
    def extract_kotlin_imports(self, source_code: str) -> Set[str]:
        """Extract Kotlin imports."""
        imports = set()
        pattern = re.compile(r'^\s*import\s+([\w\.]+)(?:\.\*)?', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            parts = match.split('.')
            
            if len(parts) >= 3:
                if parts[0] in ('com', 'org', 'io', 'net'):
                    if parts[1] in ('google', 'android', 'jetbrains', 'kotlinx', 'squareup'):
                        imports.add(parts[2])
                    else:
                        imports.add('.'.join(parts[1:3]))
                elif parts[0] in ('androidx', 'android', 'kotlin', 'kotlinx'):
                    imports.add('.'.join(parts[:2]))
                else:
                    imports.add(parts[0])
            else:
                imports.add(parts[0])
        
        return imports
    
    def extract_js_imports(self, source_code: str) -> Set[str]:
        """Extract JavaScript/TypeScript imports."""
        imports = set()
        
        es6_pattern = re.compile(r'^\s*import\s+(?:.*?\s+from\s+)?["\']([^"\']+)["\']', re.MULTILINE)
        require_pattern = re.compile(r'\brequire\(["\']([^"\']+)["\']\)', re.MULTILINE)
        
        for match in es6_pattern.findall(source_code):
            normalized = self._normalize_js_import(match)
            if normalized:
                imports.add(normalized)
        
        for match in require_pattern.findall(source_code):
            normalized = self._normalize_js_import(match)
            if normalized:
                imports.add(normalized)
        
        return imports
    
    def _normalize_js_import(self, import_path: str) -> str:
        """Normalize JavaScript import paths."""
        if import_path.startswith('./') or import_path.startswith('../'):
            return None
        
        if import_path.startswith('@'):
            import_path = import_path[1:]
        
        package = import_path.split('/')[0]
        return package
    
    def extract_c_imports(self, source_code: str) -> Set[str]:
        """Extract C/C++ includes."""
        imports = set()
        pattern = re.compile(r'^\s*#include\s*[<"]([^>"]+)[>"]', re.MULTILINE)
        
        for match in pattern.findall(source_code):
            import_name = match.rsplit('.', 1)[0]
            import_name = import_name.split('/')[-1]
            imports.add(import_name)
        
        return imports
    
    def extract_imports(self, source_code: str, file_extension: str) -> Set[str]:
        """Main method to extract imports based on file extension."""
        if not source_code or not source_code.strip():
            return set()
        
        imports = set()
        
        ext_map = {
            'py': self.extract_python_imports,
            'js': self.extract_js_imports,
            'jsx': self.extract_js_imports,
            'ts': self.extract_js_imports,
            'tsx': self.extract_js_imports,
            'java': self.extract_java_imports,
            'kt': self.extract_kotlin_imports,
            'kts': self.extract_kotlin_imports,
            'cs': self.extract_csharp_imports,
            'go': self.extract_go_imports,
            'rs': self.extract_rust_imports,
            'rb': self.extract_ruby_imports,
            'php': self.extract_php_imports,
            'swift': self.extract_swift_imports,
            'c': self.extract_c_imports,
            'cpp': self.extract_c_imports,
            'cc': self.extract_c_imports,
            'cxx': self.extract_c_imports,
            'h': self.extract_c_imports,
            'hpp': self.extract_c_imports,
        }
        
        extraction_method = ext_map.get(file_extension)
        if extraction_method:
            imports = extraction_method(source_code)
        
        # Filter out likely noise
        imports = {imp for imp in imports if imp and imp.lower() not in self.likely_noise}
        
        return imports


    def extract_repo_import_stats(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts the import statistics for all files modified by the user in one repo.
        Uses the modified files from the raw data extracted in the processor
        Returns a dict with imports_summary. For each import, we track:
        - frequency
        - start_date
        - end_date
        - duration_days

        Doing this allows us to find skills and technologies the user has worked with over time.
        """
        repo_name = project.get('repository_name', 'Unknown')
        commits_data: List[Dict[str, Any]] = project.get('user_commits', [])
        imports_data: Dict[str, Dict[str, Any]] = {}
        
        extractor = ImportsExtractor()
        
        for commit in commits_data:
            commit_date_str = commit.get('date')
            if not commit_date_str:
                continue
            
            try:
                commit_date = datetime.fromisoformat(commit_date_str)
            except (ValueError, TypeError):
                continue
            
            for mod in commit.get('modified_files', []):
                src = mod.get('source_code', '')
                if not src.strip():
                    continue
                
                filename = mod.get('filename', 'unknown')
                ext = filename.split('.')[-1].lower() if '.' in filename else ""
                
                imports = extractor.extract_imports(src, ext)
                
                for imp in imports:
                    if imp not in imports_data:
                        imports_data[imp] = {
                            "frequency": 0,
                            "start_date": commit_date,
                            "end_date": commit_date
                        }
                    imports_data[imp]["frequency"] += 1
                    if commit_date < imports_data[imp]["start_date"]:
                        imports_data[imp]["start_date"] = commit_date
                    if commit_date > imports_data[imp]["end_date"]:
                        imports_data[imp]["end_date"] = commit_date
        
        # Convert dates and calculate duration
        for imp, data in imports_data.items():
            start = data["start_date"]
            end = data["end_date"]
            data["start_date"] = start.isoformat() if start else None
            data["end_date"] = end.isoformat() if end else None
            data["duration_days"] = (end - start).days if start and end else None
        
        return imports_data


    def get_all_repo_import_stats(self, project_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Get the import statistics for all repos that were modified by the user.
            Returns a list of dicts (one per repository), each containing:
            - repository_name
            - imports_summary (as defined in extract_repo_import_stats)
            """

            repo_summaries: List[Dict[str, Any]] = []

            for project in project_data:
                if project.get('status') != 'success':
                    repo_summaries.append({
                        "repository_name": project.get('repository_name', 'Unknown'),
                        "imports_summary": {},
                        "error": project.get('error_message', 'Unknown error')
                    })
                    continue
                
                try:
                    imports_summary = self.extract_repo_import_stats(project)
                    repo_summaries.append({
                        "repository_name": project.get('repository_name', 'Unknown'),
                        "imports_summary": imports_summary
                    })
                except Exception as e:
                    repo_summaries.append({
                        "repository_name": project.get('repository_name', 'Unknown'),
                        "imports_summary": {},
                        "error": str(e)
                    })

            return repo_summaries
        

    def sort_repo_imports_in_chronological_order(self, repo_summary: Dict[str, Any]) -> Dict[str, Any]:
            """
            Sorts the imports of a single repo in chronological order by start_date DESC. This is for usage in a timeline per repository. 
            """
            imports = repo_summary.get("imports_summary", {})

            sorted_imports = sorted(imports.items(), key=lambda item: datetime.fromisoformat(item[1]["start_date"]) if item[1].get("start_date") else datetime.min, reverse=True)
            repo_summary["imports_summary"] = {imp: stats for imp, stats in sorted_imports}

            return repo_summary
        
        
    def sort_all_repo_imports_chronologically(self, all_repo_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Takes the full list from get_all_repo_import_stats() and sorts all imports across all repositories in chronological order 
            (by start_date DESC). This is for usage in a timeline across all repositories.
            """
            aggregated = []

            for repo_summary in all_repo_summaries:
                repo_name = repo_summary["repository_name"]
                imports_summary = repo_summary.get("imports_summary", {})

                for imp, stats in imports_summary.items():
                    start_str = stats.get("start_date")
                    start_dt = (
                        datetime.fromisoformat(start_str)
                        if start_str else datetime.min
                    )

                    aggregated.append({
                        "import": imp,
                        "repository_name": repo_name,
                        "start_date": stats.get("start_date"),
                        "end_date": stats.get("end_date"),
                        "duration_days": stats.get("duration_days"),
                        "frequency": stats.get("frequency"),
                        "start_dt": start_dt,   # keep this only for sorting
                    })

            aggregated.sort(key=lambda x: x["start_dt"], reverse=True)

            # remove the helper datetime object before returning
            for entry in aggregated:
                entry.pop("start_dt", None)

            return aggregated 
