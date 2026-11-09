# 🇵🇭 JobPulse PH: Automated Tech Job Market Intelligence & Application Tracker

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange.svg)](https://www.mysql.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-green.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*An end-to-end data engineering and full-stack portfolio project built to automate tech job market intelligence, aggregate listings across Philippine platforms, and track application workflows.*

</div>

---

## 📸 Overview & Architecture

**JobPulse PH** automates the entire lifecycle of job hunting and market research. It scrapes live job listings, cleans and parses unstructured data using RegEx, stores relational records safely in a MySQL database, and visualizes market trends through an interactive Streamlit dashboard.

[ Philippine Job Boards ]
│ (Python Ingestion: python-jobspy)
▼
[ Raw Data Cleaning & RegEx Parser ] (Pandas & NLP Keyword Matching)
│
▼
[ MySQL / XAMPP Relational Database ] (Normalized Schema & Indexing)
│
▼
[ Streamlit Interactive Dashboard ] (Analytics, Filters, & Application Tracker)


---

## ✨ Key Features

*   **🇵🇭 Philippine-Centric Ingestion Pipeline:** Tailored scraper powered by `python-jobspy` targeting local and regional tech openings across Indeed, LinkedIn, and ZipRecruiter.
*   **🧹 Robust ETL & NLP Parser:** Strips raw HTML descriptions and executes **Regular Expressions (RegEx)** with whole-word boundary matching to extract high-demand skills (*Python, React, Shopify, TypeScript, SQL, WordPress, PHP, JavaScript*).
*   **🗄️ Normalized Relational Database:** Built on MySQL with a structured schema (`jobs`, `companies`, `skills`, and a many-to-many `job_skills` junction table) complete with indexing for lightning-fast aggregation queries.
*   **📊 Interactive Analytics Dashboard:** Built with **Streamlit** and **Plotly** to visualize real-time tech stack demand and compare CMS platforms vs. traditional software frameworks.
*   **🎯 Built-in Application Tracker:** Features real-time search filters, sorting by posting date, direct clickable job links, and a persistent database-backed "Applied" checkbox tracker.

---

## 🛠️ Tech Stack

*   **Language:** Python 3.11+
*   **Data Processing & ETL:** Pandas, RegEx, JobSpy
*   **Database & ORM:** MySQL (via XAMPP), SQLAlchemy
*   **Dashboard & UI:** Streamlit, Plotly
*   **Environment Management:** Python-Dotenv

---

## 📂 Project File Structure

```text
jobpulse/
├── 📄 .env                  # Database connection string configuration
├── 📄 requirements.txt      # Python dependencies
├── 🗄️ database.sql          # MySQL relational schema & indexes
├── ⚙️ config.py             # SQLAlchemy database connection engine
├── 🕷️ scraper.py            # Ingestion, HTML cleaning, & RegEx skill parser
├── 🔄 loader.py             # ETL loader (handles safe upserts & relational mapping)
└── 📊 app.py                # Streamlit interactive dashboard & application tracker
⚙️ Getting Started & Installation
1. Clone the Repository & Setup Environment
Bash
git clone [https://github.com/your-username/jobpulse.git](https://github.com/your-username/jobpulse.git)
cd jobpulse
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configure Database
Open XAMPP and start the MySQL server.

Open phpMyAdmin (http://localhost/phpmyadmin), create a database named jobpulse_db, and run the SQL commands found in database.sql.

Create a .env file in your root folder and add your local connection string:

Code snippet
DATABASE_URL=mysql+pymysql://root:@localhost:3306/jobpulse_db
4. Run the ETL Pipeline
Scrape live Philippine job postings, clean descriptions, extract skills, and populate your database:

Bash
python loader.py
5. Launch the Dashboard
Start the interactive Streamlit analytics app:

Bash
streamlit run app.py
🗄️ Database Schema DDL
SQL
-- 1. Companies Table
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Jobs Master Table
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

-- 3. Skills Dictionary Table
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 4. Job-Skills Junction Table (Many-to-Many)
CREATE TABLE job_skills (
    job_id VARCHAR(36),
    skill_id INT,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_skill_id (skill_id)
);
💡 Future Enhancements
[ ] Set up an automated daily scheduler (cron job / Windows Task Scheduler) to refresh job listings automatically.

[ ] Implement salary range parsing and extraction.

[ ] Deploy the backend to Supabase / Render and the UI to Streamlit Community Cloud.

👤 Author
Built with passion by Rupert Daniel Cagas Garcia

Full-Stack Software Engineer & Data Engineer