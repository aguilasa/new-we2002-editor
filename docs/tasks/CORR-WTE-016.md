---
id: CORR-WTE-016
title: "Correção: a varredura de sítios para em `docs/` e `wte/re/`, e o `wte/README.md` continua afirmando que a §1 do plano registra 197 bitmaps"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-016: o perímetro da varredura não alcança `wte/*.md`

## Problema identificado

A WTE-TASK-09 transformou a varredura de número velho em guarda de build — o
`check_fase1.py` aborta se alguma afirmação viva de 197 / ~430 / 300 / 70
voltar. O perímetro é o que a tarefa pediu, e está escrito no script:

```python
def _markdowns() -> list[Path]:
    achados: list[Path] = []
    for base in ("docs", "wte/re"):
        achados.extend(sorted((ROOT / base).rglob("*.md")))
```

`wte/README.md` e `wte/tools/README.md` ficam fora — não por decisão registrada,
mas porque a lista tem dois itens e nenhum deles é `wte/`. E há um sítio vivo
justamente ali. O `wte/README.md` linha 95:

```
> **198, não 197.** A §1 do plano registra 197 `.bmp`; `find -iname '*.bmp'`
> acha **198**. A diferença provável é o `image/careto_base.bmp` […]
> Não foi investigado aqui — a convenção dos assets é da **WTE-TASK-08** e a
> reconciliação dos números da §1 é da **WTE-TASK-09**.
```

Três afirmações, e as três estão desatualizadas depois da WTE-TASK-09:

1. **"A §1 do plano registra 197"** — não registra mais. A §1.2 diz 198
   (`docs/PLAN-WTE-LAZARUS.md:123`) e a §1.8 diz 198
   (`docs/PLAN-WTE-LAZARUS.md:327`);
2. **"A diferença provável é o `careto_base.bmp`"** — não é diferença de
   inventário nenhuma. A WTE-TASK-08 mediu e a WTE-TASK-09 reconciliou: o erro
   era de **soma na prosa** da §1.8, que lista `53 + 105 + 32 + 7 + 1` e escreve
   197. O `careto_base.bmp` está contado nas cinco linhas;
3. **"Não foi investigado aqui — é da WTE-TASK-08 / WTE-TASK-09"** — as duas
   estão concluídas (2026-08-06). O encaminhamento aponta para trabalho que já
   aconteceu.

O `assets`, quatro linhas acima no mesmo arquivo, já diz 198. O arquivo se
contradiz.

