# src/scraper.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

SERPAPI_SEARCH_URL = "https://serpapi.com/search"

def discover_team_url(name: str, school: str) -> str | None:
    """(Still unimplemented)"""
    return None

def discover_url_via_serpapi(name: str, school: str, site: str) -> str | None:
    params = {"engine": "google", "q": f"site:{site} {name} {school}", "api_key": os.getenv("SERPAPI_KEY")}
    try:
        resp = requests.get(SERPAPI_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    for r in resp.json().get("organic_results", []):
        link = r.get("link")
        if link and site in link:
            return link
    return None

def discover_espn_url(name: str, school: str) -> str | None:
    """Legacy DuckDuckGo fallback for ESPN URLs"""
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            data={"q": f"site:espn.com/womens-college-basketball/player {name} {school}"},
            timeout=10
        )
        resp.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.select("a.result__a[href]"):
        href = a["href"]
        parsed = urlparse(href)
        # DuckDuckGo wraps real link in uddg=…  
        link = parse_qs(parsed.query).get("uddg", [href])[0]
        if "/womens-college-basketball/player/" in link:
            return link
    return None

def scrape_from_espn_url(record: dict, url: str) -> dict:
    """Robust scraper: summary block → career table → None"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return {**record, **dict.fromkeys(("points_per_game","rebounds_per_game","assists_per_game"))}

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) SUMMARY BLOCK: '2024-25 SEASON STATS'
    summary = soup.select_one("div.Table__Scroller table") or soup.select_one("div.PlayerHeader__Stats")
    if summary and "Season Stats" in resp.text:
        # ESPN’s summary block often uses spans with .value
        vals = summary.select("span.value")[:3]
        if len(vals) >= 3:
            try:
                ppg, rpg, apg = [float(v.get_text(strip=True)) for v in vals]
                return {**record, "points_per_game": ppg, "rebounds_per_game": rpg, "assists_per_game": apg}
            except ValueError:
                pass

    # 2) CAREER‑STATS TABLE fallback
    table = soup.select_one("div.Table__Scroller table")
    if table:
        tbody = table.select_one("tbody.Table__TBODY")
        # try 2024-25 then 2023-24
        for idx in ("0","1"):
            row = tbody.select_one(f'tr[data-idx="{idx}"]')
            if row:
                cells = row.find_all("td")
                try:
                    return {
                        **record,
                        "points_per_game": float(cells[2].get_text(strip=True)),
                        "rebounds_per_game": float(cells[3].get_text(strip=True)),
                        "assists_per_game": float(cells[4].get_text(strip=True))
                    }
                except (IndexError, ValueError):
                    continue

    # 3) Nothing worked
    return {**record, **dict.fromkeys(("points_per_game","rebounds_per_game","assists_per_game"))}

def scrape_player(record: dict) -> dict:
    """Master orchestrator with all fallbacks."""
    try:
        name   = f"{record['first_name']} {record['last_name']}"
        school = record["school"]
    except KeyError:
        return {**record, **dict.fromkeys(("points_per_game","rebounds_per_game","assists_per_game"))}

    # 1) Team site (not yet built)
    url = discover_team_url(name, school)
    if url:
        out = scrape_from_espn_url(record, url)
        if any(out[k] is not None for k in ("points_per_game","rebounds_per_game","assists_per_game")):
            return out

    # 2) SerpAPI → ESPN
    url = discover_url_via_serpapi(name, school, "espn.com/womens-college-basketball/player")
    if url:
        return scrape_from_espn_url(record, url)

    # 3) DuckDuckGo → ESPN
    url = discover_espn_url(name, school)
    if url:
        return scrape_from_espn_url(record, url)

    # 4) All fallbacks failed
    return {**record, **dict.fromkeys(("points_per_game","rebounds_per_game","assists_per_game"))}
