---
handler: lista_equiposChange
formulario: MainForm
endereco: 0x0040cd6c
veredito: aberto
---

# MainForm.lista_equiposChange

O handler central do editor: quase toda operação começa por escolher um time
nesta lista. 1.536 bytes, o segundo maior do `MainForm`.

## Entrada

- `lista_equipos.ItemIndex` — o time escolhido. **O combo não é populado em
  tempo de execução:** os 96 itens estão no DFM, `  0 Irlanda` … `95 Master
  L. `, e o `.lfm` os carrega verbatim.
- `lista_equipos_2.ItemIndex` — a segunda lista (time reserva), só para decidir
  se os botões de troca ficam habilitados.
- A imagem de CD, cinco bytes: as barras de força do time.
- O global em `0x0043459c` — qual dos cinco `sel_barra` está marcado.

**Evidência:** disassembly lido

## Saída

Três blocos, nesta ordem.

**1. Estado de controle.** `nacional := ItemIndex < 95` governa quase tudo:

```text
se ItemIndex = -1: sai sem fazer nada
base_team.Enabled := verdadeiro
se lista_equipos_2.ItemIndex >= 0:
    paderecha, paderecha2, paizquierda, paizquierda2,
    paderechaeizquierda        .Enabled := verdadeiro
edit_nombre1..3.Enabled   := nacional
iguala_nombres.Enabled    := nacional
etiq_nombre1..3.Enabled   := verdadeiro      ' sempre, não `nacional`
boton_nombres2iso.Enabled := nacional
boton_mcr.Enabled         := verdadeiro
boton_dialogo_tex.Enabled := verdadeiro
bandera, home1, home2, punto, banderita1  .Visible := nacional
colorear.Enabled          := nacional
```

**2. As cinco barras.** Com `nacional`, lê cinco bytes e faz
`barra<i>.Width := 11 * valor + 9`, além de `sel_barra<i>.Enabled :=
verdadeiro`; a `track_barra` recebe a posição da barra marcada e fica
habilitada. Sem `nacional`, as cinco larguras vão para **9** — que é o mesmo
`11*0 + 9`, a barra vazia —, os cinco rádios são desabilitados e a
`track_barra` também.

**3. O resto da tela.** `boton_barras2iso.Enabled := nacional`;
`lista_descarte.ItemIndex := -1` e habilitada; `parriba` habilitado; a bandeira
e o uniforme 2D redesenhados (só com `nacional`); `lista_equipos_1.ItemIndex`
espelha a seleção e alimenta a lista de jogadores; `lista_jugadores_1`
habilitada com `ItemIndex := 0`; `grabar_memory`, `grabar_camiseta`,
`mostrar_jugador_1` e `mostrar_estrategia_1` habilitados.

Com `ItemIndex > 62` — as seleções clássicas e os clubes de ML — o `home1` é
reposicionado: `Left := 7`, `Width := 100`, e o `punto` some. Abaixo disso,
`Left := 16`, `Width := 80`, `punto` visível.

**Evidência:** nao medido

> **Rebaixada de `disassembly lido` para `nao medido` em 2026-08-11.** Os
> `.Enabled :=` deste bloco não se sustentam: `TControl::SetEnabled` tem **zero**
> chamadas na `.text` inteira. Ver a seção Notas.

## Bytes tocados

**Nenhum. Só lê.** Cinco bytes por seleção, em

```text
t      = 0x45ff0 + 5 * indice
físico = 2352 * (t div 2048) + (t mod 2048) + 0x1e8178
```

com salto de `0x130` quando a leitura cruza o fim dos 2.048 bytes de dados de
um setor — a mesma aritmética sector-aware do resto do formato.

**Essa conta leva o time 0 para 2328184, que é exatamente a `OFS_TEAM_BARS` do
`we2002_core`.** Os dois oráculos falam do mesmo lugar, e é o que autoriza o
port a ler `Team.bar_*` em vez de reabrir a imagem. Conferido a cada build por
[`../../tools/check_barras.py`](../../tools/check_barras.py), que decodifica as
constantes do próprio corpo do handler em vez de as repetir.

A igualdade byte a byte foi medida uma vez, sobre uma cópia da ROM japonesa em
`work/`, contra o `dump_estado.pas`: os índices `0`, `1` e `62` batem com
`teams[i].bar_*`, e `63` e `94` com `ml_teams[i-63].bar_*`. Ou seja, os 95
itens da lista são os 63 `teams` seguidos dos 32 `ml_teams`, contíguos na
imagem e separados em dois vetores pela camada de dados.

**Evidência:** diff medido

## Pré-condições

`ItemIndex = -1` sai imediatamente — é a única checagem. Não confere se há
imagem aberta: sem imagem o `fseek`/`fgetc` iriam para um `FILE*` nulo, e o
combo só fica alcançável depois da carga.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `FindComponent` é usado sem conferir o resultado, para
`barra0..4` e `sel_barra0..4` — o mesmo padrão que a
[CORR-WTE-044](../../../docs/tasks/CORR-WTE-044.md) mediu derrubando o oráculo
com `dorsal` + N, e no mesmo handler de carga de time. Aqui os dez existem.

**Evidência:** disassembly lido

## Notas

**O Pascal está escrito**, em
[`../../src/impl/ep2002_mainform.lista_equiposChange.inc`](../../src/impl/ep2002_mainform.lista_equiposChange.inc),
e ele **não lê a imagem** — decisão medida, não atalho. As contas do original
caem nos mesmos bytes que a camada de dados já carregou:

