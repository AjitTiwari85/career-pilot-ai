from dotenv import load_dotenv
import os

load_dotenv()

HEADLESS = os.getenv("HEADLESS") == "True"
KEYWORD = os.getenv("KEYWORD")
LOCATION = os.getenv("LOCATION")
RESUME_PATH = os.getenv("RESUME_PATH")