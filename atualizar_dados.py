import time
from datetime import datetime, timedelta, timezone

from persistence.repositorio import salvar_cache
from clients.odds_client import buscar_odds_copa
from domain.estatisticas import calcular_estatisticas_gols, resultado_jogo, resumir_odds
from clients.stats_client import (
    buscar_todos_os_times,
    encontrar_time_na_lista,
    buscar_forma_recente,
    buscar_id_jogo_copa,
    buscar_head2head,
)

JANELA_HORAS = 24
ARQUIVO_SAIDA = "dados_cache.json"
PAUSA_ENTRE_JOGOS_SEGUNDOS = 25  # margem de segurança para o rate limit de 10/min


def formatar_data_jogo(commence_time_iso):
    dt = datetime.strptime(commence_time_iso, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%d/%m às %Hh%M")


def listar_jogos_proximos():
    """Busca todos os jogos futuros e filtra os que estão dentro da janela de horas."""
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
                "odds_bruto": jogo,  # guardamos o jogo bruto para resumir as odds sem buscar de novo
            })

    jogos.sort(key=lambda j: j["commence_time"])
    return jogos


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


def montar_relatorio_completo(jogo_lista, todos_os_times, qtd_jogos=5):
    time_casa_en = jogo_lista["casa"]
    time_fora_en = jogo_lista["fora"]

    id_casa, nome_casa, crest_casa = encontrar_time_na_lista(todos_os_times, time_casa_en)
    id_fora, nome_fora, crest_fora = encontrar_time_na_lista(todos_os_times, time_fora_en)

    if not id_casa or not id_fora:
        print(f"  [aviso] não encontrei IDs para {time_casa_en} x {time_fora_en} -- pulando")
        return None

    resumo_casa, jogos_recentes_casa = buscar_forma_recente(id_casa, qtd_jogos)
    resumo_fora, jogos_recentes_fora = buscar_forma_recente(id_fora, qtd_jogos)

    stats_casa = calcular_estatisticas_gols(jogos_recentes_casa, nome_casa)
    stats_fora = calcular_estatisticas_gols(jogos_recentes_fora, nome_fora)

    match_id = buscar_id_jogo_copa(time_casa_en, time_fora_en)
    head2head = buscar_head2head(match_id) if match_id else None

    for jg in jogos_recentes_casa:
        jg["_resultado"] = resultado_jogo(jg, nome_casa)
    for jg in jogos_recentes_fora:
        jg["_resultado"] = resultado_jogo(jg, nome_fora)

    return {
        "casa": nome_casa,
        "fora": nome_fora,
        "crest_casa": crest_casa,
        "crest_fora": crest_fora,
        "data_formatada": jogo_lista["data_formatada"],
        "commence_time": jogo_lista["commence_time"],
        "odds": resumir_odds(jogo_lista["odds_bruto"]),
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


def main():
    print(f"Buscando jogos das próximas {JANELA_HORAS}h...")
    jogos = listar_jogos_proximos()
    print(f"Encontrados {len(jogos)} jogo(s).\n")

    print("Buscando lista de times da Copa (uma única vez)...")
    todos_os_times = buscar_todos_os_times()  # NOVO: busca só uma vez aqui
    print("Lista carregada.\n")

    relatorios = []

    for i, jogo in enumerate(jogos, start=1):
        print(f"[{i}/{len(jogos)}] {jogo['casa']} x {jogo['fora']}")
        relatorio = montar_relatorio_completo(jogo, todos_os_times)

        if relatorio:
            relatorios.append(relatorio)
            print("  ok")
        else:
            print("  falhou ou foi pulado")

        # Pausa entre jogos para não estourar o rate limit da football-data.org
        if i < len(jogos):
            time.sleep(PAUSA_ENTRE_JOGOS_SEGUNDOS)

    saida = {
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "janela_horas": JANELA_HORAS,
        "jogos": relatorios,
    }

    salvar_cache(saida)
    
    print(f"\nConcluído. {len(relatorios)} jogo(s) salvos em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()