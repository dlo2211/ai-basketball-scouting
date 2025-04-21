# src/cbssports.py

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def scrape_from_cbs(player: Dict[str, str]) -> Dict[str, Any]:
    """
    Second‐fallback: try CBS Sports if NCAA fails.
    """
    slug = f"{player['first_name']}-{player['last_name']}".lower()
    url = f"https://www.cbssports.com/college-basketball/players/{slug}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {
            "status": resp.status_code,
            "ppg": None,
            "rpg": None,
            "apg": None,
            "source": "cbs",
            "note": f"CBS {resp.status_code}"
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    try:
        # (Adjust selectors to match CBS's actual markup)
        ppg = float(soup.select_one(".stats-ppg").text)
        rpg = float(soup.select_one(".stats-rpg").text)
        apg = float(soup.select_one(".stats-apg").text)
        return {
            "status": 200,
            "ppg": ppg,
            "rpg": rpg,
            "apg": apg,
            "source": "cbs",
            "note": ""
        }
    except Exception:
        return {
            "status": 200,
            "ppg": None,
            "rpg": None,
            "apg": None,
            "source": "cbs",
            "note": "CBS parse failed"
        }
