import streamlit as st
import pandas as pd

# 1. Page config
st.set_page_config(page_title="🏀 AI Basketball Scout", layout="wide")

# 2. Title & uploader
st.title("🏀 AI Basketball Scout – Upload Test")
uploaded = st.file_uploader("Upload roster CSV", type="csv")
if not uploaded:
    st.info("Please upload a roster CSV to begin.")
    st.stop()

# 3. Load & display
df = pd.read_csv(uploaded)
st.markdown("## CSV Preview")
st.dataframe(df, use_container_width=True)
