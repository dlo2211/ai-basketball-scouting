import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs, unquote

# SerpAPI HTTP endpoint for search
SERPAPI_SEARCH_URL = "https://serpapi.com/search"

def discover_team_url(name: str, school: str) -> str | None:
    query = f"{name} {school} athletics player profile"
    headers = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )}
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query}, timeout=10, headers=headers
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", class_="result__a", href=True):
        href = a["href"]
        if school.replace(" ", "").lower() in href.lower() and "player" in href.lower():
            return href
    return None


def scrape_from_team_url(record: dict, url: str) -> dict | None:
    # TODO: implement school-site scraping
    return None


def discover_url_via_serpapi(name: str, school: str, site: str) -> str | None:
    query = f"site:{site} {name} {school}"
    params = {"engine": "google", "q": query, "api_key": os.getenv("SERPAPI_KEY")}
    print("DEBUG SerpAPI query:", query)
    resp = requests.get(SERPAPI_SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("organic_results", [])
    print(f"DEBUG SerpAPI returned {len(results)} results")
    for r in results:
        link = r.get("link")
        if link and site in link:
            print("DEBUG serpapi selected link:", link)
            return link
    print("DEBUG serpapi: no matching link")
    return None


def discover_espn_url(name: str, school: str) -> str | None:
    query = f"site:espn.com/womens-college-basketball/player {name} {school}"
    headers = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )}
    print("DEBUG discover_espn_url query:", query)
    resp = requests.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query}, timeout=10, headers=headers
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.find_all("a", class_="result__a", href=True):
        raw = a["href"]
        parsed = urlparse(raw)
        qs = parse_qs(parsed.query)
        candidate = unquote(qs["uddg"][0]) if "uddg" in qs else raw
        print("DEBUG espn discovery candidate:", candidate)
        if "/womens-college-basketball/player/" in candidate:
            print("DEBUG espn_url selected:", candidate)
            return candidate
    print("DEBUG espn_url: none matched")
    return None


def scrape_from_espn_url(record: dict, url: str) -> dict:
    headers = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    page_text = BeautifulSoup(resp.text, "html.parser").get_text()

    stats = {"points_per_game": None, "rebounds_per_game": None, "assists_per_game": None}
    m = re.search(r"PTS\s*([\d\.]+)", page_text)
    if m:
        stats["points_per_game"] = float(m.group(1))
    m = re.search(r"REB\s*([\d\.]+)", page_text)
    if m:
        stats["rebounds_per_game"] = float(m.group(1))
    m = re.search(r"AST\s*([\d\.]+)", page_text)
    if m:
        stats["assists_per_game"] = float(m.group(1))

    return { **record, **stats }


def scrape_player(record: dict) -> dict:
    full_name = f"{record['first_name']} {record['last_name']}"
    school = record['school']

    # 1) Team site
    team_url = discover_team_url(full_name, school)
    print("DEBUG team_url:", team_url)
    if team_url:
        stats = scrape_from_team_url(record, team_url)
        if stats:
            return stats

    # 2) Manual override
    manual = record.get("espn_url")
    if manual:
        print("DEBUG using provided espn_url:", manual)
        return scrape_from_espn_url(record, manual)

    # 3) SerpAPI search
    serp_url = discover_url_via_serpapi(
        full_name,
        school,
        "espn.com/womens-college-basketball/player"
    )
    print("DEBUG serpapi espn_url:", serp_url)
    if serp_url:
        return scrape_from_espn_url(record, serp_url)

    # 4) Legacy fallback
    espn_url = discover_espn_url(full_name, school)
    print("DEBUG legacy espn_url:", espn_url)
    if espn_url:
        return scrape_from_espn_url(record, espn_url)

    # 5) Final fallback
    print("DEBUG all methods failed, returning None stats")
    return {
        **record,
        "points_per_game": None,
        "rebounds_per_game": None,
        "assists_per_game": None
    }
