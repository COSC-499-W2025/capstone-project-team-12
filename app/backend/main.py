import sys
import os
import pickle
from typing import List, Dict, Any
from pathlib import Path
from anytree.importer import DictImporter
from anytree.exporter import DictExporter
from config_manager import ConfigManager
from database_manager import DatabaseManager
from cli_interface import CLI
from analysis_pipeline import AnalysisPipeline
from main_utils import *
from input_validation import *
from resume_builder import ResumeBuilder
from resume_editor import ResumeEditor
from portfolio_builder import PortfolioBuilder
from portfolio_editor import PortfolioEditor
from file_manager import FileManager
from tree_manager import TreeManager

def main() -> None:
    cli, config_mgr = CLI(), ConfigManager()
    db_mgr, file_mgr = DatabaseManager(), FileManager()
    tree_mgr, pipeline = TreeManager(), AnalysisPipeline(cli, config_mgr, db_mgr)
    resume_builder, portfolio_builder = ResumeBuilder(), PortfolioBuilder()
    importer, exporter = DictImporter(), DictExporter()
    
    cli.print_header("Artifact Mining App")
    if not config_mgr.get_consent("file_access_consent", "Permission to access local files?", "accessing local files"):
        sys.exit("Access required.")

    while True:
        cli.print_separator("-")
        op = cli.get_input("Press: N (New), A (View All), V (View One), G (Generate), T (Thumbnail), U (Update), D (Delete), R (Reset), Q (Quit)\n> ").strip().lower()
        try:
            if op == 'n':
                path = validate_analysis_path(cli.get_input("Enter path: ").strip())
                res_id = pipeline.run_analysis(str(path), return_id=True)
                if cli.get_input("Add thumbnail? (y/N) ").lower() in ('y','yes'):
                    img = read_image(validate_thumbnail_path(cli.get_input("Image path: ")))
                    insert_thumbnail(db_mgr, cli, res_id, img)

            elif op == 'u':
                aid = cli.get_input("Analysis ID to update: ").strip()
                old_path = db_mgr.get_analysis_filepath(aid)
                if not old_path:
                    cli.print_status("ID not found.", "error"); continue
                
                print(f"Current path: {old_path}")
                new_path = cli.get_input(f"New path (Enter for '{old_path}'): ").strip() or old_path
                
                if Path(old_path).name != Path(new_path).name:
                    if cli.get_input("Paths look different. Continue? (y/n) ").lower() != 'y': continue

                res = file_mgr.load_from_filepath(new_path)
                if res['status'] == 'error': 
                    cli.print_status(res['message'], "error"); continue
                
                old_bin, old_tree_dict = db_mgr.get_fileset_data(aid)
                if not old_bin: 
                    cli.print_status("No previous data found.", "error"); continue

                merged_tree, merged_bin = tree_mgr.merge_trees(
                    importer.import_(old_tree_dict), pickle.loads(old_bin),
                    res['tree'], res['binary_data']
                )
                
                if db_mgr.save_fileset(aid, pickle.dumps(merged_bin), exporter.export(merged_tree), new_path):
                    cli.print_status("Update saved. Re-analyzing...", "success")
                    pipeline.run_analysis(new_path, existing_analysis_id=aid, preloaded_tree=merged_tree, preloaded_binary=merged_bin)

            elif op == 'a': view_all_results(db_mgr)
            elif op == 'v': view_result_by_id(db_mgr, cli, validate_uuid(cli.get_input("ID: ")))
            elif op == 'd': delete_result_by_id(db_mgr, cli, validate_uuid(cli.get_input("ID: ")))
            elif op == 'r': 
                if cli.get_input("Type 'CONFIRM DELETE': ") == "CONFIRM DELETE": delete_all_results(db_mgr)
            elif op == 'q': sys.exit(0)
            
            # ... (Existing G/T handlers abbreviated for brevity, keep logic same) ...

        except Exception as e:
            cli.print_status(f"Error: {e}", "error")
        input("Press Enter...")

if __name__ == "__main__":
    main()