---
handler: BitBtn3Click
formulario: ficha_color
endereco: 0x004069e8
veredito: aberto
---

# ficha_color.BitBtn3Click

O `OK     ` do editor de cor — e **a sétima rota de escrita na imagem de CD**,
que nenhuma task anterior tinha visto.

**Evidência:** disassembly lido

## Entrada

- `CorEmEdicao.cores`, o vetor de 16 palavras que o editor manipula;
- o **slot 1** inteiro do bloco de cor do time — o rascunho;
- a global do time em edição (`0x004335CC`);
- as sete globais de offset que a carga
  ([`0x004050D0`](../auxiliares.md)) deixou preenchidas.

**Evidência:** disassembly lido

## Saída

Trinta e cinco bytes, quatro chamadas:

```text
salva_paleta()                          ' 0x00405B48 -- vetor -> slot 1
copia_slot(origem := 1, destino := 0)   ' 0x00404F90 -- confirma o rascunho
grava_bloco_de_cor_na_imagem()          ' 0x004051A4 -- A ESCRITA
redesenha_uniforme(TimeEmCor, 0)        ' 0x004056C8
```

A ordem não comuta: a paleta tem de descer do vetor para o slot 1 antes de o
slot 1 virar slot 0, e o slot 0 é o que a gravação lê.

### A gravação, `0x004051A4`

É o **espelho exato** da carga `0x004050D0`, bloco por bloco, com a mesma
global de offset em cada um — só troca a `0x004033BC` (ler) pela `0x00403400`
(gravar):

| bloco | origem na memória | offset em | lidos | gravados |
|---|---|---|---:|---:|
| cores da bandeira | `0x00432ED4` | `[0x004331DC]` | 32 | **30** |
| forma da bandeira | `0x00432F14` | `[0x004331E8]` na carga; `[0x004331E0 + i*4]`, i de 0 a 4, na gravação | 1 | 1 × **5** |
| uniforme, jogo 0 | `0x00432F16` | `[0x004331F4]` | 32 | **30** |
| uniforme, jogo 1 | `0x00432F36` | `[0x004331F8]` | 32 | **30** |
| 8 paletas de chuteira | `0x00432F96 + n*32` | `[0x004331FC + n*4]` | 32 | 32 |
| quarta paleta | `0x00433196` | `[0x0043321C]` | 32 | **30** |
| padrão da camisa | `0x004331D6` | `[0x00433220]` | 2 | 2 |

**Duas assimetrias, e as duas são achado desta task.**

1. **Lê 32 e grava 30** em quatro dos sete blocos. A última palavra de 16 bits
   de cada paleta é carregada e **nunca devolvida**. Casa com o que o
   [`render2d.md`](../render2d.md) mediu por outro caminho — `flag_colours[15]`
   é zero nas 95 —, mas não é a mesma afirmação: aqui o motivo é que o gravador
   não a escreve, e um port que gravasse 32 mudaria bytes que o original nunca
   mudou. As chuteiras e o padrão de camisa **são** simétricos.
2. **A forma da bandeira é lida de um offset e gravada em cinco.** A carga usa
   `[0x004331E8]`, que é o terceiro dos cinco (`0x004331E0 + 8`); a gravação
   percorre os cinco. O byte mora replicado na imagem, e o editor mantém as
   cinco cópias em sincronia ao gravar enquanto confia só na do meio ao ler.

**Evidência:** disassembly lido

## Bytes tocados

Sete regiões por time, todas endereçadas por global de offset em vez de
constante — os endereços absolutos dependem do time selecionado e saem da
tabela em `.data` que a
[WTE-TASK-06](../../../docs/tasks/06-mapa-de-offsets.md) mapeou. Os tamanhos
estão na tabela acima: 30 + 5×1 + 30 + 30 + 8×32 + 30 + 2 = **383 bytes** por
gravação.

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere imagem aberta, não confere time selecionado, não
pergunta nada ao usuário. Clicar `OK` grava.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. A `0x00403400` não devolve estado que o handler leia.

**Evidência:** disassembly lido

## Justificativa do veredito `aberto`

**Não é moldura de diálogo, é gravação — e não tem dono.** A
[WTE-TASK-30](../../../docs/tasks/30-handlers-auxiliares.md) esperava *"avisos
e confirmações"* neste grupo e disse que aqui se implementa *"a moldura ... e
as tasks 29 e 32 preenchem o miolo"*. O miolo deste não é de nenhuma das duas:
é uma escrita na imagem, do tamanho de uma das seis que a
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md) carregou, e ela
está fechada.

Implementar aqui sem o gate de gravação — golden com **controle** fechando
antes, nas duas ROMs — seria opinião, que é o que a
[WTE-TASK-22](../../../docs/tasks/22-harness-golden.md) existe para impedir.

**O que já está pronto para quem herdar:** o vetor e o slot 1 são a
[`wte_cor`](../../src/wte_cor.pas) (`CorEmEdicao`, `SalvaPaleta`, `Jogo`), o
slot 0 chegou nesta task (`GuardaOriginal`/`RestauraOriginal`), e o par de
bytes de padrão de camisa já tem lugar (`PadraoDaCamisa`). Falta o escritor — e
o `we2002_offsets` ainda não expõe as sete colunas por time que a carga usa.

## Notas

**Este é o único consumidor do `PadraoDaCamisa`.** A `wte_cor` já registrava
que *"nada neste port ainda lê estes dois bytes"* e nomeava o motivo: *"o único
consumidor no original é a gravação do `BitBtn3`"*. Medido, é isso mesmo.

**As duas famílias não portadas gravam junto.** Chuteira e quarta paleta não
têm campo na camada de dados, mas a `0x004051A4` grava os 288 bytes delas a
partir do slot 0 — que é o que a carga leu da imagem. Um port que pulasse os
dois blocos gravaria menos que o original e passaria no golden **só** enquanto
ninguém os editasse; um que gravasse zeros corromperia a imagem. Quem herdar
precisa carregá-los para poder devolvê-los intactos.
