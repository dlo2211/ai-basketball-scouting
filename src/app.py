# Updated `src/app.py`
```python
import os
import json
import logging

import streamlit as st
import pandas as pd
from openai import OpenAI
from src.scraper import scrape_player

# ——— Local .env fallback (for development) ———
if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        st.info("Loaded local .env for development")
    except ImportError:
        pass  # python-dotenv not installed

# ——— Logging setup ———
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
logger.info("Starting Streamlit app…")

# ——— Read secrets from environment ———
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY    = os.getenv("SERPAPI_KEY")

if not OPENAI_API_KEY or not SERPAPI_KEY:
    st.error("API keys not found. Make sure your Streamlit Secrets or .env are configured.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Page config
st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

# Title & file upload
st.title("🏀 AI Basketball Scout")
uploaded = st.file_uploader("Upload roster CSV", type="csv")
if not uploaded:
    st.info("Please upload a roster CSV to begin.")
    st.stop()

# Load & normalize DataFrame
df = pd.read_csv(uploaded).rename(columns={
    "First Name": "first_name",
    "Last Name":  "last_name",
    "Institution": "school"
})

# Scrape & cache results
@st.cache_data(show_spinner=False)
def enrich(records):
    return pd.DataFrame([scrape_player(r) for r in records])

enriched_df = enrich(df.to_dict("records"))
st.success(f"✅ Scraped stats for {len(enriched_df)} players")

# Display enriched table
st.markdown("## Enriched Roster with Stats")
st.dataframe(enriched_df, use_container_width=True)

# Chat interface
st.markdown("---")
st.header("Chat with your Scout")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert basketball scout analyzing this roster."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask anything about this roster...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    roster_json = enriched_df.to_json(orient="records")
    api_msgs = [
        st.session_state.messages[0],
        {"role": "system", "content": f"Roster data: {roster_json}"}
    ] + st.session_state.messages[1:]
    resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=api_msgs
    )
    answer = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
```

---


