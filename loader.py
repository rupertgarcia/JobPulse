import uuid
import pandas as pd
from sqlalchemy import text
from config import get_db_engine
from scraper import run_etl_pipeline

def load_data_to_postgres(df):
    """Inserts cleaned DataFrame records into MySQL relational tables."""
    engine = get_db_engine()
    
    master_skills = ['Python', 'React', 'Shopify', 'TypeScript', 'SQL', 'WordPress', 'PHP', 'JavaScript']
    
    with engine.begin() as conn:
        for skill in master_skills:
            conn.execute(
                text("INSERT INTO skills (name) VALUES (:name) ON DUPLICATE KEY UPDATE name=name;"),
                {"name": skill}
            )
            
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM skills;"))
        skill_map = {row.name: row.id for row in result}

    inserted_count = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            company_name = row.get('company', 'Unknown Company')
            if pd.isna(company_name):
                company_name = 'Unknown Company'
                
            conn.execute(
                text("INSERT INTO companies (name) VALUES (:name) ON DUPLICATE KEY UPDATE name=name;"),
                {"name": company_name}
            )
            res = conn.execute(
                text("SELECT id FROM companies WHERE name = :name;"),
                {"name": company_name}
            ).fetchone()
            company_id = res[0]

            job_url = row.get('job_url', '')
            if not job_url:
                continue
                
            existing_job = conn.execute(
                text("SELECT id FROM jobs WHERE job_url = :url;"),
                {"url": job_url}
            ).fetchone()

            if existing_job:
                job_id = existing_job[0]
            else:
                job_id = str(uuid.uuid4())
                # Note: Ensure your jobs table has a 'source' VARCHAR column if you want to store the board name
                conn.execute(
                    text("""
                        INSERT INTO jobs (id, title, company_id, location, job_url, description, posted_date)
                        VALUES (:id, :title, :company_id, :location, :job_url, :description, :posted_date);
                    """),
                    {
                        "id": job_id,
                        "title": row.get('title', 'Software Engineer'),
                        "company_id": company_id,
                        "location": row.get('location', 'Philippines'),
                        "job_url": job_url,
                        "description": row.get('clean_description', ''),
                        "posted_date": pd.to_datetime(row.get('posted_date', pd.Timestamp.now()))
                    }
                )
                inserted_count += 1

            skills_found = row.get('extracted_skills', [])
            for skill_name in skills_found:
                if skill_name in skill_map:
                    skill_id = skill_map[skill_name]
                    conn.execute(
                        text("""
                            INSERT IGNORE INTO job_skills (job_id, skill_id)
                            VALUES (:job_id, :skill_id);
                        """),
                        {"job_id": job_id, "skill_id": skill_id}
                    )

    print(f"ETL Complete: Successfully loaded {inserted_count} new unique jobs into MySQL.")

if __name__ == "__main__":
    df_cleaned = run_etl_pipeline()
    load_data_to_postgres(df_cleaned)