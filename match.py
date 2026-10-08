import csv, os, time, json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(".env me GEMINI_API_KEY nahi mili.")
client = genai.Client(api_key=API_KEY)

PROFILE = "Skills: Python, ML basics, SEO writing, HTML, CSS, WordPress, Elementor. Looking for remote junior jobs from Pakistan."
CSV_FILE = "jobs.csv"
MAX_JOBS = 15
RETRIES = 3
GAP = 7
BAD = ("image", "tts", "live", "audio", "embedding", "native")


def pick_models():
    out = []
    try:
        for m in client.models.list():
            acts = getattr(m, "supported_actions", None) or []
            n = m.name.replace("models/", "")
            if "generateContent" in acts and "flash" in n \
                    and not any(x in n for x in BAD):
                out.append(n)
    except Exception as e:
        print("Model list nahi mili:", str(e)[:100])
    out.sort(key=lambda x: (0 if "lite" in x else 1, x))
    return out or ["gemini-2.5-flash"]


MODELS = pick_models()
idx = 0
print("Available models:", MODELS)
print("Pehla model:", MODELS[idx])


def ask(row):
    global idx
    info = "\n".join(f"{k}: {str(v)[:1000]}" for k, v in row.items()
                     if k not in ("Score", "Reason", "Applied?"))
    prompt = ("My profile:\n" + PROFILE + "\n\nJob:\n" + info +
              '\n\nScore this job 1 to 10 for me. Reply only JSON: '
              '{"score": number, "reason": "one short line"}')
    while idx < len(MODELS):
        wait = 10
        for n in range(1, RETRIES + 1):
            try:
                r = client.models.generate_content(
                    model=MODELS[idx], contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"))
                d = json.loads(r.text)
                return int(float(d["score"])), str(d["reason"])[:200]
            except Exception as e:
                m = str(e)
                if "404" in m:
                    break
                if ("429" in m or "503" in m) and n < RETRIES:
                    print(f"  Busy, {wait}s baad dobara ({n}/{RETRIES})...")
                    time.sleep(wait)
                    wait *= 2
                    continue
                if "429" in m:
                    break
                raise
        idx += 1
        if idx < len(MODELS):
            print("Agla model try:", MODELS[idx])
    raise Exception("Koi model available nahi ya quota khatam")


with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
    rd = csv.DictReader(f)
    cols = list(rd.fieldnames)
    rows = list(rd)

for c in ("Score", "Reason"):
    if c not in cols:
        cols.append(c)
        for r in rows:
            r[c] = ""

todo = [r for r in rows if not str(r.get("Score", "")).strip()]
print(f"{len(rows)} jobs hain, {len(todo)} score hona baaki hain")

done = 0
fails = 0
try:
    for row in todo[:MAX_JOBS]:
        try:
            row["Score"], row["Reason"] = ask(row)
        except Exception as e:
            print("Fail:", row.get("Job"), "->", str(e)[:120])
            fails += 1
            if fails >= 3:
                print("\nLagatar 3 fail. Baad me dobara chalao.")
                break
            continue
        fails = 0
        done += 1
        print(f"{row['Score']}/10 - {row.get('Job')} ({row['Reason']})")
        time.sleep(GAP)
finally:
    try:
        with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\n{done} jobs score ho gayi, jobs.csv update ho gayi")
    except PermissionError:
        print("\njobs.csv Excel/WPS me khuli hai, band karke dobara chalao.")