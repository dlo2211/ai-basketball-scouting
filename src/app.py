import os
import streamlit as st
import pandas as pd
from openai import OpenAI
from scraper import scrape_player

# — Page config must be first —
st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

# — Read API keys from Streamlit Secrets —
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY    = st.secrets["SERPAPI_KEY"]
if not OPENAI_API_KEY or not SERPAPI_KEY:
    st.error("Missing API keys! Add them under Settings → Secrets.")
    st.stop()

# — Initialize OpenAI client —
client = OpenAI(api_key=OPENAI_API_KEY)

# — App title & CSV uploader —
st.title("🏀 AI Basketball Scout")
uploaded = st.file_uploader("Upload roster CSV", type="csv")
if not uploaded:
    st.info("Please upload a roster CSV to begin.")
    st.stop()

# — Load & normalize DataFrame —
df = pd.read_csv(uploaded).rename(columns={
    "First Name": "first_name",
    "Last Name":  "last_name",
    "Institution": "school",
})

# — Scrape & cache results —
@st.cache_data(show_spinner=False)
def enrich(records):
    return pd.DataFrame([scrape_player(r) for r in records])

enriched_df = enrich(df.to_dict("records"))
st.success(f"✅ Scraped stats for {len(enriched_df)} players")

# — Show enriched table —
st.markdown("## Enriched Roster with Stats")
st.dataframe(enriched_df, use_container_width=True)

# — Chat interface —
st.markdown("---")
st.header("Chat with your Scout")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert basketball scout."}
    ]

# render existing messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# user input
user_msg = st.chat_input("Ask anything about this roster…")
if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # include roster as system context
    roster_json = enriched_df.to_json(orient="records")
    api_msgs = [
        st.session_state.messages[0],
        {"role": "system", "content": f"Roster data: {roster_json}"},
    ] + st.session_state.messages[1:]

    # call OpenAI
    resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=api_msgs
    )
    answer = resp.choices[0].message.content

    # display & save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
