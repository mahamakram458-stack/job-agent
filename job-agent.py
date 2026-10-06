import csv
import html
import os
import re
import time
import requests

# =====================================================
#                  SETTINGS (yahan badlo)
# =====================================================

MY_NAME = "Maham"
MY_EMAIL = ""

# Har field me kitni jobs chahiye
PER_FIELD = 10

# Har field ke keywords (job title me ye lafz hon to job match hogi)
KEYWORDS = {
    "AI and Machine Learning": ["ai", "ml", "machine learning", "llm", "nlp", "data scientist", "deep learning"],
    "SEO Content Writing": ["seo", "content", "writer", "copywriter", "writing", "editor", "blog"],
    "Website Development": ["web", "website", "frontend", "front-end", "front end", "react", "wordpress", "full-stack", "full stack", "javascript", "php", "developer", "software engineer", "backend", "back-end", "shopify", "laravel", "node", "vue", "angular", "html", "css"],
}

# Har field ki email wali skill line
SKILL_LINES = {
    "AI and Machine Learning": "I work with Python and machine learning, and I enjoy building AI-based solutions.",
    "SEO Content Writing": "I write SEO-friendly articles that are clear, well structured and easy to read.",
    "Website Development": "I build responsive websites using HTML, CSS and WordPress/Elementor.",
}

# Ye lafz title me hon to job chhor do (Spanish titles waghera)
EXCLUDE_WORDS = ["desarrollador", "ingeniero", "programador", "gerente", "analista", "dise\u00f1ador", "casino", "gambling", "betting", "chemistry"]

# Location filter: job ki location me inme se koi lafz ho to job rakho.
# Sirf USA / Europe / Canada jaisi "only" wali jobs hat jati hain, kyunke Pakistan se apply nahi ho sakti.
# Jis job ki location khali ho wo bhi rakhi jati hai.
# Filter band karna ho to LOCATION_FILTER = [] kar do.
LOCATION_FILTER = ["worldwide", "anywhere", "global", "international", "pakistan", "asia", "south asia", "apac", "middle east", "emea"]

# Naye job sites (SEO/content writing ke liye). Band karna ho to False kar do.
USE_JOBICY = True
USE_HIMALAYAS = True

# Himalayas par ye lafz search honge (sirf worldwide jobs aati hain)
SEO_SEARCHES = ["seo writer", "content writer", "copywriter", "blog writer"]

# Jobicy par kaun si categories dekhni hain ("dev" = web/software development)
JOBICY_INDUSTRIES = ["copywriting", "dev"]

# Himalayas par website development ke liye ye lafz search honge
WEB_SEARCHES = ["wordpress developer", "web developer", "frontend developer"]

# Files ke naam
CSV_FILE = "jobs.csv"
EMAILS_FILE = "emails.txt"

# =====================================================
#          Neeche code hai, ise badalne ki zaroorat nahi
# =====================================================

HEADERS = {"User-Agent": "Mozilla/5.0"}

FIELDS = {
    name: r"\b(" + "|".join(re.escape(k) for k in words) + r")\b"
    for name, words in KEYWORDS.items()
}

jobs = {}

for cat in [None, "data", "software-dev", "writing", "marketing"]:
    params = {"category": cat} if cat else {}
    try:
        r = requests.get("https://remotive.com/api/remote-jobs", params=params, headers=HEADERS, timeout=15)
        for j in r.json().get("jobs", []):
            jobs["rem-" + str(j["id"])] = {
                "title": j["title"],
                "company_name": j["company_name"],
                "url": j["url"],
                "location": j.get("candidate_required_location") or "",
            }
    except Exception as e:
        print("Remotive fail:", cat, e)
    time.sleep(3)
print("Remotive se jobs:", len(jobs))

before = len(jobs)
try:
    r = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=20)
    for j in r.json():
        if "position" not in j:
            continue
        jobs["rok-" + str(j.get("id"))] = {
            "title": j["position"],
            "company_name": j.get("company") or "your company",
            "url": j.get("url") or "https://remoteok.com",
            "location": j.get("location") or "",
        }
except Exception as e:
    print("RemoteOK fail:", e)
print("RemoteOK se jobs:", len(jobs) - before)


def to_text(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value or "")


