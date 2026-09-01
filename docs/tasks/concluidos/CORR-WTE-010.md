---
id: CORR-WTE-010
title: "Correção: a §8.7 do plano e o enunciado da WTE-TASK-06 apontam o lado errado, e o ASCII citado não é o do binário"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-010: o dword que obriga a medir está **abaixo** da tabela, e é `lmno`

## Problema identificado

A §8.7 do plano, que é a armadilha citada por nome no critério de conclusão da
WTE-TASK-06, diz:

> ### 8.7 O 32º byte da tabela não é offset
>
> A varredura da §1.7 mostra que o bloco em `0x004231a0` tem buracos (`= 0`) e é
> **seguido** de dados que **não** são offsets (`1869507948` é ASCII `l,km`).

Duas coisas erradas na mesma frase, as duas medidas pela WTE-TASK-06:

1. **O lado.** Esse dword está em `0x00423190` — **16 bytes abaixo** da tabela,
   não acima. O que a tabela é seguida é de `67305984` (`0x04030200`), que não
   passa no filtro por outro motivo. Quem obriga a medir o limite *inferior* é o
   ASCII; o superior cai por conteúdo.
2. **O texto.** `1869507948` little-endian é `6c 6d 6e 6f` = **`lmno`**, pedaço
   da tabela de alfabeto vizinha. `l,km` não sai desses bytes em nenhuma ordem.

O enunciado da própria WTE-TASK-06 (linha 45) copia as duas.

O Log da tarefa registra o achado e diz por que parou ali:

> Registrado no `offsets.md`; a §8.7 do plano **não foi editada** — é decisão do
> thread principal.

Foi a decisão certa para quem executa, e deixa o resíduo: a §8.7 é o que o
executor da WTE-TASK-19 vai ler antes de mexer em offset, e ela manda olhar o
lado que não tem nada. É a mesma forma da
[CORR-WTE-006](/docs/tasks/concluidos/CORR-WTE-006.md) e da
[CORR-WTE-009](/docs/tasks/concluidos/CORR-WTE-009.md): a medição existe, o documento que
comanda a execução não a recebeu.

**A conclusão da §8.7 continua de pé** — o bloco é cercado de não-offset dos dois
lados, e o limite tem de ser medido. Só a evidência é que está do lado errado.

## Evidência

O dword citado, lido do binário nesta revisão:

```
$ python3 -c "... img.va_to_offset(0x00423190) ..."
0x00423190 = 1869507948 = b'lmno'
```

A tabela começa 16 bytes depois, em `0x004231a0`, e vai até `0x004231e8`:

```
tabela1: 0x4231a0..0x4231e8 = 72 bytes, 18 slots, preenchidos 11, buracos 7
tabela2: 0x423634..0x423648 = 20 bytes, 5 slots, preenchidos 5, buracos 0
```

Os dois critérios de limite superior concordam, medidos:

```
tabela 0x4231a0 end=0x4231e8 | proxima ref de .data: 0x4231e8 | concorda: True
tabela 0x423634 end=0x423648 | proxima ref de .data: 0x423648 | concorda: True
```

E nada dentro do intervalo é referenciado — só a base:

```
0x4231a0..0x4231e8: refs internas = 0; base referenciada = True
0x423634..0x423648: refs internas = 0; base referenciada = True
```

## Causa raiz

A §8.7 foi escrita a partir da varredura descartável de 2026-08-05, que não
distinguiu o dword de antes do de depois; a WTE-TASK-06 mediu e registrou no
relatório dela, sem mandato para editar o plano.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

§8.7: manter a armadilha e trocar a evidência. O bloco continua tendo buracos e
continua exigindo limite medido — o que muda é que o vizinho ASCII (`lmno`, em
`0x00423190`) fica **abaixo** dele e é o que obriga a medir o limite *inferior*,
enquanto o superior sai por conteúdo e por referência, medidas que concordam.
Vale apontar para [`../../wte/re/offsets.md`](../../../wte/re/offsets.md), que traz
o critério escrito.

O título "O 32º byte da tabela não é offset" também não descreve o que foi
medido — a tabela tem 72 bytes e 7 buracos internos; o 32º byte é um deles, não
o fim. Reescrever para algo como "o limite da tabela tem de ser medido dos dois
lados".

### Arquivo: `docs/tasks/concluidos/06-mapa-de-offsets.md`

Linha 45, no enunciado: mesma correção de lado e de ASCII. O Log fica como está
— ele é histórico e já registra o achado.

**Fora de escopo:** o "19 de 69" da §1.7, que a
[WTE-TASK-09](/docs/tasks/concluidos/09-fechamento-fase-1.md) tem no quadro de
reconciliação (`19 de 69 offsets | dump_offsets.py`) — e que, medido nesta
revisão, confere.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar — §8.7 |
| `docs/tasks/concluidos/06-mapa-de-offsets.md` | modificar — enunciado, linha 45 |

## Verificação

- [x] `grep -rn "l,km" docs/` não devolve nada — fora do
      `correcoes-progresso.md`, que registra o sintoma e tem de continuar
      registrando
- [x] `grep -rn "1869507948" docs/` mostra as passagens já com `0x00423190`,
      `lmno` e o lado certo
- [x] A §8.7 continua dizendo que o limite tem de ser medido, e aponta para o
      critério escrito do `offsets.md`
- [x] `python3 wte/tools/dump_offsets.py --check` verde (nenhum gerado tocado)
- [x] Links de markdown conforme `.claude/rules/links.md`
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

A §8.7 manteve a armadilha e trocou a evidência. O bloco continua cercado de
não-offset, e agora o texto diz **por que cada lado cai**, que é o que obriga a
medir os dois com critérios diferentes: abaixo, em `0x00423190`, o `1869507948`
= `6c 6d 6e 6f` = `lmno`, pedaço da tabela de alfabeto vizinha, que fixa o
limite inferior; acima, logo depois de `0x004231e8`, o `67305984` (`0x04030200`),
que cai por conteúdo e não por ser texto. Ganhou ponteiro para o
`wte/re/offsets.md`, onde o critério está escrito.

O título trocou: "O 32º byte da tabela não é offset" não descrevia o medido — a
tabela tem 72 bytes e 7 buracos internos, e o 32º byte é um deles, não o fim.
Virou "O limite da tabela tem de ser medido dos dois lados".

O enunciado da WTE-TASK-06 recebeu a mesma correção de lado e de ASCII. O Log
dela fica como está — é histórico, e já registra o achado.

**Problemas encontrados:**

Nenhum. Os três valores foram relidos do binário antes de escrever:
`0x00423190` = `1869507948` = `b'lmno'`, `0x004231a0` = `2002316` (primeiro
slot), `0x004231e8` = `67305984` = `b'\x00\x02\x03\x04'`.

**Arquivos criados/modificados:**

- `docs/PLAN-WTE-LAZARUS.md` — §8.7, título e evidência
- `docs/tasks/concluidos/06-mapa-de-offsets.md` — enunciado, seção 1
- `docs/tasks/concluidos/correcoes-progresso.md`
