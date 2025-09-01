import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///soulbloom.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    APP_SECRET = os.getenv("APP_SECRET", "dev-secret")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
