import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from db_utils import DB_connector

# new commit qebfkjebkjfe
# REMEMBER TO REPLACE THE FUNCT NAMES IN REPO

class DatabaseManager:
    def __init__(self):
        """Initialize database connection."""
        self.db = DB_connector()
    

    # old funct name: create_new_result(self) -> str:

    def create_analyses(self) -> str:
        """
        Create a new Analysis entry and initialize associated 1:1 records.
        Returns the analysis_id UUID (str).
        """
        try:
            #central record
            query = """
                INSERT INTO Analyses DEFAULT VALUES
                RETURNING analysis_id;
            """
            res_analysis = self.db.execute_update(query, returning=True)
            
            if not res_analysis:
                raise Exception("Failed to generate analysis_id")

            analysis_id = str(res_analysis['analysis_id'])
            a_uuid = uuid.UUID(analysis_id)

            #start child tables so that later on we can just update instead of inserting
            
            #results
            self.db.execute_update("INSERT INTO Results (analysis_id) VALUES (%s);", (a_uuid,))

            #tracked data
            self.db.execute_update("INSERT INTO Tracked_Data (analysis_id) VALUES (%s);", (a_uuid,))

            #resumes
            self.db.execute_update("INSERT INTO Resumes (analysis_id) VALUES (%s);", (a_uuid,))

            #portfolios
            self.db.execute_update("INSERT INTO Portfolios (analysis_id) VALUES (%s);", (a_uuid,))
            
            #we ar enot initializing fileset here
            #filesets are created only when files are actually uploaded via save_fileset.

            print(f"Created new analysis chain with ID: {analysis_id}")
            return analysis_id

        except Exception as e:
            print(f"Error creating new analyses: {e}")
            raise


    def save_fileset(self, analysis_id: str, file_binary: bytes, file_tree: Dict) -> bool:
        """
        Updates the Fileset (binary) for the analysis and appends the new filetree.
        Logic: 
        1. UPSERT the Filesets table (Ensure only 1 fileset row per analysis, update binary if exists).
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
                update_query = "UPDATE Filesets SET file_data = %s WHERE fileset_id = %s;"
                self.db.execute_update(update_query, (file_binary, fileset_id))
            else:
                #insert new fileset
                insert_query = """
                    INSERT INTO Filesets (analysis_id, file_data) 
                    VALUES (%s, %s) 
                    RETURNING fileset_id;
                """
                res = self.db.execute_update(insert_query, (uid, file_binary), returning=True)
                fileset_id = res['fileset_id']

            #add to filetree
            #just append new row here
            tree_query = "INSERT INTO Filetrees (fileset_id, filetree) VALUES (%s, %s);"
            self.db.execute_update(tree_query, (fileset_id, json.dumps(file_tree)))
            
            print(f"Saved fileset and tree for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Error saving fileset: {e}")
            return False

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
            print(f"Error saving metadata analysis: {e}")
            return False


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
            print(f"Error saving text analysis: {e}")
            return False
    #done
    #will probably have to modify the output for the llm results
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
            print(f"Error saving resume points: {e}")
            return False

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
            print(f"Error saving package insights: {e}")
            return False
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
            print(f"Error saving repository analysis: {e}")
            return False
    
    def save_tracked_data(
        self,
        analysis_id: str,
        metadata_results: Dict[str, Dict[str, Any]],
        bow_cache: Optional[List[List[str]]] = None,
        project_data: Optional[Dict[str, Any]] = None,
        package_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save raw data to Tracked_Data table and return success status (bool)."""
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
            print(f"Error saving tracked data: {e}")
            return False

    def save_resume_data(self, analysis_id: str, resume_data: Dict[str, Any]) -> bool:
        """
        Save detailed resume sections to the Resumes table.
        Expects keys: summary, projects, skills, languages, full_resume.
        """
        try:
            # Helper to optionally dump json
            def d(key): return json.dumps(resume_data.get(key)) if key in resume_data else None

            query = """
                UPDATE Resumes
                SET summary = COALESCE(%s, summary),
                    projects = COALESCE(%s, projects),
                    skills = COALESCE(%s, skills),
                    languages = COALESCE(%s, languages),
                    full_resume = COALESCE(%s, full_resume)
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(query, (
                d('summary'), d('projects'), d('skills'), d('languages'), d('full_resume'),
                uuid.UUID(analysis_id)
            ))
            
            print(f"Saved resume table data for analysis_id: {analysis_id}")
            return True
        except Exception as e:
            print(f"Error saving resume table data: {e}")
            return False

    def get_analysis_data(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete analysis data by joining all tables on analysis_id
        """
        try:
            query = """
                SELECT 
                    a.analysis_id,
                    r.topic_vector, r.resume_points, r.project_insights, r.package_insights, r.metadata_insights,
                    t.bow_cache, t.project_data, t.package_data, t.metadata_stats,
                    res.summary as resume_summary, res.full_resume, res.projects as resume_projects, res.skills as resume_skills
                FROM Analyses a
                LEFT JOIN Results r ON a.analysis_id = r.analysis_id
                LEFT JOIN Tracked_Data t ON a.analysis_id = t.analysis_id
                LEFT JOIN Resumes res ON a.analysis_id = res.analysis_id
                WHERE a.analysis_id = %s;
            """
            results = self.db.execute_query(query, (uuid.UUID(analysis_id),))
            
            if not results:
                return None

            #main result data
            row = results[0]
            

            return {
                "analysis_id": str(row['analysis_id']),
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
                }
            }
        except Exception as e:
            print(f"Error retrieving analysis: {e}")
            return None

    def get_all_results_summary(self) -> List[Dict[str, Any]]:
        """Retrieve a summary of all results from the database."""
        try:
            query = """
                SELECT r.analysis_id, r.metadata_insights 
                FROM Results r 
                JOIN Analyses a ON r.analysis_id = a.analysis_id 
                ORDER BY a.analysis_id;
            """
            results = self.db.execute_query(query)
            #convert UUID to string for JSON compatibility if needed later
            for result in results:
                result['analysis_id'] = str(result['analysis_id'])
            return results
        except Exception as e:
            print(f"Error retrieving all results: {e}")
            return []

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis and all associated data.
        Manually deletes children first in case ON DELETE CASCADE is missing in SQL.
        """
        try:
            uid = uuid.UUID(analysis_id)
            
            #1. Delete Filetrees (via Filesets lookup)
            #2. get rid of direct child tables
            #3. delete parent
            self.db.execute_update("""
                DELETE FROM Filetrees 
                WHERE fileset_id IN (SELECT fileset_id FROM Filesets WHERE analysis_id = %s);
            """, (uid,))
            
            #kill children
            self.db.execute_update("DELETE FROM Filesets WHERE analysis_id = %s;", (uid,))
            self.db.execute_update("DELETE FROM Tracked_Data WHERE analysis_id = %s;", (uid,))
            self.db.execute_update("DELETE FROM Results WHERE analysis_id = %s;", (uid,))
            self.db.execute_update("DELETE FROM Resumes WHERE analysis_id = %s;", (uid,))
            self.db.execute_update("DELETE FROM Portfolios WHERE analysis_id = %s;", (uid,))
            
            #kill parent
            self.db.execute_update("DELETE FROM Analyses WHERE analysis_id = %s;", (uid,))
            
            print(f"Successfully deleted analysis: {analysis_id}")
            return True
        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False

    def wipe_all_data(self) -> bool:
        """Delete all records from all tables."""
        try:
            query = "TRUNCATE TABLE Analyses, Filesets, Filetrees, Results, Tracked_Data, Resumes, Portfolios RESTART IDENTITY CASCADE;"
            self.db.execute_update(query)
            print("Successfully wiped all data.") 
            return True
        except Exception as e:
            print(f"Error wiping database tables: {e}")
            return False
    
    def save_analysis_thumbnail(self, analysis_id: str, data: BinaryIO) -> bool:
        """Update thumbnail image for a particular analysis result."""
        try:
            query = "UPDATE Results SET thumbnail_image = %s WHERE analysis_id = %s;"
            self.db.execute_update(query, (data, uuid.UUID(analysis_id)))
            
            print(f"Successfully added thumbnail image to analysis_id: {analysis_id}")
            return True
        except Exception as e:
            print(f"Error inserting image: {e}")
            return False
    
    def get_analysis_thumbnail(self,analysis_id):
        """Retrieve thumbnail image for a particular analysis result."""
        try:
            query = "SELECT thumbnail_image from Results WHERE analysis_id = %s;"
            result = self.db.execute_query(query, (analysis_id,))
            return result
        except Exception as e:
            raise Exception(f"Error Retrieving image: {e}")
             
    def close(self):
        """Close the database connection."""
        #DB_connector uses context managers, so connections auto-close
        pass