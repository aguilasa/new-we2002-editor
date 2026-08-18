# `re/formacoes.md` — as 18 formações do campinho tático

Produto da [CORR-WTE-062](../../docs/tasks/CORR-WTE-062.md). Gerado
por [`../tools/dump_formacoes.py`](../tools/dump_formacoes.py).
**Não editar à mão.** A tabela está em [`formacoes.tsv`](formacoes.tsv); a
unidade Pascal é
[`../src/wte_formacoes.pas`](../src/wte_formacoes.pas).

## O que é

`lista_formaciones` tem **18** itens e a tabela tem
**18** registros de **44** bytes — quatro colunas de
11 bytes cada. Ela vive em `0x00433f0c`, **não existe no
arquivo**, e é montada pelo `estrategia.FormCreate` com quatro
`rep movsd` a partir de quatro blobs contíguos de `.data`. O fim dela
encosta em `0x00434224`, que é o primeiro dos quatro
ponteiros globais — e é essa contiguidade que fecha o tamanho.

| Blob | Coluna | Vai para | Faixa | Serve para |
|---|---|---|---|---|
| `0x00423be4` | `papel` | `reg+0x00` | 0..21 | indexa as 22 abreviaturas de `0x00423b8c` |
| `0x00423cb0` | `x` | `reg+0x0b` | 0..43 | `DestinoX = x × 8 − 2` |
| `0x00423d7c` | `y` | `reg+0x16` | 0..87 | `DestinoY = ((y − 3) div 2) × 5 − 7` |
| `0x00423e48` | `zona` | `reg+0x21` | 0..10 | indexa as 11 `ZONAS` do `wte_zonas.pas` |

## O que o handler faz com isso

`estrategia.lista_formacionesClick` (`0x00409aa0`) **não tem número**:
ele aponta quatro ponteiros (`0x00434224`, `0x28`, `0x2c`, `0x30`) para
dentro do registro escolhido e chama duas auxiliares. Uma calcula as
seis tabelas da animação e liga o `reloj`; a outra pinta os onze
`etiqposN`.

O item **1** (`DEFAULT`) é o outro ramo: em vez da tabela, ele lê o
buffer da formação viva do time (`0x00432e88`), que é preenchido por
`0x0040a0b4` — rotina de abertura do formulário, **não portada**.

## As três conferências que abortam

1. **Faixa.** `papel` cabe nas 22 abreviaturas e `zona` nas 11 zonas
   do `wte_zonas.pas` — outra fonte, gerada por outro script.
2. **O destino cabe no `campo`**, que o `.lfm` diz ser
   395×246. O jogador 0 fica de fora: as três rotinas do
   original iteram `1..10`, e vários registros trazem `x = y = 0`, que
   daria `(−2, −12)`.
3. **O destino cai na grade do arrasto.** `x × 8 − 2` é ≡ 6 (mod 8), e
   a grade do `rectanguloDragOver` tem passo 8 e fase 5 com raio 7 —
   `5 − 7` também é ≡ 6 (mod 8). No Y, `5k − 7` é ≡ 3 (mod 5). As
   posições que a formação impõe caem **exatamente** onde o arrasto
   solta a bola, e as duas leituras vieram de rotinas diferentes.

## O passo da animação

`0x004099b0` guarda um `long double` de 80 bits que vale
**0.2**. Com os quatro quadros do `relojTimer` isso cobre
**80%** do trajeto; o ramo de encaixe dá o último
quinto de uma vez. Não é correção de arredondamento de um pixel.

## As 18 formações

Posição do jogador 1 (o mais recuado dos dez de campo), para dar
tamanho; a tabela inteira está no `.tsv`.

| # | Nome | Papéis (0..10) | Zonas (0..10) |
|--:|---|---|---|
| 0 | `STOCK` | -- Za Za Le Ld Vl Ae Ad Me At At | 0 1 1 2 3 4 5 6 7 8 8 |
| 1 | `DEFAULT` | -- -- -- -- -- -- -- -- -- -- -- | 0 0 0 0 0 0 0 0 0 0 0 |
| 2 | `4 - 5 - 1  A` | -- Za Za Le Ld Vl Ae Ad Me Me At | 0 1 1 2 3 4 5 6 7 7 8 |
| 3 | `4 - 5 - 1  B` | -- Za Za Le Ld Vl Vl Ae Ad Me At | 0 1 1 2 3 4 4 5 6 7 8 |
| 4 | `4 - 4 - 2  A` | -- Za Za Le Ld Vl Ae Ad Me At At | 0 1 1 2 3 4 5 6 7 8 8 |
| 5 | `4 - 4 - 2  B` | -- Za Za Le Ld Vl Vl Me Me At At | 0 1 1 2 3 4 4 7 7 8 8 |
| 6 | `4 - 3 - 3  A` | -- Za Za Le Ld Vl Me Me At Pe Pd | 0 1 1 2 3 4 7 7 8 9 10 |
| 7 | `4 - 3 - 3  B` | -- Za Za Le Ld Vl Vl Me At Pe Pd | 0 1 1 2 3 4 4 7 8 9 10 |
| 8 | `3 - 6 - 1  A` | -- Za Za Za Vl Ae Ad Me Me Me At | 0 1 1 1 4 5 6 7 7 7 8 |
| 9 | `3 - 6 - 1  B` | -- Za Za Za Vl Vl Ae Ad Me Me At | 0 1 1 1 4 4 5 6 7 7 8 |
| 10 | `3 - 5 - 2  A` | -- Za Za Za Vl Ae Ad Me Me At At | 0 1 1 1 4 5 6 7 7 8 8 |
| 11 | `3 - 5 - 2  B` | -- Za Za Za Vl Vl Ae Ad Me At At | 0 1 1 1 4 4 5 6 7 8 8 |
| 12 | `3 - 4 - 3  A` | -- Za Za Za Vl Ae Ad Me At Pe Pd | 0 1 1 1 4 5 6 7 8 9 10 |
| 13 | `3 - 4 - 3  B` | -- Za Za Za Vl Vl Me Me At Pe Pd | 0 1 1 1 4 4 7 7 8 9 10 |
| 14 | `5 - 4 - 1  A` | -- Za Za Za Le Ld Vl Ae Ad Me At | 0 1 1 1 2 3 4 5 6 7 8 |
| 15 | `5 - 4 - 1  B` | -- Za Za Za Le Ld Vl Vl Me Me At | 0 1 1 1 2 3 4 4 7 7 8 |
| 16 | `5 - 3 - 2  A` | -- Za Za Za Le Ld Vl Me Me At At | 0 1 1 1 2 3 4 7 7 8 8 |
| 17 | `5 - 3 - 2  B` | -- Za Za Za Le Ld Vl Vl Me At At | 0 1 1 1 2 3 4 4 7 8 8 |
