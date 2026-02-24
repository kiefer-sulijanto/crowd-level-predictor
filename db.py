import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get the URL from environment variables for security
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres.ctzfnwoljtitpibavupf:SvpmDNE0VW9gwmJA@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")

def get_engine():
    """Creates and returns a SQLAlchemy engine with optimized pooling"""
    return create_engine(
        DB_URL,
        pool_size=10,         # Keeps 10 connections ready to go
        max_overflow=20,     # Allows extra connections during heavy 209k row loads
        pool_recycle=3600    # Refreshes connections every hour
    )