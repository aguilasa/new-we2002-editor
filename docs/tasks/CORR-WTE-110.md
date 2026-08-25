---
id: CORR-WTE-110
title: "Correção: os quatro casos de borda foram medidos num vetor só, e o critério diz \"por campo\""
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-110: as bordas foram medidas em `names`, e são quatro campos

## Problema identificado

O segundo critério da [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md) é

> - [x] Os quatro casos de borda testados **por campo** — em
>   [`test_bordas.pas`](../../wte/tests/test_bordas.pas), **10 de 10**
>   conferências, headless

As dez conferências passam — conferido nesta revisão, compilando e rodando o
programa. Mas os dois grupos que medem **borda de campo** (o `N` exato e a
travessia sem terminador, e a cadeia vazia) tocam **um único vetor**:
`t.names[0]` e `t.names[1]`, de 20 bytes. Os outros três campos do inventário
nunca aparecem:

| Campo | Vetor | Capacidade | Aparece nos grupos 1 e 2? |
|---|---|---:|---|
| `edit_nombre2` | `names` | 20 B | **sim** |
| `edit_nombre1` | `kanji_name` | 20 B | não (só como saída do codec, no grupo 3) |
| `casilla_nombre` | `name` | 11 B | **não** |
| `edit_nombre3` | `abbreviations` | 4 B | **não** |

**O que ficou de fora é justamente o mais apertado.** O `abbreviations` tem 4
bytes para limite 3 — a menor folga do inventário — e mora **coladinho** no
`kanji_name` dentro do `TTeam`, que é a mesma vizinhança que o grupo 1 usa para
medir a travessia em `names`. Se houver um lugar onde o `- 1` do terminador
erra, é ali.

A parte estrutural **está** coberta para os quatro: o gerador aborta se
`lim_max > capacidade - 1`, e isso vale campo a campo. O que não está medido é
o **comportamento** — o que a leitura devolve num vetor curto sem terminador, e
o que a cadeia vazia produz — nos três que ficaram de fora.

Nada disso está errado; o que falta é o critério dizer o que foi feito. Hoje
ele diz "por campo" e a medição é por **classe**, num representante.

## Evidência

As dez conferências, rodadas em 2026-08-25:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
fpc -Mobjfpc -Fu$PWD/wte/src -FU/tmp/b -o/tmp/b/tb wte/tests/test_bordas.pas
/tmp/b/tb
```

```text
10/10 conferencias de borda passaram
```

E o que elas tocam:

```bash
grep -nE "t\.(names|abbreviations|kanji_name)|p\.name" wte/tests/test_bordas.pas
```

```text
87:    t.names[0][i] := AnsiChar(Ord('A') + (i mod 26));
88:  t.names[0][19] := #0;
89:  ConfereInt('grupo1/N-exato/comprimento', Length(Cadeia(t.names[0])), 19);
94:    t.names[0][i] := 'X';
96:    t.names[1][i] := 'Y';
97:  t.names[1][19] := #0;
101:  ConfereInt('grupo1/sem-terminador/atravessa', Length(Cadeia(t.names[0])), 39);
103:          Copy(Cadeia(t.names[0]), 21, 3), 'YYY');
120:  Confere('grupo2/vazia/le-como-vazia', Cadeia(t.names[0]), '');
127:  t.names[0][0] := 'A'; t.names[0][1] := 'B'; t.names[0][2] := #0;
128:  t.names[0][3] := 'C';
129:  Confere('grupo2/sujo-depois-do-NUL', Cadeia(t.names[0]), 'AB');
```

Nenhuma ocorrência de `abbreviations`, de `p.name` nem de `t.kanji_name` como
**destino** de borda — o `kanji_name` só aparece no grupo 3, como saída do
`KanjiToAscii`.

| Afirmado | Medido |
|---|---|
| quatro casos de borda **por campo** | quatro casos numa classe, no vetor de 20 B |
| 10 de 10 conferências | 10 de 10 ✓ |

## Causa raiz

Os grupos foram escritos por **caso de borda** e não por campo, e o critério
foi marcado com a contagem de conferências, que é outra coisa.

## Correção

Duas saídas, e a primeira é barata o bastante para não valer a segunda.

### Arquivo: `wte/tests/test_bordas.pas` *(preferida)*

Repetir os grupos 1 e 2 sobre os outros três vetores. O corpo já é
parametrizável: os dois grupos só precisam do ponteiro do vetor e da
capacidade, e a asserção do `N` exato é `Length(Cadeia(v)) = cap - 1`.

Vale começar pelo `abbreviations` — 4 bytes, limite 3, vizinho do
`kanji_name` — porque é onde a travessia teria consequência visível: encher os
4 sem terminador faz a leitura entrar no slot de kanji do mesmo time.

### Arquivo: `docs/tasks/36-buffers-e-truncamento.md` *(se a primeira não valer)*

Trocar *"testados por campo"* por o que foi medido, com a razão:

> Os quatro casos foram medidos **por classe**, no `names` (20 B), porque a
> borda é do `Cadeia()` e não do campo; a parte que **é** por campo — o limite
> caber no vetor — está no gerador, que aborta campo a campo.

Escrever qual dos dois se escolheu, e por quê; narrowing sem registro é o que
esta task inteira existe para não deixar acontecer.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/test_bordas.pas` | modificar |
| `wte/re/buffers.md` | regerar, se a contagem de conferências aparecer lá |
| `docs/tasks/36-buffers-e-truncamento.md` | modificar |

## Verificação

- [ ] `grep -c "abbreviations" wte/tests/test_bordas.pas` maior que zero, e o
      programa continua verde
- [ ] A contagem de conferências no critério bate com a que o programa imprime
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
