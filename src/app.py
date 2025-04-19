import subprocess, streamlit as st
sha = subprocess.getoutput("git rev-parse --short HEAD")
import streamlit as st
import os
import json
import logging
import pandas as pd
from scraper import scrape_player

# ——— Debug: list installed packages ———
installed = sorted(f"{p.project_name}=={p.version}" for p in pkg_resources.working_set)

enriched_df = enrich(df.to_dict("records"))
st.success(f"✅ Scraped stats for {len(enriched_df)} players")

# Display table
st.markdown("## Enriched Roster with Stats")
st.dataframe(enriched_df, use_container_width=True)

# Chat interface
st.markdown("---")
st.header("Chat with your Scout")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":"You are an expert basketball scout."}]
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
user_input = st.chat_input("Ask anything about this roster...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    roster_json = enriched_df.to_json(orient="records")
    api_msgs = [
        st.session_state.messages[0],
        {"role":"system","content":f"Roster data: {roster_json}"}
    ] + st.session_state.messages[1:]
    resp = OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
        model="gpt-4o-mini", messages=api_msgs
    )
    answer = resp.choices[0].message.content
    st.session_state.messages.append({"role":"assistant","content":answer})
    st.chat_message("assistant").write(answer)
