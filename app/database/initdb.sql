CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SELECT uuid_generate_v4();

CREATE TABLE IF NOT EXISTS
Analyses(
    analysis_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    fileset_id integer REFERENCES Filesets(fileset_id),
    data_id integer REFERENCES Tracked_Data(data_id),
    result_id integer REFERENCES Results(result_id),
    resume_id integer Results Resumes(resume_id),
    portfolio_id integer REFERENCES Portfolios(portfolio_id),
    
    
)

CREATE TABLE IF NOT EXISTS
Filesets(
    fileset_id SERIAL PRIMARY KEY,
    analysis_id uuid REFERENCES Analyses(analysis_id) NOT NULL
    file_data bytea -- Only the most recent set of binary data for the files is maintained. 
                    --But multiple trees can be maintained for the same analysis in Filetrees table
)

CREATE TABLE IF NOT EXISTS
Filetrees(
    filetree_id SERIAL PRIMARY KEY,
    fileset_id integer REFERENCES Filesets(fileset_id),
    filetree JSON
)

CREATE TABLE IF NOT EXISTS 
Tracked_Data(
    data_id SERIAL DEFAULT PRIMARY KEY,
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
 analysis_id integer REFERENCES Analyses(analysis_id),
 summary JSON,
 projects JSON,
 skills JSON,
 languages JSON,
 full_resume JSON
)
CREATE TABLE IF NOT EXISTS
Portfolios(
    portfolio_id SERIAL PRIMARY KEY,
    analysis_id integer REFERENCES Analyses(analysis_id)
    --TODO determine portfolio output columns

    
)

CREATE DATABASE test_db 
WITH TEMPLATE "user";