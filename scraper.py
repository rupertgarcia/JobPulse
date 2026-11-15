import re
from datetime import datetime
import pandas as pd
from jobspy import scrape_jobs

def fetch_philippine_jobs(search_terms=[
    "Software Engineer", 
    "Full Stack Developer", 
    "Python Developer", 
    "React Developer"
], location="Philippines", results_wanted=25):
    """Fetches live job postings with isolated error handling per platform."""
    all_jobs = []
    platforms = ["indeed", "linkedin", "zip_recruiter"]
    
    for term in search_terms:
        for site in platforms:
            print(f"Scraping '{term}' on {site} for '{location}'...")
            try:
                df_site = scrape_jobs(
                    site_name=[site],
                    search_term=term,
                    location=location,
                    results_wanted=results_wanted,
                    hours_old=168, # Last 7 days
                    country_indeed='Philippines'
                )
                if not df_site.empty:
                    all_jobs.append(df_site)
            except Exception as e:
                print(f"⚠️ Notice: Skipped {site} for '{term}' due to rate limit/block: {e}")
            
    if all_jobs:
        combined_df = pd.concat(all_jobs, ignore_index=True)
        # Drop duplicate URLs
        combined_df = combined_df.drop_duplicates(subset=['job_url'])
        print(f"Successfully scraped {len(combined_df)} unique jobs in the Philippines.")
        return combined_df
    else:
        print("Live scraping returned no results. Falling back to sample dataset.")
        return get_fallback_jobs()

def get_fallback_jobs():
    """Provides fallback sample data if live scraping encounters blocks."""
    return pd.DataFrame([
        {
            "title": "Full-Stack Software Engineer (React / TypeScript)",
            "company": "Manila Tech Solutions",
            "location": "Taguig, Metro Manila, PH",
            "job_url": "https://ph.indeed.com/viewjob?jk=example1",
            "site": "indeed",
            "description": "<p>Looking for a Full Stack Engineer proficient in Next.js, TypeScript, React, PostgreSQL, and Python.</p>",
            "date_posted": datetime.now().strftime('%Y-%m-%d'),
            "min_amount": 50000,
            "max_amount": 80000,
            "currency": "PHP",
            "job_type": "Full-time"
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
    """Extracts technical skills using case-insensitive Regex whole-word boundaries."""
    target_skills = [
        'Python', 'React', 'Next.js', 'TypeScript', 'JavaScript', 
        'SQL', 'PostgreSQL', 'MySQL', 'PHP', 'Shopify', 'WordPress', 
        'Tailwind', 'Node.js', 'REST APIs', 'Docker'
    ]
    found_skills = []
    
    for skill in target_skills:
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, description_text, re.IGNORECASE):
            found_skills.append(skill)
            
    return list(set(found_skills))

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
    
    # Ensure optional columns exist from jobspy output
    for col in ['min_amount', 'max_amount', 'currency', 'job_type', 'source']:
        if col not in df.columns:
            df[col] = None

    if 'description' not in df.columns:
        df['description'] = ""
    if 'posted_date' not in df.columns:
        df['posted_date'] = datetime.now()

    df['clean_description'] = df['description'].apply(clean_html)
    df['extracted_skills'] = df['clean_description'].apply(extract_skills)
    
    return df

if __name__ == "__main__":
    processed_df = run_etl_pipeline()
    print(processed_df[['title', 'company', 'source', 'min_amount', 'max_amount', 'extracted_skills']].head())