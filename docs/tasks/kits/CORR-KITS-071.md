---
id: CORR-KITS-071
---

# CORR-KITS-071 — Reabrir os critérios 1b e 2: encaixe e manga curta sem resposta

Origin: [KITS-TASK-43](/docs/tasks/kits/43-medir-encaixe-mangas.md)

## Problem

O critério 1 da KITS-TASK-43 pede, para as seções 93 e 95–102, "a seção do corpo cuja matriz elas dividem, ou a matriz própria que recebem"; o critério 2 pede "se manga curta e manga longa são seções alternativas da mesma peça". Os dois estão marcados [x]. As respostas entregues são "nenhum par decide" (um ajuste projetivo com 9–10 pontos contra 11 incógnitas) e "não medida, os dois times vestem manga longa". O Objetivo ("que transformação cada seção recebe e a que peça do corpo se prende") fica sem resposta. O Log diz que o método mudou de ler a matriz do GTE (como faz o `looks --pose`) para um ajuste de geometria, e esse ajuste não decide a pergunta. Só a regra de troca (93 no lugar de 97) ficou estabelecida.

## Evidência

```text
$ grep -n "^- \[x\]" docs/tasks/kits/43-medir-encaixe-mangas.md | cut -c1-120
21:- [x] `oracle.py --attach 5` colado no Log, com duas contagens. ...
22:- [x] A regra na §4.3: ... e se a manga curta e
$ grep -n "não foi medida\|Negativa medida\|limite da medida" docs/PLAN-KITS-PY.md
621:- **Manga curta contra longa não foi medida.** ...
632:**Negativa medida: a mesma câmera não separa peça de peça aqui.** ...
636:demais para dizer se duas peças dividem a matriz. Isso é limite da medida, e a
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach 5 --frame-json work/kits-oracle/attach-5.json
  player  1 ( 44 prims) section  95,  9 point(s): alone 1.09 px; one camera with section 2 1.28 px, ...
  player  3 ( 44 prims) section  95,  9 point(s): alone 1.35 px; one camera with section 2 4.76 px, ...
```

## Root cause

A task fechou sobre um resultado negativo. O instrumento planejado (a carga de matriz do GTE por seção) foi trocado por um ajuste projetivo subdeterminado. A pergunta da manga curta precisa de um estado de partida com manga curta, o que é decisão do usuário pela regra da fase 10 do perfil.

## Fix

**Decisão do dono do repositório.** Desmarcar os critérios 1 (segunda contagem) e 2 em `docs/tasks/kits/43-medir-encaixe-mangas.md`, ou reescrevê-los com o consentimento dele. Abrir trabalho de seguimento para (a) ler a matriz do GTE por seção do `MODEL.BIN` no código da partida, em `tools/kits/oracle.py`, e (b) um estado de partida com manga curta, que é decisão do usuário. Registrar os dois como abertos na §4.3.

## Arquivos a criar ou modificar

- `docs/tasks/kits/43-medir-encaixe-mangas.md`
- `docs/PLAN-KITS-PY.md`
- `tools/kits/oracle.py`

## Verificação

`grep -n "^- \[x\] A regra na §4.3" docs/tasks/kits/43-medir-encaixe-mangas.md` casa hoje; não pode casar até o encaixe e a manga curta serem medidos ou o critério ser reescrito formalmente.

## Log de Execução

Reproduzido em 2026-10-06 sobre `9aeca0e`: os critérios 1 e 2 da task 43 estavam `[x]`, mas o
encaixe e a manga curta ficaram sem resposta. Pela saída do
`oracle.py --attach 5 --frame-json work/kits-oracle/attach-5.json`, o melhor par conjunto (95+2
do jogador 1, 1,28 px) cai dentro da faixa de uma seção sozinha (0,56 a 2,18 px). O ajuste não
separa peça de peça.

Decisão do dono do repositório, nesta sessão: **reabrir com trabalho de seguimento**.

Conserto:

- `docs/tasks/kits/43-medir-encaixe-mangas.md`: os critérios 1 e 2 voltam a `[ ]`, cada um com
  uma linha dizendo o que está medido e o que passou adiante.
- `docs/PLAN-KITS-PY.md` §4.3: um bloco "Aberto" com as duas perguntas. O encaixe vai para a
  KITS-TASK-44, e a manga curta espera um save state de partida com manga curta, decisão do
  usuário.
- KITS-TASK-44 (`docs/tasks/kits/44-matriz-gte-model-bin.md`): aberta pelo `rite new-task` e
  registrada no commit f2b7057. Ela lê a matriz do GTE por seção do `MODEL.BIN` no código da
  partida, como o `looks --pose` faz.

O terceiro ponto da Correção, a leitura em `tools/kits/oracle.py`, é o trabalho da própria
KITS-TASK-44 e não foi feito aqui. O `FIT_PIXELS` fica para a CORR-KITS-073.

```text
$ grep -n "^- \[x\] A regra na §4.3" docs/tasks/kits/43-medir-encaixe-mangas.md
(sem saída)
$ sh rite check --cycle kits
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```
