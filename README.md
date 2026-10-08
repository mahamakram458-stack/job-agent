# AI Job Agent

Python tool jo remote jobs dhoondta hai, Gemini se unhe score deta hai, aur Streamlit app me dikhata hai.

## Features
- Remotive API se jobs dhoondna (website development, SEO writing, AI/ML)
- Application emails ka draft banana (emails.txt)
- Gemini match score (jobs ko 1-10 score deta hai)
- Streamlit app (jobs table, minimum score slider, link se job kholna)

## Setup
1. Packages install karo:
   ```
   pip install -r requirements.txt
   ```
2. Project folder me `.env` file banao:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## Use
```
python job-agent.py   # naye jobs dhoondo
python match.py       # jobs ko score karo
streamlit run app.py  # app kholo
```

## Files
- `job-agent.py` : jobs dhoondta hai
- `match.py` : Gemini se score deta hai
- `app.py` : Streamlit app

## Future plans
- Streamlit Cloud par live deploy