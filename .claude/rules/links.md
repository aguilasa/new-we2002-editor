# Convenções de link em Markdown

## Dentro de `docs/`, link é `/docs/` + o caminho do arquivo

Todo link de um markdown de `docs/` (ou de qualquer subpasta dela) para **outro
markdown dentro de `docs/`** usa `/docs/` + o caminho do arquivo a partir da
raiz do repositório. Nunca caminho relativo.

| Alvo | Escreva | Não escreva |
| --- | --- | --- |
| `docs/PLAN-LINUX.md` | `/docs/PLAN-LINUX.md` | `PLAN-LINUX.md`, `../PLAN-LINUX.md` |
| `docs/tasks/01-ferramental.md` | `/docs/tasks/01-ferramental.md` | `01-ferramental.md`, `tasks/01-ferramental.md` |
| `docs/tasks/CORR-WTE-001.md` | `/docs/tasks/CORR-WTE-001.md` | `./CORR-WTE-001.md` |
| `docs/prompts/03-corrigir.md` | `/docs/prompts/03-corrigir.md` | `../prompts/03-corrigir.md` |

Vale **de qualquer arquivo para qualquer arquivo** dentro de `docs/`, inclusive
entre irmãos no mesmo diretório: o `progresso.md` linka
`/docs/tasks/CORR-WTE-001.md`, não `CORR-WTE-001.md`.

**Por que absoluto, se relativo funciona.** Funciona *por acaso*: quebra assim
que o arquivo muda de diretório, e as tabelas de `docs/tasks/` são exatamente o
conteúdo que migra — uma linha copiada do `progresso.md` para outro doc leva o
link junto. O `/docs/...` é o que o GitHub resolve a partir da raiz do
repositório, e é o mesmo texto em todo arquivo, não importa quão fundo ele
esteja.

**Diferença para o projeto `snes`.** Lá o `docs/` é a raiz servida por uma
ferramenta local, e o link é `/tasks/...`, sem o `docs/`. Aqui não há
ferramenta servindo nada — quem resolve é o GitHub, a partir da raiz do
repositório. Por isso o prefixo `/docs/`: copiar a forma do `snes` produziria
link quebrado.

## Template em bloco de código conta

A regra alcança o link escrito **dentro de bloco de código** quando o bloco é
modelo do que vira markdown de verdade. É o caso dos templates de tabela de
`docs/prompts/`: o link do modelo é o que o `/executar` e o `/revisar` copiam
para o `progresso.md` e o `correcoes-progresso.md`. Os destinos ali são
placeholder (`/docs/tasks/CORR-WTE-XXX.md`,
`/docs/tasks/XX-nome-do-arquivo.md`) — não são link quebrado, e ficam **fora**
da conferência de existência abaixo.

## Alvo fora de `docs/`

`CLAUDE.md`, `NOTICE.md`, `README.md`, `wte/re/*`, `src/*`, `.claude/*`
continuam com **link relativo comum**, como está hoje:

```markdown
[NOTICE.md](../NOTICE.md)
[CLAUDE.md](../CLAUDE.md)
[README.md](../../wte/README.md)
```

## Fora de `docs/`, a regra não vale

`CLAUDE.md` e `.claude/**` não são governados por ela. Ali link relativo comum
(`[.claude/rules/links.md](.claude/rules/links.md)`) é o certo — é como o
GitHub e o editor resolvem.

## Conferência

Forma do link:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rnoE '\]\([^)]*\.md[^)]*\)' --include='*.md' docs | grep -v '](/docs/'
```

Deve sobrar só alvo fora de `docs/` (`../NOTICE.md`, `../CLAUDE.md`,
`../../wte/...`) e URL absoluta.

Destino existe (`docs/prompts/` fica de fora, pelos placeholders):

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rhoE '\]\(/docs/[^)#]*\)' --include='*.md' docs/*.md docs/tasks |
  sed 's#^](/##; s#)$##' | sort -u |
  while read p; do [ -f "$p" ] || echo "QUEBRADO: $p"; done
```

Saída vazia é o esperado. Rode antes de commitar doc que ganhou link novo.
