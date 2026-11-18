import uuid
import time
import pandas as pd
from sqlalchemy import text
from config import get_db_engine
from scraper import run_etl_pipeline

def load_data_to_database(df):
    """Inserts cleaned DataFrame records into MySQL relational tables with performance tracking."""
    start_time = time.time()
    engine = get_db_engine()
    
    master_skills = [
        'Python', 'React', 'Next.js', 'TypeScript', 'JavaScript', 
        'SQL', 'PostgreSQL', 'MySQL', 'PHP', 'Shopify', 'WordPress', 
        'Tailwind', 'Node.js', 'REST APIs', 'Docker'
    ]
    
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
    skipped_count = 0
    
    with engine.begin() as conn:
        for _, row in df.iterrows():
            company_name = row.get('company', 'Unknown Company')
            if pd.isna(company_name) or not company_name:
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
                skipped_count += 1
                job_id = existing_job[0]
            else:
                job_id = str(uuid.uuid4())
                
                # Sanitize values to prevent pandas NaN errors with MySQL
                min_sal = row.get('min_amount')
                max_sal = row.get('max_amount')
                min_sal = float(min_sal) if pd.notna(min_sal) else None
                max_sal = float(max_sal) if pd.notna(max_sal) else None

                job_type = row.get('job_type')
                job_type = str(job_type) if pd.notna(job_type) and job_type else 'Full-time'

                currency = row.get('currency')
                currency = str(currency) if pd.notna(currency) and currency else 'PHP'

                source_val = row.get('source')
                source_val = str(source_val) if pd.notna(source_val) and source_val else 'indeed'

                conn.execute(
                    text("""
                        INSERT INTO jobs (
                            id, title, company_id, location, job_url, description, 
                            posted_date, min_salary, max_salary, currency, job_type, source
                        )
                        VALUES (
                            :id, :title, :company_id, :location, :job_url, :description, 
                            :posted_date, :min_sal, :max_sal, :currency, :job_type, :source
                        );
                    """),
                    {
                        "id": job_id,
                        "title": row.get('title', 'Software Engineer'),
                        "company_id": company_id,
                        "location": row.get('location', 'Philippines'),
                        "job_url": job_url,
                        "description": row.get('clean_description', ''),
                        "posted_date": pd.to_datetime(row.get('posted_date', pd.Timestamp.now())),
                        "min_sal": min_sal,
                        "max_sal": max_sal,
                        "currency": currency,
                        "job_type": job_type,
                        "source": source_val
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

    elapsed_time = round(time.time() - start_time, 2)
    print("\n----------------------------------------")
    print(f"🚀 ETL Complete in {elapsed_time} seconds!")
    print(f"✅ Successfully inserted: {inserted_count} new unique jobs.")
    print(f"⏭️ Skipped duplicates: {skipped_count} jobs.")
    print("----------------------------------------")

if __name__ == "__main__":
    df_cleaned = run_etl_pipeline()
    load_data_to_database(df_cleaned)