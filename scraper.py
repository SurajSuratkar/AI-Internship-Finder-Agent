# scraper.py
import requests
from bs4 import BeautifulSoup

from config import INTERNSHALA_SEARCH_URL, LINKEDIN_SEARCH_URL, WELLFOUND_SEARCH_URL, JOBRIGHT_SEARCH_URL
import time

def fetch_internshala(max_items=20):
    jobs = []
    try:
        r = requests.get(INTERNSHALA_SEARCH_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # find internships - class names may change; we try robust extraction
        cards = soup.select(".individual_internship") or soup.select(".internship_meta")
        for card in cards[:max_items]:
            title = card.select_one(".job-internship-name, h3")
            company = card.select_one(".link_display_like_text, .company_name")
            link_tag = card.select_one("a")
            link = "https://internshala.com" + link_tag['href'] if link_tag and link_tag.get('href', '').startswith('/') else (link_tag['href'] if link_tag else "")
            jobs.append({"source":"internshala","title":(title.text.strip() if title else "Untitled"), "company":(company.text.strip() if company else "Unknown"), "link":link, "location": ""})
    except Exception as e:
        print("⚠️ Internshala fetch error:", e)
    return jobs

def fetch_linkedin(max_items=20):
    jobs = []
    try:
        r = requests.get(LINKEDIN_SEARCH_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a.base-card__full-link, a.result-card__full-card-link")
        for a in cards[:max_items]:
            title = a.text.strip()
            link = a.get("href")
            jobs.append({"source":"linkedin","title":title,"company":"LinkedIn","link":link,"location":""})
    except Exception as e:
        print("⚠️ LinkedIn fetch error:", e)
    return jobs

def fetch_wellfound(max_items=20):
    jobs = []
    try:
        r = requests.get(WELLFOUND_SEARCH_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a[data-test='job-link'], a.job-link")
        for a in cards[:max_items]:
            title = a.text.strip()
            link = "https://wellfound.com" + a.get("href")
            jobs.append({"source":"wellfound","title":title,"company":"Wellfound","link":link,"location":""})
    except Exception as e:
        print("⚠️ Wellfound fetch error:", e)
    return jobs

def fetch_jobright(max_items=20):
    jobs = []
    try:
        r = requests.get(JOBRIGHT_SEARCH_URL, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a.job-card, .job-listing a")
        for a in cards[:max_items]:
            title = a.text.strip()
            link = a.get("href")
            if link and link.startswith("/"):
                link = "https://www.jobright.ai" + link
            jobs.append({"source":"jobright","title":title,"company":"Jobright","link":link,"location":""})
    except Exception as e:
        print("⚠️ Jobright fetch error:", e)
    return jobs

def fetch_all_jobs(max_per_site=20):
    jobs = []
    jobs += fetch_internshala(max_per_site)
    jobs += fetch_linkedin(max_per_site)
    jobs += fetch_wellfound(max_per_site)
    jobs += fetch_jobright(max_per_site)
    return jobs
