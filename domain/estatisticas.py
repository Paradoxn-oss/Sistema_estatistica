def calcular_estatisticas_gols(jogos, nome_time):
    gols_marcados = 0
    gols_sofridos = 0
    clean_sheets = 0

    for jogo in jogos:
        if jogo["casa"] == nome_time:
            marcados, sofridos = jogo["placar_casa"], jogo["placar_fora"]
        else:
            marcados, sofridos = jogo["placar_fora"], jogo["placar_casa"]

        gols_marcados += marcados
        gols_sofridos += sofridos
        if sofridos == 0:
            clean_sheets += 1

    total_jogos = len(jogos)
    media_marcados = round(gols_marcados / total_jogos, 2) if total_jogos else 0
    media_sofridos = round(gols_sofridos / total_jogos, 2) if total_jogos else 0

    return {
        "gols_marcados": gols_marcados,
        "gols_sofridos": gols_sofridos,
        "media_marcados": media_marcados,
        "media_sofridos": media_sofridos,
        "clean_sheets": clean_sheets,
    }


def resultado_jogo(jogo, nome_time):
    if jogo["casa"] == nome_time:
        gols_time, gols_adv = jogo["placar_casa"], jogo["placar_fora"]
    else:
        gols_time, gols_adv = jogo["placar_fora"], jogo["placar_casa"]

    if gols_time > gols_adv:
        return "V"
    elif gols_time < gols_adv:
        return "D"
    return "E"

def resumir_odds(jogo):
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