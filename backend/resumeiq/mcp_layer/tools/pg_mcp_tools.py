import json
import os
import logging
import psycopg2
from psycopg2 import pool
from typing import Any, Literal
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_pg_tools")

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_DB", "talent_match"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
}

logger.info(f"[MCP-POSTGRES] Connected - host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, dbname={DB_CONFIG['dbname']}")

_connection_pool = None

def _get_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **DB_CONFIG
        )
    return _connection_pool

@contextmanager
def get_connection():
    pg_pool = _get_pool()
    conn = pg_pool.getconn()
    try:
        yield conn
    finally:
        pg_pool.putconn(conn)

def init_db():
    logger.info("[MCP-POSTGRES] init_db() called via MCP - creating tables...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    linkedin_url VARCHAR(500),
                    skills JSONB,
                    resume_parsed_data JSONB,
                    total_experience_years INT,
                    current_company VARCHAR(255),
                    current_job_title VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
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
                    environment_details JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
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
                    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
                    FOREIGN KEY (job_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
                );
            """)
            cur.execute("""
                DROP TRIGGER IF EXISTS update_candidates_timestamp ON candidates;
            """)
            cur.execute("""
                CREATE TRIGGER update_candidates_timestamp
                BEFORE UPDATE ON candidates
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            """)
            cur.execute("""
                DROP TRIGGER IF EXISTS update_job_descriptions_timestamp ON job_descriptions;
            """)
            cur.execute("""
                CREATE TRIGGER update_job_descriptions_timestamp
                BEFORE UPDATE ON job_descriptions
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            """)
            conn.commit()


def query_db(query: str, params: list | None = None) -> dict[str, Any]:
    logger.info(f"[MCP-POSTGRES] query_db() called - query={query[:50]}...")
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or [])
                if query.strip().upper().startswith("SELECT"):
                    if cur.description is None:
                        return {"rows": [], "count": 0}
                    columns = [desc[0] for desc in cur.description]
                    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
                    return {"rows": rows, "count": len(rows)}
                else:
                    conn.commit()
                    return {"rows_affected": cur.rowcount, "last_row_id": cur.lastrowid}
        except Exception as e:
            conn.rollback()
            logger.error(f"[MCP-POSTGRES] query_db() error - {str(e)}")
            return {"error": str(e)}


def _validate_candidate(data: dict) -> list[str]:
    errors = []
    required = ["first_name", "last_name", "email"]
    for field in required:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    if data.get("email") and "@" not in data["email"]:
        errors.append("Invalid email format")
    return errors

def _validate_job(data: dict) -> list[str]:
    errors = []
    if not data.get("job_title"):
        errors.append("Missing required field: job_title")
    if data.get("job_type") and data["job_type"] not in ("full-time", "part-time", "contract", "internship"):
        errors.append("Invalid job_type")
    return errors

def _validate_application(data: dict) -> list[str]:
    errors = []
    if not data.get("candidate_id"):
        errors.append("Missing required field: candidate_id")
    if not data.get("job_id"):
        errors.append("Missing required field: job_id")
    return errors


def insert_candidate(data: str) -> dict[str, Any]:
    try:
        candidate = json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] insert_candidate() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}"}
    
    logger.info(f"[MCP-POSTGRES] insert_candidate() called - email={candidate.get('email')}")
    
    validation_errors = _validate_candidate(candidate)
    if validation_errors:
        return {"error": "; ".join(validation_errors)}
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO candidates (first_name, last_name, email, phone, linkedin_url, skills, total_experience_years, current_company, current_job_title)
                    VALUES (%(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(linkedin_url)s, %(skills)s, %(total_experience_years)s, %(current_company)s, %(current_job_title)s)
                    RETURNING id
                """, {
                    "first_name": candidate.get("first_name"),
                    "last_name": candidate.get("last_name"),
                    "email": candidate.get("email"),
                    "phone": candidate.get("phone"),
                    "linkedin_url": candidate.get("linkedin_url"),
                    "skills": candidate.get("skills"),
                    "total_experience_years": candidate.get("total_experience_years"),
                    "current_company": candidate.get("current_company"),
                    "current_job_title": candidate.get("current_job_title"),
                })
                conn.commit()
                return {"id": cur.fetchone()[0]}
        except Exception as e:
            conn.rollback()
            logger.error(f"[MCP-POSTGRES] insert_candidate() error - {str(e)}")
            return {"error": str(e)}


