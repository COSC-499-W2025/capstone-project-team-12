from collections import defaultdict
from typing import Dict, Any, List, Tuple
from datetime import datetime

class MetadataAnalyzer:
    """
    Analyzes extracted metadata for insights
    """
    def __init__(self, metadata_store: Dict[str, Dict[str, Any]]):
        '''
        Initialize with metadata store
        '''
        self.metadata_store = metadata_store

    def analyze_all(self) -> Dict[str, Any]:
        """
        Perform complete metadata analysis
        """
        try:
            if not self.metadata_store:
                print("Metadata store is empty")
                return self._create_empty_results()

            basic_stats = self._calculate_basic_stats()
            extension_stats = self._calculate_extension_stats()
            skill_stats, primary_skills = self._calculate_skill_stats(extension_stats)
            date_stats = self._calculate_date_stats()

            self._add_percentages(extension_stats, skill_stats, basic_stats['total_files'])

            analysis: Dict[str, Any] = {
                'basic_stats': basic_stats,
                'extension_stats': extension_stats,
                'skill_stats': skill_stats,
                'primary_skills': primary_skills,
                'date_stats': date_stats
            }
            
            return analysis
        except Exception as e:
            raise ValueError(f"Metadata analysis failed: {e}")

    def _create_empty_results(self) -> Dict[str, Any]:
        """
        Create empty analysis results
        """
        return {
            'basic_stats': {
                'total_files': 0,
                'total_size': 0,
                'total_lines': 0,
                'total_words': 0,
                'total_characters': 0
            },
            'extension_stats': {},
            'skill_stats': {},
            'primary_skills': [],
            'date_stats': {
                'by_creation_date': {},
                'by_modified_date': {},
                'recent_activity_count': 0,
                'activity_level': 'unknown'
            }
        }

    def _add_percentages(self, extension_stats: Dict[str, Any], skill_stats: Dict[str, Any], total_files: int) -> None:
        """
        Add percentage calculations to extension and skill statistics
        """
        if total_files == 0:
            return
            
        # add percentages to extension stats
        for ext_stats in extension_stats.values():
            ext_stats['percentage'] = round((ext_stats['count'] / total_files) * 100, 2)
        
        # add percentages to skill stats
        for skill_stat in skill_stats.values():
            skill_stat['percentage'] = round((skill_stat['file_count'] / total_files) * 100, 2)

    
    def _calculate_basic_stats(self) -> Dict[str, int]:
        """
        Calculate basic statistics from metadata
        """
        try:
            total_files: int = len(self.metadata_store)
            total_size: int = 0
            total_lines: int = 0
            total_words: int = 0
            total_characters: int = 0
            
            for metadata in self.metadata_store.values():
                try:
                    total_size += metadata.get('file_size', 0)
                    total_lines += metadata.get('line_count', 0)
                    total_words += metadata.get('word_count', 0)
                    total_characters += metadata.get('character_count', 0)
                except Exception as e:
                    print(f"Error processing metadata entry: {e}")
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_lines': total_lines,
                'total_words': total_words,
                'total_characters': total_characters
            }
        except Exception as e:
            print(f"Failed to calculate basic stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'total_lines': 0,
                'total_words': 0,
                'total_characters': 0
            }
    
    def _calculate_extension_stats(self) -> Dict[str, Any]:
        '''
        Calculate statistics by file extension
        '''
        try:
            extension_totals = defaultdict(lambda: {'count': 0, 'total_size': 0})

            # calculate totals by extension
            for metadata in self.metadata_store.values():
                try:
                    ext = metadata.get('file_extension', '')
                    size = metadata.get('file_size', 0)
                    extension_totals[ext]['count'] += 1
                    extension_totals[ext]['total_size'] += size
                except Exception as e:
                    print(f"Error processing metadata entry for extension stats: {e}")

            extension_stats: Dict[str, Any] = {}

            # compile final extension stats
            for ext, data in extension_totals.items():
                try:
                    count = data['count']
                    total_size = data['total_size']
                    avg_size = total_size / count if count > 0 else 0
                    category = self._classify_extension(ext)

                except Exception as e:
                    print(f"Error processing extension stats for {ext}: {e}")
                    count = 0
                    total_size = 0
                    avg_size = 0
                    category = "unknown"

                extension_stats[ext] = {
                    'extension': ext,
                    'count': count,
                    'total_size': total_size,
                    'avg_size': avg_size,
                    'category': category
                }
            return extension_stats
        except Exception as e:
            print(f"Failed to calculate extension stats: {e}")
            return {}

    def _calculate_skill_stats(self, extension_stats: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Calculate statistics for each skill category
        """
        skill_stats: Dict[str, Any] = {}

        try:
            for ext_stats in extension_stats.values():
                try:
                    category = ext_stats['category']
                    if category not in skill_stats:
                        skill_stats[category] = {
                            'category': category,
                            'file_count': 0,
                            'total_size': 0,
                            'is_primary': False
                        }
                    skill_stats[category]['file_count'] += ext_stats['count']
                    skill_stats[category]['total_size'] += ext_stats['total_size']
                except Exception as e:
                    print(f"Error processing skill stats for category {category}: {e}")

            # check if skill_stats is empty before sorting
            if not skill_stats:
                return {}, []

            # determine top 3 skills based on file count
            sorted_skills: List[Dict[str, Any]] = sorted(skill_stats.values(), key=lambda x: x['file_count'], reverse=True)
            primary_skills: List[str] = [skill['category'] for skill in sorted_skills[:3]]

            for skill in skill_stats:
                skill_stats[skill]['is_primary'] = skill_stats[skill]['category'] in primary_skills
            return skill_stats, primary_skills
        except Exception as e:
            print(f"Failed to calculate skill stats: {e}")
            return {}, []
    
    def _calculate_date_stats(self) ->  Dict[str, Any]:
        """
        Calculate productivity statistics by date ranges
        """
        try:
            creation_months: Dict[str, List[str]] = defaultdict(list)
            modified_months: Dict[str, List[str]] = defaultdict(list)
            recent_files:int = 0
            today = datetime.now()

            for metadata in self.metadata_store.values(): 
                try:
                    filename = metadata.get('filepath', 'unknown_file')

                    # count files by their creation and modified months
                    creation_date_str: str = metadata.get('creation_date', None)
                    if creation_date_str != 'unknown_date' and creation_date_str:
                        creation_date: datetime = datetime.strptime(creation_date_str, '%m/%d/%Y')
                        creation_month = creation_date.strftime("%Y-%m")
                        creation_months[creation_month].append(filename)

                    modified_date_str = metadata.get('last_modified_date', None)
                    if modified_date_str != 'unknown_date' and modified_date_str:
                        modified_date = datetime.strptime(modified_date_str, '%m/%d/%Y')
                        modified_month = modified_date.strftime("%Y-%m")
                        modified_months[modified_month].append(filename)
                        
                        # if file recently modified (within last 30 days), consider it as recent
                        if (today - modified_date).days <= 30:
                            recent_files += 1

                except Exception as e:
                    print(f"Error processing metadata entry for date stats: {e}")
                    continue

            # sort months in descending order (most recent first) and filename alphabetically
            sorted_creation_months = {month: sorted(files) for month, files in sorted(creation_months.items(), key=lambda x: x[0], reverse=True)}
            sorted_modified_months = {month: sorted(files) for month, files in sorted(modified_months.items(), key=lambda x: x[0], reverse=True)}

            # activity level = high if >30% files recently modified, else moderate
            activity_level = "high" if recent_files > len(self.metadata_store) * 0.3 else "moderate"
        
            return {
                'by_creation_date': dict(sorted_creation_months),
                'by_modified_date': dict(sorted_modified_months),
                'recent_activity_count': recent_files,
                'activity_level': activity_level,
            }
        except Exception as e:
            print(f"Failed to calculate date stats: {e}")
            return {
                'by_creation_date': {},
                'by_modified_date': {},
                'recent_activity_count': 0,
                'activity_level': 'unknown'
            }
        
    def _classify_extension(self, ext: str) -> str:
        """
        Classify file extension into categories
        """
        try:
            categories = {
                'DevOps': {'.dockerfile', '.yml', '.yaml', '.sh', '.bash', '.env', '.ini', '.cfg'},
                'Documentation': {'.txt', '.md', '.docx', '.doc', '.pdf', '.rtf', '.tex'},
                'Web Development': {'.html', '.htm', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue'},
                'Mobile App Development': {'.kt', '.swift', '.m', '.dart', '.xml', '.gradle'},
                'Data Science': {'.ipynb', '.r', '.rmd'},
                'Database': {'.sql', '.db', '.sqlite'},
                'Backend Development': {'.py', '.java', '.go', '.rb', '.php', '.cs', '.cpp', '.c'},
                'Frontend Development': {'.html', '.htm', '.css', '.js', '.ts'}
            }

            for category, ext_set in categories.items():
                if ext in ext_set:
                    return category

            return "Other"

        except Exception as e:
            print(f"Error classifying extension {ext}: {e}")
            return "Other"
    
    def return_metadata_stats(self) -> Dict[str, Any]:
        """
        Return raw metadata statistics
        """
        try:
            return self.metadata_store
        except Exception as e:
            print(f"Failed to return metadata stats: {e}")
            return {}
            
# Manual testing
if __name__ == "__main__":
    
    # Create test metadata for analysis
    test_metadata = {
        'project/main.py': {
            'filepath' : 'project/main.py',
            'file_size': 2048,
            'line_count': 150,
            'word_count': 450,
            'character_count': 2800,
            'file_extension': '.py',
            'creation_date': '04/15/2025',
            'last_modified_date': '10/20/2025'
        },
        'project/utils.js': {
            'filepath' : 'project/utils.js',
            'file_size': 1024,
            'line_count': 80,
            'word_count': 300,
            'character_count': 1800,
            'file_extension': '.js',
            'creation_date': '01/20/2025',
            'last_modified_date': '11/18/2025'
        },
        'project/README.md': {
            'filepath' : 'project/README.md',
            'file_size': 512,
            'line_count': 25,
            'word_count': 120,
            'character_count': 800,
            'file_extension': '.md',
            'creation_date': '01/10/2025',
            'last_modified_date': '07/15/2025'
        },
        'project/test.py': {
            'filepath' : 'project/test.py',
            'file_size': 3072,
            'line_count': 200,
            'word_count': 600,
            'character_count': 4200,
            'file_extension': '.py',
            'creation_date': '05/18/2025',
            'last_modified_date': '11/10/2025'
        },
        'project/test.html': {
            'filepath' : 'project/test.html',
            'file_size': 1234,
            'line_count': 100,
            'word_count': 345,
            'character_count': 4200,
            'file_extension': '.html',
            'creation_date': '01/09/2024',
            'last_modified_date': '10/31/2025'
        },
        'project/api.java': {
            'filepath' : 'project/api.java',
            'file_size': 2468,
            'line_count': 50,
            'word_count': 100,
            'character_count': 1000,
            'file_extension': '.java',
            'creation_date': '08/10/2025',
            'last_modified_date': '11/01/2025'
        },
        'project/docker-compose.yaml': {
            'filepath' : 'project/docker-compose.yaml',
            'file_size': 2468,
            'line_count': 50,
            'word_count': 100,
            'character_count': 1000,
            'file_extension': '.yaml',
            'creation_date': '04/24/2025',
            'last_modified_date': '10/27/2025'
        }
    }
    
    try:
        analyzer = MetadataAnalyzer(test_metadata)
        results = analyzer.analyze_all()
        
        print("Basic Statistics:")
        print(f"Total Files: {results['basic_stats']['total_files']}")
        print(f"Total Size: {results['basic_stats']['total_size']} bytes")
        print(f"Total Lines: {results['basic_stats']['total_lines']}")
        print(f"Total Words: {results['basic_stats']['total_words']}")
        
        print("Extension Statistics:")
        for ext, stats in results['extension_stats'].items():
            print(f"{ext}: {stats['count']} files ({stats['percentage']}%), {stats['total_size']} bytes, {stats['category']}")
        print()
        
        print("Date Statistics:")
        print(f"Creation Dates: {results['date_stats']['by_creation_date']}")
        print(f"Modified Dates: {results['date_stats']['by_modified_date']}")
        print(f"Recent Activity: {results['date_stats']['recent_activity_count']} files")
        print(f"Activity Level: {results['date_stats']['activity_level']}\n")

        print("Skill Statistics:")
        for skill_name, skill_stats in results['skill_stats'].items():
            primary_indicator = " (PRIMARY)" if skill_stats['is_primary'] else ""
            print(f"{skill_name}{primary_indicator}: {skill_stats['file_count']} files ({skill_stats['percentage']}%)")
        print(f"\nPrimary Skills: {', '.join(results['primary_skills'])}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()