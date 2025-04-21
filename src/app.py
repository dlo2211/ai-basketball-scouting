# ... your existing imports ...
import streamlit as st
import pandas as pd
from src.scraper import scrape_player

st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

# — Read your CSV file upload …
uploaded = st.file_uploader("Upload players CSV", type="csv")
if uploaded:
    players_df = pd.read_csv(uploaded)
    enriched_rows = []
    for _, row in players_df.iterrows():
        base = {"first_name": row.first_name, "last_name": row.last_name}
        stats = scrape_player(base)
        enriched_rows.append({**base, **stats})
    enriched = pd.DataFrame(enriched_rows)

    # Display with source & note
    enriched = enriched.astype(str)
    st.dataframe(enriched[[
        "first_name","last_name","status",
        "ppg","rpg","apg","source","note"
    ]])
