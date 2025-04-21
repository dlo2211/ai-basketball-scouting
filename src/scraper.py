# src/scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

from src.espn import scrape_from_espn
from src.ncaa import scrape_from_ncaa
from src.cbssports import scrape_from_cbs
from src.sportsref import scrape_from_sportsref

def scrape_player(player: Dict[str, str]) -> Dict[str, Any]:
    """
    Try ESPN first, then NCAA.com, then CBS Sports, and finally Sports-Reference.
    Always return a dict with status, ppg, rpg, apg, source, note.
    """
    # 1) ESPN
    res = scrape_from_espn(player)
    if res["status"] == 200 and any(res[k] is not None for k in ("ppg","rpg","apg")):
        return {**res, "source": "espn", "note": ""}

    # 2) NCAA.com fallback
    res = scrape_from_ncaa(player)
    if res["status"] == 200 and any(res[k] is not None for k in ("ppg","rpg","apg")):
        return res

    # 3) CBS Sports fallback
    res = scrape_from_cbs(player)
    if res["status"] == 200 and any(res[k] is not None for k in ("ppg","rpg","apg")):
        return res

    # 4) Sports‑Reference last resort
    res = scrape_from_sportsref(player)
    note = "" if any(res[k] is not None for k in ("ppg","rpg","apg")) else "No stats found"
    return {**res, "source": "sportsref", "note": note}