# ---------- Jobicy (writing + dev jobs) ----------
if USE_JOBICY:
    before = len(jobs)
    for industry in JOBICY_INDUSTRIES:
        for geo in ["anywhere", "asia"]:
            try:
                r = requests.get(
                    "https://jobicy.com/api/v2/remote-jobs",
                    params={"count": 50, "geo": geo, "industry": industry},
                    headers=HEADERS,
                    timeout=20,
                )
                got = r.json().get("jobs", [])
                print(f"Jobicy {industry}/{geo}: {len(got)} jobs mili (status {r.status_code})")
                for j in got:
                    jobs["jic-" + str(j["id"])] = {
                        "title": html.unescape(j["jobTitle"]),
                        "company_name": html.unescape(j.get("companyName") or "your company"),
                        "url": j["url"],
                        "location": to_text(j.get("jobGeo")),
                    }
            except Exception as e:
                print("Jobicy fail:", industry, geo, e)
            time.sleep(2)
    print("Jobicy se jobs:", len(jobs) - before)

# ---------- Himalayas (SEO / content searches) ----------
if USE_HIMALAYAS:
    before = len(jobs)
    for q in SEO_SEARCHES + WEB_SEARCHES:
        try:
            r = requests.get(
                "https://himalayas.app/jobs/api/search",
                params={"q": q, "worldwide": "true", "sort": "recent"},
                headers=HEADERS,
                timeout=20,
            )
            for j in r.json().get("jobs", []):
                places = ", ".join(x.get("name", "") for x in (j.get("locationRestrictions") or []))
                key = "him-" + str(j.get("guid") or j.get("applicationLink"))
                jobs[key] = {
                    "title": j["title"],
                    "company_name": j.get("companyName") or "your company",
                    "url": j["applicationLink"],
                    "location": places or "Worldwide",
                }
        except Exception as e:
            print("Himalayas fail:", q, e)
        time.sleep(3)
    print("Himalayas se jobs:", len(jobs) - before)


def location_ok(job):
    if not LOCATION_FILTER:
        return True
    loc = job["location"].lower().strip()
    if not loc:
        return True
    return any(word in loc for word in LOCATION_FILTER)


def title_ok(job):
    title = job["title"].lower()
    return not any(word in title for word in EXCLUDE_WORDS)


all_jobs = []
counts = {name: 0 for name in FIELDS}
skipped_location = 0
skipped_title = 0

for job in jobs.values():
    if not title_ok(job):
        skipped_title += 1
        continue
    if not location_ok(job):
        skipped_location += 1
        continue
    text = job["title"].lower()
    for skill, pattern in FIELDS.items():
        if counts[skill] < PER_FIELD and re.search(pattern, text):
            job["my_skill"] = skill
            all_jobs.append(job)
            counts[skill] += 1
            break

# ---------- emails.txt ----------
with open(EMAILS_FILE, "w", encoding="utf-8") as f:
    for job in all_jobs:
        skill = job["my_skill"]
        f.write(f"Subject: Application for {job['title']}\n\n")
        f.write(f"Dear {job['company_name']} Hiring Team,\n\n")
        f.write(f"I am writing to apply for the {job['title']} position. ")
        f.write(f"{SKILL_LINES[skill]}\n\n")
        f.write("I am a fast learner, I work well independently, and I can start right away. ")
        f.write("I would be happy to share samples of my work on request.\n\n")
        f.write(f"Job link: {job['url']}\n\n")
        f.write("Thank you for your time.\n\n")
        f.write(f"Regards,\n{MY_NAME}\n")
        f.write(f"Email: {MY_EMAIL}\n")
        f.write("\n" + "-" * 40 + "\n\n")

# ---------- jobs.csv tracker ----------
rows = {}
if os.path.exists(CSV_FILE):
    try:
        with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("Link"):
                    rows[row["Link"]] = row
    except Exception as e:
        print("Purani jobs.csv parhne me masla:", e)

new_count = 0
for job in all_jobs:
    if job["url"] not in rows:
        rows[job["url"]] = {
            "Job": job["title"],
            "Company": job["company_name"],
            "Link": job["url"],
            "Applied?": "nahi",
        }
        new_count += 1

try:
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Job", "Company", "Link", "Applied?"])
        writer.writeheader()
        writer.writerows(rows.values())
    print(f"\njobs.csv update: {new_count} nayi jobs, total {len(rows)}")
except PermissionError:
    print("\njobs.csv Excel/WPS me khuli hai, usay band karo aur dobara chalao.")

# ---------- summary ----------
print(f"\nMatch hui jobs: {len(all_jobs)}")
print(f"Location se hata di gayi: {skipped_location} | Title (Spanish waghera) se hata di gayi: {skipped_title}")
for i, job in enumerate(all_jobs, 1):
    print(f"{i}. [{job['my_skill']}] {job['title']}")

print("\n--- Hisaab ---")
for name, n in counts.items():
    print(f"{name}: {n} jobs")
print(f"{EMAILS_FILE} me drafts ban gaye")