import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from environment variables.")

def get_db_engine():
    """Creates and returns a SQLAlchemy database engine."""
    engine = create_engine(DATABASE_URL)
    return engine