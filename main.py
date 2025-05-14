from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.base import Base
from routes import auth
from database import engine

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix='/auth')

# Create database tables automatically
Base.metadata.create_all(engine)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to EduLearn API"}