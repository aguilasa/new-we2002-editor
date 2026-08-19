---
id: CORR-WTE-057
title: "Correção: a conferência de tela cobre 3 dos 5 grupos de campo que o critério enumera"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-057: a conferência de tela cobre 3 dos 5 grupos de campo que o critério enumera

## Problema identificado

O critério de tela da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) foi
reduzido por decisão de 2026-08-11 (seção "O item 2 tinha um ciclo dentro"), e a
redação que ficou **enumera cinco grupos de campo**:

> A conferência de tela cobre o que o grupo de carga produz: nome do time nos
> três campos, as cinco barras de força, **os 23 números de camisa**, **a lista
> de jogadores**, e **o estado de habilitação dos controles que o `nacional`
> governa**. Bandeira e uniforme ficam fora, como pendência nomeada da
> WTE-TASK-29.

O aparato entregue —
[`compara_tela.sh`](../../wte/tools/compara_tela.sh) +
[`compara_tela.py`](../../wte/tools/compara_tela.py) — compara um recorte de
**520×240 px do canto superior esquerdo** da janela. O próprio comentário do
script diz o que está lá dentro, e são três dos cinco:

```
# O recorte comparado: o canto superior esquerdo da janela, que e onde moram o
# combo de time, as cinco barras e os tres campos de nome.
REC_W=520
REC_H=240
```

Os 23 números de camisa e a lista de jogadores **caem fora do recorte**, e o
estado de habilitação nunca foi confrontado com o do original. O critério, ainda
assim, está marcado `[x]`.

O terceiro item é o que mais custa: a seção **Saída** da spec do
`lista_equiposChange` — a que lista os ~20 `.Enabled :=` que o Pascal reproduz —
está com evidência **`nao medido`** desde a sexta passagem, porque
`TControl::SetEnabled` tem zero `call rel32` na `.text`. A conferência de tela é
o único instrumento que restou para julgar aquela seção, e ela não olhou para
lá.

## Evidência

Posição absoluta dos controles no `MainForm`, somando `Left`/`Top` pela cadeia
de pais do [`MainForm.dfm`](../../wte/re/dfm/MainForm.dfm):

| Controle | Posição absoluta | Dentro do recorte 520×240? |
|---|---|---|
| `lista_equipos` | (16, 36) | sim |
| `barra1` | (92, 106) | sim |
| `boton_barras2iso` | (16, 184) | sim |
| `lista_jugadores_1` | (48, **392**) | **não** |
| `dorsal1` | (16, **432**) | **não** |
| `dorsal23` | (434, **432**) | **não** |

A montagem gerada nesta revisão confirma o recorte —
`work/tela/time-63-lado-a-lado.png` mostra combo, barras, bandeira/uniforme e os
três campos de nome, e termina acima da faixa dos `dorsalN` e da lista de
jogadores.

Reprodução da medição que **existe**, feita nesta revisão (todos os números
batem com o afirmado):

```
$ bash wte/tools/compara_tela.sh 2 9 63
compara_tela: time 2   barras oraculo/port [64, 53, 75, 75, 75]  5 de 5 vs core
compara_tela: time 9   barras oraculo/port [75, 64, 75, 75, 75]  5 de 5 vs core
compara_tela: time 63  barras oraculo/port [104, 75, 97, 97, 97] 4 de 5 vs core
```

O que **não** existe é qualquer saída, medida ou montagem, dos outros três
grupos.

Evidência da seção Saída, hoje:

```
$ awk '/^## Saída/,/^## Bytes/' wte/re/spec/MainForm.lista_equiposChange.md \
    | grep 'Evidência'
**Evidência:** nao medido
```

E o Pascal que herda a dúvida:

```
$ grep -c 'Enabled :=' wte/src/impl/ep2002_mainform.lista_equiposChange.inc
20
```

## Causa raiz

O recorte foi dimensionado para o que a medição em pixel sabia julgar — a barra,
cuja largura é `11*v + 9` e portanto número do jogo virado pixel — e a
enumeração do critério não foi reconferida contra ele antes de marcar `[x]`.

