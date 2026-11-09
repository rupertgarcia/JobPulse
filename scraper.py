import re
from datetime import datetime
import pandas as pd
from jobspy import scrape_jobs

def fetch_philippine_jobs(search_terms=["Software Engineer", "Full Stack Developer", "Python Developer"], location="Philippines", results_wanted=20):
    """Fetches live job postings across platforms tailored to the Philippines."""
    all_jobs = []
    
    for term in search_terms:
        print(f"Fetching live jobs for '{term}' in '{location}'...")
        try:
            df_jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter"],
                search_term=term,
                location=location,
                results_wanted=results_wanted,
                hours_old=168, # Last 7 days
                country_indeed='Philippines'
            )
            if not df_jobs.empty:
                all_jobs.append(df_jobs)
        except Exception as e:
            print(f"Scraping failed for term '{term}': {e}")
            
    if all_jobs:
        combined_df = pd.concat(all_jobs, ignore_index=True)
        # Drop duplicate URLs if multiple search terms return the same job
        combined_df = combined_df.drop_duplicates(subset=['job_url'])
        print(f"Successfully scraped {len(combined_df)} unique jobs in the Philippines.")
        return combined_df
    else:
        print("Live scraping returned no results. Falling back to sample dataset.")
        return get_fallback_jobs()

def get_fallback_jobs():
    """Provides fallback sample data if live scraping encounters rate limits."""
    return pd.DataFrame([
        {
            "title": "Python / Django Developer",
            "company": "Manila Tech Solutions",
            "location": "Taguig, Metro Manila, PH",
            "job_url": "https://ph.indeed.com/viewjob?jk=example1",
            "site": "indeed",
            "description": "<p>Looking for a Python Developer experienced in SQL, React, and building REST APIs.</p>",
            "date_posted": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "title": "Shopify E-Commerce Specialist",
            "company": "Cebu Digital Hub",
            "location": "Cebu City, PH",
            "job_url": "https://www.linkedin.com/jobs/view/example2",
            "site": "linkedin",
            "description": "Seeking a developer skilled in Shopify theme development, WordPress, PHP, and JavaScript.",
            "date_posted": datetime.now().strftime('%Y-%m-%d')
        }
    ])

def clean_html(raw_html):
    """Strips HTML tags and standardizes whitespace."""
    if pd.isna(raw_html):
        return ""
    cleaner = re.compile('<.*?>')
    text = re.sub(cleaner, '', str(raw_html))
    return ' '.join(text.split())

def extract_skills(description_text):
    """Extracts technical skills using case-insensitive Regex word boundaries."""
    target_skills = ['Python', 'React', 'Shopify', 'TypeScript', 'SQL', 'WordPress', 'PHP', 'JavaScript']
    found_skills = []
    
    for skill in target_skills:
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, description_text, re.IGNORECASE):
            found_skills.append(skill)
            
    return found_skills

def run_etl_pipeline():
    """Executes the complete Ingestion, Cleaning, and Extraction pipeline."""
    df = fetch_philippine_jobs()
    
    column_mapping = {
        'site': 'source',
        'job_url': 'job_url',
        'job_title': 'title',
        'company': 'company',
        'location': 'location',
        'description': 'description',
        'date_posted': 'posted_date'
    }
    df = df.rename(columns=column_mapping)
    
    if 'description' not in df.columns:
        df['description'] = ""
    if 'posted_date' not in df.columns:
        df['posted_date'] = datetime.now()
    if 'source' not in df.columns:
        df['source'] = 'indeed'

    df['clean_description'] = df['description'].apply(clean_html)
    df['extracted_skills'] = df['clean_description'].apply(extract_skills)
    
    return df

if __name__ == "__main__":
    processed_df = run_etl_pipeline()
    print(processed_df[['title', 'company', 'source', 'extracted_skills']].head())