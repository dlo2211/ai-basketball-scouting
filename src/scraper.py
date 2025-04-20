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
                flags=re.DOTALL,
            )
            if m:
                html_table = m.group(1)

    if not html_table:
        return {"ppg": None, "rpg": None, "apg": None}

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

def scrape_from_sportsref(record: Dict[str, str]) -> Dict[str, Any]:
    """Fallback scraper: Sports-Reference college basketball with directory + retry suffixes."""
    first = record.get("first_name", "").lower()
    last = record.get("last_name", "").lower()
    if not first or not last:
        return {"ppg": None, "rpg": None, "apg": None}

    initial = last[0]
    for idx in (1, 2, 3):
        slug = f"{last}-{first}-{idx}"
        url = f"https://www.sports-reference.com/cbb/players/{initial}/{slug}.html"
        resp = requests.get(url, timeout=5)
        print(f"Trying Sports-Ref URL {url!r} → status", resp.status_code)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            return parse_sportsref_stats(soup)

    return {"ppg": None, "rpg": None, "apg": None}

def scrape_player(record: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrator: try ESPN first; if any stat is missing, fall back to Sports-Reference."""
    from espn_scraper import scrape_from_espn  # adjust this import if needed

    primary = scrape_from_espn(record)
    if None in (primary.get("ppg"), primary.get("rpg"), primary.get("apg")):
        fallback = scrape_from_sportsref(record)
        return {
            "ppg": primary.get("ppg") or fallback.get("ppg"),
            "rpg": primary.get("rpg") or fallback.get("rpg"),
            "apg": primary.get("apg") or fallback.get("apg"),
        }
    return primary
