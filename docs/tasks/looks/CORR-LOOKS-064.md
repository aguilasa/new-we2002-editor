---
id: CORR-LOOKS-064
title: "Correção: \"603 a 1.680\" e \"1,4x a 4,4x\" não são o que as corridas imprimem, e três textos ainda dizem o que a quinta sessão desmentiu"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-064: os números e a prosa da LOOKS-TASK-28 ficaram atrás das próprias corridas

## Problema identificado

Recorridos hoje os gates da
[`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), os números
reproduzem. Mas dois deles não são os que os documentos citam, e três textos
dizem coisas que a quinta sessão desmentiu:

1. **"quadros diferentes dão 603 a 1.680"** — no critério 4 da task e na
   §10.3 (m) do plano. As corridas imprimem **603 e 1.483** (slot 2) e
   **670 e 1.452** (slot 1). O próprio `confront.MATCH_SHARE` diz *"603 to 1483
   pixels"*. O 1.680 não sai de corrida nenhuma que exista hoje.
2. **"por 1,4x a 4,4x"** — no critério 5, no Log (quinta sessão) e na
   §6 (h). Sobre a saída do `--silhouette-styles` as razões vão de **1,36x a
   4,73x**: 563/119 (slot 2, foto `C1`, contra o nosso `I3`) passa do 4,4x. O
   número saiu de conta à mão, porque o gate não imprime razão nenhuma (ver a
   [`CORR-LOOKS-063`](/docs/tasks/looks/CORR-LOOKS-063.md)).
3. **Duas docstrings do `confront.py` descrevem o gate ao contrário.** O
   `STYLE_SWAP` diz *"`--silhouette-styles` asserts it -- and fails"*, e o
   `STYLE_TUPLES` diz *"`--silhouette-styles` asserts that it does, and fails
   … the head band picks the right style in 2 of 3"*. O gate sai **0
   problem(s)** e 6 de 6. O `fit_centre` repete a mesma frase duas vezes
   seguidas.
4. **A §10.3 (m) se contradiz no mesmo veredito.** Primeiro: *"Isso e a nossa
   escolha de medir lugares a partir da raiz viram **uma** translação, medida
   uma vez e mantida fixa."* Vinte linhas abaixo: *"a comparação tem de ser
   **livre de translação** … Uma translação única mantida fixa soa mais
   rigorosa e mede outra coisa"*. O código faz a segunda (`fit_centre` por
   comparação); a primeira frase é da primeira sessão.
5. **O Log abre com "Executado em: 2026-09-18 — PARCIAL"** numa task
   `concluído`. As sessões seguintes estão abaixo, mas quem lê o cabeçalho lê
   parcial.

## Evidência

Na árvore de `54c4888`:

```text
$ python tools/looks/confront.py --silhouette
    control: frame 60 captured twice, 2383 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [603, 1483] pixel(s)
    ...
    control: frame 60 captured twice, 2376 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [670, 1452] pixel(s)
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-styles
    game A-A1-A-A-A: ... head band A1 202*  C1 357  I3 274      # 1,36x
    game A-C1-A-A-A: ... head band A1 488  C1 119*  I3 563      # 4,73x
    ...
confront --silhouette-styles: 0 problem(s) over 2 slot(s)

$ grep -n "1.680\|4,4x" docs/PLAN-LOOKS-PY.md docs/tasks/looks/28-a-camera-do-jogo.md
docs/PLAN-LOOKS-PY.md:2232:slots: **6 de 6**, por 1,4x a 4,4x (`confront.py --silhouette-styles`).
docs/PLAN-LOOKS-PY.md:2820:> 1.680.
docs/tasks/looks/28-a-camera-do-jogo.md:51:      pixel de diferença, e quadros diferentes dão 603 a 1.680. Os limiares
docs/tasks/looks/28-a-camera-do-jogo.md:56:      por 1,4x a 4,4x (`--silhouette-styles`). No corpo inteiro o estilo não se
docs/tasks/looks/28-a-camera-do-jogo.md:542:trocados — discordam, por 1,4x a 4,4x. Uma captura (slot 1, `C1`) derivou a

$ grep -n "and fails\|2 of 3" tools/looks/confront.py
1006:It is still run and printed, and `--silhouette-styles` asserts it -- and fails.
1187:`--silhouette-styles` asserts that it does, and fails; `--silhouette` does not
1190:2 of 3, A1 being the one it misses.

$ sed -n 2807,2809p docs/PLAN-LOOKS-PY.md
> painel é o deslocamento de desenho da GPU**, não o GTE. Isso e a nossa
> escolha de medir lugares a partir da raiz viram **uma** translação, medida
> uma vez e mantida fixa.
```

## Causa raiz

Cinco sessões na mesma task, cada uma reescrevendo o veredito da anterior, e o
fechamento transcreveu as razões de conta à mão e não reconciliou o texto das
sessões anteriores.

## Correção

### Arquivos: `docs/tasks/looks/28-a-camera-do-jogo.md` e `docs/PLAN-LOOKS-PY.md`

- "603 a 1.680" vira **603 a 1.483** (ou "603 a 1.483 no slot 2, 670 a 1.452
  no slot 1"), na task e na §10.3 (m).
- "1,4x a 4,4x" vira o que o gate passar a imprimir (a
  [`CORR-LOOKS-063`](/docs/tasks/looks/CORR-LOOKS-063.md)); medido hoje,
  **1,36x a 4,73x** — critério 5, Log e §6 (h).
- Na §10.3 (m), a frase da translação "medida uma vez e mantida fixa" é
  corrigida para a comparação livre de translação que o código faz.
- O cabeçalho do Log deixa de dizer só **PARCIAL**: parcial na primeira
  sessão, fechada na quinta.

### Arquivo: `tools/looks/confront.py`

As docstrings de `STYLE_SWAP` e `STYLE_TUPLES` dizem o que o
`--silhouette-styles` faz hoje (close-up, 6 de 6), mantendo como histórico o
que foi medido antes do conserto. O `fit_centre` perde a frase repetida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/28-a-camera-do-jogo.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `tools/looks/confront.py` | modificar (só docstrings) |

## Verificação

- [ ] `grep -rn "1.680\|4,4x" docs/PLAN-LOOKS-PY.md docs/tasks/looks/28-a-camera-do-jogo.md`
      vazio, e os números novos iguais ao que `confront.py --silhouette` e
      `--silhouette-styles` imprimem
- [ ] `grep -n "and fails" tools/looks/confront.py` não alcança o
      `--silhouette-styles`
- [ ] a §10.3 (m) não diz mais "mantida fixa" sobre a translação do painel
- [ ] `python tools/looks/selftest.py --quiet` verde (a regra 1 varre as
      docstrings)
- [ ] `python tools/check_tasks.py` ok
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
