# card-prices

Daily snapshot of TCGplayer market prices for Pokémon and One Piece singles, used by the Collection Valuer app.

- `build_prices.py` pulls TCGplayer's catalog and prices from tcgcsv.com.
- `.github/workflows/daily-prices.yml` runs it every morning (Sydney time) and commits `data/pokemon.json` and `data/onepiece.json`.
- Run it on demand: Actions tab → **Daily TCGplayer prices** → **Run workflow**.
