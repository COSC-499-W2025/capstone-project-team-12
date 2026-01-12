import hashlib
from typing import List, BinaryIO, Dict, Any
from anytree import Node
from file_manager import FileManager
from tree_processor import TreeProcessor
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

class AnalysisPipeline:
    def __init__(self, cli, config_manager, database_manager):
        self.cli = cli
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.file_data_list: List = []

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

    #main execution func
    def run_analysis(self, filepath: str) -> None:
        self.cli.print_status("Loading file manager...", "info")

        file_manager = FileManager()
        fm_result: Dict[str, str | Node | None] = file_manager.load_from_filepath(filepath)

        if "status" not in fm_result:
            self.cli.print_status("FileManager did not return expected status.", "error")
            return

        if fm_result["status"] == "error":
            self.cli.print_status(f"Load Error: {fm_result.get('message', 'Unknown error')}", "error")
            return

        # Success path
        self.cli.print_status(f"File Manager: {fm_result.get('message', 'No message')}", "success")

        # Update internal state (formerly global file_data_list)
        self.file_data_list = fm_result.get("binary_data", [])
        if not self.file_data_list:
            self.cli.print_status("No binary data returned. Text preprocessing may fail.", "warning")
        else:
            self.cli.print_status(f"Loaded {len(self.file_data_list)} binary file(s).", "success")

        if "tree" not in fm_result or fm_result["tree"] is None:
            self.cli.print_status("FileManager did not return a tree.", "error")
            return
        
        file_tree: Node = fm_result["tree"]

        try:
            tree_processor = TreeProcessor()
            processed_tree: Node = tree_processor.process_file_tree(file_tree)
            self.cli.print_status("Tree structure processed successfully.", "success")
        except (ValueError, TypeError, RuntimeError) as e:
            self.cli.print_status(f"Tree processing failed: {e}", "error")
            return
        except Exception as e:
            self.cli.print_status(f"Error processing tree: {e}", "error")
            return

        binary_data: List[bytes] = fm_result.get("binary_data")
        if not isinstance(binary_data, list):
            self.cli.print_status("Warning: Binary data format unexpected. Proceeding empty.", "warning")
            binary_data = []
        
        self.cli.print_header("Metadata Analysis")
        metadata_extractor = MetadataExtractor()
        metadata_results: Dict[str, Dict[str, Any]] = metadata_extractor.extract_all_metadata(processed_tree, binary_data)
        
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

        git_repos: List[Node] = tree_processor.get_git_repos() 

        doc_topic_vectors: list = []
        topic_term_vectors: list = []
        timeline: list = []
        dictionary = None
        lda_model = None
        final_bow = []
        medium_summary = ""

        try:
            text_nodes: List[Node] = tree_processor.get_text_files()
            code_nodes: List[Node] = tree_processor.get_code_files()
            
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
                
            else:
                self.cli.print_status("No text/code files found to process.", "warning")
        except Exception as e:
            self.cli.print_status(f"Error during content analysis: {e}", "error")

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
                        self.cli.print_status("Repositories processed successfully.", "success")
                        
                        analyzer = RepositoryAnalyzer(github_username)

                        #Generate the insights for ALL projects (not just what is displayed to allow for storage in db)
                        analyzed_repos = analyzer.generate_project_insights(processed_git_repos)

                        if not analyzed_repos:
                            self.cli.print_status("No successful repository analyses.", "warning")
                        else:
                            self.cli.print_status(f"Analyzed {len(analyzed_repos)} repositories.", "success")

                             # Infer user roles for each individual project
                            for repo in analyzed_repos:
                                role_info = analyzer.infer_user_role(repo)
                                repo['user_role'] = role_info['role']
                                repo['role_blurb'] = role_info['blurb']
                            
                            # Generate the project timeline
                            timeline = analyzer.create_chronological_project_list(processed_git_repos)

                            # when generate_project_insights is run, the returned values are sorted by importance already
                            display_project_summary(analyzed_repos, top_n=3)

                            # display the detailed insights only for top 3 projects
                            display_project_insights(analyzed_repos, top_n=3)

                            display_project_timeline(timeline)
                        
                except Exception as e:
                    self.cli.print_status(f"Repository processing failed: {e}", "error")
                    import traceback
                    traceback.print_exc()
            else:
                self.cli.print_status("Skipping Git linking.", "info")
        
        text_analysis_data = {
            "num_documents": len(doc_topic_vectors),
            "num_topics": len(topic_term_vectors),
            "doc_topic_vectors": doc_topic_vectors,
            "topic_term_vectors": topic_term_vectors
        } if doc_topic_vectors else {}
        
        project_analysis_data = {
            "analyzed_insights": analyzed_repos if analyzed_repos else [],
            "timeline": timeline if timeline else []
        } if git_repos else []
        
        try:
            self.cli.print_header("AI Summary Generation")
            self.cli.print_status("Collecting analysis statistics...", "info")
            data_bundle = collect_stats(
                metadata_stats=metadata_results,
                metadata_analysis=metadata_analysis,
                text_analysis=text_analysis_data,
                project_analysis=project_analysis_data
            )
            
            topn_keywords = 10
            topic_keywords = []
            if lda_model is not None and dictionary is not None:
                num_topics = len(topic_term_vectors) if topic_term_vectors else 0
                for topic_id in range(num_topics):
                    words = [w for (w, _) in lda_model.show_topic(topic_id, topn=topn_keywords)]
                    topic_keywords.append({"topic_id": topic_id, "keywords": words})

            doc_top_topics = []
            for doc_idx, vec in enumerate(doc_topic_vectors or []):
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
                medium_summary = llm_client.generate_summary(topic_vector_bundle)
                self.cli.print_header("Standard Summary")
                print(medium_summary)
                print("=" * 60 + "\n")
                
            except Exception as e:
                self.cli.print_status(f"Error generating summary: {e}", "error")
        
        except Exception as e:
            self.cli.print_status(f"Error collecting statistics: {e}", "error")

        # save tracked data and insights to database
        try:
            result_id: int = self.database_manager.create_new_result()
            # save tracked data
            self.database_manager.save_tracked_data(result_id, metadata_results, final_bow, processed_git_repos)

            # save insights
            self.database_manager.save_metadata_analysis(result_id, metadata_analysis)
            self.database_manager.save_text_analysis(result_id, doc_topic_vectors, topic_term_vectors)
            self.database_manager.save_repository_analysis(result_id, project_analysis_data)
            self.database_manager.save_resume_points(result_id, medium_summary)
        except Exception as e:
            self.cli.print_status(f"Error saving result to database: {e}", "error")