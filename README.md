# Remote Job Finder Agent

A Python agent that finds remote jobs for me in three fields, filters out jobs I cannot apply to from Pakistan, drafts application emails, and tracks which jobs I have applied to.

## What it does

1. Collects remote jobs from 4 sources: **Remotive, RemoteOK, Jobicy and Himalayas**
2. Matches each job title to one of my fields using keywords:
   - AI and Machine Learning
   - SEO Content Writing
   - Website Development
3. Filters jobs by location (keeps Worldwide / Anywhere / Asia / Pakistan jobs) and removes unwanted titles
4. Writes a ready-to-send application email draft for every matched job (`emails.txt`)
5. Saves jobs in a tracker (`jobs.csv`) with an **Applied?** column. Old jobs are never added twice, only new ones.

## Tech used

- Python
- `requests` (job site APIs)
- `csv`, `re`, `html` (standard library)

## How to run

```
pip install requests
python job-agent.py
```

Close `jobs.csv` in Excel/WPS before running, otherwise it cannot be updated.

## Settings

All settings are at the top of `job-agent.py`:

- `MY_NAME`, `MY_EMAIL` for the email drafts
- `PER_FIELD` for how many jobs per field
- `KEYWORDS` to change the fields and matching words
- `LOCATION_FILTER` to control which locations are kept
- `USE_JOBICY`, `USE_HIMALAYAS` to turn sites on or off

## Output files

- `jobs.csv`: job tracker (Job, Company, Link, Applied?)
- `emails.txt`: application email drafts

Both files are in `.gitignore` because they contain personal data.

## Future plans

- Gemini-based match score between my CV and each job
- Streamlit app
- Daily automatic run with email or Telegram alerts

## Author

Maham, learning AI Engineering.