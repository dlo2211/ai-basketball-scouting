# src/app.py
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from csv_loader import load_players
from scraper import scrape_player
import openai

# Load environment variables
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="AI Basketball Scouting Assistant", layout="wide")
st.title("🏀 AI Basketball Scouting Assistant")

# Initialize session state for dataframes and conversation history
if "df" not in st.session_state:
    st.session_state.df = None
if "df_enriched" not in st.session_state:
    st.session_state.df_enriched = None
if "conversation" not in st.session_state:
    st.session_state.conversation = None

# -----------------------------------------------------------------------------
# 1) File Upload Section
# -----------------------------------------------------------------------------
st.header("1. Upload Roster CSV")
uploaded_file = st.file_uploader(
    label="Browse and upload your NCAA roster CSV file",
    type=["csv"],
    help="Select a CSV with columns First Name, Last Name, Institution"
)

if uploaded_file:
    st.info("Loading roster into DataFrame...")
    st.session_state.df = load_players(uploaded_file)
    st.success(f"Loaded {len(st.session_state.df)} players")
    st.dataframe(st.session_state.df)

# -----------------------------------------------------------------------------
# 2) Data Enrichment (Scraping)
# -----------------------------------------------------------------------------
st.header("2. Scrape Stats")
if st.session_state.df is not None:
    if st.button("Run Scraping Logic"):
        with st.spinner("Enriching each player with PPG/RPG/APG..."):
            enriched = [scrape_player(row.to_dict()) for _, row in st.session_state.df.iterrows()]
            st.session_state.df_enriched = pd.DataFrame(enriched)
    if st.session_state.df_enriched is not None:
        st.success("Scraping complete!")
        st.dataframe(st.session_state.df_enriched)
        csv_bytes = st.session_state.df_enriched.to_csv(index=False).encode()
        st.download_button(
            label="Download enriched_players.csv",
            data=csv_bytes,
            file_name="enriched_players.csv",
            mime="text/csv",
        )

        # ---------------------------------------------------------------------
        # 3) Chat‑Style Filtering
        # ---------------------------------------------------------------------
        st.header("3. Chat‑Style Filtering")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=openai.api_key)

        if st.session_state.conversation is None:
            system_msg = {
                "role": "system",
                "content": (
                    "You convert natural‑language filters into pandas query expressions. "
                    "Columns: first_name, last_name, school, points_per_game, rebounds_per_game, assists_per_game. "
                    "Respond with exactly the boolean expression, e.g. 'points_per_game >= 2.5'."
                )
            }
            st.session_state.conversation = [system_msg]

        user_input = st.chat_input("Type a filter (e.g. 'under 8 PPG')")
        if user_input:
            st.session_state.conversation.append({"role": "user", "content": user_input})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.conversation,
                temperature=0.0
            )
            expr = resp.choices[0].message.content.strip()
            st.session_state.conversation.append({"role": "assistant", "content": expr})

            st.markdown(f"**Applying filter:** `{expr}`")
            try:
                df_filtered = st.session_state.df_enriched.query(expr)
                if df_filtered.empty:
                    st.warning("No players matched your criteria.")
                else:
                    st.dataframe(df_filtered)
            except Exception as e:
                st.error(f"Failed to apply filter: {e}")
