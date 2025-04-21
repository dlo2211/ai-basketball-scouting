import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any

def parse_sportsref_stats(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract PPG, RPG, APG from a Sports-Reference college basketball page.
    """
    live = soup.find("table", id="per_game")
    html_table = str(live) if live else None

    if not html_table:
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

    try:
        df = pd.read_html(html_table)[0]
    except ValueError:
        return {"ppg": None, "rpg": None, "apg": None}

    if df.empty:
        return {"ppg": None, "rpg": None, "apg": None}

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
    Given {"first_name": "...", "last_name": "..."}, fetch and parse stats.
    """
    last, first = player["last_name"].lower(), player["first_name"].lower()
    slug = f"{last}-{first}"
    url = f"https://www.sports-reference.com/cbb/players/{last[0]}/{slug}-1.html"
    print(f"Trying Sports‑Ref URL '{url}'", end="")
    resp = requests.get(url)
    print(f" → status {resp.status_code}")
    if resp.status_code != 200:
        return {"status": resp.status_code, "ppg": None, "rpg": None, "apg": None}

    soup = BeautifulSoup(resp.text, "html.parser")
    stats = parse_sportsref_stats(soup)
    return {"status": 200, **stats}

# For backward‑compat with app.py
scrape_player = scrape_from_sportsref
