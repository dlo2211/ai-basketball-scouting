# src/app.py

import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from src.scraper import scrape_player

# Load .env
load_dotenv()

st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content":
            "You are AI Basketball Scout ChatBot. "
            "I will upload a roster CSV, you will scrape each player's 2024‑25 (or 2023‑24) PPG/RPG/APG, "
            "then we’ll chat about that enriched roster."
        }
    ]

st.title("🏀 AI Basketball Scout")
st.write("This is a conversational front end powered by OpenAI. Upload a roster to begin.")

# 1) File uploader
uploaded = st.file_uploader("Choose a roster CSV", type="csv")

@st.cache_data(show_spinner=False)
def get_enriched_df(records):
    """Scrape all players once, showing progress."""
    df_list = []
    prog = st.progress(0, text="Scraping stats…")
    total = len(records)
    for idx, rec in enumerate(records, start=1):
        df_list.append(scrape_player(rec))
        prog.progress(idx / total, text=f"Processed {idx}/{total}")
    return pd.DataFrame(df_list)

# 2) Process upload
if uploaded:
    raw_df = pd.read_csv(uploaded)
    raw_df = raw_df.rename(columns={
        "First Name": "first_name",
        "Last Name":  "last_name",
        "Institution":"school"
    })
    records = raw_df.to_dict(orient="records")

    # Only scrape once per session
    if "enriched_df" not in st.session_state:
        st.session_state.enriched_df = get_enriched_df(records)
        st.success(f"✅ Scraped stats for {len(records)} players")

# If no data yet, stop here
if "enriched_df" not in st.session_state:
    st.stop()

# 3) Tabs: Roster view and Chat
tab1, tab2 = st.tabs(["Roster", "Scout Chat"])

with tab1:
    st.markdown("### Enriched Roster with Stats")
    st.dataframe(st.session_state.enriched_df, use_container_width=True)

with tab2:
    st.header("Chat with your Scout")
    # render history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    # get user input
    user_input = st.chat_input("Ask a question about this roster…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        roster_json = json.dumps(st.session_state.enriched_df.to_dict(orient="records"))
        api_msgs = [
            st.session_state.messages[0],
            {"role": "system", "content": f"Roster data: {roster_json}"}
        ] + st.session_state.messages[1:]

        with st.spinner("🤖 Thinking…"):
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_msgs
            )
            answer = resp.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
