# AI Internship Finder Agent

**An end-to-end automation agent that finds AI/ML internship job listings, scores them with an LLM, and auto-applies to top matches.**

---

## 🔎 Project Overview

A Python-based agent that:

* Scrapes job listings from LinkedIn, Internshala, Wellfound, and Jobright.
* Uses an LLM (Groq / OpenAI / Gemini) to score relevance for AI/ML roles.
* Attempts automated applications (Easy Apply / site-specific flows) using Selenium.
* Logs applied jobs, sends email notifications, and saves manual-review items.

This project is intended for personal automation use and learning; be mindful of each platform's terms of service.

---

## 🚀 Features

* Multi-site scraping (LinkedIn, Internshala, Wellfound, Jobright)
* LLM-based relevance scoring with automatic model fallback
* Browser automation for applying (Selenium + webdriver-manager)
* Applied-job persistence (`applied_jobs.txt`) and manual-review CSV output
* Email notifications when applications are submitted
* Dry-run mode for safe testing

---

## 🧭 Repo Structure

```
AI Internship Finder Agent/
├── job_agent.py            # Main orchestration script
├── auto_apply_agent.py     # Selenium automation helpers (LinkedIn, Internshala, ...)
├── email_notifier.py       # Simple email/Gmail notifier
├── config.py               # Project constants (URLs, thresholds, filenames)
├── .env                   # Secret keys & credentials (not committed)
├── applied_jobs.txt        # URLs of jobs already applied (generated)
├── matched_manual.csv      # Jobs that require manual review (generated)
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Requirements

* Python 3.10+ (3.11/3.13 tested)
* Google/ Groq / OpenAI API key (one of them configured)
* Google Chrome (or Chromium) installed
* pip packages (see `requirements.txt`)

Example `requirements.txt` (recommended):

```
requests
beautifulsoup4
python-dotenv
selenium
webdriver-manager
groq
openai
google-generativeai
```

---

## ⚙️ Setup (quick)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in project root and add credentials (see below).
4. Create/verify `config.py` (example provided in README).

---

## 🔐 Environment (.env) example

Create `.env` (DO NOT commit) and add:

```
# AI provider (choose one)
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk-...
# GEMINI_API_KEY=ya29....

# Site credentials (only when you enable auto apply)
LINKEDIN_EMAIL=you@example.com
LINKEDIN_PASSWORD=your_linkedin_password
INTERNSHALA_EMAIL=you@example.com
INTERNSHALA_PASSWORD=your_internshala_password
WELLFOUND_EMAIL=you@example.com
WELLFOUND_PASSWORD=your_wellfound_password
JOBRIGHT_EMAIL=you@example.com
JOBRIGHT_PASSWORD=your_jobright_password

# Email notifier (Gmail app password recommended)
GMAIL_USER=youremail@gmail.com
GMAIL_PASS=your_gmail_app_password

# Runtime toggles
DRY_RUN=true
MAX_JOBS_TO_APPLY=20
```

**Note about `#` in values:** If a password contains `#` and you use a `.env` file, wrap the value in quotes:

```
PASSWORD="pa#ssword123"
```

---

## 🧩 Sample `config.py`

```python
import os
# Provider keys will be read from .env via python-dotenv in scripts
# Scraper URLs
LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=AI%20Machine%20Learning%20Internship"
INTERNSHALA_SEARCH_URL = "https://internshala.com/internships/keywords-ai-machine-learning"
WELLFOUND_SEARCH_URL = "https://wellfound.com/"
JOBRIGHT_SEARCH_URL = "https://www.jobright.ai/"

# Limits & thresholds
MAX_JOBS_TO_APPLY = 20
MAX_JOBS_PER_SITE = 20
AI_RELEVANCE_THRESHOLD = 6

# Files
APPLIED_JOBS_FILE = "applied_jobs.txt"
MATCHED_CSV = "matched_manual.csv"

# Credentials come from .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
INTERNSHALA_EMAIL = os.getenv('INTERNSHALA_EMAIL')
INTERNSHALA_PASSWORD = os.getenv('INTERNSHALA_PASSWORD')
```

---

## ▶️ How to run

1. Dry run (no apply) — safe test:

```bash
# ensure DRY_RUN=true in .env or config toggles
python job_agent.py
```

2. Real run (careful):

* Set `DRY_RUN=false` and add credentials in `.env`.
* Run:

```bash
python job_agent.py
```

---

## 🐞 Troubleshooting & Tips

* **No API key / quota errors**: If using OpenAI/Gemini/Groq, ensure key is set and account has quota. Use free/no-cost alternatives if out of quota.
* **Model not found**: Update to the recommended model name or SDK version. Check provider docs.
* **Sites block scraping**: LinkedIn/Wellfound may block bot requests. Use authenticated browser automation (Selenium) for reliability, or add rotating proxies / time delays.
* **CAPTCHA / 2FA**: Automation can be blocked by CAPTCHA or OTP flows — the script will detect and stop; handle those manually.
* **Selenium errors**: Ensure Chrome/Chromedriver compatibility and `webdriver-manager` is installed. If headless fails, run with `headless=False` to debug.

---

## 🧾 Safety & Legal

Automating applications may violate platform terms of service. Use this project for **learning and personal productivity only**. Do not spam or abuse automated applications — limit the number of applies and respect site rules.

---

## 🙏 Credits & Acknowledgements

* Uses `BeautifulSoup`, `requests` for scraping
* Uses `selenium` + `webdriver-manager` for automation
* LLM scoring via Groq / OpenAI / Gemini

---

## 📎 Contact / Next Steps

If you want, I can:

* Provide a `requirements.txt` and `setup.bat`/`setup.sh` for one-click setup
* Harden the agent to run as a scheduled job (systemd / Windows Task Scheduler)
* Add logging, screenshots for failed applies, and a dashboard

---

*Happy coding — use responsibly!*
