# stats_client.py
import requests
from config import FOOTBALL_API_KEY

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}


def buscar_id_time(nome_time):
    """
    Busca o ID de um time da Copa do Mundo pelo nome (em inglês).
    Retorna o ID ou None se não encontrar.
    """
    response = requests.get(f"{BASE_URL}/competitions/WC/teams", headers=HEADERS)
    response.raise_for_status()
    times = response.json()["teams"]

    nome_busca = nome_time.lower()
    for time in times:
        if nome_busca in time["name"].lower():
            return time["id"], time["name"]

    return None, None


def buscar_forma_recente(team_id, quantidade=5):
    """
    Busca os últimos N jogos finalizados de um time (qualquer competição,
    não só a Copa, já que forma recente importa mesmo de fora do torneio).
    Retorna o resumo (vitórias/empates/derrotas) e a lista de jogos.
    """
    response = requests.get(
        f"{BASE_URL}/teams/{team_id}/matches",
        headers=HEADERS,
        params={"status": "FINISHED", "limit": quantidade},
    )
    response.raise_for_status()
    dados = response.json()

    resumo = dados.get("resultSet", {})
    jogos = []

    for partida in dados.get("matches", []):
        jogos.append({
            "data": partida["utcDate"][:10],
            "competicao": partida["competition"]["name"],
            "casa": partida["homeTeam"]["name"],
            "fora": partida["awayTeam"]["name"],
            "placar_casa": partida["score"]["fullTime"]["home"],
            "placar_fora": partida["score"]["fullTime"]["away"],
        })

    return resumo, jogos


def calcular_estatisticas_gols(jogos, nome_time):
    """
    A partir da lista de jogos recentes (que já temos), calcula:
    - gols marcados e sofridos (total e média)
    - quantos jogos sem sofrer gol (clean sheets)
    """
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

def buscar_id_jogo_copa(nome_casa, nome_fora):
    try:
        response = requests.get(f"{BASE_URL}/competitions/WC/matches", headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None

    matches = response.json().get("matches", [])
    nome_casa = nome_casa.lower()
    nome_fora = nome_fora.lower()

    for match in matches:
        casa = match["homeTeam"]["name"].lower()
        fora = match["awayTeam"]["name"].lower()
        if (nome_casa in casa and nome_fora in fora) or \
           (nome_casa in fora and nome_fora in casa):
            return match["id"]

    return None


def buscar_head2head(match_id, limite=5):
    """
    Busca o histórico de confrontos diretos entre os dois times de um jogo.
    Se a API recusar (rate limit, erro de rede, etc.), retorna None
    em vez de travar a página inteira.
    """
    if not match_id:
        return None

    try:
        response = requests.get(
            f"{BASE_URL}/matches/{match_id}/head2head",
            headers=HEADERS,
            params={"limit": limite},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None  # rate limit ou outro erro — segue sem head2head

    dados = response.json()
    resumo_h2h = dados.get("aggregates", {})
    confrontos = []

    for partida in dados.get("matches", []):
        confrontos.append({
            "data": partida["utcDate"][:10],
            "competicao": partida["competition"]["name"],
            "casa": partida["homeTeam"]["name"],
            "fora": partida["awayTeam"]["name"],
            "placar_casa": partida["score"]["fullTime"]["home"],
            "placar_fora": partida["score"]["fullTime"]["away"],
        })

    return {"resumo": resumo_h2h, "confrontos": confrontos}