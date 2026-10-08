import os
import subprocess
import sys

import pandas as pd
import streamlit as st

CSV_FILE = "jobs.csv"

st.set_page_config(page_title="Job Agent", layout="wide")
st.title("AI Job Agent")


def run_script(name):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    with st.spinner(f"{name} chal rahi hai, thora wait karo..."):
        r = subprocess.run(
            [sys.executable, name],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )
    out = (r.stdout + r.stderr).strip()
    st.code(out[-1500:] if out else "Koi output nahi")


c1, c2 = st.columns(2)
if c1.button("Naye jobs dhoondo"):
    run_script("job-agent.py")
if c2.button("Score karo"):
    run_script("match.py")

try:
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
except FileNotFoundError:
    st.warning("jobs.csv nahi mili. Pehle 'Naye jobs dhoondo' dabao.")
    st.stop()

if "Score" not in df.columns:
    st.info("Abhi score nahi hue. 'Score karo' dabao.")
    st.stop()

df["Score"] = pd.to_numeric(df["Score"], errors="coerce")

min_score = st.slider("Minimum score", 0, 10, 7)
show = df[df["Score"] >= min_score].sort_values("Score", ascending=False)

st.write(f"{len(show)} jobs dikh rahi hain (total {len(df)})")
st.dataframe(
    show,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="Kholo"),
    },
)