from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Read database URL from env for flexibility; fallback to SQLite for easy local dev.
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://root:No_password09%21%3C%3E@localhost:3306/chatdb"
)

# Auto-create database if using MySQL
if SQLALCHEMY_DATABASE_URL.startswith("mysql"):
    try:
        import sqlalchemy
        from sqlalchemy import text
        # Separate base url and db name
        base_url, db_name = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)
        # Handle optional query params in db_name
        db_name = db_name.split('?')[0]
        temp_engine = sqlalchemy.create_engine(base_url)
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
            conn.commit()
    except Exception as e:
        print(f"Failed to auto-create database (might already exist or permission issue): {e}")

# If the user hasn't configured MySQL locally, allow using a sqlite file for quick dev/tests
if SQLALCHEMY_DATABASE_URL.startswith("sqlite") or SQLALCHEMY_DATABASE_URL == "sqlite:///:memory:":
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Optional SQL echo for debugging
if os.environ.get("DEV_DB_ECHO", "false").lower() in ("1", "true", "yes"):
    engine.echo = True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()