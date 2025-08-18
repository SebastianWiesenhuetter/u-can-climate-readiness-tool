# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load .env from backend/.env
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine & session
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# Base class for models to inherit
Base = declarative_base()
