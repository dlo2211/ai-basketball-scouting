# src/ncaa.py

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def scrape_from_ncaa(player: Dict[str, str]) -> Dict[str, Any]:
    """
    Fallback #1: scrape stats from data.ncaa.com
    """
    last, first = player["last_name"].lower(), player["first_name"].lower()
    url = f"https://data.ncaa.com/casbasketball/{last}-{first}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {
            "status": resp.status_code,
            "ppg": None, "rpg": None, "apg": None,
            "source": "ncaa",
            "note": f"NCAA {resp.status_code}"
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    try:
        ppg = float(soup.select_one(".stat-ppg").text)
        rpg = float(soup.select_one(".stat-rpg").text)
        apg = float(soup.select_one(".stat-apg").text)
        return {
            "status": 200,
            "ppg": ppg, "rpg": rpg, "apg": apg,
            "source": "ncaa",
            "note": ""
        }
    except Exception:
        return {
            "status": 200,
            "ppg": None, "rpg": None, "apg": None,
            "source": "ncaa",
            "note": "NCAA parse failed"
        }
