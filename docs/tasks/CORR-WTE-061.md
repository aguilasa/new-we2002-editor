---
id: CORR-WTE-061
title: "Correção: o `MaxLength` de `edit_nombre1` é o literal 5, lido da tela, sem lastro no formato"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-061: um limite que só a tela sustenta

## Problema identificado

O `MainForm.FormShow` do port faz:

```pascal
edit_nombre1.MaxLength := 5;
edit_nombre2.MaxLength := SizeOf(Jogo.teams[0].mixed_case_name) - 1;
```

**As duas linhas não têm o mesmo lastro.** A segunda sai da camada de dados e o
[`dump_truncamento.py`](../../wte/tools/dump_truncamento.py) confere a cada
`make check`. A primeira é **um literal**, e o único apoio dele é uma leitura de
tela: o oráculo mostra `ABC.D` quando se digita `AB-C.D E`.

A leitura está certa — foi ela que achou a divergência que a passagem anterior
tinha introduzido. O que falta é o **porquê**: o original calcula
`[0x00433a10] div 2`, logo aquela global vale 10, e **qual campo do formato tem
10 bytes não foi medido**. Enquanto isso, o 5 é número mágico: sobrevive por
coincidência de medição, e nada avisa se o campo mudar.

## Evidência

O que o gerador emite hoje, e ele já se declara:

```
$ cut -f2,3,5,6 wte/re/truncamento.tsv | head -3
campo	maxlength	expressao	destino
edit_nombre1	5	[0x00433a10] div 2	
edit_nombre2	19	[0x00433b48] - 1	mixed_case_name
```

A coluna `destino` do `edit_nombre1` sai **vazia**, e a `nota` da mesma linha
diz por quê: *"valor medido na tela (compara_tela.sh --nomes, 2026-08-18); o
destino no formato continua **nao medido**"*.

A tentativa anterior e por que ela passou:

```
DESTINOS["edit_nombre1"] = ("wte/src/we2002_team.pas", "raw_kanji_name")
# 40 bytes, div 2 = 20 -- a conferencia PASSOU, e a tela diz 5
```

A conferência do gerador compara a **aritmética** contra o destino que a tabela
`DESTINOS` declara, e a tabela é escrita à mão. Ela não prova o mapeamento — e
foi exatamente assim que 20 entrou no port.

## Causa raiz

`0x00433a10` é `.bss`, e **nenhum `mov` direto a escreve**. Ela é lida como base
de uma tabela de 312 bytes por linha (`lea ecx,[eax*8+0x433a10]` em
`0x00403cf4`), e o `0x0040cc2b` lê a **coluna 0 da linha 0** dela. A origem é a
tabela de offsets em `0x004231a0`, que o `0x0040db76` copia — os dois endereços
aparecem lado a lado, um em `[ebp-0xd0]` e o outro em `[ebp-0xcc]`.

Ou seja: o número existe no formato e o caminho até ele está mapeado. O que não
foi feito é percorrê-lo.

## Correção

1. ler o `0x0040cbc8` — a rotina que preenche a tabela de `0x00433a10` a partir
   de `0x004231a0` — e descobrir **o que é a coluna 0**. Se for comprimento de
   campo, o `dump_offsets.py` já tem a linha 0 e o número sai de lá;
2. com o destino nomeado, devolver `DESTINOS["edit_nombre1"]` ao gerador e
   deixar a conferência voltar a valer — **e conferir que o resultado é 5**, não
   escolher o campo que dê 5;
3. trocar o literal do `FormShow` pela mesma expressão da linha vizinha.

Se a leitura mostrar que a coluna 0 **não** é largura de campo, o resultado é
que a expressão do original não é derivável do formato, e o literal 5 fica —
mas com a razão escrita. **Também fecha.**

### Arquivos

- [`wte/tools/dump_truncamento.py`](../../wte/tools/dump_truncamento.py) — a
  tabela `DESTINOS` e o `MEDIDO_NA_TELA`
- [`wte/src/impl/ep2002_mainform.FormShow.inc`](../../wte/src/impl/ep2002_mainform.FormShow.inc)