Isto **não é falha da execução da WTE-TASK-09** dentro do que ela pedia: o
enunciado manda varrer `docs/ wte/re/`, e ali a varredura fechou em zero —
remedido abaixo. É o perímetro que ficou estreito demais para a tese que o
próprio `fase-1.md` §6 defende ("corrigir a §1 não fecha um número errado — ele
se espalha").

## Evidência

A guarda está verde, e o sítio existe:

```
$ python3 wte/tools/check_fase1.py --check
1 arquivo em dia com os produtos da fase 1 + we-team-editor/we-team-editor.exe;
0 sitio com numero velho

$ grep -n '197' wte/README.md
95:> **198, não 197.** A §1 do plano registra 197 `.bmp`; `find -iname '*.bmp'`
```

O "18 → 0" que o `fase-1.md` §6 publica está **certo dentro do perímetro** —
conferido remedindo a árvore anterior à correção, com o mesmo script:

```
$ git archive 65cc4be docs wte/re | tar -x -C <tmp>
$ python3 -c '<varrer() com ROOT=<tmp>>'
197 bitmaps: 8
~430 componentes: 4
300 imports de rtl60/vcl60: 2
70 strings com enchimento: 4
TOTAL antes (remedido no commit 65cc4be): 18
```

Os quatro números batem com a tabela `SITIOS`. O que falta é o alcance, não a
contagem.

Cuidado ao alargar: `wte/tools/README.md:37` cita `430` de propósito —

```
| `test_check_fase1.py` ✅ | […] o corte por contexto que separa os `430`
componentes do setor 430 do outro projeto |
```

— e o contexto `componente|controle` casa. É narração da guarda, do mesmo tipo
que já está em `NARRACAO`; alargar sem tratá-la deixa o `--check` vermelho na
hora.

## Causa raiz

`_markdowns()` enumera `docs` e `wte/re` porque foi isso que o enunciado da
WTE-TASK-09 escreveu, e ninguém perguntou se `wte/*.md` também afirma número
da §1 — o `wte/README.md` afirma desde a WTE-TASK-02.

## Correção

### Arquivo: `wte/tools/check_fase1.py`

Alargar o perímetro para os markdowns de `wte/` inteiro, mantendo `wte/re/` como
está:

```python
def _markdowns() -> list[Path]:
    achados: list[Path] = []
    for base in ("docs", "wte"):
        achados.extend(sorted((ROOT / base).rglob("*.md")))
    return achados
```

`rglob` sobre `wte` já cobre `wte/re/`, então a segunda base sai. Acrescentar a
narração da guarda ao conjunto que fica de fora, com a razão ao lado:

```python
NARRACAO = {
    "docs/tasks/correcoes-progresso.md",
    "docs/tasks/09-fechamento-fase-1.md",
    "wte/re/assets.md",
    "wte/re/strings.md",
    "wte/tools/README.md",   # narra a propria guarda: cita 430 para explicar o corte
    f"wte/re/{MD_NAME}",
}
```

Atualizar o docstring do módulo e a §6 do texto gerado, que hoje dizem
"markdowns de `docs/` e `wte/re/`".

### Arquivo: `wte/tools/test_check_fase1.py`

O `TestePerimetro` monta árvore temporária; acrescentar `wte/README.md` ao
`test_plano_e_progresso_ficam_no_perimetro` e `wte/tools/README.md` ao
`test_narracao_e_prompt_saem_do_perimetro`. Sem isso o alargamento não tem teste
que o segure.

### Arquivo: `wte/README.md`

Trocar o bloco de citação por registro fechado, sem encaminhamento e sem
atribuir 197 ao plano. Algo como:

```markdown
> **São 198.** A §1 do plano já registra 198 — a WTE-TASK-08 mediu o inventário
> e a WTE-TASK-09 reconciliou. O "197" que circulava era **erro de soma na
> prosa** da §1.8, que lista `53 + 105 + 32 + 7 + 1` e escrevia 197; o
> `image/careto_base.bmp`, solto na raiz de `image/`, sempre esteve contado.
> Ver [`re/assets.md`](re/assets.md) e [`re/fase-1.md`](re/fase-1.md).
```

O número certo aparece uma vez, e o texto passa a ser história com destino, não
pendência.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase1.py` | modificar |
| `wte/tools/test_check_fase1.py` | modificar |
| `wte/README.md` | modificar |
| `wte/re/fase-1.md` | modificar (**pelo gerador** — a §6 nomeia o perímetro) |

## Verificação

- [ ] `grep -rnE '\b197\b' --include='*.md' wte docs | grep -v CORR-WTE- |
      grep -v correcoes-progresso` não devolve afirmação viva
- [ ] `python3 wte/tools/check_fase1.py --check` verde depois do alargamento
- [ ] `python3 -m unittest test_check_fase1` verde, com os dois testes novos
- [ ] `make -C wte check` verde de ponta a ponta
- [ ] O `fase-1.md` §6 nomeia o perímetro novo, e foi **regerado**, não editado
- [ ] `roms/` intocada; `we-team-editor.exe` só para leitura

## Log de Execução

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

`_markdowns()` passou a varrer `docs/` + `wte/` (o `rglob` sobre `wte` já cobre
`wte/re/`, então a segunda base saiu), o `wte/tools/README.md` entrou em
`NARRACAO` com a razão ao lado, e o bloco do `wte/README.md` virou registro
fechado — sem encaminhamento para tarefa concluída e sem atribuir 197 ao plano.
Três testes novos no `test_check_fase1.py`, um deles sobre o `_markdowns()`
direto: o `_no_perimetro` sozinho não segurava o alargamento, porque ele diria
`True` para `wte/README.md` mesmo com a base velha — nunca era chamado.

**Problemas encontrados:**

Um que a CORR não previu: alargar o perímetro invalida a coluna "sítios antes".
Os 18 foram medidos com `docs/` + `wte/re/`; sob o perímetro novo, a mesma
árvore (`git archive 65cc4be docs wte`) devolve **19** — o nono sítio de bitmaps
é justamente o `wte/README.md`. A constante de `SITIOS` foi remedida e a §6 da
saída passou a dizer com que comando o número volta.

**Arquivos criados/modificados:**

- `wte/tools/check_fase1.py` — perímetro, `NARRACAO`, `SITIOS[0].antes` 8 → 9,
  docstring e §6 da saída
- `wte/tools/test_check_fase1.py` — `wte/README.md` no perímetro,
  `wte/tools/README.md` fora, teste do `_markdowns()`, teste de resíduo no
  `wte/README.md`, e o total de `SITIOS` 18 → 19
- `wte/README.md` — o bloco dos bitmaps
- `wte/re/fase-1.md` — regerado
