# src/app.py

import streamlit as st
import pandas as pd
from typing import Dict, Any
from src.scraper import scrape_player

st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")
st.title("🏀 AI Basketball Scout")

# — Read API keys …
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY    = st.secrets["SERPAPI_KEY"]

st.sidebar.header("Upload roster CSV")
uploaded = st.sidebar.file_uploader("Drag and drop file here", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    # Expect columns: first_name, last_name
    stats = []
    for row in df.to_dict(orient="records"):
        s = scrape_player(row)
        stats.append(s)
    stats_df = pd.DataFrame(stats)
    result = pd.concat([df, stats_df], axis=1)

    st.success(f"Scraped stats for {len(result)} players")
    st.dataframe(result)

    # … your existing chat UI below …
