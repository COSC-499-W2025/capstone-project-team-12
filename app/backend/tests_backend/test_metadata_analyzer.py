from metadata_analyzer import *

class TestMetadataAnalyzer:
    def get_sample_metadata(self):
        """
        Create sample metadata for testing
        """
        return {
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
            'file_size': 357,
            'line_count': 124,
            'word_count': 542,
            'character_count': 937,
            'file_extension': '.yaml',
            'creation_date': '04/24/2025',
            'last_modified_date': '10/12/2025'
        },
        'project/analysis.r': {
            'filepath' : 'project/analysis.r',
            'file_size': 123,
            'line_count': 3,
            'word_count': 10,
            'character_count': 30,
            'file_extension': '.r',
            'creation_date': '10/12/2025',
            'last_modified_date': '10/01/2025'
        }
        }

    def setup_method(self):
        """Setup for each test method"""
        self.sample_metadata = self.get_sample_metadata()
        self.analyzer = MetadataAnalyzer(self.sample_metadata)
        self.results = self.analyzer.analyze_all()

    def test_empty_metadata(self):
        """Test analysis with empty metadata store"""
        empty_analyzer = MetadataAnalyzer({})
        results = empty_analyzer.analyze_all()
        
        assert results['basic_stats']['total_files'] == 0
        assert len(results['extension_stats']) == 0
        assert len(results['skill_stats']) == 0

    def test_basic_stats_calculation(self):
        basic_stats = self.results['basic_stats']
        assert basic_stats['total_files'] == 8
        assert basic_stats['total_size'] == 10838
        assert basic_stats['total_lines'] == 732
        assert basic_stats['total_words'] == 2467
        assert basic_stats['total_characters'] == 15767

    def test_extension_stats_calculation(self):
        """Test extension statistics calculation"""
        extension_stats = self.results['extension_stats']

        # test a few extensions
        assert '.py' in extension_stats
        assert '.md' in extension_stats
        assert '.yaml' in extension_stats

        # test the
        py_stats = extension_stats.get('.py')
        assert py_stats is not None
        assert py_stats['count'] == 2
        assert py_stats['total_size'] == 5120

    def test_skill_stats_calculation(self):
        """Test skill statistics calculation"""
        skill_stats = self.results['skill_stats']
        primary_skills = self.results['primary_skills']
        
        assert len(skill_stats) == 5
        assert 'Backend Development' in skill_stats
        assert 'Documentation' in skill_stats
        assert len(primary_skills) == 3
        assert 'Backend Development' in primary_skills

    def test_date_stats_calculation(self):
        """Test date statistics calculation"""
        date_stats = self.results['date_stats']

        # test creation dates are properly extracted
        assert len(date_stats['by_creation_date']) == 6
        assert '2025-10' in date_stats['by_creation_date']
        assert '2024-01' in date_stats['by_creation_date']

        # test modification dates are properly extracted
        assert len(date_stats['by_modified_date']) == 3
        assert '2025-11' in date_stats['by_modified_date']
        assert '2025-07' in date_stats['by_modified_date']

        # test filepath saved with dates
        assert 'project/test.py' in date_stats['by_creation_date']['2025-05']
        assert 'project/README.md' in date_stats['by_creation_date']['2025-01']
        assert 'project/docker-compose.yaml' in date_stats['by_modified_date']['2025-10']
        assert 'project/test.py' in date_stats['by_modified_date']['2025-11']

        # test that dates are sorted in descending order (most recent first)
        creation_dates = list(date_stats['by_creation_date'].keys())
        modification_dates = list(date_stats['by_modified_date'].keys())
        assert creation_dates == sorted(creation_dates, reverse=True)
        assert modification_dates == sorted(modification_dates, reverse=True)

        # test activity
        assert date_stats['recent_activity_count'] == 4
        assert date_stats['activity_level'] == "high"

    def test_extension_classification(self):
        """Test extension classification"""
        assert self.analyzer._classify_extension('.py') == 'Backend Development'
        assert self.analyzer._classify_extension('.js') == 'Web Development'
        assert self.analyzer._classify_extension('.md') == 'Documentation'

    def test_percentages_calculation(self):
        """Test percentage calculations in stats"""
        extension_stats = self.results['extension_stats']
        skill_stats = self.results['skill_stats']
        total_files = self.results['basic_stats']['total_files']

        # check percentages in extension stats
        for ext, stats in extension_stats.items():
            expected_percentage = (stats['count'] / total_files) * 100
            assert abs(stats['percentage'] - expected_percentage) < 0.01  # allow small floating point error

        # check percentages in skill stats
        for skill_name, stats in skill_stats.items():
            expected_percentage = (stats['file_count'] / total_files) * 100
            assert abs(stats['percentage'] - expected_percentage) < 0.01