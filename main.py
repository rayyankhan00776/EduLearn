# main.py
from fastapi import FastAPI 
from models.base import Base
from routes import auth
from database import engine

app = FastAPI()

# Register routes
app.include_router(auth.router, prefix='/auth')

# Create database tables automatically
Base.metadata.create_all(engine)