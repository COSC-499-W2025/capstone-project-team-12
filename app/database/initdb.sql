CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SELECT uuid_generate_v4();

CREATE TABLE IF NOT EXISTS
Analyses(
    analysis_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    analysis_title TEXT DEFAULT NULL,
    original_file_path text,  
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    thumbnail_image bytea DEFAULT NULL
    
);

CREATE TABLE IF NOT EXISTS
Filesets(
    fileset_id SERIAL PRIMARY KEY,
    analysis_id uuid NOT NULL UNIQUE REFERENCES Analyses(analysis_id) ON DELETE CASCADE,
    file_data bytea, 
    file_data_tree_id integer,
    latest_file_path text  
);

CREATE TABLE IF NOT EXISTS
Filetrees(
    filetree_id SERIAL PRIMARY KEY,
    fileset_id integer NOT NULL REFERENCES Filesets(fileset_id)ON DELETE CASCADE,
    filetree JSON
);

CREATE TABLE IF NOT EXISTS 
Tracked_Data(
    data_id SERIAL PRIMARY KEY,
    analysis_id uuid NOT NULL REFERENCES Analyses(analysis_id)  ON DELETE CASCADE,
    bow_cache JSON,
    project_data JSON,
    package_data JSON,
    metadata_stats JSON
);

CREATE TABLE IF NOT EXISTS 
Results(
    result_id SERIAL PRIMARY KEY,
    analysis_id uuid  NOT NULL REFERENCES Analyses(analysis_id) ON DELETE CASCADE,
    topic_vector JSON, 
    resume_points JSON,
    project_insights JSON,
    package_insights JSON,
    metadata_insights JSON
);

CREATE TABLE IF NOT EXISTS
Resumes(
 resume_id SERIAL PRIMARY KEY,
 resume_title TEXT DEFAULT NULL,
 analysis_id uuid NOT NULL REFERENCES Analyses(analysis_id) ON DELETE CASCADE,
 resume_data JSON
);

CREATE TABLE IF NOT EXISTS
Portfolios(
    portfolio_id SERIAL PRIMARY KEY,
    portfolio_title TEXT DEFAULT NULL,
    analysis_id uuid NOT NULL REFERENCES Analyses(analysis_id) ON DELETE CASCADE,
    portfolio_data JSON
    
);

ALTER TABLE Filesets
ADD CONSTRAINT latest_filetree_tracking
FOREIGN KEY (file_data_tree_id) REFERENCES Filetrees(filetree_id);

CREATE DATABASE test_db 
WITH TEMPLATE "user";