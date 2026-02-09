import pytest
from analysis_pipeline import *
from unittest.mock import Mock,MagicMock,patch


#Series of fixtures for testing that follows

@pytest.fixture
def pipeline():
    #mock the dependencies
    return AnalysisPipeline(MagicMock(), MagicMock(), MagicMock())


@pytest.fixture
def mock_text_nodes():
    """Mock text nodes"""
    text_node1 = Node("text1.txt", file_data={'binary_index': 0})
    text_node1.filepath = "/path/text1.txt"
    text_node2 = Node("text2.md", file_data={'binary_index': 1})
    text_node2.filepath = "/path/text2.md"
    return [text_node1,text_node2]


@pytest.fixture
def mock_code_nodes():
    """Mock code nodes"""
    code_node1 = Node("code1.py", file_data={'binary_index': 2})
    code_node1.filepath = "/path/code1.py"
    code_node2 = Node("code2.cpp", file_data={'binary_index': 3})
    code_node2.filepath = "/path/code2.cpp"
    return [code_node1, code_node1]


@pytest.fixture
def sample_bin_data_array():
    """Mock bin data for tests"""
    return [
        b"Capybara text file information.",
        b"Serious non-capybara information",
        b"def some_python_func():\n return [some_python_return,another_python_return]",
        b"char** someCppFunction(){\n char** response = {'data1','data2'};\n return responce;}"
    ]

def test_data_helpers(pipeline,mock_text_nodes,sample_bin_data_array):
    """Tests if the pipeline can correctly fetch and convert binary data"""
    pipeline.file_data_list = sample_bin_data_array
    
    assert pipeline.get_bin_data_by_Id(0) == b"Capybara text file information."
    
    assert pipeline.get_bin_data_by_IdList([1,2]) == [
        b"Serious non-capybara information",
        b"def some_python_func():\n return [some_python_return,another_python_return]"
    ]
    
    assert pipeline.get_bin_data_by_Nodes(mock_text_nodes) == [
        b"Capybara text file information.",
        b"Serious non-capybara information"
        ]
    
    assert pipeline.binary_to_str([b"Test_string1",b"Test_string2"]) == ["Test_string1","Test_string2"]

@patch("analysis_pipeline.FileManager")
def test_file_load_failure(mock_fm, pipeline):
    """Tests that the pipeline stops if the file fails to load"""
    #forcing hte file manager to return error
    mock_fm.return_value.load_from_filepath.return_value = {"status": "error", "message": "fail"}
    pipeline.run_analysis("fake_path")
    pipeline.cli.print_status.assert_any_call("File Manager Error:Load Error: fail", "error")

#test topic analysis pipeline for both cache miss and cache hit cases
#The worlds longest test signature lmao, if you have any ideas to concise it let me know
@patch('analysis_pipeline.generate_topic_vectors')
@patch('analysis_pipeline.remove_pii')
@patch('analysis_pipeline.combined_preprocess')
@patch('analysis_pipeline.BoWCache')
def test_topic_pipeline(mock_cache_cls, mock_preprocess, mock_pii,mock_gen, #Patched Mocks
    pipeline, mock_text_nodes, mock_code_nodes, sample_bin_data_array):#Fixtured Mocks
        
        #====MOCKING VARIOUS SHARED RETURNS===#
        pipeline.file_data_list = sample_bin_data_array
         
        #Mock Codepreprocessor data based on fixture's data
        processed_docs = [
            ['capybara','text','file','info'],
            ['serious','no','capybara','info'],
            ['some', 'python', 'function'],
            ['some','function','response']
        ]
        mock_preprocess.return_value = processed_docs
        
        #Mock anonymization return
        anonymized_docs = processed_docs #same as processed_docs for convenience, any issues with anonymization should be handled by test_pii_remover.py 
        mock_pii.return_value = anonymized_docs
        
        # Setup topic generation
        mock_lda = Mock()
        mock_dictionary = Mock()
        doc_topic_vectors = [[0.5, 0.3]]
        topic_term_vectors = [[0.4, 0.3]]
        mock_lda.show_topic.return_value = [('data', 0.3), ('process', 0.25)]
        mock_gen.return_value = (mock_lda,mock_dictionary, [[0.5, 0.3]], [[0.4, 0.3]])
        #====END OF SHARED MOCKS===#
       
        #====START OF CACHE MISS CASE====#    
        # Setup cache with miss for testing cache miss case
        mock_cache = Mock()
        mock_cache.has.return_value = False
        mock_cache_cls.return_value = mock_cache
        
        #Actual function execution
        result = pipeline.run_topic_analysis_pipeline(mock_text_nodes, mock_code_nodes)
        
        # Verify cache miss flow
        mock_cache.has.assert_called()
        mock_cache.set.assert_called_once()
        
        # Verify different steps were called with appropriate calls
        mock_preprocess.assert_called_once()
        mock_pii.assert_called_once_with(processed_docs)
        
        #Verify topic generation was called
        mock_gen.assert_called_once_with(anonymized_docs)
        
        # Verify return values
        lda_model, dictionary, doc_vecs, topic_vecs, bow = result
        assert lda_model == mock_lda
        assert dictionary == mock_dictionary
        assert doc_vecs == doc_topic_vectors
        assert topic_vecs == topic_term_vectors
        assert bow == anonymized_docs
        #====END OF CACHE MISS CASE====#        
        
        #====START OF CACHE HIT CASE====# 
        #Setup cache with hit case
        #another reuse for convenience
        cached_bow = processed_docs
        mock_cache = Mock()
        mock_cache.has.return_value = True
        mock_cache.get.return_value = cached_bow
        mock_cache_cls.return_value = mock_cache
        
        #Actual function execution
        result = pipeline.run_topic_analysis_pipeline(mock_text_nodes, mock_code_nodes)
        
        # Verify cache hit flow
        mock_cache.has.assert_called_once()
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called() 
        

        # Verify topic generation was called 
        mock_gen.assert_called_with(cached_bow)
        
        # Verify return values
        lda_model, dictionary, doc_vecs, topic_vecs, bow = result
        assert lda_model == mock_lda
        assert dictionary == mock_dictionary
        assert doc_vecs == doc_topic_vectors
        assert topic_vecs == topic_term_vectors
        assert bow == cached_bow

