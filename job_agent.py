# job_agent.py
import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv

import config
from auto_apply_agent import apply_linkedin, apply_internshala, apply_wellfound, apply_jobright
from email_notifier import send_email

# Load environment
load_dotenv()

# Configure Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ No Groq API key found! Please set GROQ_API_KEY in .env file.")
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client initialized successfully (LLaMA 3.3 70B + fallback)")

# --- Helper Functions ---
def load_applied():
    if not os.path.exists(config.APPLIED_JOBS_FILE):
        return set()
    with open(config.APPLIED_JOBS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_applied(url):
    with open(config.APPLIED_JOBS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

# --- Job Fetchers ---
def fetch_internshala():
    print("🔍 Fetching Internshala...")
    jobs = []
    try:
        r = requests.get(config.INTERNSHALA_SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".individual_internship") or soup.select(".internship_meta")
        for card in cards[:config.MAX_JOBS_TO_APPLY]:
            title = card.select_one(".job-internship-name") or card.select_one(".heading_4_5")
            company = card.select_one(".link_display_like_text")
            link_tag = card.select_one("a")
            link = "https://internshala.com" + link_tag["href"] if link_tag and link_tag.get("href") else None
            jobs.append({
                "source": "Internshala",
                "title": title.text.strip() if title else "Untitled",
                "company": company.text.strip() if company else "Unknown",
                "link": link
            })
    except Exception as e:
        print("⚠️ Error fetching Internshala jobs:", e)
    return jobs


def fetch_linkedin():
    print("🔍 Fetching LinkedIn (best-effort)...")
    jobs = []
    try:
        r = requests.get(config.LINKEDIN_SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("a", class_="base-card__full-link")
        for a in items[:config.MAX_JOBS_PER_SITE]:
            jobs.append({
                "source": "LinkedIn",
                "title": a.text.strip(),
                "company": "LinkedIn",
                "link": a.get("href")
            })
    except Exception as e:
        print("⚠️ LinkedIn fetch failed:", e)
    return jobs


def fetch_wellfound():
    print("🔍 Fetching Wellfound...")
    jobs = []
    try:
        r = requests.get(config.WELLFOUND_SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("a")
        for a in items[:config.MAX_JOBS_PER_SITE]:
            text = a.text.strip()
            if "intern" in text.lower() or "machine learning" in text.lower():
                link = "https://wellfound.com" + a.get("href", "")
                jobs.append({"source": "Wellfound", "title": text, "company": "Wellfound", "link": link})
    except Exception as e:
        print("⚠️ Wellfound fetch failed:", e)
    return jobs


def fetch_jobright():
    print("🔍 Fetching Jobright...")
    jobs = []
    try:
        r = requests.get(config.JOBRIGHT_SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("a")
        for a in items[:config.MAX_JOBS_PER_SITE]:
            text = a.text.strip()
            if text and ("machine learning" in text.lower() or "intern" in text.lower()):
                link = a.get("href")
                if link and link.startswith("/"):
                    link = "https://www.jobright.ai" + link
                jobs.append({"source": "Jobright", "title": text, "company": "Jobright", "link": link})
    except Exception as e:
        print("⚠️ Jobright fetch failed:", e)
    return jobs


# --- AI Analysis using Groq (LLaMA 3.3 with fallback) ---
def analyze_with_groq(description):
    if not client:
        return {"score": 0, "summary": "No API client configured"}

    prompt = f"""
    You are an AI internship analyzer. Rate this job description from 1 to 10 for AI/ML relevance.
    Return JSON only:
    {{
      "score": <number>,
      "summary": "<short reasoning>"
    }}
    Job Description:
    {description}
    """

    try:
        # Try primary model first (70B)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise AI/ML relevance evaluator."},
                {"role": "user", "content": prompt}
            ]
        )
    except Exception as e1:
        print("⚠️ 70B model failed, retrying with 8B-instant:", e1)
        # Fallback model (lighter)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a precise AI/ML relevance evaluator."},
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e2:
            print(f"❌ Both Groq models failed: {e2}")
            return {"score": 0, "summary": "Analysis failed"}

    try:
        text = response.choices[0].message.content.strip()
        import json
        return json.loads(text)
    except Exception:
        return {"score": 0, "summary": response.choices[0].message.content.strip()}


# --- Main Function ---
def main():
    print("🚀 Starting AI Internship Finder Agent...\n")
    applied = load_applied()
    all_jobs = []
    all_jobs += fetch_internshala()
    all_jobs += fetch_linkedin()
    all_jobs += fetch_wellfound()
    all_jobs += fetch_jobright()
    print(f"\n📊 Total internships fetched: {len(all_jobs)}")

    matched = []
    applied_count = 0

    for job in all_jobs:
        if applied_count >= config.MAX_JOBS_TO_APPLY:
            break
        url = job.get("link")
        if not url or url in applied:
            continue

        desc = f"{job['title']} at {job['company']} ({job['source']})"
        score_obj = analyze_with_groq(desc)
        score = score_obj.get("score", 0)
        summary = score_obj.get("summary", "")
        print(f"→ {job['source']} | {job['title']} | score {score}")

        if score >= config.AI_RELEVANCE_THRESHOLD:
            print("  ⭐ Selected for apply:", job['title'])
            success = False
            reason = "Not attempted"
            try:
                if job['source'] == "LinkedIn":
                    ok, reason = apply_linkedin(url, config.LINKEDIN_EMAIL, config.LINKEDIN_PASSWORD, headless=False)
                    success = ok
                elif job['source'] == "Internshala":
                    ok, reason = apply_internshala(url, config.INTERNSHALA_EMAIL, config.INTERNSHALA_PASSWORD, headless=False)
                    success = ok
                elif job['source'] == "Wellfound":
                    ok, reason = apply_wellfound(url, config.WELLFOUND_EMAIL, config.WELLFOUND_PASSWORD, headless=False)
                    success = ok
                elif job['source'] == "Jobright":
                    ok, reason = apply_jobright(url, config.JOBRIGHT_EMAIL, config.JOBRIGHT_PASSWORD, headless=False)
                    success = ok
            except Exception as e:
                reason = str(e)

            if success:
                save_applied(url)
                applied.add(url)
                applied_count += 1
                print(f"✅ Applied to {job['title']} ({job['source']})")
                subj = f"Applied to {job['title']} at {job['company']}"
                body = f"Applied to {job['title']} ({job['source']})\nLink: {url}\nReason: {reason}\nScore: {score}\nSummary: {summary}"
                send_email(subj, body)
            else:
                print(f"⚠️ Could not auto-apply ({reason}). Saving for manual review.")
                matched.append({**job, "score": score, "summary": summary, "apply_status": reason})

        time.sleep(2)

    if matched:
        keys = ["source", "title", "company", "link", "score", "summary", "apply_status"]
        with open(config.MATCHED_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for m in matched:
                writer.writerow({k: m.get(k, "") for k in keys})
        print(f"💾 Saved {len(matched)} manual-review entries to {config.MATCHED_CSV}")

    print(f"\n🎉 Completed. Applied to {applied_count} jobs (attempted).")


if __name__ == "__main__":
    main()
