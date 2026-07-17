from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

HEADLESS = os.getenv("HEADLESS") == "True"
KEYWORD = os.getenv("KEYWORD")
LOCATION = os.getenv("LOCATION")
RESUME_PATH = os.getenv("RESUME_PATH")