class test_topic_vector_editing:
    def test_reviews_proceed_immediately(pipeline):
        """Tests that if user chooses to proceed immediately, the pipeline continues"""
        initial_bundle = {
            'topic_keywords': [
                {'topic_id': 0, 'keywords': ['data', 'code']},
                {'topic_id': 1, 'keywords': ['user', 'login']}
            ]
        }
        #user inputs p
        pipeline.cli.display_topic_review_menu.return_value = 'P'

        result = pipeline.review_topic_bundle(initial_bundle)

        assert result == initial_bundle
        pipeline.cli.print_status.assert_called_with("Proceeding with current topics.", "success")


    def test_reviews_delete_topic(pipeline):
        """Tests that it correctly deletes a topic"""
        initial_bundle = {
            'topic_keywords': [
                {'topic_id': 0, 'keywords': ['data', 'code']},
                {'topic_id': 1, 'keywords': ['user', 'login']}
            ]
        }

        #we want to edit, then , then we input 1, then we select del, then p
        pipeline.cli.display_topic_review_menu.side_effect = ['E', 'P']
        pipeline.cli.get_input.return_value = '1'  #topic to delete
        pipeline.cli.get_granular_input.return_value = ('del', None)

        result = pipeline.review_topic_bundle(initial_bundle)
        final_topics = result['topic_keywords']
        assert len(final_topics) == 1
        assert final_topics[0]['topic_id'] == 0
        pipeline.cli.print_status.assert_any_call("Topic 1 has been deleted.", "success")


    def test_review_manual_editing(pipeline):
        """Test the manual editing/granular edits workflow"""
        initial_bundle = {
            'topic_keywords': [{'topic_id': 0, 'keywords': ['bad', 'middle']}]
        }

        #from main meny, E then P after edits
        pipeline.cli.display_topic_review_menu.side_effect = ['E', 'P']
        
        pipeline.cli.get_input.side_effect = ["0", "better", "good"]

        pipeline.cli.get_granular_input.side_effect = [
            ('replace_one', 0), 
            ('add', None), 
            ('back', None)
        ]

        result = pipeline.review_topic_bundle(initial_bundle)

        keywords = result['topic_keywords'][0]['keywords']
        assert keywords[0] == 'better'  #replaced
        assert keywords[1] == 'middle'  #same
        assert keywords[2] == 'good'    #added

