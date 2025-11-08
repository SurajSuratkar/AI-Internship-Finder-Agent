# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Login credentials for auto-apply (fill in .env)
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

INTERNSHALA_EMAIL = os.getenv("INTERNSHALA_EMAIL")
INTERNSHALA_PASSWORD = os.getenv("INTERNSHALA_PASSWORD")

WELLFOUND_EMAIL = os.getenv("WELLFOUND_EMAIL")
WELLFOUND_PASSWORD = os.getenv("WELLFOUND_PASSWORD")

JOBRIGHT_EMAIL = os.getenv("JOBRIGHT_EMAIL")
JOBRIGHT_PASSWORD = os.getenv("JOBRIGHT_PASSWORD")

# Email notify
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

# Scraper URLs
INTERNSHALA_SEARCH_URL = "https://internshala.com/internships/keywords-ai-machine-learning"
LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=AI%20Machine%20Learning%20Internship"
WELLFOUND_SEARCH_URL = "https://wellfound.com/role/machine-learning-intern"
JOBRIGHT_SEARCH_URL = "https://www.jobright.ai/jobs?q=machine+learning+intern"

# Runtime settings
MAX_JOBS_TO_APPLY = int(os.getenv("MAX_JOBS_TO_APPLY") or 20)
AI_RELEVANCE_THRESHOLD = int(os.getenv("AI_RELEVANCE_THRESHOLD") or 6)

# Files
APPLIED_JOBS_FILE = "applied_jobs.txt"
MATCHED_CSV = "matched_jobs.csv"
RESUME_FILE = os.getenv("RESUME_FILE") or "resume.txt"
MAX_JOBS_PER_SITE = 20
