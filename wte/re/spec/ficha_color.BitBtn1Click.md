---
handler: BitBtn1Click
formulario: ficha_color
endereco: 0x00406968
veredito: implementado
---

# ficha_color.BitBtn1Click

O `Original` do editor de cor: desfaz tudo o que foi editado desde que a
janela abriu, **sem fechá-la**.

**Evidência:** disassembly lido

## Entrada

- o **slot 0** do bloco de cor do time — a cópia intocada;
- `lista_col1.ItemIndex` (campo `+0x398`), o jogo de uniforme em exibição;
- o byte de forma da bandeira do slot 0 (`0x00432F14`);
- a tabela de 95 bytes em `0x004231E8`, que a
  [WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md) portou como
  `FORMA_PADRAO` na [`wte_uniformes`](../../src/wte_uniformes.pas).

O `Sender` não é olhado. Os dois campos saem do
[`campos.tsv`](../campos.tsv): `+0x398` é o `lista_col1` e `+0x39C` é o
`lista_col0`.

**Evidência:** disassembly lido

## Saída

```text
copia_slot(origem := 0, destino := 1)   ' 0x00404F90
repinta_as_16_amostras()                ' 0x00405D6C
redesenha_bandeira()                    ' 0x00405270
redesenha_uniforme(TimeEmCor, lista_col1.ItemIndex)   ' 0x004056C8

i := 0
enquanto FORMA_PADRAO[i] <> forma_do_slot0: i := i + 1
lista_col0.ItemIndex := i
```

**O que a cópia de slot move** — medido no corpo da `0x00404F90`, que endereça
tudo por `origem` e `destino` e roda 0x20 vezes:

| bloco | base | tamanho por slot |
|---|---|---|
| cores da bandeira | `0x00432ED4` | 32 |
| uniforme, jogo 0 | `0x00432F16` | 32 |
| uniforme, jogo 1 | `0x00432F36` | 32 |
| 8 paletas de chuteira | `0x00432F96` | 8 × 32 |
| quarta paleta | `0x00433196` | 32 |
| forma da bandeira | `0x00432F14` | 1 |
| padrão da camisa | `0x004331D6` | 2 |

O passo de slot é 32 para os blocos de uma paleta, 64 para o par de uniformes
e 256 para as chuteiras — os `lea` do corpo (`[eax*8+base]` com o índice já
deslocado) dão os três sem ambiguidade. E fecham o círculo com o
[`render2d.md`](../render2d.md): a bandeira que o desenhista lê é
`0x00432EF4`, que é `0x00432ED4 + 32` — o slot **1**, o rascunho.

**A última linha é uma busca, não um cálculo.** O combo de forma mostra nome de
time e **indexa** a tabela de formas padrão, então repor a seleção exige achar
a primeira posição cujo valor seja a forma restaurada.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não há chamada de escrita no corpo nem em nenhuma das quatro
rotinas que ele chama. Gravar é o [`BitBtn3`](ficha_color.BitBtn3Click.md).

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não confere time selecionado nem imagem aberta — se o editor abriu, o
time existe.

**Evidência:** disassembly lido

## Comportamento de erro

**A busca da forma não tem fim.** O laço em `0x004069A6` incrementa até
encontrar o byte e não confere limite: forma que não esteja entre as 95 da
tabela faz a varredura sair do fim dela e devolver um índice qualquer, ou
estourar. Não há teste de faixa em lugar nenhum do corpo.

**Evidência:** disassembly lido

## Notas

**O slot 0 não existia no port, e passou a existir aqui.** A
[`wte_cor`](../../src/wte_cor.pas) registrava a ausência nas suas próprias
palavras — *"o slot 0 do original — a cópia intocada, que o `BitBtn1` restaura
— não tem equivalente aqui, e quem precisar dele é o desfazer, que ainda não
foi portado"*. Este handler é o desfazer. A `wte_cor` ganhou
`GuardaOriginal`/`RestauraOriginal` e o par de bytes de padrão de camisa entrou
na foto junto, porque a `0x00404F90` o copia.

**Onde a foto é tirada, e por que isso é equivalente e não igual.** No original
o slot 0 é preenchido a cada troca de time, pela carga
(`0x004050F0` lê da imagem, `0x00405198` copia para o slot 1). No port a foto
sai no [`colorearClick`](MainForm.colorearClick.md), imediatamente antes do
`ShowModal`. A diferença só apareceria se o time mudasse com o editor aberto, e
ele é **modal**: não muda.

**A varredura do port pára no fim da tabela.** Reproduzir o laço sem limite
seria reproduzir comportamento indefinido, que não é comportamento — a mesma
decisão, com as mesmas palavras, que a
[`botonClick`](ficha_color.botonClick.md) tomou para a família fora de 0..3.
Forma ausente da tabela deixa o combo como está.

**As duas famílias não portadas voltam junto assim mesmo.** Chuteira e quarta
paleta não têm campo na camada de dados, então não há o que restaurar nelas —
mas também não há o que editar, porque a
[`SalvaPaleta`](../../src/wte_cor.pas) recusa família não portada. Restaurar o
que ninguém escreveu é vazio nos dois lados.
