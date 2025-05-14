# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PostgreSQL DB URL
DATABASE_URL = "postgresql://postgres:Rayyan123%40@localhost:5432/EduLearn"

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to provide DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()