class TestRunRepoAnalysisPipeline:
    """Tests for run_repo_analysis_pipeline method"""

    def test_empty_input(self, pipeline):
        """Test that empty git_repos input returns empty lists"""
        result = pipeline.run_repo_analysis_pipeline([], [])
        
        assert result == ([], [], [], [])

    def test_userskipping(self, pipeline):
        """Test that skipping GitHub username returns empty lists"""
        git_repos = [{"path": "/repo1"}, {"path": "/repo2"}]
        
        pipeline.cli.get_input.return_value = ""  # Empty username
        
        result = pipeline.run_repo_analysis_pipeline(git_repos, [])
        
        pipeline.cli.print_status.assert_called_with("Skipping Git linking.", "info")
        assert result == ([], [], [], [])

    @patch('analysis_pipeline.RepositoryProcessor')
    def test_repo_process(self, mock_repo_processor,pipeline, sample_bin_data_array):
        """Test RepositoryProcessor is initialized with correct parameters"""
        git_repos = [{"path": "/repo1"}]
        pipeline.cli.get_input.side_effect = ["testuser", "test@email.com"]
        
        mock_processor = MagicMock()
        mock_processor.process_repositories.return_value = []
        mock_repo_processor.return_value = mock_processor
        
        pipeline.run_repo_analysis_pipeline(git_repos, sample_bin_data_array)
        
        mock_repo_processor.assert_called_once_with(
            username="testuser",
            binary_data_array=sample_bin_data_array,
            user_email="test@email.com"
        )

    @patch('analysis_pipeline.RepositoryProcessor')
    def test_repo_process_noemail(self, mock_repoprocessor, pipeline, sample_bin_data_array):
        """Test that None is passed for email when user doesn't provide one"""
        git_repos = [{"path": "/repo1"}]
        pipeline.cli.get_input.side_effect = ["testuser", ""]
        
        mock_processor = MagicMock()
        mock_processor.process_repositories.return_value = []
        mock_repoprocessor.return_value = mock_processor
        
        pipeline.run_repo_analysis_pipeline(git_repos, sample_bin_data_array)
        
        mock_repoprocessor.assert_called_once_with(
            username="testuser",
            binary_data_array=sample_bin_data_array,
            user_email=None
        )

    @patch('analysis_pipeline.RepositoryProcessor')
    def test_repo_process_failure(self, mock_repoprocessor, pipeline):
        """Test error message when no repositories are processed"""
        git_repos = [{"path": "/repo1"}]
        pipeline.cli.get_input.side_effect = ["testuser", "test@email.com"]
        
        mock_processor = MagicMock()
        mock_processor.process_repositories.return_value = None
        mock_repoprocessor.return_value = mock_processor
        
        pipeline.run_repo_analysis_pipeline(git_repos, [])
        
        pipeline.cli.print_status.assert_any_call(
            "No repositores to process.", "error"
        )

    
    #Primary test for the entire repo analysis pipeline
    @patch('analysis_pipeline.rerank_projects')
    @patch('analysis_pipeline.choose_projects_for_analysis')
    @patch('analysis_pipeline.RepositoryAnalyzer')
    @patch('analysis_pipeline.ImportsExtractor')
    @patch('analysis_pipeline.RepositoryProcessor')
    def test_successful_pipeline_execution(
        self, mock_repoprocessor, mock_importprocessor,
        mock_repoanalyzer, mock_choose, 
        mock_rerank, pipeline
    ):
        """Test successful execution of the entire pipeline"""
        #fake data and fake user input
        git_repos = [{"path": "/repo1"}]
        pipeline.cli.get_input.side_effect = ["testuser", "test@email.com"]
        
        #setup arrays and data for test result
        processed_repos = [{"repo_name": "test-repo"}]
        selected_repos = [{"repo_name": "test-repo"}]
        analyzed_repos = [{"repository_name": "test-repo", "score": 10}]
        imports_data = [{"repository_name": "test-repo", "imports_summary": {"numpy": 5}}]
        timeline = [{"repo": "test-repo", "date": "2024-01"}]
        reranked_repos = [{"repository_name": "test-repo", "score": 15}]
        
        #mock repo_processor
        mock_processor = MagicMock()
        mock_processor.process_repositories.return_value = processed_repos
        mock_repoprocessor.return_value = mock_processor
        
        #mock user choosing
        mock_choose.return_value = selected_repos
        
        #Mock repo analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.generate_project_insights.return_value = analyzed_repos
        mock_analyzer.create_chronological_project_list.return_value = timeline
        mock_repoanalyzer.return_value = mock_analyzer
        
        #Mock Imports handler
        mock_imports = MagicMock()
        mock_imports.get_all_repo_import_stats.return_value = imports_data
        mock_importprocessor.return_value = mock_imports
        
        #Fake user reranking
        mock_rerank.return_value = reranked_repos
        
        #Actual Execution
        result = pipeline.run_repo_analysis_pipeline(git_repos, [])
        
        # Verify analyzer was initialized correctly
        mock_repoanalyzer.assert_called_once_with("testuser", "test@email.com")
        
        # Verify insights and imports were generated
        mock_analyzer.generate_project_insights.assert_called_once_with(selected_repos)
        mock_imports.get_all_repo_import_stats.assert_called_once_with(selected_repos)
        
        # Verify reranking happened
        mock_rerank.assert_called_once()
        
        # Verify timeline was created
        mock_analyzer.create_chronological_project_list.assert_called_once_with(reranked_repos)
        
        # Verify return values
        assert result == (git_repos, reranked_repos, timeline, processed_repos)
    
def test_metadata_pipeline():
    assert True

