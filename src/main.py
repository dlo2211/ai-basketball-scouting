import os
from dotenv import load_dotenv
import pandas as pd
from csv_loader import load_players
from scraper import scrape_player
import openai

# ---------------------------------------------------------------------------
# 1) BATCH SCRAPE AS BEFORE
# ---------------------------------------------------------------------------
def batch_scrape(csv_path: str, output_csv: str = "enriched_players.csv") -> pd.DataFrame:
    load_dotenv()  # loads SERPAPI_KEY, OPENAI_API_KEY, etc.

    df = load_players(csv_path)
    enriched = []
    for _, row in df.iterrows():
        rec = row.to_dict()
        print(f"⌛ Processing {rec['first_name']} {rec['last_name']}…")
        enriched.append(scrape_player(rec))

    df_enriched = pd.DataFrame(enriched)
    df_enriched.to_csv(output_csv, index=False)
    print(f"\n✅ Saved enriched data to {output_csv}")
    print(df_enriched.head(10))
    return df_enriched

# ---------------------------------------------------------------------------
# 2) CHAT‑STYLE FILTERING WITH OpenAI v1
# ---------------------------------------------------------------------------
def chat_filter_loop(df: pd.DataFrame):
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_msg = {
        "role": "system",
        "content": (
            "You are an assistant that converts user’s natural‑language filters "
            "into pandas query expressions. The DataFrame columns are: "
            "first_name, last_name, school, points_per_game, rebounds_per_game, assists_per_game. "
            "Respond with exactly the boolean expression (e.g. points_per_game >= 2.5)."
        )
    }
    convo = [system_msg]

    print("\n💬 Chat‑style filtering ready! Examples:")
    print(" • show me players under 8 PPG")
    print(" • schools containing 'State'")
    print(" • assists above 2.5\n")

    while True:
        user_msg = input("You: ")
        if user_msg.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        convo.append({"role": "user", "content": user_msg})
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=convo,
            temperature=0.0
        )
        expr = resp.choices[0].message.content.strip()
        convo.append({"role": "assistant", "content": expr})

        print(f"\n🔍 Applying filter: {expr}")
        try:
            df_filt = df.query(expr)
            if df_filt.empty:
                print("⚠️ No rows matched.")
            else:
                print(df_filt.to_string(index=False))
        except Exception as e:
            print(f"❌ Failed to apply filter: {e}")
        print("\n—\n")

if __name__ == "__main__":
    roster_csv = "womens_basketball_players_2024_25.csv"
    if not os.path.exists(roster_csv):
        raise FileNotFoundError(f"Roster CSV not found at {roster_csv}")
    print(f"ℹ️ Using roster CSV: {roster_csv}")

    df = batch_scrape(roster_csv)
    chat_filter_loop(df)
