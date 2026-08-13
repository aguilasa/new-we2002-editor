# `re/legendas.md` — as legendas enumeradas da ficha do jogador

Produto da [WTE-TASK-26](../../docs/tasks/26-handlers-de-edicao.md).
Gerado por [`../tools/dump_legendas.py`](../tools/dump_legendas.py) a
partir de `we-team-editor/we-team-editor.exe`. **Não editar à mão.** As tabelas estão em
[`legendas.tsv`](legendas.tsv); este arquivo é a leitura delas, e a unidade
Pascal correspondente é
[`../src/wte_legendas.pas`](../src/wte_legendas.pas).

## Por que elas não se leem do arquivo

A primeira vive em `0x00423798` e é um
`AnsiString[12][8]` — 12 linhas de 8
ponteiros, passo `0x20`. **No disco ela é zero:** ponteiro de
`AnsiString` não existe em arquivo. Quem a monta é o inicializador da
unidade, `0x00401da8`..`0x0040295e`, com 150 chamadas ao
construtor de `AnsiString` a partir de literal.

Por isso este dumper decodifica em vez de transcrever: as cadeias estão
no `.exe` e sairiam num `strings`, mas **qual cadeia vai em qual slot**
só está na ordem das chamadas.

## Quem lê a tabela

Os dois lados da ficha do jogador:

- `jugador.flechasapaClick` (`0x00408088`) — ao mexer numa seta, indexa
  `[sufixo − 1][Position]` e escreve no `valorapa` correspondente;
- `0x0040756c` (o que enche a ficha) — na abertura, para os mesmos doze.

## A tabela da ficha

55 das 96 posições têm texto. O resto é um
espaço — não cadeia vazia, e é o que o original constrói para as linhas
curtas.

| Linha | `flechasapa` | `Max` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|--:|--:|--:|---|---|---|---|---|---|---|---|
| 0 | `flechasapa1` | 7 | `Gl` | `Za` | `Lt` | `Vl` | `Al` | `Me` | `At` | `Po` |
| 1 | `flechasapa2` | 3 | `A` | `B` | `C` | `D` | — | — | — | — |
| 2 | `flechasapa3` | 31 | — | — | — | — | — | — | — | — |
| 3 | `flechasapa4` | 7 | `A` | `B` | `C` | `D` | `E` | `F` | `G` | `H` |
| 4 | `flechasapa5` | 6 | `A` | `B` | `C` | `D` | `E` | `F` | `G` | — |
| 5 | `flechasapa6` | 6 | `A` | `B` | `C` | `D` | `E` | `F` | `G` | — |
| 6 | `flechasapa7` | 63 | — | — | — | — | — | — | — | — |
| 7 | `flechasapa8` | 7 | `A` | `B` | `C` | `D` | `E` | `F` | `G` | `H` |
| 8 | `flechasapa9` | 31 | — | — | — | — | — | — | — | — |
| 9 | `flechasapa10` | 7 | `A` | `B` | `C` | `D` | `E` | `F` | `G` | `H` |
| 10 | `flechasapa11` | 2 | `Dire.` | `Esq.` | `Dois` | — | — | — | — | — |
| 11 | `flechasapa12` | 1 | `NO` | `YES` | — | — | — | — | — | — |

**A coluna `Max` é a conferência, não enfeite.** Ela vem do formulário
(`wte/re/dfm/jugador.dfm`) e a contagem de células com texto vem do código; o gerador
**aborta** se as duas discordarem. Nenhuma linha da tabela diz a que
controle pertence — só a ordem em que o inicializador constrói —, e é o
casamento das doze faixas que sustenta a atribuição.

Nas três linhas vazias o `Max` é maior que as 8 colunas: `flechasapa7`
(altura) e `flechasapa9` (idade) mostram número, e `flechasapa3` (forma
do cabelo) tem tabela própria.

## A tabela de flechasapa3

Contígua à primeira, em `0x00423918`: 32 cadeias em
fila, `Max` 31 mais um.

```text
  A1  A2  A3  B1  B2  B3  B4  B5  B6  C1  C2  D1  D2  E1  E2  F1  F2  F3  G1  H1  I1  I2  I3  J1  K1  L1  L2  L3  M1  N1  O1  P1
```

As mesmas 32 da contagem de `image/pelo/pelo_<n>.bmp` — ver a §5 de
[`assets.md`](assets.md).

## O que mais o inicializador monta

Das 150 cadeias, 96 são a tabela da ficha e
32 são a do cabelo. As demais estão no TSV com a tabela
`resto` — entram aqui porque saem da mesma varredura, não porque a
ficha as use.
