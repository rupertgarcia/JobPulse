JobPulse PH: Automated Tech Job Market Intelligence & Application Tracker
An end-to-end data engineering and full-stack portfolio project built to automate tech job market intelligence, aggregate listings across Philippine platforms, and track application workflows.

✨ Key Features
Automated Ingestion Pipeline: Python-based scraper powered by python-jobspy targeting major job boards (Indeed, LinkedIn, ZipRecruiter) filtered for the Philippines tech market.

ETL & NLP Skill Extraction: Cleans raw HTML job descriptions and uses Regular Expressions (RegEx) with whole-word boundary matching to extract high-demand skills (Python, React, Shopify, TypeScript, SQL, WordPress, PHP, JavaScript).

Relational Database Architecture: Built on MySQL / XAMPP with a fully normalized relational schema (jobs, companies, skills, and a many-to-many job_skills junction table) complete with indexing for fast aggregation.

Interactive Analytics Dashboard: Built with Streamlit and Plotly to visualize real-time tech stack demand, regional market trends, and CMS vs. traditional framework market share.

Built-in Job Application Tracker: Interactive UI featuring live search filters, sorting by posting date, direct clickable external job links, and a persistent database-backed "Applied" checkbox tracker.

🛠️ Tech Stack
Language: Python 3.11+

Data Processing & ETL: Pandas, RegEx, JobSpy

Database & ORM: MySQL (via XAMPP), SQLAlchemy

Dashboard & UI: Streamlit, Plotly

Environment Management: Python-Dotenv

📂 Project File Structure
Plaintext
jobpulse/
├── .env                  # Database connection string configuration
├── requirements.txt      # Python dependencies
├── database.sql          # MySQL relational schema & indexes
├── config.py             # SQLAlchemy engine configuration
├── scraper.py            # Ingestion, HTML cleaning, & RegEx skill parser
├── loader.py             # ETL loader (handles safe upserts & relational mapping)
└── app.py                # Streamlit interactive dashboard & application tracker
⚙️ Getting Started & Installation
1. Clone the Repository & Setup Environment
Bash
git clone https://github.com/your-username/jobpulse.git
cd jobpulse
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configure Database
Open XAMPP and start the MySQL server.

Open phpMyAdmin (http://localhost/phpmyadmin), create a database named jobpulse_db, and run the SQL commands found in database.sql.

Create a .env file in your root folder and add your local credentials:

Code snippet
DATABASE_URL=mysql+pymysql://root:@localhost:3306/jobpulse_db
4. Run the ETL Pipeline
Scrape live Philippine job postings, clean the descriptions, extract skills, and populate your database:

Bash
python loader.py
5. Launch the Dashboard
Start the interactive Streamlit analytics app:

Bash
streamlit run app.py
📊 Database Schema DDL
SQL
-- Companies Table
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs Master Table
CREATE TABLE jobs (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_id INT,
    location VARCHAR(255),
    job_url TEXT NOT NULL,
    description TEXT,
    posted_date DATETIME,
    is_applied BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_posted_date (posted_date),
    INDEX idx_company_id (company_id)
);

-- Skills Dictionary Table
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Job-Skills Junction Table
CREATE TABLE job_skills (
    job_id VARCHAR(36),
    skill_id INT,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_skill_id (skill_id)
);
💡 Future Enhancements
[ ] Add automated daily cron job / scheduler to refresh job listings automatically.

[ ] Integrate salary range parsing and extraction.

[ ] Deploy the backend to Supabase / Render and the UI to Streamlit Community Cloud.

Built with passion by Rupert Daniel Garcia