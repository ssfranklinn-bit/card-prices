"""Builds compact TCGplayer price files for Pokémon and One Piece from tcgcsv.com.

tcgcsv.com republishes TCGplayer's official catalog and market prices once a day.
Output: data/pokemon.json and data/onepiece.json
  {"updated": "...", "groups": [[groupId, name, abbreviation], ...],
   "cards": [[groupIndex, productId, name, number, subType, market, low], ...]}
Only singles (rows with a collector number) are kept.
"""
import csv, io, json, os, time, urllib.request
from datetime import datetime, timezone

BASE = "https://tcgcsv.com/tcgplayer"
GAMES = {"pokemon": 3, "onepiece": 68}
UA = {"User-Agent": "card-prices-daily/1.0 (github.com/ssfranklinn-bit/card-prices)"}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def num(v):
    try:
        return round(float(v), 2) if v not in ("", None) else None
    except ValueError:
        return None


def build(game, cat):
    groups = json.loads(get(f"{BASE}/{cat}/groups"))["results"]
    out_groups, cards = [], []
    for g in groups:
        try:
            text = get(f"{BASE}/{cat}/{g['groupId']}/ProductsAndPrices.csv")
        except Exception as e:
            print(f"skip {g['groupId']} {g['name']}: {e}")
            continue
        gi = len(out_groups)
        kept = 0
        for row in csv.DictReader(io.StringIO(text)):
            number = (row.get("extNumber") or "").strip()
            if not number:
                continue
            market, low = num(row.get("marketPrice")), num(row.get("lowPrice"))
            cards.append([gi, int(row["productId"]), row.get("name", ""), number,
                          row.get("subTypeName", ""), market, low])
            kept += 1
        if kept:  # gi is this group's index, since it is appended only when it has cards
            out_groups.append([g["groupId"], g["name"], g.get("abbreviation") or ""])
        time.sleep(0.15)
    return out_groups, cards


def main():
    os.makedirs("data", exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    for game, cat in GAMES.items():
        groups, cards = build(game, cat)
        with open(f"data/{game}.json", "w", encoding="utf-8") as f:
            json.dump({"updated": stamp, "groups": groups, "cards": cards}, f,
                      ensure_ascii=False, separators=(",", ":"))
        print(game, len(groups), "sets", len(cards), "rows")


if __name__ == "__main__":
    main()
