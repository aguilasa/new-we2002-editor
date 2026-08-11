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

**Evidência:** disassembly lido

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

**Veredito `aberto`: a spec está medida, o Pascal não está escrito.** Falta
resolver três auxiliares que este handler chama e que não são dele:

| Endereço | O que faz | De quem é |
|---|---|---|
| `0x0040b2d8` | preenche `lista_jugadores_1` com os 23 nomes | próxima passagem da WTE-TASK-25 |
| `0x00405270`, `0x004056c8` | desenham bandeira e uniforme 2D | [WTE-TASK-32](../../../docs/tasks/32-camisa-e-bandeira-2d.md) |
| `0x0040b0b4`, `0x0040b188` | ainda sem leitura | próxima passagem |

Escrever metade do corpo agora deixaria o `check_fase2.py` contando o handler
como "com corpo escrito" — o índice afirmaria pronto o que está pela metade, e
é justamente esse tipo de mentira de índice que o projeto já pagou duas vezes.

**O `95` não é o número de times, é o índice do modelo de Master League.** O
item 95 do combo é `95 Master L. `, o time-modelo que a ML usa ao criar clube;
ele não tem barra, bandeira, uniforme nem nome editável, e é por isso que
`nacional` desliga tudo isso. Os times de verdade são 0…94.

**A largura da barra é `11*v + 9`, não uma escala.** Vindo do disassembly como
`v*11 + 9` (`lea` duplo mais `add`), e não de proporção sobre um máximo: o
valor 0 dá 9 px, que é a barra vazia desenhada no DFM.
