---
id: CORR-WTE-064
title: "Correção: o lote do `edit_nombre1` está provado e a conta dá um a mais que o oráculo"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-064: um a mais, e não é o campo errado desta vez

## Problema identificado

A [CORR-WTE-061](/docs/tasks/CORR-WTE-061.md) fechou o que se propunha: o
`0x00433a10` deixou de ser global anônima e passou a ter lote nomeado. Ela
também mediu, na mesma passagem, que **a derivação dá 6 e o oráculo corta em
5** para o time 2.

Não é mais "o destino não foi medido". O destino está provado por três lados
independentes, e é a *aritmética* que sobra um.

## Evidência

O lote, decodificado do binário e não declarado à mão:

```
$ python3 wte/tools/dump_truncamento.py --check
truncamento: ... (o gerador aborta se [0x00433a10] deixar de ser
             0x004231a0[0][0], que vale 2002316 = OFS_TEAM_NAME_KANJI)
```

A travessia do original (`0x00403c0c`), emulada byte a byte com o pulo de setor
do `0x00403388`, sobre `roms/japanese-shift-jis.bin`:

```
time 2, lote kanji : inicio 2003952  bytes 83 45 83 46 81 5B 83 8B 83 59 00 00
                     largura = 12    ->  sar 1  ->  6
time 2, lote name3 : inicio 2004968  bytes 57 41 4C 45 53 00 00 00
                     largura = 8     ->  dec    ->  7
```

E a tela, com `A B-C.DEFG` — texto escolhido para que o sexto caractere seja um
`D` **visível**:

| campo | oráculo | derivação |
|---|---|---|
| `edit_nombre1` | `A BC.` — **5** | 6 |
| `edit_nombre2` | `A BC.DE` — **7** | 7 ✔ |
| `edit_nombre3` | `ABC` — 3 | 3 ✔ |

**O mesmo modelo acerta o segundo campo e erra o primeiro por um.** É isso que
faz este resto valer uma correção própria em vez de uma nota: se o modelo
estivesse errado, o `edit_nombre2` não fecharia — e ele fecha, inclusive
corrigindo os 19 que o port usava.

## Causa raiz

**Não medida.** O que já foi descartado, para a próxima passagem não repetir:

- **não é o índice do time.** Nenhum dos 96 índices de salto produz
  `(kanji div 2, name3 - 1) == (5, 7)`; a varredura está no Log da
  CORR-WTE-061;
- **não é a imagem.** As duas ROMs dão largura 12 para o time 2, e a cópia de
  trabalho do oráculo é byte-idêntica à ROM na região do lote;
- **não é o pulo de setor.** O `fixup` do `0x00403388` cai exatamente em
  2003624 → 2003928, que é o `OFS_TEAM_NAME_KANJI_A` que o `we2002_core` já
  usava como salto manual. Os dois concordam;
- **não é a atribuição de campo.** O `campos.tsv` põe `edit_nombre1` em
  `MainForm+0x35c`, que é o alvo do `SetMaxLength` de `0x0040cc43`, o que
  recebe `[0x00433a10] div 2`;
- **não é outro escritor.** `0x0040cbc8` é chamado só de `0x0040d1c3`, dentro
  do `lista_equiposChange`, e a leitura acontece na mesma função logo depois.

Sobra o corpo de `0x00403c0c`: `esi` nasce 1, os dois laços contam, e o campo
`+4` recebe `lea eax,[esi+1]`. Para o time 2 isso dá 12, e para dar 5 depois do
`sar` teria de dar 10 ou 11. **Todas as larguras do lote kanji são múltiplas
de 4**, então `div 2` nunca é ímpar — o que sozinho mostra que o modelo do
contador está errado em algum ponto, e não que falte um caso especial.

## Correção

1. reler `0x00403c0c` **instrução a instrução**, sem paráfrase, com atenção a
   onde `esi` é incrementado em relação ao `getc` — a hipótese mais barata é o
   laço de salto deixar o cursor uma posição diferente da que a emulação
   assume, e o erro só aparecer no lote de dois bytes por caractere;
2. se a releitura não fechar, instrumentar: rodar o oráculo sob o Wine com um
   `WINEDEBUG` de chamadas de arquivo, ou medir a tela em **três times de
   larguras diferentes** e ver se a diferença é constante em 1 ou proporcional;
3. com a conta fechada, tirar o literal do
   [`LimiteDoNome1`](../../wte/src/impl/ep2002_mainform.aux.inc) e a entrada de
   `CONTRADIZ_A_TELA` do
   [`dump_truncamento.py`](../../wte/tools/dump_truncamento.py).

Se a releitura mostrar que a largura do lote kanji **não** é derivável, o
literal fica — mas aí com a razão medida, e não com "a conta dá outro número".

### Arquivos

- [`wte/tools/dump_truncamento.py`](../../wte/tools/dump_truncamento.py) — a
  tabela `CONTRADIZ_A_TELA`
- [`wte/src/impl/ep2002_mainform.aux.inc`](../../wte/src/impl/ep2002_mainform.aux.inc)
  — o `LimiteDoNome1`
- [`wte/re/spec/MainForm.lista_equiposChange.md`](../../wte/re/spec/MainForm.lista_equiposChange.md)
