import streamlit as st
import pandas as pd
from scraper import scrape_player

# 1. Page config
st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

# 2. Title & uploader
st.title("🏀 AI Basketball Scout – Scrape Test")
uploaded = st.file_uploader("Upload roster CSV", type="csv")
if not uploaded:
    st.info("Please upload a roster CSV to begin.")
    st.stop()

# 3. Load & normalize
df = pd.read_csv(uploaded).rename(columns={
    "First Name":"first_name",
    "Last Name":"last_name",
    "Institution":"school"
})

# 4. Scrape & cache
@st.cache_data(show_spinner=False)
def enrich(records):
    return pd.DataFrame([scrape_player(r) for r in records])

enriched_df = enrich(df.to_dict("records"))
st.markdown("## Scraped Stats")
st.dataframe(enriched_df, use_container_width=True)
