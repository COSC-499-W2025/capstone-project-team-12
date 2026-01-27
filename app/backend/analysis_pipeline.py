import hashlib
from typing import List, BinaryIO, Dict, Any
from anytree import Node
from file_manager import FileManager
from repo_detector import RepoDetector
from file_classifier import FileClassifier
from repository_processor import RepositoryProcessor
from metadata_extractor import MetadataExtractor
from metadata_analyzer import MetadataAnalyzer
from repository_analyzer import RepositoryAnalyzer
from combined_preprocess import combined_preprocess
from pii_remover import remove_pii
from topic_vectors import generate_topic_vectors
from stats_cache import collect_stats
from cache.bow_cache import BoWCache, BoWCacheKey
from llm_online import OnlineLLMClient
from llm_local import LocalLLMClient
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from project_selection import choose_projects_for_analysis
from project_reranking import rerank_projects
from imports_extractor import ImportsExtractor

class AnalysisPipeline:
    
    #Dataclasses for bundling input data and result data
    class data_bundle_cls:
        def __init__(self):
            self.metadata_results: Dict[str, Dict[str, Any]] = []
            self.timeline: list = []
            self.dictionary = None
            self.lda_model = None
            self.final_bow = []
            self.processed_git_repos = []
        
    class result_bundle_cls:
        def __init__(self):
            self.metadata_analysis: dict[str,any]
            self.doc_topic_vectors: list = []
            self.topic_term_vectors: list = []
            self.project_analysis_data:dict= None
            self.medium_summary = ""   
    
    def __init__(self, cli, config_manager, database_manager):
        self.cli = cli
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.file_data_list: List = []
        self.file_classifer = FileClassifier()
        self.data_bundle = self.data_bundle_cls()
        self.result_bundle = self.result_bundle_cls()
        self.repo_detector = RepoDetector()

    #helpers from amin
    def get_bin_data_by_Id(self, bin_Idx: int) -> BinaryIO | None:
        if self.file_data_list is None or len(self.file_data_list) == 0:
            self.cli.print_status("Empty List: Initialize by calling File", "error")
            return None
        return self.file_data_list[bin_Idx]

    def get_bin_data_by_IdList(self, bin_Idx_list: List[int]) -> List[BinaryIO]:
        if self.file_data_list is None or len(self.file_data_list) == 0:
            self.cli.print_status("Empty List: Initialize by calling File", "error")
            return None
        
        response_List: List[BinaryIO | None] = []
        for bin_Idx in bin_Idx_list:
            response_List.append(self.get_bin_data_by_Id(bin_Idx))
        return response_List

    def get_bin_data_by_Nodes(self, nodes: List[Node]) -> List[BinaryIO | None]:
        if nodes is None:
            raise ValueError("Error preparing datalist in pipeline!: No nodes given!")
        
        IdList: List[int] = []
        for node in nodes:
            IdList.append(node.file_data['binary_index'])
        return self.get_bin_data_by_IdList(IdList)

    def binary_to_str(self, bin_data: List[BinaryIO]) -> List[str]:
        result = []
        for data in bin_data:
            try:
                result.append(data.decode('utf-8', errors='ignore') if data else '')
            except (AttributeError, UnicodeDecodeError):
                result.append('')
        return result

    def review_topic_bundle(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        provides a way for the user to edit the extracted topics before sending it to the llm
        allows users to view, edit (remove or replace) and confirm the extracted topics
        
        Args:
            bundle: Dictionary containing 'topic_keywords' (list of dicts with 'topic_id' and 'keywords')
            
        Returns:
            The modified bundle with updated topic_keywords.
        """
        topic_keywords = bundle.get('topic_keywords', [])
        
        if not topic_keywords:
            self.cli.print_status("No topics to review.", "warning")
            return bundle
        
        while True:
            choice = self.cli.display_topic_review_menu(topic_keywords)
            
            if choice == 'P':
                self.cli.print_status("Proceeding with current topics.", "success")
                break
            
            elif choice == 'E':
                #get the topic id to edit
                valid_ids = {topic['topic_id'] for topic in topic_keywords}
                topic_id_input = self.cli.get_input("\nEnter the Topic ID you want to edit: \n> ").strip()
                
                try:
                    topic_id = int(topic_id_input)
                except ValueError:
                    self.cli.print_status(f"Invalid input. '{topic_id_input}' is not a valid number.", "error")
                    continue
                
                if topic_id not in valid_ids:
                    self.cli.print_status(f"Topic ID {topic_id} does not exist. Valid IDs: {sorted(valid_ids)}", "error")
                    continue
                
                #find the topic dict
                topic_dict = None
                for t in topic_keywords:
                    if t['topic_id'] == topic_id:
                        topic_dict = t
                        break
                
                #enter the editing sub-loop
                while True:
                    self.cli.display_topic_edit_details(topic_dict)
                    action_type, index = self.cli.get_granular_input()
                    
                    if action_type == 'back':
                        #return to main menu
                        break
                    
                    elif action_type == 'del':
                        #delete entire topic
                        topic_keywords = [t for t in topic_keywords if t['topic_id'] != topic_id]
                        self.cli.print_status(f"Topic {topic_id} has been deleted.", "success")
                        break
                    
                    elif action_type == 'all':
                        #rewrite all keywords
                        new_keywords_input = self.cli.get_input("\nEnter the new comma-separated keywords: \n> ").strip()
                        new_keywords = [kw.strip() for kw in new_keywords_input.split(',') if kw.strip()]
                        topic_dict['keywords'] = new_keywords
                        self.cli.print_status(f"All keywords for Topic {topic_id} have been replaced.", "success")
                    
                    elif action_type == 'add':
                        #add new keyword
                        new_word = self.cli.get_input("\nEnter the new keyword to add: \n> ").strip()
                        if new_word:
                            topic_dict['keywords'].append(new_word)
                            self.cli.print_status(f"Added '{new_word}' to Topic {topic_id}.", "success")
                        else:
                            self.cli.print_status("No keyword entered. Nothing added.", "warning")
                    
                    elif action_type == 'replace_one':
                        #replace specific keyword at index
                        keywords = topic_dict.get('keywords', [])
                        if index < 0 or index >= len(keywords):
                            self.cli.print_status(f"Invalid index {index}. Valid range: 0 to {len(keywords) - 1}.", "error")
                        else:
                            old_word = keywords[index]
                            new_word = self.cli.get_input(f"\nReplace '{old_word}' with: \n> ").strip()
                            if new_word:
                                keywords[index] = new_word
                                self.cli.print_status(f"Replaced '{old_word}' with '{new_word}'.", "success")
                            else:
                                self.cli.print_status("No keyword entered. Nothing replaced.", "warning")
                    
                    elif action_type == 'remove_one':
                        # Remove specific keyword at index
                        keywords = topic_dict.get('keywords', [])
                        if index < 0 or index >= len(keywords):
                            self.cli.print_status(f"Invalid index {index}. Valid range: 0 to {len(keywords) - 1}.", "error")
                        else:
                            removed_word = keywords.pop(index)
                            self.cli.print_status(f"Removed '{removed_word}' from Topic {topic_id}.", "success")
                    
                    elif action_type == 'invalid':
                        # Invalid input, continue sub-loop to re-display options
                        continue
        
        bundle['topic_keywords'] = topic_keywords
        return bundle

    def load_files(self,filepath:str):
        """Validates and loads files from filepath using Filemanager"""
        self.cli.print_status("Loading file manager...", "info")

        file_manager = FileManager()
        fm_result: Dict[str, str | Node | None] = file_manager.load_from_filepath(filepath)

        if "status" not in fm_result:
            raise RuntimeError("FileManager did not return expected status.")

        if fm_result["status"] == "error":
            raise RuntimeError(f"Load Error: {fm_result.get('message', 'Unknown error')}")

        # Success path
        self.cli.print_status(f"File Manager: {fm_result.get('message', 'No message')}", "success")

        # Update internal state (formerly global file_data_list)
        self.file_data_list = fm_result.get("binary_data", [])
        if not self.file_data_list:
            self.cli.print_status("No binary data returned. Text preprocessing may fail.", "warning")
        else:
            self.cli.print_status(f"Loaded {len(self.file_data_list)} binary file(s).", "success")

        if "tree" not in fm_result or fm_result["tree"] is None:
            raise RuntimeError("FileManager did not return a tree.")
        
        return fm_result
            
    def save_results(self,data_bundle,results_bundle,return_id:bool = False)->str:
         # save tracked data and insights to database
        try:
            result_id: str = self.database_manager.create_new_result() 
            # save tracked data
            self.database_manager.save_tracked_data(result_id, data_bundle.metadata_results, data_bundle.final_bow, data_bundle.processed_git_repos)

            # save insights
            self.database_manager.save_metadata_analysis(result_id, results_bundle.metadata_analysis)
            self.database_manager.save_text_analysis(result_id, results_bundle.doc_topic_vectors, results_bundle.topic_term_vectors)
            self.database_manager.save_repository_analysis(result_id, results_bundle.project_analysis_data)
            self.database_manager.save_resume_points(result_id, results_bundle.medium_summary)
            if return_id:
                return result_id
        except Exception as e:
            self.cli.print_status(f"Error saving result to database: {e}", "error")
    
    def classify_files(self,filetree,binary_data):
        #classify and retrieve text and code files        
        textfile_nodes: List[Node] = []
        codefile_nodes: List[Node] = []
        try:
            
            textfile_nodes, codefile_nodes, binary_data = self.file_classifer.classify_files(filetree,binary_data)
            self.cli.print_status("File classification completed successfully.", "success")
        except Exception as e:
            self.cli.print_status(f"File Classifier error :{e}: Aborting analysis")
            return
        
        
        #identify and retrieve git repos:        
        git_repos: List[Node] = []
        try:
            self.repo_detector.process_git_repos(filetree)
            git_repos = self.repo_detector.get_git_repos()
            if git_repos:
                self.cli.print_status(f"Tree structure for .git repo processed successfully.", "success")
        except (ValueError, TypeError, RuntimeError) as e:
            self.cli.print_status(f"Failed to detect git repositories: {e}", "error")
            return
        except Exception as e:
            self.cli.print_status(f"Unexpected error detecting git repositories: {e}", "error")
            return
        
        return textfile_nodes,codefile_nodes,git_repos,binary_data
    
    def run_topic_analysis_pipeline(self,text_nodes,code_nodes):
    
        doc_topic_vectors: list = []
        topic_term_vectors: list = []
        dictionary = None
        lda_model = None
        final_bow = []

        try:
            
            if text_nodes or code_nodes:
                self.cli.print_header("Content Analysis")
                self.cli.print_status(f"Found {len(text_nodes)} text files and {len(code_nodes)} code files.", "info")
                self.cli.print_status("Running Bag-of-Words (BoW) pipeline...", "info")

                preprocess_signature = {
                    "lemmatizer": True,
                    "stopwords": "nltk_english_default",
                    "pii_removal": True,
                    "filters": ["text", "code"],
                    "normalize_code": True
                }

                all_nodes: List[Node] = text_nodes + code_nodes
                file_paths = [getattr(file, "filepath", str(file.name)) for file in all_nodes]
                joined_paths = "|".join(file_paths)
                repo_id = hashlib.md5(joined_paths.encode()).hexdigest()
                head_commit = None

                key = BoWCacheKey(repo_id, head_commit, preprocess_signature)
                cache = BoWCache()
                final_bow: List[List[str]] = []

                if cache.has(key):
                    cached = cache.get(key)
                    if cached is not None:
                        final_bow = cached
                        self.cli.print_status(f"Cache hit! Retrieved BoW for {len(final_bow)} documents.", "success")
                    else: 
                        self.cli.print_status("Cache corrupted - regenerating...", "warning")

                if not cache.has(key) or cached is None:
                    self.cli.print_status("Cache miss - processing text...", "info")
                    text_binary_data = self.get_bin_data_by_Nodes(text_nodes) if text_nodes else []
                    code_binary_data = self.get_bin_data_by_Nodes(code_nodes) if code_nodes else []
                    text_data = self.binary_to_str(text_binary_data) if text_nodes else []
                    code_data = self.binary_to_str(code_binary_data) if code_nodes else []

                    processed_docs = combined_preprocess(text_nodes, text_data, code_nodes, code_data, normalize=True)
                    anonymized_docs = remove_pii(processed_docs)
                    final_bow = anonymized_docs
                    cache.set(key, final_bow)
                    self.cli.print_status(f"Processed and cached {len(final_bow)} documents.", "success")

                self.cli.print_status("Generating topic models...", "info")
                lda_model, dictionary, doc_topic_vectors, topic_term_vectors = generate_topic_vectors(final_bow)
                self.cli.print_status(f"Generated {len(topic_term_vectors)} topics from {len(doc_topic_vectors)} documents.", "success")

                print("\n--- Top Topics Identified ---")
                for i in range(min(5, len(topic_term_vectors))):
                    top_words = lda_model.show_topic(i, topn=5)
                    words_str = ", ".join([word for word, prob in top_words])
                    print(f"Topic {i}: {words_str}")
                
                return lda_model,dictionary,doc_topic_vectors,topic_term_vectors,final_bow
                
            else:
                self.cli.print_status("No text/code files found to process.", "warning")
        except Exception as e:
           raise Exception(f"Error during topic analysis: {e}")
    
    def run_metadata_analysis_pipeline(self,text_nodes,code_nodes,binary_data):        
        self.cli.print_header("Metadata Analysis")
        metadata_extractor = MetadataExtractor()
        all_nodes = text_nodes + code_nodes
        metadata_results: Dict[str, Dict[str, Any]] = metadata_extractor.extract_all_metadata(all_nodes, binary_data)

        total_files: int = len(metadata_results)
        if total_files > 0:
            self.cli.print_status(f"Processed metadata for {total_files} files", "success")

        metadata_analyzer = MetadataAnalyzer(metadata_results)
        metadata_analysis = metadata_analyzer.analyze_all()
        
        print("\n--- File Extension Statistics ---")
        print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
        print("-" * 70)
        for ext, stats in metadata_analysis['extension_stats'].items():
            print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
        print(f"\nPrimary programming languages: {', '.join(metadata_analysis['primary_languages'])}\n")
        
        return metadata_results,metadata_analysis
    
    def run_repo_analysis_pipeline(self,git_repos,binary_data):
        processed_git_repos: List[Dict[str, Any]] = None
        analyzed_repos: List[Dict[str, Any]] = None

        if git_repos:
            self.cli.print_header("Repository Linking")
            print(f"Detected {len(git_repos)} git repositories.")

            github_username: str = self.cli.get_input("Enter GitHub username to link (Press Enter to skip): \n> ").strip().lower()
            
            if github_username:
                user_email: str = self.cli.get_input("Enter GitHub email associated with the account: \n> ").strip().lower()

                repo_processor = RepositoryProcessor(
                    username=github_username,
                    binary_data_array=binary_data,
                    user_email=user_email if user_email else None
                )
                
                try:
                    processed_git_repos = repo_processor.process_repositories(git_repos)
                    if not processed_git_repos:
                        self.cli.print_status("No repositores to process.", "error")
                    else:
                        for repo in processed_git_repos:
                            repo["name"] = (
                                repo.get("repo_name")
                                or repo.get("name")
                                or repo.get("repo_url")
                                or "Unnamed Repository"
                            )

                        # Allow user to choose which projects to analyze
                        selected_repos = choose_projects_for_analysis(processed_git_repos)
                        self.cli.print_status("Repositories processed successfully.", "success")
                        
                        analyzer = RepositoryAnalyzer(github_username, user_email)
                        imports_extractor = ImportsExtractor()

                        #Generate the insights for ALL selected projects (not just what is displayed to allow for storage in db)
                        analyzed_repos = analyzer.generate_project_insights(selected_repos)
                        imports_data = imports_extractor.get_all_repo_import_stats(selected_repos)

                        # merge imports_data back into analyzed_repos
                        for repo in analyzed_repos:
                            repo_name = repo.get('repository_name')
                            matching_import = next(
                                (imp for imp in imports_data if imp.get('repository_name') == repo_name),
                                None
                            )
                            if matching_import:
                                repo['imports_summary'] = matching_import.get('imports_summary', {})
                            else:
                                repo['imports_summary'] = {}

                        if not analyzed_repos:
                            self.cli.print_status("No successful repository analyses.", "warning")
                        else:
                            self.cli.print_status(f"Analyzed {len(analyzed_repos)} repositories.", "success")
                            # Allow user to rerank projects
                            self.cli.print_status("Ready to rank/re-rank projects.\n", "info")
                            analyzed_repos = rerank_projects(analyzed_repos)
                            # Generate the project timeline
                            timeline = analyzer.create_chronological_project_list(analyzed_repos)

                            # when generate_project_insights is run, the returned values are sorted by importance already
                            display_project_summary(analyzed_repos, top_n=3)

                            # display the detailed insights only for top 3 projects
                            display_project_insights(analyzed_repos, top_n=3)

                            display_project_timeline(timeline)
                            return git_repos,analyzed_repos,timeline,processed_git_repos
                        
                except Exception as e:
                    raise RuntimeError(f"Repository processing failed: {e}")
            else:
                self.cli.print_status("Skipping Git linking.", "info")
                return [],[],[],[]
        
    def run_AI_NLG(self,data_bundle,result_bundle,text_analysis_data):
        try:
            self.cli.print_header("AI Summary Generation")
            self.cli.print_status("Collecting analysis statistics...", "info")
            ai_data_bundle = collect_stats(
                metadata_stats=data_bundle.metadata_results,
                metadata_analysis=result_bundle.metadata_analysis,
                text_analysis=text_analysis_data,
                project_analysis=result_bundle.project_analysis_data
            )
            
            topn_keywords = 10
            topic_keywords = []
            if data_bundle.lda_model is not None and data_bundle.dictionary is not None:
                num_topics = len(result_bundle.topic_term_vectors) if result_bundle.topic_term_vectors else 0
                for topic_id in range(num_topics):
                    words = [w for (w, _) in data_bundle.lda_model.show_topic(topic_id, topn=topn_keywords)]
                    topic_keywords.append({"topic_id": topic_id, "keywords": words})

            doc_top_topics = []
            for doc_idx, vec in enumerate(result_bundle.doc_topic_vectors or []):
                if not vec:
                    doc_top_topics.append({"doc_id": doc_idx, "top_topics": []})
                    continue
                top_pairs = sorted([(i, p) for i, p in enumerate(vec)], key=lambda x: x[1], reverse=True)[:2]
                doc_top_topics.append({
                    "doc_id": doc_idx,
                    "top_topics": [{"topic_id": i, "prob": float(p)} for i, p in top_pairs]
                })

            topic_vector_bundle = {
                "topic_keywords": topic_keywords,
                "top_topics": doc_top_topics,
            }
            
            topic_vector_bundle = self.review_topic_bundle(topic_vector_bundle)

            #extract detected skills from metadata analysis
            detected_skills = []
            if result_bundle.metadata_analysis:
                primary_languages = result_bundle.metadata_analysis.get('primary_languages', [])
                primary_skills = result_bundle.metadata_analysis.get('primary_skills', [])
                #combine languages and skills, we can let the user decide on the scope
                seen = set()
                for skill in primary_languages + primary_skills:
                    if skill and skill not in seen:
                        detected_skills.append(skill)
                        seen.add(skill)
            
            user_highlights = []
            if detected_skills:
                user_highlights = self.cli.display_skill_selection_menu(detected_skills)
            
            #add the new highlights into the bundle
            topic_vector_bundle['user_highlights'] = user_highlights
            #allow user to review and edit topic keywords
            #no db saving for edited topic words tho (for now)
            
            
            self.cli.print_privacy_notice()

            online_consent = self.config_manager.get_consent(
                key="online_llm_consent",
                prompt_text="Do you consent to using the ONLINE LLM?",
                component="sending data to the Online LLM"
            )

            if online_consent:
                self.cli.print_status("Mode: Online LLM", "success")
                try:
                    llm_client = OnlineLLMClient()
                except ValueError as e:
                    self.cli.print_status(f"Online Init failed: {e}. Falling back to Local.", "error")
                    llm_client = LocalLLMClient()
            else:
                self.cli.print_status("Mode: Local LLM", "success")
                llm_client = LocalLLMClient()
            
            self.cli.print_status("Generating project summary (this may take a moment)...", "info")
            
            try:
                result_bundle.medium_summary = llm_client.generate_summary(topic_vector_bundle)
                self.cli.print_header("Standard Summary")
                print(result_bundle.medium_summary)
                print("=" * 60 + "\n")
                return result_bundle.medium_summary
                
            except Exception as e:
                raise RuntimeError(f"Error generating summary: {e}")
        except Exception as e:
            raise RuntimeError(f"Error collecting statistics: {e}")
    
    #main execution func
    def run_analysis(self, filepath: str,return_id = False) -> None|str:
        """
        Runs the various analysis pipelines in sequence. 
        Important Note: 
            - Early steps common to all pipelines return from function when error is encountered
            - When Pipelines encounter error, error is printed to console and next pipeline is executed.
        """
        #Load Files using Filemanager
        try:
            fm_result = self.load_files(filepath) #File loading logic in helper function
        except Exception as e:
            self.cli.print_status(f"File Manager Error:{e}","error")
            return
        
        #Load various parts of fm_result as vars for downstream use
        filetree:Node = fm_result["tree"] #Extract Filetree from fm_result
        
        binary_data: List[bytes] = fm_result.get("binary_data")
        if not isinstance(binary_data, list):
            self.cli.print_status("File Manager Error: Binary data not loaded. Aborting analysis.", " error") #changed because without any binary data cannot do any analysis
            binary_data = []
            return
       
        #classify loaded files in text or code and extract git repos
        try:
            textfile_nodes,codefile_nodes,git_repos,binary_data = self.file_classifer.classify_files(filetree,binary_data)
        except Exception as e:
            self.cli.print_status("File Classifier Error, Aborting analysis:{e}")
            
        #run metadata analysis
        try:
            self.data_bundle.metadata_results, self.result_bundle.metadata_analysis = self.run_metadata_analysis_pipeline(textfile_nodes,codefile_nodes,binary_data)
        except Exception as e:
            self.cli.print_status(f"Metadata Analysis Error:{e}","error")
       
        #run topic analysis_pipeline
        try:
            self.data_bundle.lda_model, self.data_bundle.dictionary, self.result_bundle.doc_topic_vectors, self.result_bundle.topic_term_vectors,self.data_bundle.final_bow = self.run_topic_analysis_pipeline(textfile_nodes,codefile_nodes)
        except Exception as e:
            self.cli.print_status(f"Topic Analysis Error: {e}","error")
        
        #run git_repo_analysis
        try:    
            git_repos,analyzed_repos,timeline,processed_git_repos = self.run_repo_analysis_pipeline(git_repos,binary_data)
        except Exception as e:
            self.cli.print_status(f"{e}","error")
            import traceback
            traceback.print_exc()
            
        text_analysis_data = {
            "num_documents": len(self.result_bundle.doc_topic_vectors),
            "num_topics": len(self.result_bundle.topic_term_vectors),
            "doc_topic_vectors": self.result_bundle.doc_topic_vectors,
            "topic_term_vectors": self.result_bundle.topic_term_vectors
        } if self.result_bundle.doc_topic_vectors else {}
        
        #Save project data to bundle
        self.result_bundle.project_analysis_data = {
            "analyzed_insights": analyzed_repos if analyzed_repos else [],
            "timeline": timeline if timeline else []
        } if git_repos else {}
        self.data_bundle.processed_git_repos = processed_git_repos
        
        #Run AI based Natural language generation
        self.result_bundle.medium_summary = self.run_AI_NLG(self.data_bundle,self.result_bundle,text_analysis_data)
        
        #Save All relevent input data and results to DB
        self.save_results(self.data_bundle,self.result_bundle)