from config.config import (
    HEADLESS,
    KEYWORD,
    LOCATION,
    RESUME_PATH,
)

def main():
    print("===== CareerPilot-AI =====")
    print(f"Headless: {HEADLESS}")
    print(f"Keyword: {KEYWORD}")
    print(f"Location: {LOCATION}")
    print(f"Resume Path: {RESUME_PATH}")

if __name__ == "__main__":
    main()