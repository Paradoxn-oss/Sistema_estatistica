"""
app.py

Aplicação Flask local para o analisador de jogos da Copa do Mundo.

Diferente da versão anterior, este app NUNCA chama as APIs externas.
Ele só lê o arquivo dados_cache.json, que é gerado separadamente pelo
script atualizar_dados.py.

Fluxo de uso:
    1. Rode "python atualizar_dados.py" (gera/atualiza o dados_cache.json)
    2. Rode "python app.py" (serve o site, lendo só o arquivo)
    3. Abra http://localhost:5000

Sempre que quiser dados mais recentes, rode o passo 1 de novo.
"""

from flask import Flask, render_template
from persistence.repositorio import carregar_cache

app = Flask(__name__)


def encontrar_jogo_no_cache(jogos, time_casa, time_fora):
    """Localiza um jogo específico dentro da lista já carregada do cache."""
    for jogo in jogos:
        if jogo["casa"] == time_casa and jogo["fora"] == time_fora:
            return jogo
    return None


@app.route("/", methods=["GET"])
def index():
    """Lista os jogos disponíveis no cache, como cards clicáveis."""
    cache = carregar_cache()

    jogos_lista = [
        {
            "casa": j["casa"],
            "fora": j["fora"],
            "data_formatada": j["data_formatada"],
            "crest_casa": j.get("crest_casa"),
            "crest_fora": j.get("crest_fora"),
        }
        for j in cache["jogos"]
    ]

    return render_template(
        "index.html",
        jogos=jogos_lista,
        relatorio=None,
        erro=None,
        atualizado_em=cache.get("atualizado_em"),
    )


@app.route("/jogo/<time_casa>/<time_fora>", methods=["GET"])
def ver_jogo(time_casa, time_fora):
    """Mostra o relatório completo de um jogo específico, já vindo do cache."""
    cache = carregar_cache()

    jogos_lista = [
        {
            "casa": j["casa"],
            "fora": j["fora"],
            "data_formatada": j["data_formatada"],
            "crest_casa": j.get("crest_casa"),
            "crest_fora": j.get("crest_fora"),
        }
        for j in cache["jogos"]
    ]

    relatorio = encontrar_jogo_no_cache(cache["jogos"], time_casa, time_fora)

    if not relatorio:
        erro = (
            f"Não encontrei dados para '{time_casa}' x '{time_fora}' no cache. "
            "Rode 'python atualizar_dados.py' para atualizar."
        )
        return render_template(
            "index.html", jogos=jogos_lista, relatorio=None, erro=erro,
            atualizado_em=cache.get("atualizado_em"),
        )

    for nome_time, dados in relatorio["forma"].items():
        dados["forma_classificada"] = [
            (jg, jg["_resultado"]) for jg in dados["jogos"]
        ]

    return render_template(
        "index.html", jogos=jogos_lista, relatorio=relatorio, erro=None,
        atualizado_em=cache.get("atualizado_em"),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)