import sqlite3
import pandas as pd
import os

CSV_PATH = "cell-count.csv"
DB_PATH = "cell-count.db"

SCHEMA = """
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY
);

CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    condition  TEXT,
    age        INTEGER,
    sex        TEXT,
    treatment  TEXT,
    response   TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE samples (
    sample_id                   TEXT PRIMARY KEY,
    subject_id                  TEXT NOT NULL,
    sample_type                 TEXT,
    time_from_treatment_start   INTEGER,
    FOREIGN KEY (subject_id)    REFERENCES subjects(subject_id)
);

CREATE TABLE cell_counts (
    sample_id   TEXT NOT NULL,
    population  TEXT NOT NULL,
    count       INTEGER NOT NULL,
    PRIMARY KEY (sample_id, population),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);
"""

def main(): 

    df = pd.read_csv(CSV_PATH)

    if os.path.exists(DB_PATH) :
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    projects = df[["project"]].drop_duplicates()
    projects.columns = ["project_id"]
    projects.to_sql("projects", conn, if_exists = "append", index = False)

    subjects = df[["subject", "project", "condition", "age",
                "sex", "treatment", "response"]].drop_duplicates()
    subjects.columns = ["subject_id", "project_id", "condition", "age",
                        "sex", "treatment", "response"]
    subjects.to_sql("subjects", conn, if_exists = "append", index = False)
    
    samples = df[["sample", "subject", "sample_type",
                  "time_from_treatment_start"]].drop_duplicates()
    samples.columns = ["sample_id", "subject_id", "sample_type",
                       "time_from_treatment_start"]
    samples.to_sql("samples", conn, if_exists = "append", index = False)

    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    cell_counts = df.melt(
        id_vars = ["sample"],
        value_vars = populations,
        var_name = "population", 
        value_name = "count"
    )
    cell_counts.columns = ["sample_id", "population", "count"]
    cell_counts.to_sql("cell_counts", conn, if_exists = "append", index = False)

    conn.commit()
    conn.close()
    print(f"Done. Database written to {DB_PATH}")
    print(f" {len(projects)} projects, {len(subjects)} subjects, "
          f" {len(samples)} samples, {len(cell_counts)} cell-count rows")
    
if __name__ == "__main__":
    main()