## Correção

### Arquivo: `wte/tools/compara_tela.sh`

Estender o recorte, ou acrescentar um segundo, que alcance a faixa dos
`dorsal1..23` (y ≈ 432) e a `lista_jugadores_1` (y ≈ 392). A janela tem 544×495,
então a altura cheia cabe.

O que a altura cheia **arrasta junto** é o que a WTE-TASK-29 possui — medido no
mesmo `MainForm.dfm`, `bandera` ocupa x 232..312 / y 36..84 e `home1`+`home2`
ocupam x 232..312 / y 104..168, e a montagem desta revisão mostra que os dois
lados já divergem ali. Ou o recorte vira **dois**, ou a caixa
x 232..312 / y 36..168 é excluída por coordenada — nunca por altura, que é o
que o corte atual faz e é o que esconde os três grupos que faltam.

Documentar no cabeçalho o que cada recorte cobre, com a mesma clareza da linha
que hoje justifica os 520×240.

### Arquivo: `wte/tools/compara_tela.py`

Os 23 números de camisa e a lista de jogadores são **texto**, e o próprio
enunciado da task manda compará-los por olho humano — a montagem lado a lado
basta, e não é preciso medi-los em pixel. O que a ferramenta deve garantir é que
eles **estejam** na montagem.

O estado de habilitação é diferente e vale medir: controle desabilitado no GTK2 e
no Win32 é desenhado em cinza, e a diferença é de cor sobre uma região conhecida.
Se a medição não for confiável entre os dois toolkits, então diga isso e trate o
item como comparação humana também — **mas registre o veredito por controle**,
porque é essa a única régua que a seção Saída `nao medido` ainda pode receber.

### Arquivo: `wte/re/spec/MainForm.lista_equiposChange.md`

Estender a seção "A conferência de tela" com o veredito dos três grupos novos, um
por um. Se o estado de habilitação bater com o do original nos três times, a
seção Saída pode subir de `nao medido` para `observação de tela` — que é
exatamente o valor que o [`GABARITO.md`](../../wte/re/spec/GABARITO.md) define
para "inferido do efeito visível, sem confirmar nos bytes", e é a verdade sobre
como aquele Pascal foi escrito.

### Arquivo: `docs/tasks/25-handlers-de-carga.md`

