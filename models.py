import csv
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(".env me GEMINI_API_KEY nahi mili. Check karo.")

client = genai.Client(api_key=API_KEY)


def pick_model():
    """Available models me se pehla text wala flash model chunta hai."""
    skip = ["live", "audio", "tts", "image", "transcribe", "translate",
            "robotics", "lyria", "thinking", "embedding", "veo"]
    for m in client.models.list():
        name = m.name.replace("models/", "")
        actions = getattr(m, "supported_actions", None) or []
        if actions and "generateContent" not in actions:
            continue
        if "flash" in name and not any(w in name for w in skip):
            return name
    raise SystemExit("Koi flash model nahi mila. python models.py chala ke dekho.")


MODEL = pick_model()
print("Model:", MODEL)

MY_PROFILE = """
Skills: Python and machine learning basics, SEO content writing,
website development with HTML, CSS, WordPress and Elementor.
Looking for: remote jobs, junior or entry level, can work from Pakistan.
"""

CSV_FILE = "jobs.csv"
COLUMNS = ["Job", "Company", "Link", "Applied?", "Score", "Reason"]
MAX_JOBS = 15  # ek baar me kitni jobs score karni hain

try:
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
except FileNotFoundError:
    raise SystemExit("jobs.csv nahi mili. Pehle python job-agent.py chalao.")

print(len(rows), "jobs jobs.csv me hain")

done = 0
for row in rows:
    if row.get("Score"):
        continue
    if done >= MAX_JOBS:
        break

    prompt = (
        f"Candidate profile:\n{MY_PROFILE}\n"
        f"Job title: {row['Job']}\nCompany: {row['Company']}\n\n"
        "Give a match score from 1 to 10 and a short reason (max 12 words). "
        "Reply ONLY in this format: 8 | reason"
    )

    try:
        resp = client.models.generate_content(model=MODEL, contents=prompt)
        text = resp.text.strip()
        if "|" in text:
            score, reason = text.split("|", 1)
        else:
            score, reason = text, ""
        row["Score"] = score.strip()
        row["Reason"] = reason.strip()
    except Exception as e:
        print("Fail:", row["Job"], "->", e)
        continue

    done += 1
    print(f"{row['Score']}/10 - {row['Job']} ({row['Reason']})")
    time.sleep(4)

try:
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{done} jobs score ho gayi, jobs.csv update ho gayi")
except PermissionError:
    print("\njobs.csv Excel/WPS me khuli hai, band karke dobara chalao.")