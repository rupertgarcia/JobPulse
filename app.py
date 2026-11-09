import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from config import get_db_engine

# Page Configuration
st.set_page_config(
    page_title="JobPulse PH: Tech Market Intelligence", 
    page_icon="🇵🇭", 
    layout="wide"
)

st.title("🇵🇭 JobPulse PH: Philippine Tech Job Intelligence Dashboard")
st.markdown("Tracking tech stack demand, remote/local market trends, and managing your job applications.")

@st.cache_resource
def get_connection():
    return get_db_engine()

engine = get_connection()

# --- Load Analytics Queries ---
query_top_skills = text("""
SELECT 
    s.name AS skill_name, 
    COUNT(js.job_id) AS demand_count
FROM skills s
JOIN job_skills js ON s.id = js.skill_id
JOIN jobs j ON js.job_id = j.id
WHERE j.posted_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY s.name
ORDER BY demand_count DESC
LIMIT 10;
""")

query_cms_vs_trad = text("""
SELECT 
    CASE 
        WHEN s.name IN ('Shopify', 'WordPress') THEN 'CMS Platforms'
        ELSE 'Traditional Frameworks / Languages'
    END AS category,
    s.name AS skill_name,
    COUNT(js.job_id) AS mention_count
FROM skills s
JOIN job_skills js ON s.id = js.skill_id
GROUP BY category, s.name
ORDER BY mention_count DESC;
""")

# --- Load Jobs Data for Table & Tracker ---
query_all_jobs = text("""
SELECT j.id, j.title, c.name AS company, j.location, j.job_url, j.posted_date, j.is_applied
FROM jobs j
JOIN companies c ON j.company_id = c.id
ORDER BY j.posted_date DESC;
""")

try:
    with engine.connect() as conn:
        df_skills = pd.DataFrame(conn.execute(query_top_skills).fetchall(), columns=['skill_name', 'demand_count'])
        df_cms = pd.DataFrame(conn.execute(query_cms_vs_trad).fetchall(), columns=['category', 'skill_name', 'mention_count'])
        df_jobs = pd.DataFrame(conn.execute(query_all_jobs).fetchall(), columns=['id', 'title', 'company', 'location', 'job_url', 'posted_date', 'is_applied'])
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    df_skills, df_cms, df_jobs = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- Dashboard Visualizations ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top Demanded Technical Skills (PH)")
    if not df_skills.empty:
        fig_skills = px.bar(df_skills, x='skill_name', y='demand_count', color='skill_name', template='plotly_white')
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("Run `python loader.py` to populate data.")

with col2:
    st.subheader("🛒 CMS Platforms vs. Traditional Frameworks")
    if not df_cms.empty:
        fig_cms = px.pie(df_cms, names='skill_name', values='mention_count', hole=0.4, color='category', template='plotly_white')
        st.plotly_chart(fig_cms, use_container_width=True)
    else:
        st.info("Run `python loader.py` to populate data.")

st.markdown("---")

# --- Interactive Job Board & Application Tracker ---
st.subheader("📋 Philippine Job Listings & Application Tracker")

if not df_jobs.empty:
    # Filter Controls
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_query = st.text_input("🔍 Search job titles or companies", "")
    with col_f2:
        filter_applied = st.selectbox("Filter Application Status", ["All Jobs", "Not Applied", "Applied"])

    # Apply search filter
    filtered_df = df_jobs.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['company'].str.contains(search_query, case=False, na=False)
        ]
    
    if filter_applied == "Applied":
        filtered_df = filtered_df[filtered_df['is_applied'] == True]
    elif filter_applied == "Not Applied":
        filtered_df = filtered_df[filtered_df['is_applied'] == False]

    st.markdown(f"Showing **{len(filtered_df)}** listings:")

    # Render interactive list with checkboxes and clickable links
    for index, row in filtered_df.iterrows():
        cols = st.columns([0.6, 2.5, 1.5, 1.5, 1])
        
        job_id = row['id']
        is_checked = bool(row['is_applied'])
        
        with cols[0]:
            # Checkbox to toggle application status in database
            new_status = st.checkbox("Applied", value=is_checked, key=f"job_{job_id}")
            if new_status != is_checked:
                with engine.begin() as conn:
                    conn.execute(
                        text("UPDATE jobs SET is_applied = :status WHERE id = :id"),
                        {"status": new_status, "id": job_id}
                    )
                st.rerun()
                
        with cols[1]:
            st.markdown(f"**{row['title']}**")
            st.caption(f"{row['company']}")
            
        with cols[2]:
            st.text(row['location'])
            
        with cols[3]:
            st.text(str(row['posted_date'])[:10])
            
        with cols[4]:
            st.markdown(f"[View Job Link]({row['job_url']})", unsafe_allow_html=True)
            
        st.divider()
else:
    st.info("No job listings found. Run `python loader.py` to fetch fresh listings from the Philippines.")