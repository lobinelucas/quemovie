# Site do Que Movie (link da bio)

Catálogo das dicas do @quemovie: "Tá a fim de sentir o quê?" (filtro por sentimento), filtro por Movie/Série/Minissérie, Selo Lobine e busca por nome ou streaming. A capa leva pro Reel.

## Arquivos

- `index.html`: o site. Não guarda dados, lê tudo do `dados.js`.
- `dados.js`: o catálogo (título, tipo, ano, sentimentos, selo, link do Reel, capa, onde ver).
- `atualizar_streaming.py`: atualiza o "Onde ver" de cada título com os streamings do Brasil.
- `capas/`, `marca/`, `fontes/`: imagens e fonte.

## Onde ver (streaming)

- Fonte: API do TMDB, que repassa os dados da JustWatch. É grátis.
- Exigência do TMDB: manter o crédito à JustWatch no rodapé do site (já está lá).
- Precisa de uma chave do TMDB (conta grátis em themoviedb.org, Configurações > API).
  A chave fica no arquivo `.chaves` da raiz do projeto (linha `TMDB_KEY=`). Nunca subir a chave pro GitHub.
- Rodar: `python atualizar_streaming.py`. Ele mostra uma tabela com o título que achou no TMDB,
  pra conferir se bateu certo. Se algum vier errado, coloque o `tmdb_id` certo no `dados.js`.
- Ao publicar o site, agendar essa rotina pra rodar uma vez por dia (ex.: GitHub Actions com a
  chave como segredo) e republicar o `dados.js`.

## Post novo

Ao finalizar um vídeo, adicionar o título no topo da lista em `dados.js` com: tipo (`filme`, `serie` ou `minisserie`),
titulo, ano, data, link do Reel, capa (cena do filme, 600×800, em `capas/`), sentimentos e, se for o caso, `"selo": true`.
Depois rodar a rotina de streaming.

Sentimentos (vários por título): `pra-rir`, `pra-ficar-feliz`, `beira-do-sofa`, `pra-se-emocionar`,
`pra-se-apegar`, `pra-se-envolver`, `pra-sair-chocado`, `pra-pegar-no-sono`.

Selo Lobine de melhor do mundo (`"selo": true`): por enquanto só The Wire e Band of Brothers. Desenho em `marca/selo_lobine.svg`.
