# src/scraper.py

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment
from typing import Dict, Any

def parse_sportsref_stats(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract PPG, RPG, APG from a Sports-Reference college basketball page.
    Uses pandas.read_html on either:
     1) the live <table id="per_game">, or
     2) the commented-out table inside <div id="all_per_game">.
    """
    # 1) Try the live table first
    live_table = soup.find("table", id="per_game")
    html_table = None

    if live_table:
        html_table = str(live_table)
    else:
        # 2) Fallback: extract the commented table inside div#all_per_game
        wrapper = soup.find("div", id="all_per_game")
        if wrapper:
            m = re.search(
                r'<!--\s*(<table[^>]*id="per_game"[^>]*>.*?</table>)\s*-->',
                str(wrapper),
                flags=re.DOTALL
            )
            if m:
                html_table = m.group(1)

    if not html_table:
        return {"ppg": None, "rpg": None, "apg": None}

    # 3) Parse with pandas

    # 3) Parse with pandas
    try:
        df = pd.read_html(html_table)[0]
    except ValueError:
        return {"ppg": None, "rpg": None, "apg": None}

    if df.empty:
        return {"ppg": None, "rpg": None, "apg": None}

    # 4) Take the last row
    last = df.iloc[-1]
    ppg = last.get("PTS", last.get("PPG", None))
    rpg = last.get("TRB", last.get("RPG", None))
    apg = last.get("AST", last.get("APG", None))

    return {
        "ppg": float(ppg) if ppg not in (None, "") else None,
        "rpg": float(rpg) if rpg not in (None, "") else None,
        "apg": float(apg) if apg not in (None, "") else None,
    }

def scrape_from_sportsref(player: Dict[str, str]) -> Dict[str, Any]:
    """
    Build the URL based on player’s name, fetch the page, and return stats.
    """
    slug = f"{player['last_name'].lower()}-{player['first_name'].lower()}"
    url = f"https://www.sports-reference.com/cbb/players/{player['last_name'][0].lower()}/{slug}-1.html"
    print(f"Trying Sports‑Ref URL '{url}'", end="")

    resp = requests.get(url)
    print(f" → status {resp.status_code}")
    if resp.status_code != 200:
        return {"ppg": None, "rpg": None, "apg": None}

    soup = BeautifulSoup(resp.text, "html.parser")
    return parse_sportsref_stats(soup)

# alias for backward‑compat with app.py’s import
scrape_player = scrape_from_sportsref
