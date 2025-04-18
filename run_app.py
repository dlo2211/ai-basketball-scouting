#!/usr/bin/env python3
import os, sys

# 1. Prepend the pip‑env site‑packages to sys.path
# Adjust the path if your Python version differs
site_pkgs = os.path.join(
    os.getcwd(), 
    ".pythonlibs", "lib", "python3.11", "site-packages"
)
if os.path.isdir(site_pkgs):
    sys.path.insert(0, site_pkgs)

# 2. Set Streamlit server options via environment
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_PORT"] = os.getenv("PORT", "8501")

# 3. Call Streamlit’s CLI entrypoint
from streamlit.web import cli as stcli
sys.argv = ["streamlit", "run", "src/app.py"]
sys.exit(stcli.main())
