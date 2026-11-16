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


def update_application_status(job_id, status):
    applied_key = f"job_applied_{job_id}"
    denied_key = f"job_denied_{job_id}"
    is_applied = bool(st.session_state[applied_key])
    is_denied = bool(st.session_state[denied_key])

    if status == "applied" and is_applied:
        is_denied = False
    elif status == "denied" and is_denied:
        is_applied = False

    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE jobs
                SET is_applied = :is_applied, is_denied = :is_denied
                WHERE id = :id
            """),
            {"is_applied": is_applied, "is_denied": is_denied, "id": job_id}
        )

    st.session_state[applied_key] = is_applied
    st.session_state[denied_key] = is_denied


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
SELECT j.id, j.title, c.name AS company, j.location, j.job_url, j.posted_date, j.is_applied, j.is_denied
FROM jobs j
JOIN companies c ON j.company_id = c.id
ORDER BY j.posted_date DESC;
""")

try:
    with engine.connect() as conn:
        df_skills = pd.DataFrame(conn.execute(query_top_skills).fetchall(), columns=['skill_name', 'demand_count'])
        df_cms = pd.DataFrame(conn.execute(query_cms_vs_trad).fetchall(), columns=['category', 'skill_name', 'mention_count'])
        df_jobs = pd.DataFrame(conn.execute(query_all_jobs).fetchall(), columns=['id', 'title', 'company', 'location', 'job_url', 'posted_date', 'is_applied', 'is_denied'])
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    df_skills, df_cms, df_jobs = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- Dashboard Visualizations ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top Demanded Technical Skills (PH)")
    if not df_skills.empty:
        fig_skills = px.bar(df_skills, x='skill_name', y='demand_count', color='skill_name', template='plotly_white')
        st.plotly_chart(fig_skills, width="stretch")
    else:
        st.info("Run `python loader.py` to populate data.")

with col2:
    st.subheader("🛒 CMS Platforms vs. Traditional Frameworks")
    if not df_cms.empty:
        fig_cms = px.pie(df_cms, names='skill_name', values='mention_count', hole=0.4, color='category', template='plotly_white')
        st.plotly_chart(fig_cms, width="stretch")
    else:
        st.info("Run `python loader.py` to populate data.")

st.markdown("---")

# --- Interactive Job Board & Application Tracker ---
st.subheader("📋 Philippine Job Listings & Application Tracker")

if not df_jobs.empty:
    # Filter Controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_query = st.text_input("🔍 Search job titles or companies", "")
    with col_f2:
        filter_status = st.selectbox("Filter Application Status", ["All Jobs", "Not Applied", "Applied", "Denied"])
    with col_f3:
        date_order = st.selectbox("Sort by posting date", ["Latest first", "Oldest first"])

    # Apply search filter
    filtered_df = df_jobs.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['company'].str.contains(search_query, case=False, na=False)
        ]
    
    if filter_status == "Applied":
        filtered_df = filtered_df[filtered_df['is_applied'] == True]
    elif filter_status == "Denied":
        filtered_df = filtered_df[filtered_df['is_denied'] == True]
    elif filter_status == "Not Applied":
        filtered_df = filtered_df[
            (filtered_df['is_applied'] == False) & (filtered_df['is_denied'] == False)
        ]

    filtered_df = filtered_df.sort_values(
        'posted_date',
        ascending=date_order == "Oldest first",
        na_position="last"
    )

    page_size = 10
    filter_state = (search_query, filter_status, date_order)
    if st.session_state.get("job_filter_state") != filter_state:
        st.session_state.job_filter_state = filter_state
        st.session_state.job_page = 1

    total_jobs = len(filtered_df)
    total_pages = max(1, (total_jobs + page_size - 1) // page_size)
    current_page = min(st.session_state.get("job_page", 1), total_pages)
    st.session_state.job_page = current_page

    st.markdown(f"Showing **{total_jobs}** listings:")
    if total_jobs > page_size:
        page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
        with page_col1:
            if st.button("← Previous", disabled=current_page == 1, key="previous_job_page"):
                st.session_state.job_page -= 1
                st.rerun()
        with page_col2:
            st.markdown(f"<div style='text-align: center'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)
        with page_col3:
            if st.button("Next →", disabled=current_page == total_pages, key="next_job_page"):
                st.session_state.job_page += 1
                st.rerun()

    # Render interactive list with checkboxes and clickable links
    page_start = (current_page - 1) * page_size
    page_df = filtered_df.iloc[page_start:page_start + page_size]
    for index, row in page_df.iterrows():
        cols = st.columns([0.7, 0.7, 2.3, 1.5, 1.3, 1])
        
        job_id = row['id']
        is_applied = bool(row['is_applied'])
        is_denied = bool(row['is_denied'])
        applied_key = f"job_applied_{job_id}"
        denied_key = f"job_denied_{job_id}"

        if applied_key not in st.session_state:
            st.session_state[applied_key] = is_applied
        if denied_key not in st.session_state:
            st.session_state[denied_key] = is_denied
        
        with cols[0]:
            st.checkbox(
                "Applied",
                key=applied_key,
                on_change=update_application_status,
                args=(job_id, "applied")
            )

        with cols[1]:
            st.checkbox(
                "Denied",
                key=denied_key,
                on_change=update_application_status,
                args=(job_id, "denied")
            )

        with cols[2]:
            st.markdown(f"**{row['title']}**")
            st.caption(f"{row['company']}")
            
        with cols[3]:
            st.text(row['location'])
            
        with cols[4]:
            st.text(str(row['posted_date'])[:10])
            
        with cols[5]:
            st.markdown(f"[View Job Link]({row['job_url']})", unsafe_allow_html=True)
            
        st.divider()
else:
    st.info("No job listings found. Run `python loader.py` to fetch fresh listings from the Philippines.")