Depois de fechado, o critério de tela cita a medição dos cinco grupos. Enquanto
não estiver, o `[x]` daquela linha é afirmação maior que a evidência.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/compara_tela.sh` | modificar |
| `wte/tools/compara_tela.py` | modificar |
| `wte/tools/test_compara_tela.py` | modificar |
| `wte/re/spec/MainForm.lista_equiposChange.md` | modificar |
| `docs/tasks/25-handlers-de-carga.md` | modificar |

## Verificação

- [x] `bash wte/tools/compara_tela.sh 2 9 63` produz montagem contendo os 23
      `dorsalN` e a `lista_jugadores_1` dos dois lados
- [x] O veredito de cada um dos cinco grupos está escrito na spec, por time —
      o de habilitação é por **controle**, no par time 2 × time-modelo 95, que é
      onde `nacional` muda
- [x] A seção Saída da spec do `lista_equiposChange` deixa de estar `nao medido`,
      ou diz por que continua — subiu para `observacao de tela`, com os 13
      controles medidos e os 8 de fora nomeados
- [x] `python3 wte/tools/spec_index.py --check` continua verde
- [x] `make -C wte check` verde
- [x] `bash wte/tools/golden_check.sh wte/tests/roteiros/golden-01-arranque.txt
      --modo controle` fecha antes de qualquer medição de tela — `PASSOU:
      byte-identico`
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-11

**Resumo do que foi feito:**

O recorte medido de 520×240 **ficou onde estava**, e é a segunda das duas rotas
que a correção autorizava. A razão é a que o próprio arquivo já dava para não
crescer por altura, e ela é mais forte do que parecia: `banderita1` (y 339) é
laranja e entraria na detecção de banda, que já achou barra a mais duas vezes. A
montagem é que passou a sair da **janela inteira**, e com ela vieram os dois
grupos que faltavam. `confere_cobertura()` reprova montagem que não alcance a
base dos `dorsal1..23` — recorte curto voltou a ser erro dito.

O estado de habilitação virou medida própria, `compara_tela.sh --habilitacao`.
Três decisões dela:

1. **O par de times não podia ser 2, 9 e 63.** `nacional := ItemIndex < 95`, e
   os três são nacionais: a metade desabilitada da tela nunca tinha aparecido em
   medição nenhuma. O par é 2 × **95** (`95 Master L. `).
2. **A régua é "mudou ou não mudou", dentro de cada lado**, não a cor do cinza:
   gtk2 e Win32 não desenham o mesmo cinza, e exigir isso reprovaria o port por
   ser gtk2.
3. **A régua tem faixa.** O port deriva para baixo — medido: 6 px em y 90, 8 em
   y 154, **21** na faixa dos dorsais —, então abaixo de y 240 o retângulo do
   DFM deixa de nomear o controle certo. Oito controles ficaram declarados
   `fora_da_faixa` e vão por olho humano; `confere_faixa()` aborta se alguém
   marcar como medido um controle abaixo dela.

Treze controles medidos. A assimetria que a Saída afirmava e ninguém tinha
confrontado — `edit_nombreN` segue `nacional`, `etiq_nombreN` não — **é real**:
os três rótulos medem 0 px de mudança nos dois lados. Com isso a seção Saída
subiu de `nao medido` para `observacao de tela`.

**Problemas encontrados:**

**Dois defeitos do port, os dois em grupo que o recorte antigo escondia.** Não
foram corrigidos aqui — são comportamento do Pascal, e esta correção é do
instrumento; pedem correção própria, com o gate de tela refeito depois:

1. **Os `dorsal1..23` mostram um a menos.** Time 63: oráculo
   `1 5 6 3 2 11 …`, port `0 4 5 2 1 10 …`, e o mesmo desconto na legenda
   realçada e no contador `SPC/Livre`. O byte é 0-based e quem soma é a tela —
   `legacy/mfc/edDlg.cpp:2877` faz `_itoa(str_numeri[0]+1, …)`; o
   `PreencheCamisas` do port não faz.
2. **O `iguala_nombres` não é desabilitado no time-modelo.** Zero pixel de
   mudança contra 518 do oráculo. A linha existe no `.inc`, o `.lfm` nasce
   `Enabled = False` como o DFM, e o vizinho `boton_nombres2iso` — mesmo
   `TSpeedButton`, mesmo `Flat`, mesmo grupo — acinzenta certo. Causa não achada.

**Um número da própria evidência desta correção estava errado**, e o conserto é
para cima: ela cita `grep -c 'Enabled :=' … = 20`, e o arquivo tem **27**. O
sintoma não muda — 27 `.Enabled :=` sem confirmação em vez de 20.

**Arquivos criados/modificados:**

- `wte/tools/compara_tela.sh` — recorte `cheia` além do `topo`, modo
  `--habilitacao`, `recorta()` no lugar do heredoc repetido
- `wte/tools/compara_tela.py` — `CONTROLES`, `ANCORA`, `FAIXA_CALIBRADA_Y`,
  `calibra`, `confere_cobertura`, `confere_faixa`, `compara_habilitacao`,
  `relata_habilitacao`, montagem da janela inteira
- `wte/tools/test_compara_tela.py` — 10 testes novos (30 no total): calibração,
  cobertura, e os vereditos de habilitação plantados nos dois sentidos
- `wte/re/spec/MainForm.lista_equiposChange.md` — Saída para
  `observacao de tela`; a conferência de tela com os cinco grupos e os dois
  defeitos novos
- `docs/tasks/25-handlers-de-carga.md` — o critério de tela diz o que passou a
  ser medido, e nomeia os dois defeitos como trabalho de fora
