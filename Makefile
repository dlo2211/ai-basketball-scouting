.PHONY: setup smoke test run

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

smoke:
	. venv/bin/activate && \
	python3 - <<EOF2 \
from src.scraper import scrape_from_sportsref;\
print(scrape_from_sportsref({"first_name":"Zion","last_name":"Williamson"}))\
EOF2

test:
	. venv/bin/activate && pytest --maxfail=1 -q

run:
	. venv/bin/activate && streamlit run src/app.py
