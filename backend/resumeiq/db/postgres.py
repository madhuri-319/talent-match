import os
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_DB", "resume_ranker"),
    "user": os.environ.get("POSTGRES_USER", "${username}"),
    "password": os.environ.get("POSTGRES_PASSWORD", "${password}"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_database_if_not_exists():
    """Create the database if it doesn't already exist."""
    db_name = DB_CONFIG["dbname"]
    config_without_db = {k: v for k, v in DB_CONFIG.items() if k != "dbname"}
    conn = psycopg2.connect(**config_without_db)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f'CREATE DATABASE "{db_name}"')
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    finally:
        conn.close()


def init_db():
    logger.info(f"Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}, database: {DB_CONFIG['dbname']}")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Update timestamp trigger function
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)

            # Candidates
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    linkedin_url VARCHAR(500),
                    skills JSONB,
                    total_experience_years INT,
                    current_company VARCHAR(255),
                    current_job_title VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)

            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_candidates_ts'
                    ) THEN
                        CREATE TRIGGER trg_candidates_ts
                        BEFORE UPDATE ON candidates
                        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
                    END IF;
                END $$;
            """)

            # Job Descriptions
            cur.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id SERIAL PRIMARY KEY,
                    job_title VARCHAR(255) NOT NULL,
                    job_type VARCHAR(20) DEFAULT 'full-time'
                        CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship')),
                    required_skills JSONB,
                    min_experience_years INT,
                    max_experience_years INT,
                    job_description TEXT,
                    qualifications TEXT,
                    number_of_positions INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)

            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_job_descriptions_ts'
                    ) THEN
                        CREATE TRIGGER trg_job_descriptions_ts
                        BEFORE UPDATE ON job_descriptions
                        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
                    END IF;
                END $$;
            """)

            # Applications
            cur.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    candidate_id INT NOT NULL,
                    job_id INT NOT NULL,
                    match_score DECIMAL(5, 2),
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (candidate_id, job_id),
                    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (job_id) REFERENCES job_descriptions(id)
                        ON DELETE CASCADE
                );
            """)

            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_applications_ts'
                    ) THEN
                        CREATE TRIGGER trg_applications_ts
                        BEFORE UPDATE ON applications
                        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
                    END IF;
                END $$;
            """)

            conn.commit()
            logger.info("All tables and triggers created successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()
