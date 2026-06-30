import requests
from config import ODDS_API_KEY

BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds"

def buscar_odds_copa(regions="eu", markets="h2h,totals"):
    """
    Busca odds de todos os jogos disponíveis da Copa do Mundo 2026.
    Retorna a lista de jogos (cada um com seus bookmakers e mercados).
    """
    params = {
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal",
        "apiKey": ODDS_API_KEY,
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()  # lança erro se status != 200

    return response.json()


