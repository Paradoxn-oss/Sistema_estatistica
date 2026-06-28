from flask import Flask, render_template
from datetime import datetime, timedelta, timezone

from odds_client import buscar_odds_copa, encontrar_jogo, resumir_odds
from stats_client import buscar_id_time, buscar_forma_recente
from stats_client import buscar_id_time, buscar_forma_recente, calcular_estatisticas_gols, buscar_id_jogo_copa, buscar_head2head

app = Flask(__name__)

JANELA_HORAS = 24

def montar_relatorio(time_casa_en, time_fora_en, qtd_jogos=5):
    """
    Busca odds + forma recente dos dois times e organiza tudo num dicionário
    para o template usar.
    """
    jogos_odds = buscar_odds_copa()
    jogo_odds = encontrar_jogo(jogos_odds, time_casa_en, time_fora_en)

    id_casa, nome_casa = buscar_id_time(time_casa_en)
    id_fora, nome_fora = buscar_id_time(time_fora_en)

    if not id_casa or not id_fora:
        return None, f"Não encontrei um dos dois times: '{time_casa_en}' ou '{time_fora_en}'."

    resumo_casa, jogos_recentes_casa = buscar_forma_recente(id_casa, qtd_jogos)
    resumo_fora, jogos_recentes_fora = buscar_forma_recente(id_fora, qtd_jogos)

    relatorio = {
        "casa": nome_casa,
        "fora": nome_fora,
        "odds": resumir_odds(jogo_odds),
        "forma": {
            nome_casa: {"resumo": resumo_casa, "jogos": jogos_recentes_casa},
            nome_fora: {"resumo": resumo_fora, "jogos": jogos_recentes_fora},
        },
    }
    return relatorio, None


def resultado_jogo(jogo, nome_time):
    """Classifica um jogo do histórico em V, E ou D para o time dado."""
    if jogo["casa"] == nome_time:
        gols_time, gols_adv = jogo["placar_casa"], jogo["placar_fora"]
    else:
        gols_time, gols_adv = jogo["placar_fora"], jogo["placar_casa"]

    if gols_time > gols_adv:
        return "V"
    elif gols_time < gols_adv:
        return "D"
    return "E"


def formatar_data_jogo(commence_time_iso):
    """Converte '2026-06-28T19:00:00Z' em algo legível como '28/06 às 19h00'."""
    dt = datetime.strptime(commence_time_iso, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%d/%m às %Hh%M")


def listar_jogos_formatados():
    """Busca todos os jogos futuros e devolve uma lista pronta para o template."""
    jogos_brutos = buscar_odds_copa()

    agora = datetime.now(timezone.utc)
    limite = agora + timedelta(hours=JANELA_HORAS)

    jogos = []
    for jogo in jogos_brutos:
        commence = datetime.strptime(jogo["commence_time"], "%Y-%m-%dT%H:%M:%SZ")
        commence = commence.replace(tzinfo=timezone.utc)

        if agora <= commence <= limite:
            jogos.append({
                "casa": jogo["home_team"],
                "fora": jogo["away_team"],
                "data_formatada": formatar_data_jogo(jogo["commence_time"]),
                "commence_time": jogo["commence_time"],
            })

    jogos.sort(key=lambda j: j["commence_time"])
    return jogos

def montar_relatorio(time_casa_en, time_fora_en, qtd_jogos=5):
    jogos_odds = buscar_odds_copa()
    jogo_odds = encontrar_jogo(jogos_odds, time_casa_en, time_fora_en)

    id_casa, nome_casa = buscar_id_time(time_casa_en)
    id_fora, nome_fora = buscar_id_time(time_fora_en)

    if not id_casa or not id_fora:
        return None, f"Não encontrei um dos dois times: '{time_casa_en}' ou '{time_fora_en}'."

    resumo_casa, jogos_recentes_casa = buscar_forma_recente(id_casa, qtd_jogos)
    resumo_fora, jogos_recentes_fora = buscar_forma_recente(id_fora, qtd_jogos)

    # NOVO: estatísticas de gols calculadas a partir do que já temos
    stats_casa = calcular_estatisticas_gols(jogos_recentes_casa, nome_casa)
    stats_fora = calcular_estatisticas_gols(jogos_recentes_fora, nome_fora)

    # NOVO: confronto direto
    match_id = buscar_id_jogo_copa(time_casa_en, time_fora_en)
    head2head = buscar_head2head(match_id) if match_id else None

    relatorio = {
        "casa": nome_casa,
        "fora": nome_fora,
        "odds": resumir_odds(jogo_odds),
        "head2head": head2head,
        "forma": {
            nome_casa: {
                "resumo": resumo_casa,
                "jogos": jogos_recentes_casa,
                "stats_gols": stats_casa,
            },
            nome_fora: {
                "resumo": resumo_fora,
                "jogos": jogos_recentes_fora,
                "stats_gols": stats_fora,
            },
        },
    }
    return relatorio, None




@app.route("/", methods=["GET"])
def index():
    """Página inicial: lista todos os jogos futuros como cards clicáveis."""
    jogos = listar_jogos_formatados()
    return render_template("index.html", jogos=jogos, relatorio=None, erro=None)


@app.route("/jogo/<time_casa>/<time_fora>", methods=["GET"])
def ver_jogo(time_casa, time_fora):
    """Mostra a análise de um jogo específico, escolhido a partir da lista."""
    jogos = listar_jogos_formatados()

    relatorio, erro = montar_relatorio(time_casa, time_fora)

    if erro:
        return render_template("index.html", jogos=jogos, relatorio=None, erro=erro)

    for nome_time, dados in relatorio["forma"].items():
        dados["forma_classificada"] = [
            (jg, resultado_jogo(jg, nome_time)) for jg in dados["jogos"]
        ]

    return render_template("index.html", jogos=jogos, relatorio=relatorio, erro=None)

if __name__ == "__main__":
    app.run(debug=True, port=5000)