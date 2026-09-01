---
handler: BitBtn3Click
formulario: ficha_color
endereco: 0x004069e8
veredito: implementado
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
[WTE-TASK-06](../../../docs/tasks/concluidos/06-mapa-de-offsets.md) mapeou. Os tamanhos
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

## Como o veredito fechou

Fechou pela [CORR-WTE-081](../../../docs/tasks/concluidos/CORR-WTE-081.md), segunda das
três gravações órfãs, com o par
[`golden-16-cor`](../../tests/roteiros/golden-16-cor.txt) nos três modos do
[`golden_check.sh`](../../tools/golden_check.sh): `controle` byte-idêntico,
`positivo` detectando o byte plantado em 405228, `golden` byte-idêntico contra
o oráculo.

**O roteiro edita antes de gravar, e aqui isso era obrigatório.** Ao contrário
do `golden-15`, cujo `Comple.` é destrutivo sozinho, as sete regiões daqui saem
do que a carga leu: clicar `OK` sem editar devolveria os mesmos bytes e um port
que não gravasse nada passaria. Um clique no `aclarar` resolve — ele percorre a
faixa do gradiente inteira (1..16), então não depende de amostra selecionada.
Medido: 30 bytes mudam em `OFS_FLAG_COLOURS+96`, e mais nada além dos três do
arranque.

**As sete colunas por time entraram por gerador, não à mão.** O
[`dump_blococor.py`](../../tools/dump_blococor.py) lê do `.exe` a tabela de 95
bytes de `0x00423247` — que **não é identidade**: 86 valores distintos, times
compartilham paleta de bandeira — e as cinco bases de `0x00423634`, e emite o
[`wte_blococor.pas`](../../src/wte_blococor.pas). Ele aborta se qualquer uma de
oito âncoras deixar de bater com um `OFS_*` do `we2002_core`, entre elas o time
36 (`OFS_FLAG_COLOURS_SENEGAL`, o `cmp eax,0x24` do original) e as cinco cópias
da forma.

**A armadilha custou uma corrida de golden, e ela não estava na spec.** O
uniforme começa na **segunda** palavra do vetor: o offset que o `0x00404E70`
calcula é `OFS_KIT_PREVIEW + 2`, ou seja `cores[1]`, enquanto a bandeira começa
em `cores[0]`. Gravar os dois do mesmo jeito desloca os 30 bytes de uma palavra
e estraga o uniforme inteiro — 44 bytes de diferença em `OFS_KIT_PREVIEW+130`.
É a mesma assimetria que o [`render2d.md`](../render2d.md) já tinha medido por
outro caminho ("16 na bandeira, 15 no uniforme"), e que a
[`wte_render2d`](../../src/wte_render2d.pas) já usava para desenhar.

**As duas famílias não portadas saem de uma carga nova.** A
`CarregaBlocoDeCorDaImagem` da [`wte_cor`](../../src/wte_cor.pas) lê da imagem
as oito paletas de chuteira, a quarta paleta e o par de padrão de camisa quando
o `colorearClick` abre o editor — que é onde o original as lê. Com ela o `OK`
devolve os 353 bytes que ninguém edita exatamente como estavam.

E ela consertou de passagem uma divergência latente: o `PadraoDaCamisa`
nascia com o literal `(0, $65)` e **nunca era carregado**. As duas ROMs deste
repositório guardam `00 65` naquele offset, então o gate não teria visto — mas
qualquer imagem com outro padrão teria o padrão sobrescrito pelo port.

## Notas

**Este é o único consumidor do `PadraoDaCamisa`.** A `wte_cor` já registrava
que *"nada neste port ainda lê estes dois bytes"* e nomeava o motivo: *"o único
consumidor no original é a gravação do `BitBtn3`"*. Medido, é isso mesmo.

**As duas famílias não portadas gravam junto.** Chuteira e quarta paleta não
têm campo na camada de dados, mas a `0x004051A4` grava os 288 bytes delas a
partir do slot 0 — que é o que a carga leu da imagem. Um port que pulasse os
dois blocos gravaria menos que o original e passaria no golden **só** enquanto
ninguém os editasse; um que gravasse zeros corromperia a imagem. Foi por isso
que a `CarregaBlocoDeCorDaImagem` teve de existir: elas não são modeladas, e o
único jeito de devolver o que não se modela é guardar os bytes como estão.
