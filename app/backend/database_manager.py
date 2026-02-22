import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from db_utils import DB_connector

class DatabaseManager:
    """Primary Database interaction class for all downstream modules. 
        For saves/inserts/delete methods returns true on success and raises RuntimeError on failure 
        For gets/get_all methods returns the requested result and LookupError on failure"""
    def __init__(self):
        """Initialize database connection."""
        self.db = DB_connector()
    

    # old funct name: create_new_result(self) -> str:
    def create_analysis(self, file_path: str = None) -> str:
        """
        Create a new Analysis entry and initialize associated 1:1 records.
        Returns the analysis_id UUID (str).
        """
        try:
            #central record
            # Updated to include original_file_path
            query = """
                INSERT INTO Analyses (original_file_path)
                VALUES (%s)
                RETURNING analysis_id;
            """
            res_analysis = self.db.execute_update(query, (file_path,), returning=True)
            
            if not res_analysis:
                raise Exception("Failed to generate analysis_id")

            analysis_id = str(res_analysis[0]['analysis_id'])
            a_uuid = uuid.UUID(analysis_id)

            #start child tables so that later on we can just update instead of inserting
            
            #results
            self.db.execute_update("INSERT INTO Results (analysis_id) VALUES (%s);", (a_uuid,))

            #tracked data
            self.db.execute_update("INSERT INTO Tracked_Data (analysis_id) VALUES (%s);", (a_uuid,))

            #resume and portfolio row init removed, there can be multiple resumes and portfolios.
            #save_resume,update_resume,save_portfolio,update_portfolio methods manage insert and update as necessary
                        
            #we ar enot initializing fileset here
            #filesets are created only when files are actually uploaded via save_fileset.

            print(f"Created new analysis chain with ID: {analysis_id}")
            return analysis_id

        except Exception as e:
            raise RuntimeError(f"Error creating new analyses: {e}")

    def get_analysis_filepath(self, analysis_id: str) -> Optional[str]:
        """
        Retrieve the current file path associated with an analysis ID.
        Prioritizes the path in Filesets (current) over Analyses (original).
        """
        try:
            query = """
                SELECT f.latest_file_path as current_path, a.original_file_path as original_path
                FROM Analyses a
                LEFT JOIN Filesets f ON a.analysis_id = f.analysis_id
                WHERE a.analysis_id = %s;
            """
            result = self.db.execute_query(query, (uuid.UUID(analysis_id),))
            if result:
                return result[0]['current_path'] or result[0]['original_path']
            return None
        except Exception as e:
            raise LookupError(f"Error fetching analysis file path: {e}")
    

    def get_fileset_data(self, analysis_id: str) -> Tuple[Optional[bytes], Optional[Dict]]:
        """
        Retrieves the binary file_data and the latest filetree for an analysis.
        """
        try:
            uid = uuid.UUID(analysis_id)
            
            query = """
                SELECT fs.file_data, ft.filetree
                FROM Filesets fs
                LEFT JOIN Filetrees ft ON fs.file_data_tree_id = ft.filetree_id
                WHERE fs.analysis_id = %s;
            """
            results = self.db.execute_query(query, (uid,))
            
            if not results:
                return None, None
            
            row = results[0]
            binary_data = bytes(row['file_data']) if row['file_data'] else None
            tree_data = row['filetree']
            
            return binary_data, tree_data

        except Exception as e:
            print(f"Error fetching fileset data: {e}")
            raise LookupError

    def save_fileset(self, analysis_id: str, file_binary: bytes, file_tree: Dict, file_path: str) -> bool:
        """
        Updates the Fileset (binary) for the analysis and appends the new filetree.
        Logic: 
        1. UPDATE the Filesets table (Ensure only 1 fileset row per analysis, update binary if exists).
        2. INSERT the new tree into Filetrees linked to that fileset.
        """
        try:
            uid = uuid.UUID(analysis_id)
            
            #check if fileset exists to determine INSERT or UPDATE
            check_query = "SELECT fileset_id FROM Filesets WHERE analysis_id = %s;"
            existing = self.db.execute_query(check_query, (uid,))
            if existing:
                #update existing binary
                fileset_id = existing[0]['fileset_id']
                # Updated to update latest_file_path
                update_query = "UPDATE Filesets SET file_data = %s, latest_file_path = %s WHERE fileset_id = %s;"
                self.db.execute_update(update_query, (file_binary, file_path, fileset_id))
            else:
                #insert new fileset
                # Updated to insert latest_file_path
                insert_query = """
                    INSERT INTO Filesets (analysis_id, file_data, latest_file_path) 
                    VALUES (%s, %s, %s) 
                    RETURNING fileset_id;
                """
                res = self.db.execute_update(insert_query, (uid, file_binary, file_path), returning=True)
                # Correctly using [0] here as db_utils now returns list
                fileset_id = res[0]['fileset_id']

            #add to filetree
            #just append new row here
            tree_query = "INSERT INTO Filetrees (fileset_id, filetree) VALUES (%s, %s) RETURNING filetree_id;"
            tree_res = self.db.execute_update(tree_query, (fileset_id, json.dumps(file_tree)),returning=True)
            print(f"Saved fileset (path: {file_path}) and tree for analysis_id: {analysis_id}")
            
            try:
                if not fileset_id:
                    print (f"Error associating new tree to updated fileset, defaulted to NULL: Invalid or Null fileset_id")
                    raise ValueError
                
                new_tree_id = tree_res[0]['filetree_id']
                
                #Set returning=False because this UPDATE statement does not return anything
                fileset_tree_query = "UPDATE Filesets SET file_data_tree_id = %s WHERE fileset_id = %s;"
                self.db.execute_update(fileset_tree_query, (new_tree_id, fileset_id), returning=False)
                
            except Exception as e:
                raise RuntimeError(f"Error associating new tree to updated fileset, defaulted to NULL: Failed Query execution:{e}") # Add custom raised error to identify association failure instead of fileset failure
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error saving fileset: {e}")

    def save_metadata_analysis(self, analysis_id: str, metadata_insights: Dict[str, Any]) -> bool:
        """Save metadata analysis results to the Results table."""
        try:
            query = """
                UPDATE Results
                SET metadata_insights = %s
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query, 
                (json.dumps(metadata_insights, default=str), uuid.UUID(analysis_id))
            )
            
            #good till now
            print(f"Saved metadata analysis for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error saving metadata analysis: {e}")


    #updated
    def save_text_analysis(
        self,
        analysis_id: str,
        doc_topic_vectors: List[List[float]],
        topic_term_vectors: List[List[Tuple[str, float]]]
    ) -> bool:
        """Save text analysis topic vectors to the database and return success status (bool)."""
        try:
            topic_data = {
                "doc_topic_vectors": doc_topic_vectors,
                "topic_term_vectors": topic_term_vectors
            }
            
            query = """
                UPDATE Results
                SET topic_vector = %s
                WHERE analysis_id = %s;
            """
            self.db.execute_update(query, (json.dumps(topic_data), uuid.UUID(analysis_id)))
            print(f"Saved text analysis for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error saving text analysis: {e}")

    def save_resume_points(self, analysis_id: str, points: List[str]) -> bool:
        """Save generated resume points to the Results table."""
        try:
            query = """
                UPDATE Results
                SET resume_points = %s
                WHERE analysis_id = %s;
            """
            self.db.execute_update(query, (json.dumps(points), uuid.UUID(analysis_id)))
            print(f"Saved resume points for analysis_id: {analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error saving resume points: {e}")

    #done
    def save_package_analysis(self, analysis_id: str, insights: Dict[str, Any]) -> bool:
        """Save package analysis insights to the Results table."""
        try:
            query = """
                UPDATE Results
                SET package_insights = %s
                WHERE analysis_id = %s;
            """
            self.db.execute_update(query, (json.dumps(insights), uuid.UUID(analysis_id)))
            print(f"Saved package insights for analysis_id: {analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error saving package insights: {e}")
    #updated
    def save_repository_analysis(
        self,
        analysis_id: str,
        project_analysis_data: Dict[str, Any]
    ) -> bool:
        """Save repository analysis results to the database and return success status (bool).
        Includes the processed repositories, analyzed insights, and the timeline with the relevant 
        project data.
        Thus project_analysis_data: Dict contaning:
            - analyzed_insights: Detailed project insights generated for ALL projects
            - timeline: Basic project information sorted in chronological order for timeline output
        
        """
        try:
            query = """
                UPDATE Results
                SET project_insights = %s
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query,
                (json.dumps(project_analysis_data, default=str), uuid.UUID(analysis_id))
            )
            
            print(f"Saved repository analysis for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error saving repository analysis: {e}")
    
    def save_tracked_data(
        self,
        analysis_id: str,
        metadata_results: Dict[str, Dict[str, Any]],
        bow_cache: Optional[List[List[str]]] = None,
        project_data: Optional[Dict[str, Any]] = None,
        package_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save raw data to Tracked_Data table and return true on success otherwise raises error."""
        try:
            query = """
                UPDATE Tracked_Data
                SET metadata_stats = %s,
                    bow_cache = COALESCE(%s, bow_cache),
                    project_data = COALESCE(%s, project_data),
                    package_data = COALESCE(%s, package_data)
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query,
                (
                    json.dumps(metadata_results),
                    json.dumps(bow_cache) if bow_cache is not None else None,
                    json.dumps(project_data, default=str) if project_data is not None else None,
                    json.dumps(package_data) if package_data is not None else None,
                    uuid.UUID(analysis_id)
                )
            )
            print(f"Saved tracked data for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error saving tracked data: {e}")

    def save_resume(self,analysis_id:str,resume_data:Dict[str,Any],resume_title:str = None)->int:
        """
        Insert new resume into the Resumes table with new data
        resume_title is optional, set to None to skip it , also default value
        """
        try:
            if not resume_data:
                raise RuntimeError(f"Empty resume data passed to db manager")
            
            query = """
                INSERT INTO Resumes (resume_title,analysis_id,resume_data)
                VALUES (%s, %s ,%s) RETURNING resume_id;
            """
            resume_json = json.dumps(resume_data)
        
            result = self.db.execute_update(query, (resume_title,analysis_id,resume_json),returning=True)
            resume_id = result[0] #get returned new resume_id
            print(f"Saved new resume with resume id:{resume_id} to db for analysis_id:{analysis_id}")
            return resume_id
        
        except Exception as e:
            raise RuntimeError(f"Error saving new resume: {e}")
        
        
    def update_resume(self, resume_id: str, resume_data: Dict[str, Any],resume_title=None) -> bool:
        """
        Update existing resume in the Resumes table with new data
        resume_title is optional, set to None to skip it , also default value
        """
        try:
            if not resume_data:
                raise RuntimeError(f"Empty resume data passed to db manager")
            
            query = """
                UPDATE Resumes
                SET (resume_data,resume_title) = (%s,%s)
                WHERE resume_id = %s RETURNING analysis_id;
            """
            resume_json = json.dumps(resume_data)
        
            result = self.db.execute_update(query, (resume_json,resume_title,resume_id))
            analysis_id = result[0] #get analysis_id of associated analysis
            print(f"Successfully updated resume with resume_id:{resume_id} for analysis id:{analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error updating resume with resume_id{resume_id}: {e}")
        
    def save_portfolio(self,analysis_id:str,portfolio_data:Dict[str,Any],portfolio_title:str = None)->bool:
        """
        Insert new Portfolio into the Resumes table with new data
        portfolio_title is optional, set to None to skip it , also default value
        """
        try:
            if not portfolio_data:
                raise RuntimeError(f"Empty portfolio data passed to db manager")
            
            query = """
                INSERT Into Portfolios (portfolio_title,analysis_id,portfolio_data)
                VALUES (%s, %s ,%s) RETURNING resume_id;
            """
            portfolio_json = json.dumps(portfolio_data)
        
            result = self.db.execute_update(query, (portfolio_title,analysis_id,portfolio_json),returning=True)
            portfolio_id = result[0] #get returned new resume_id
            print(f"Saved new portfolio with portfolio_id:{portfolio_id} to db for analysis_id:{analysis_id}")
            return True
        
        except Exception as e:
            raise RuntimeError(f"Error saving new portfolio:{e}")
        
        
    def update_portfolio(self, portfolio_id: str, portfolio_data: Dict[str, Any],portfolio_title=None) -> bool:
        """
        Update existing portfolio in the Portfolio table with new data
        portfolio_title is optional, set to None to skip it , also default value
        """
        try:
            if not portfolio_data:
                raise RuntimeError(f"Empty portfolio data passed to db manager")
            
            query = """
                UPDATE Portfolios
                SET (portfolio_data,portfolio_title) = (%s,%s)
                WHERE portfolio_id = %s RETURNING analysis_id;
            """
            portfolio_json = json.dumps(portfolio_data)
        
            result = self.db.execute_update(query, (portfolio_json,portfolio_title,portfolio_id))
            analysis_id = result[0] #get analysis_id of associated analysis
            print(f"Successfully updated portfolio with portfolio_id:{portfolio_id} for analysis id:{analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error updating portfolio with portfolio_id:{portfolio_id}: {e}")
   
    def get_all_resumes(self):
        try:
            query = """
                SELECT * FROM Resumes 
            """
            
            result = self.db.execute_query(query,())
            
            if not result:
                raise LookupError("Database returned None")
            return result
        except Exception as e:
            raise LookupError(f"Error retrieving Resumes:{e}")
    

    def get_resumes_by_analysis_id(self,analysis_id:str):
        try:
            query = """
                SELECT * from Resumes res WHERE res.analysis_id = %s
            """
            
            result = self.db.execute_query(query,(analysis_id,))
            
            if not result:
                raise LookupError("Database returned None")
            return result
        
        except Exception as e:
            raise LookupError(f"Error retrieving Resumes for analysis_id: {analysis_id}:{e}")
    
    def get_resume_by_resume_id(self,resume_id:int):
        try:
            if not isinstance(resume_id,int):
                raise ValueError(f"Invalid resume_id")
            
            query = """Select * from Resumes res WHERE res.resume_id = %s"""
            
            result = self.db.execute_query(query,(resume_id,))    

            if not result:
                raise LookupError("Database returned None")
            return result
        except Exception as e:
            raise LookupError(f"Error retrieving resume for resume_id{resume_id}: {e}")   

    def get_all_portfolios(self):
        try:
            query = """
                SELECT * FROM Portfolios 
            """
            
            result = self.db.execute_query(query,())
            
            if not result:
                raise LookupError("Database returned None")
            return result
        except Exception as e:
            raise LookupError(f"Error retrieving Portfolios:{e}")
    
    def get_portfolios_by_analysis_id(self,analysis_id:str):
        try:
            query = """
                SELECT * from Portfolios port WHERE port.analysis_id = %s
            """
            
            result = self.db.execute_query(query,(analysis_id,))
            
            if not result:
                raise LookupError("Database returned None")
            return result
        except Exception as e:
            raise LookupError(f"Error retrieving Resumes for analysis_id: {analysis_id}:{e}")
    
    def get_portfolio_by_portfolio_id(self,portfolio_id:int):
        try:
            if not isinstance(portfolio_id,int):
                raise ValueError(f"Invalid portfolio_id")
            
            query = """Select * from portfolio port WHERE port.portfolio_id = %s"""
            
            result = self.db.execute_query(query,(portfolio_id,))    

            if not result:
                raise LookupError("Database returned None")
            return result
        except Exception as e:
            raise LookupError(f"Error retrieving portfolio for portfolio_id{portfolio_id}: {e}")   

        
    def get_analysis_data(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete analysis data by joining all tables on analysis_id
        """
        try:
            query = """
                SELECT 
                    a.analysis_id,a.analysis_title,
                    r.topic_vector, r.resume_points, r.project_insights, r.package_insights, r.metadata_insights,
                    t.bow_cache, t.project_data, t.package_data, t.metadata_stats,
                    res.resume_data,
                    port.portfolio_data
                FROM Analyses a
                LEFT JOIN Results r ON a.analysis_id = r.analysis_id
                LEFT JOIN Tracked_Data t ON a.analysis_id = t.analysis_id
                LEFT JOIN Resumes res ON a.analysis_id = res.analysis_id
                LEFT JOIN Portfolios port ON a.analysis_id = port.analysis_id
                WHERE a.analysis_id = %s;
            """
            results = self.db.execute_query(query, (uuid.UUID(analysis_id),))
            
            if not results:
                raise LookupError("Database returned None")

            #main result data
            row = results[0]
            

            return {
                "analysis_id": str(row['analysis_id']),
                "analysis_title":str(row['analysis_title']),
                "topic_vector": row['topic_vector'],
                "resume_points": row['resume_points'],
                "project_insights": row['project_insights'],
                "package_insights": row['package_insights'],
                "metadata_insights": row['metadata_insights'],
                "tracked_data": {
                    "bow_cache": row['bow_cache'],
                    "project_data": row['project_data'],
                    "package_data": row['package_data'],
                    "metadata_stats": row['metadata_stats']
                },
                "resume_data":row['resume_data'],
                "portfolio_data":row['portfolio_data']
            }
        except Exception as e:
            raise LookupError(f"Error retrieving analysis: {e}")

    def get_all_analyses_summary(self) -> List[Dict[str, Any]]:
        """Retrieve a summary of all results from the database."""
        try:
            # Updated to use latest_file_path and original_file_path
            query = """
                SELECT r.analysis_id,a.analysis_title, r.metadata_insights, r.project_insights, COALESCE(f.latest_file_path, a.original_file_path) as file_path
                FROM Results r 
                JOIN Analyses a ON r.analysis_id = a.analysis_id 
                LEFT JOIN Filesets f ON r.analysis_id = f.analysis_id
                ORDER BY a.analysis_id;
            """
            results = self.db.execute_query(query)
            #convert UUID to string for JSON compatibility if needed later
            for result in results:
                result['analysis_id'] = str(result['analysis_id'])
            return results
        except Exception as e:
            raise LookupError(f"Error retrieving all results: {e}")

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis and all associated data.
        """
        try:
            uid = uuid.UUID(analysis_id)
            
            #Cascade added to db, manual deletion of children not required
            
            #kill parent
            self.db.execute_update("DELETE FROM Analyses WHERE analysis_id = %s;", (uid,))
            
            print(f"Successfully deleted analysis: {analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error deleting analysis: {e}")

    def wipe_all_data(self) -> bool:
        """Delete all records from all tables."""
        try:
            query = "TRUNCATE TABLE Analyses, Filesets, Filetrees, Results, Tracked_Data, Resumes, Portfolios RESTART IDENTITY CASCADE;"
            self.db.execute_update(query)
            print("Successfully wiped all data.") 
            return True
        except Exception as e:
            raise RuntimeError(f"Error wiping database tables: {e}")
    
    def save_analysis_thumbnail(self, analysis_id: str, data: BinaryIO) -> bool:
        """Update thumbnail image for a particular analysis."""
        try:
            query = "UPDATE Analyses SET thumbnail_image = %s WHERE analysis_id = %s;"
            self.db.execute_update(query, (data, uuid.UUID(analysis_id)))
            
            print(f"Successfully added thumbnail image to analysis_id: {analysis_id}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error inserting image: {e}")

    
    def get_analysis_thumbnail(self,analysis_id):
        """Retrieve thumbnail image for a particular analysis."""
        try:
            query = "SELECT thumbnail_image from Analyses WHERE analysis_id = %s;"
            result = self.db.execute_query(query, (analysis_id,))
            return result
        except Exception as e:
            raise LookupError(f"Error Retrieving image: {e}")
             
    
    def close(self):
        """Close the database connection."""
        #DB_connector uses context managers, so connections auto-close
        pass