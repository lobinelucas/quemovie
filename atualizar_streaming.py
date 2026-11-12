"""
Atualiza o "Onde ver" de cada título do Que Movie com os streamings do Brasil.

Fonte: TMDB (dados de streaming fornecidos pela JustWatch).
O site precisa manter o crédito à JustWatch no rodapé, é exigência do TMDB.

Uso:
    1. Crie uma conta grátis em https://www.themoviedb.org e gere a chave em
       Configurações > API (serve a "API Key" ou o "API Read Access Token").
    2. Salve a chave na variável de ambiente TMDB_KEY (ou num arquivo .tmdb_key
       nesta pasta, que não deve ir pro GitHub).
    3. Rode:  python atualizar_streaming.py

Só usa biblioteca padrão do Python. Lê e regrava o dados.js.
"""

import datetime
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

PASTA = pathlib.Path(__file__).resolve().parent
DADOS = PASTA / "dados.js"
PREFIXO = "window.CATALOGO = "
PAIS = "BR"
API = "https://api.themoviedb.org/3"

# Variações que poluem a lista (mesmo serviço com anúncio, canais dentro da Amazon etc.)
IGNORAR = ("with Ads", "Standard with Ads", "Amazon Channel", "Basic with Ads")


def chave():
    k = os.environ.get("TMDB_KEY", "").strip()
    arq = PASTA / ".tmdb_key"
    if not k and arq.exists():
        k = arq.read_text(encoding="utf-8").strip()
    chaves = PASTA.parent / ".chaves"  # mesmo arquivo de chaves das outras ferramentas do projeto
    if not k and chaves.exists():
        for linha in chaves.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith("TMDB_KEY="):
                k = linha.split("=", 1)[1].strip()
    if not k:
        sys.exit("Faltou a chave do TMDB. Defina TMDB_KEY ou crie o arquivo .tmdb_key.")
    return k


def chamar(caminho, **params):
    k = chave()
    headers = {"accept": "application/json"}
    if k.startswith("ey"):  # token de leitura (v4)
        headers["Authorization"] = "Bearer " + k
    else:  # api key (v3)
        params["api_key"] = k
    url = API + caminho + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def ler():
    texto = DADOS.read_text(encoding="utf-8")
    inicio = texto.index(PREFIXO) + len(PREFIXO)
    cabecalho = texto[: texto.index(PREFIXO)]
    return cabecalho, json.loads(texto[inicio:].strip().rstrip(";"))


def salvar(cabecalho, cat):
    DADOS.write_text(cabecalho + PREFIXO + json.dumps(cat, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def achar_id(t):
    tipo = "movie" if t["tipo"] == "filme" else "tv"
    params = {"query": t.get("original") or t["titulo"], "language": "pt-BR"}
    params["year" if tipo == "movie" else "first_air_date_year"] = t["ano"]
    res = chamar(f"/search/{tipo}", **params).get("results", [])
    return res[0]["id"] if res else None


CANAIS = {" amazon channel": "Prime Video", " apple tv channel": "Apple TV"}


def nomes(lista):
    vistos, bases, saida = set(), set(), []
    for p in sorted(lista or [], key=lambda x: x.get("display_priority", 999)):
        n = p["provider_name"]
        baixo = n.lower()
        # Canal pago dentro de outro serviço ("Adrenalina Pura Amazon channel") vira
        # "Adrenalina Pura (canal no Prime Video)". O mesmo canal em dois lugares aparece uma vez só.
        sufixo = next((s for s in CANAIS if baixo.endswith(s)), None)
        if sufixo:
            base = n[: -len(sufixo)].strip()
            if base.lower() in ("hbo max", "max", "netflix") or base.lower() in bases:
                continue
            bases.add(base.lower())
            n = f"{base} (canal no {CANAIS[sufixo]})"
        elif any(x.lower() in baixo for x in IGNORAR):
            continue
        if n in vistos:
            continue
        vistos.add(n)
        saida.append(n)
    return saida


def main():
    cabecalho, cat = ler()
    print(f"{'TÍTULO':32} {'TMDB':>8}  ONDE VER")
    for t in cat["titulos"]:
        tipo = "movie" if t["tipo"] == "filme" else "tv"
        if not t.get("tmdb_id"):
            t["tmdb_id"] = achar_id(t)
        if not t["tmdb_id"]:
            print(f"{t['titulo'][:32]:32} {'?':>8}  não achei no TMDB, confira o título/ano")
            continue
        info = chamar(f"/{tipo}/{t['tmdb_id']}", language="pt-BR")
        nome_tmdb = info.get("title") or info.get("name")
        br = chamar(f"/{tipo}/{t['tmdb_id']}/watch/providers").get("results", {}).get(PAIS, {})
        t["onde"] = nomes(br.get("flatrate")) + [n for n in nomes(br.get("free")) if n not in nomes(br.get("flatrate"))]
        principais = [n for n in t["onde"] if "(canal no " not in n]
        if principais:  # canal pago à parte só aparece quando não tem streaming principal
            t["onde"] = principais
        if t["onde"]:
            t.pop("nos_cinemas", None)  # chegou no streaming: sai o aviso de cinema
        elif t.get("nos_cinemas"):
            t["onde"] = ["Nos cinemas"]
        t["so_aluguel"] = not t["onde"] and bool(br.get("rent") or br.get("buy"))
        t["onde_link"] = br.get("link", "")
        mostra = ", ".join(t["onde"]) or ("só aluguel" if t["so_aluguel"] else "sem streaming no BR")
        print(f"{t['titulo'][:32]:32} {t['tmdb_id']:>8}  {mostra}   (TMDB: {nome_tmdb})")
    cat["atualizado"] = datetime.date.today().isoformat()
    cat["fonte"] = "JustWatch via TMDB"
    salvar(cabecalho, cat)
    print(f"\nPronto. dados.js atualizado em {cat['atualizado']}.")


if __name__ == "__main__":
    main()