def insert_job(data: str) -> dict[str, Any]:
    try:
        job = json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] insert_job() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}"}
    
    logger.info(f"[MCP-POSTGRES] insert_job() called - job_title={job.get('job_title')}")
    
    validation_errors = _validate_job(job)
    if validation_errors:
        return {"error": "; ".join(validation_errors)}
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO job_descriptions (job_title, job_type, required_skills, min_experience_years, max_experience_years, job_description, qualifications, number_of_positions, environment_details)
                    VALUES (%(job_title)s, %(job_type)s, %(required_skills)s, %(min_experience_years)s, %(max_experience_years)s, %(job_description)s, %(qualifications)s, %(number_of_positions)s, %(environment_details)s)
                    RETURNING id
                """, {
                    "job_title": job.get("job_title"),
                    "job_type": job.get("job_type", "full-time"),
                    "required_skills": job.get("required_skills"),
                    "min_experience_years": job.get("min_experience_years"),
                    "max_experience_years": job.get("max_experience_years"),
                    "job_description": job.get("job_description"),
                    "qualifications": job.get("qualifications"),
                    "number_of_positions": job.get("number_of_positions", 1),
                    "environment_details": job.get("environment_details"),
                })
                conn.commit()
                return {"id": cur.fetchone()[0]}
        except Exception as e:
            conn.rollback()
            logger.error(f"[MCP-POSTGRES] insert_job() error - {str(e)}")
            return {"error": str(e)}


def insert_application(data: str) -> dict[str, Any]:
    try:
        app = json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] insert_application() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}"}
    
    logger.info(f"[MCP-POSTGRES] insert_application() called - candidate_id={app.get('candidate_id')}, job_id={app.get('job_id')}")
    
    validation_errors = _validate_application(app)
    if validation_errors:
        return {"error": "; ".join(validation_errors)}
    
    with get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO applications (candidate_id, job_id, match_score)
                    VALUES (%(candidate_id)s, %(job_id)s, %(match_score)s)
                    RETURNING id
                """, app)
                conn.commit()
                return {"id": cur.fetchone()[0]}
        except Exception as e:
            conn.rollback()
            logger.error(f"[MCP-POSTGRES] insert_application() error - {str(e)}")
            return {"error": str(e)}


def get_candidates(filters: str = "{}") -> dict[str, Any]:
    try:
        filt = json.loads(filters)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] get_candidates() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}", "rows": [], "count": 0}
    
    logger.info(f"[MCP-POSTGRES] get_candidates() called - filters={filt}")
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM candidates WHERE 1=1"
            params = []
            if filt.get("is_active") is not None:
                query += " AND is_active = %s"
                params.append(filt["is_active"])
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
            return {"rows": rows, "count": len(rows)}


def get_jobs(filters: str = "{}") -> dict[str, Any]:
    try:
        filt = json.loads(filters)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] get_jobs() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}", "rows": [], "count": 0}
    
    logger.info(f"[MCP-POSTGRES] get_jobs() called - filters={filt}")
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT id, job_title, job_description, environment_details, created_at, updated_at, is_active FROM job_descriptions WHERE 1=1"
            params = []
            if filt.get("is_active") is not None:
                query += " AND is_active = %s"
                params.append(filt["is_active"])
            cur.execute(query, params)
            rows = []
            for row in cur.fetchall():
                row_dict = {
                    "id": row[0],
                    "job_title": row[1],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "is_active": row[6],
                }
                if row[2]:
                    job_desc = row[2]
                    if isinstance(job_desc, str):
                        job_desc = json.loads(job_desc)
                    row_dict["job_description"] = job_desc
                if row[3]:
                    env_details = row[3]
                    if isinstance(env_details, str):
                        env_details = json.loads(env_details)
                    row_dict["environment_details"] = env_details
                rows.append(row_dict)
            return {"rows": rows, "count": len(rows)}


def get_applications(filters: str = "{}") -> dict[str, Any]:
    try:
        filt = json.loads(filters)
    except json.JSONDecodeError as e:
        logger.error(f"[MCP-POSTGRES] get_applications() JSON parse error - {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}", "rows": [], "count": 0}
    
    logger.info(f"[MCP-POSTGRES] get_applications() called - filters={filt}")
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM applications WHERE 1=1"
            params = []
            if filt.get("candidate_id"):
                query += " AND candidate_id = %s"
                params.append(filt["candidate_id"])
            if filt.get("job_id"):
                query += " AND job_id = %s"
                params.append(filt["job_id"])
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
            return {"rows": rows, "count": len(rows)}