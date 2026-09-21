# Convenções de link em Markdown

## Dentro de `docs/`, link é `/docs/` + o caminho do arquivo

Todo link de um markdown de `docs/` (ou de qualquer subpasta dela) para **outro
markdown dentro de `docs/`** usa `/docs/` + o caminho do arquivo a partir da
raiz do repositório. Nunca caminho relativo.

| Alvo | Escreva | Não escreva |
| --- | --- | --- |
| `docs/PLAN-LINUX.md` | `/docs/PLAN-LINUX.md` | `PLAN-LINUX.md`, `../PLAN-LINUX.md` |
| `docs/tasks/concluidos/01-ferramental.md` | `/docs/tasks/concluidos/01-ferramental.md` | `01-ferramental.md`, `tasks/01-ferramental.md` |
| `docs/tasks/concluidos/CORR-WTE-001.md` | `/docs/tasks/concluidos/CORR-WTE-001.md` | `./CORR-WTE-001.md` |
| `docs/prompts/03-corrigir.md` | `/docs/prompts/03-corrigir.md` | `../prompts/03-corrigir.md` |

Vale **de qualquer arquivo para qualquer arquivo** dentro de `docs/`, inclusive
entre irmãos no mesmo diretório: o `progresso.md` linka
`/docs/tasks/concluidos/CORR-WTE-001.md`, não `CORR-WTE-001.md`.

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

## Nos arquivos de ciclo, tudo é absoluto — e quem confere é o Rite

Desde a migração para o Rite (`rite.toml`, `link_style = "root-absolute"`), os
arquivos que ele governa — tasks, CORRs, os dois arquivos de progresso de cada
ciclo e os perfis de `docs/prompts/` — usam caminho a partir da raiz **para
qualquer alvo**, inclusive fora de `docs/`: `/CLAUDE.md`, `/src/app/X.hpp`. O
`rite.py check` reprova link relativo nesses arquivos, e o `rite.py relink`
converte. O GitHub resolve os dois do mesmo jeito; a regra única é o que deixa a
conferência mecânica.

As tabelas desses arquivos são geradas pelo Rite, então os modelos de tabela
que moravam nos prompts antigos e nos `*.template.md` deixaram de existir.

## Alvo fora de `docs/`, no resto de `docs/`

Fora dos arquivos de ciclo, `CLAUDE.md`, `NOTICE.md`, `README.md`, `wte/re/*`,
`src/*`, `.claude/*` continuam com **link relativo comum**, como está hoje:

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
grep -rnoE '\]\([^)]*\.md[^)]*\)' --include='*.md' docs |
  grep -v '](/docs/' | grep -v '](/<CICLO>/'
```

Deve sobrar só alvo fora de `docs/` (`../NOTICE.md`, `../CLAUDE.md`,
`../../wte/...`) e URL absoluta.

**Nos arquivos de ciclo, a conferência é do Rite:** `rite.py check --all
--include-archived` confere forma e existência de todo link, fora de bloco de
código e de crases — é a distinção "consciente de cerca" da seção abaixo, feita
por ferramenta. Os comandos daqui servem para o resto de `docs/`.

Destino existe (o arquivo de `docs/tasks/concluidos/` fica de fora — ver abaixo):

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
for f in docs/*.md docs/tasks/*.md docs/tasks/*/*.md; do
  case "$f" in docs/tasks/concluidos/*|*.template.md) continue;; esac
  grep -hoE '\]\(/docs/[^)#]*\)' "$f"
done | sed 's#^](/##; s#)$##' | sort -u |
  while read p; do [ -f "$p" ] || echo "QUEBRADO: $p"; done
```

**Por que o laço em vez de um glob maior.** `docs/tasks/*/*.md` sozinho
engoliria `docs/tasks/concluidos/`, que está fora **de propósito** (ver abaixo).
O laço alcança **ciclo vivo em subpasta** — `docs/tasks/port-mcr/`, desde
2026-09-07 — e continua excluindo o arquivo morto. E vale saber de antemão: o
motivo da exclusão não é a pasta, é o **`CORR-*.md`**, que é cheio de
transcrição de `grep` e de `git show` dentro de bloco de código. Quando os
`CORR-*` de um ciclo vivo tiverem transcrição, a exclusão certa passa a ser por
`CORR-*.md`, não por pasta — dizer isso agora custa uma frase, e descobrir
depois custa um falso vermelho.

Saída vazia é o esperado. Rode antes de commitar doc que ganhou link novo.

## O arquivo de `docs/tasks/concluidos/`

Projeto encerrado vai inteiro para `docs/tasks/concluidos/` — tasks, correções e
os dois arquivos de progresso juntos (`rite.py archive` faz o `git mv` e
reescreve os links). **A regra do `/docs/` continua
valendo lá dentro**, com o caminho completo: `/docs/tasks/concluidos/CORR-WTE-001.md`.

O que muda é a **conferência de existência**, e por um motivo específico: os
`CORR-*.md` são cheios de bloco de código com saída de `grep`, de `git show` e
com fonte de gerador, e ali `](/docs/tasks/…)` é **transcrição do que um arquivo
dizia**, não link. Um `grep` de texto não distingue as duas coisas, e a
conferência acusaria dezenas de falsos quebrados — a de 2026-09-01 media dez.
Corrigir a transcrição seria falsificar evidência.

A varredura do move de 2026-09-01 foi feita **consciente de cerca** (só reescreve
link fora de bloco de código) e não sobrou link vivo quebrado no arquivo. Se
precisar reconferir, use a mesma distinção; a forma preguiçosa dá falso
vermelho.
