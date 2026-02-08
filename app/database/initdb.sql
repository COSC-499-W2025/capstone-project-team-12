CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SELECT uuid_generate_v4();

CREATE TABLE IF NOT EXISTS
Analyses(
    analysis_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    file_path text -- Added to track the original source path
);

CREATE TABLE IF NOT EXISTS
Filesets(
    fileset_id SERIAL PRIMARY KEY,
    analysis_id uuid REFERENCES Analyses(analysis_id) NOT NULL UNIQUE,
    file_data bytea, -- Stores the most recent binary blob (pickled list of bytes)
    file_data_tree_id integer,
    file_path text -- Added: Tracks the current path of this specific fileset version
);

CREATE TABLE IF NOT EXISTS
Filetrees(
    filetree_id SERIAL PRIMARY KEY,
    fileset_id integer REFERENCES Filesets(fileset_id),
    filetree JSON
);

CREATE TABLE IF NOT EXISTS 
Tracked_Data(
    data_id SERIAL PRIMARY KEY,
    analysis_id uuid REFERENCES Analyses(analysis_id) NOT NULL,
    bow_cache JSON,
    project_data JSON,
    package_data JSON,
    metadata_stats JSON
);

CREATE TABLE IF NOT EXISTS 
Results(
    result_id SERIAL PRIMARY KEY,
    analysis_id uuid REFERENCES Analyses(analysis_id) NOT NULL,
    topic_vector JSON, --changed to JSON for more flexibility--
    resume_points JSON,
    project_insights JSON,
    package_insights JSON,
    metadata_insights JSON,
    thumbnail_image bytea DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS
Resumes(
 resume_id SERIAL PRIMARY KEY,
 analysis_id uuid REFERENCES Analyses(analysis_id),
 summary JSON,
 projects JSON,
 skills JSON,
 languages JSON,
 full_resume JSON
);

CREATE TABLE IF NOT EXISTS
Portfolios(
    portfolio_id SERIAL PRIMARY KEY,
    analysis_id uuid REFERENCES Analyses(analysis_id)
);

ALTER TABLE Filesets
ADD CONSTRAINT latest_filetree_tracking
FOREIGN KEY (file_data_tree_id) REFERENCES Filetrees(filetree_id);

CREATE DATABASE test_db 
WITH TEMPLATE "user";