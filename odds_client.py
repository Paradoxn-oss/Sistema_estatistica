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


def encontrar_jogo(jogos, time_casa, time_visitante):
    """
    Filtra a lista de jogos para encontrar um confronto específico.
    Busca de forma flexível (case-insensitive, parcial).
    """
    time_casa = time_casa.lower()
    time_visitante = time_visitante.lower()

    for jogo in jogos:
        home = jogo["home_team"].lower()
        away = jogo["away_team"].lower()
        if (time_casa in home and time_visitante in away) or \
           (time_casa in away and time_visitante in home):
            return jogo

    return None

def resumir_odds(jogo):
    """
    Calcula a média do moneyline e do over/under entre todas as casas.
    """
    if not jogo:
        return None

    precos_casa, precos_fora, precos_empate = [], [], []
    precos_over, precos_under = [], []

    for bookmaker in jogo["bookmakers"]:
        for market in bookmaker["markets"]:
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    if outcome["name"] == jogo["home_team"]:
                        precos_casa.append(outcome["price"])
                    elif outcome["name"] == jogo["away_team"]:
                        precos_fora.append(outcome["price"])
                    elif outcome["name"] == "Draw":
                        precos_empate.append(outcome["price"])
            elif market["key"] == "totals":
                for outcome in market["outcomes"]:
                    if outcome["name"] == "Over":
                        precos_over.append(outcome["price"])
                    elif outcome["name"] == "Under":
                        precos_under.append(outcome["price"])

    media = lambda lista: round(sum(lista) / len(lista), 2) if lista else None

    return {
        "casa_de_apostas_consultadas": len(jogo["bookmakers"]),
        "odd_media_casa": media(precos_casa),
        "odd_media_fora": media(precos_fora),
        "odd_media_empate": media(precos_empate),
        "odd_media_over_2_5": media(precos_over),
        "odd_media_under_2_5": media(precos_under),
    }