| O que o original calcula | Onde a camada de dados já tem |
|---|---|
| as cinco barras, por `2352 * (t div 2048) + …` | `OFS_TEAM_BARS`, conferida byte a byte |
| os nomes, pela tabela em `0x004231a0` | a mesma tabela que virou os `OFS_*` |
| os 23 nomes de jogador e os 23 números | o mesmo elenco, `players[]` e `squad_numbers` |

Isso é o método da §4.2 rendendo o que promete pela terceira vez nesta task:
**`0x00404374` (881 B) e `0x00403f00` (328 B) não precisaram ser lidos.** O que
eles fazem é achar bytes cujo endereço já conhecemos por outro caminho.

**Veredito ainda `aberto`, e a seção Saída acima está sob suspeita.**

A tentativa de conferir contra a tela produziu dois achados, um deles contra
esta própria spec.

**1. O combo do port não abre por clique — e não é falta de window manager.**
A primeira leitura foi essa, e estava errada: `xdotool windowfocus` funciona e
a lista continua sem abrir. A causa está no DFM — `lista_equipos` nasce
**`Enabled = False`**, no original ([`../dfm/MainForm.dfm`](../dfm/MainForm.dfm)
linha 715) e portanto no `.lfm`. Controle desabilitado ignora clique, com ou sem
gerenciador de janela. O que falta é o port habilitá-lo depois de carregar a
imagem.

**2. E aí vem o problema: `TControl::SetEnabled` nunca é chamado.** O símbolo é
importado do `vcl60.bpl` e tem thunk em `0x00422884`; a `.text` inteira tem
**zero** `call rel32` para ele, e a única referência ao slot `0x0043ec1c` do IAT
é o próprio thunk. No mesmo bloco, para comparar: `SetText` 78 chamadas,
`GetText` 24, `SetVisible` 14.

A seção **Saída** desta spec lista uma dúzia de `.Enabled := verdadeiro` com
evidência `disassembly lido`. Com zero chamadas a `SetEnabled`, ou o original
liga esses controles por outro caminho — RTTI (`Typinfo` **é** importado), o
`Parent`, ou o `TWinControl` —, ou aquela leitura foi inferida da tela e
rotulada como disassembly. **Enquanto não se souber qual, a seção Saída não é
medida**, e o Pascal já escrito herda a dúvida: ele reproduz exatamente esses
`.Enabled :=`.

É o custo de ainda não ter conferido contra a tela, e a razão de o veredito
continuar `aberto`.

O que o corpo do port **não** faz, com dono nomeado: a bandeira e o uniforme 2D
(`0x00405270` e `0x004056c8`) são da
[WTE-TASK-32](../../../docs/tasks/32-camisa-e-bandeira-2d.md). Ele deixa os
controles com a visibilidade certa; quem os desenha é a 32.

**A tabela de auxiliares que estava aqui listava cinco endereços, e estava
curta.** Ela era escrita à mão; medido pelo
[`dump_auxiliares.py`](../../tools/dump_auxiliares.py), este handler chama
**treze** rotinas internas. Parte da diferença é rotina de biblioteca, que a
tabela à mão descartaria de propósito — mas `0x004050d0` e `0x0040cbc8`
carregam dado do jogo, e essas não estavam sendo descartadas: não estavam sendo
vistas. A lista viva está em [`../auxiliares.md`](../auxiliares.md).

**A lista de jogadores não é traduzida, é filtrada.** `0x0040b2d8` recebe a
lista de times e a lista de jogadores, esvazia a segunda e a preenche com 23
nomes lidos da imagem. Ele indexa duas tabelas em `.data` pelo próprio byte
lido, e a leitura barata seria "são tabelas de tradução, como o `KanjiToAscii`
do `we2002_core`". Medido, as duas são **identidade**: a rotina copia letra,
dígito, `.` e espaço, troca **qualquer byte acima de `z` por `?`** e descarta o
resto. Contra o `we2002_core`, que devolve espaço para byte desconhecido, isso
é divergência de tela — não de gravação. Conferido a cada build pelo
`dump_auxiliares.py`, que aborta se as tabelas deixarem de ser identidade.

**E a fronteira de setor é calculada, não tabelada.** A leitura de nome passa
por `0x00403388`, que não recebe offset: pergunta ao `ftell` onde está e, se
`posição mod 2352 = 2072`, avança 304. É a mesma geometria que o `we2002_core`
tem pré-somada nos `OFS_*` — o original a resolve em tempo de execução. Terceira
vez que os dois oráculos se encontram no mesmo lugar por caminhos diferentes,
depois da `OFS_TEAM_BARS` acima e da tabela de offsets que `0x0040cbc8` varre a
partir de `0x004231a0`, exatamente onde a
[WTE-TASK-06](../../../docs/tasks/06-mapa-de-offsets.md) a registrou.

**O `95` não é o número de times, é o índice do modelo de Master League.** O
item 95 do combo é `95 Master L. `, o time-modelo que a ML usa ao criar clube;
ele não tem barra, bandeira, uniforme nem nome editável, e é por isso que
`nacional` desliga tudo isso. Os times de verdade são 0…94.

**A largura da barra é `11*v + 9`, não uma escala.** Vindo do disassembly como
`v*11 + 9` (`lea` duplo mais `add`), e não de proporção sobre um máximo: o
valor 0 dá 9 px, que é a barra vazia desenhada no DFM.
