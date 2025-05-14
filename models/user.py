from sqlalchemy import TEXT, VARCHAR, Column, LargeBinary, DateTime, Integer
from models.base import Base
from sqlalchemy.sql import func

class Student(Base):
    __tablename__ = 'students'
    id = Column(TEXT, primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    education_level = Column(VARCHAR(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(TEXT, primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    subject = Column(VARCHAR(100), nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    highest_qualification = Column(VARCHAR(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())