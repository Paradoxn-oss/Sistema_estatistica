import json
import os

ARQUIVO_CACHE = "dados_cache.json"


def salvar_cache(dados: dict) -> None:
    with open(ARQUIVO_CACHE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_cache() -> dict:
    if not os.path.exists(ARQUIVO_CACHE):
        return {"atualizado_em": None, "jogos": []}

    with open(ARQUIVO_CACHE, "r", encoding="utf-8") as f:
        return json.load(f)