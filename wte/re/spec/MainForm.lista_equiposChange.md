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

> **Percorreu `disassembly lido` → `nao medido` → `observacao de tela` → de
> volta a `disassembly lido`**, e cada troca foi de natureza. Caiu em
> 2026-08-11 porque `TControl::SetEnabled` tem **zero** `call rel32` na `.text`
> inteira, e a dúzia de `.Enabled :=` desta seção não tinha, aparentemente, de
> onde ter sido lida; subiu para `observacao de tela` no mesmo dia pela
> [CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md), que mediu o **efeito**
> na tela do próprio oráculo, controle a controle.
>
> **A WTE-TASK-26 achou o mecanismo, e ele estava nos bytes o tempo todo:
> `SetEnabled` é virtual.** O original chama `call DWORD PTR [reg+0x64]` depois
> de carregar o VMT em `[obj]` — três vezes dentro deste handler, em
> `0x0040ce9b`, `0x0040cee9` e `0x0040d05c`. Chamada virtual não produz `call
> rel32` para o símbolo, e é exatamente por isso que a contagem dava zero. O
> slot é conferido a cada build pelo
> [`sonda_dorsal.py --check`](../../tools/sonda_dorsal.py), contra o
> `vcl60.bpl`. Ver a seção Notas.

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
A primeira leitura foi essa, e estava errada. A causa está no DFM —
`lista_equipos` nasce **`Enabled = False`**, no original
([`../dfm/MainForm.dfm`](../dfm/MainForm.dfm) linha 715) e portanto no `.lfm`.
Controle desabilitado ignora clique. O `FormShow` do port passou a habilitar os
três combos de time depois de carregar a imagem, e com isso **o port é
dirigível**: `xdotool windowfocus` seguido de clique e `Down` troca de time.
A dropdown continua sem abrir dos **dois** lados — no oráculo também não abre —,
e não precisa: o `Down` sobre o combo focado muda a seleção e dispara o
handler, que é como os roteiros 07/08/11 sempre funcionaram.

**2. `TControl::SetEnabled` nunca é chamado — e a explicação é que ele é
virtual.** O símbolo é importado do `vcl60.bpl` e tem thunk em `0x00422884`; a
`.text` inteira tem **zero** `call rel32` para ele, e a única referência ao
slot `0x0043ec1c` do IAT é o próprio thunk. No mesmo bloco, para comparar:
`SetText` 78 chamadas, `GetText` 24, `SetVisible` 14.

Isso pôs em dúvida, por três passagens, a dúzia de `.Enabled := verdadeiro` da
seção **Saída**: com zero chamadas, ou o original ligava o controle por outro
caminho — RTTI (`Typinfo` **é** importado), o `Parent`, o `TWinControl` —, ou
aquela leitura tinha sido inferida da tela e rotulada como disassembly.

**A resposta é a primeira, e ela estava nos bytes deste handler.** O original
carrega o VMT do controle em `[obj]` e chama o slot `0x64`:

```text
eax := form.campo_do_controle
ecx := [eax]              ' o VMT
dl  := 1                  ' o valor de Enabled
call [ecx + 0x64]         ' TControl.SetEnabled, virtual
```

Três vezes só aqui — `0x0040ce9b` (`edi+0x47c`), `0x0040cee9` (`edi+0x448`) e
`0x0040d05c`, este último sobre o `sel_barra<i>` que o `FindComponent` acabou
de devolver dentro do laço das barras. **Chamada virtual não deixa `call
rel32`**, e é por isso, e só por isso, que a contagem dava zero. A busca
anterior procurava a forma errada.

O slot é medido, não afirmado: o valor exportado de
`@Controls@TControl@SetEnabled$qqro` aparece a `0x64` bytes do início do VMT em
**108 classes** do `vcl60.bpl` — entre elas `TRadioButton`, `TComboBox`,
`TStaticText` e `TImage`, que são as que o `MainForm` instancia —, e o nome de
cada uma sai de `[vmt - 0x2c]`, o mesmo `vmtClassName` que a
[`sonda_dorsal.py`](../../tools/sonda_dorsal.py) já usava. A conferência roda a
cada `make -C wte check` e reprova em qualquer outro slot.

Com isso a seção Saída volta a `disassembly lido`, e a medição de tela da
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) deixa de ser a única
sustentação dos 27 `.Enabled :=` do Pascal — passa a ser a segunda, que é onde
ela vale mais.

**O veredito continua `aberto` pelo que sobrou**, e sobrou comportamento, não
leitura: os dois defeitos que a conferência de tela achou — os `dorsal1..23` um
a menos e o `iguala_nombres` que o port não desabilita — não têm conserto até
agora.

> Esta frase já esteve errada duas vezes. A
> [CORR-WTE-059](../../../docs/tasks/CORR-WTE-059.md) corrigiu a primeira
> ("é o custo de ainda não ter conferido contra a tela", escrita na 6ª
> passagem, desmentida pela seção que a 8ª pôs logo abaixo); a segunda foi
> dizer que o mecanismo de habilitação "continua sem resposta nos bytes", o que
> deixou de valer quando alguém procurou `call [reg+0x64]` em vez de `call
> rel32`. O parágrafo de fecho é lido como veredito: quando a seção acima muda,
> ele muda junto.

## A conferência de tela — os cinco grupos, e os quatro erros que ela achou

Dirigida por [`../../tools/compara_tela.sh`](../../tools/compara_tela.sh), que
leva os dois lados ao mesmo índice e **confirma o do port pelo número de
disparos no `trace.log`** antes de comparar; a medição é do
[`compara_tela.py`](../../tools/compara_tela.py). ROM japonesa.

O critério da [WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md) enumera
cinco grupos de campo. Por três passagens a conferência cobriu **três** — o
recorte comparado tinha 240 px de altura, e a `lista_jugadores_1` está em y 392
e os `dorsal1..23` em y 432. A
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) abriu os outros dois, e cada
um trouxe um erro do port que nada mais pegaria:

| Grupo do critério | Régua | Veredito |
|---|---|---|
| nome do time nos três campos | montagem, olho humano | bate (com a divergência de filtro do `Nome1`, já registrada) |
| as cinco barras de força | pixel, nos três times | **bate**, 15 larguras idênticas |
| os 23 números de camisa | montagem, olho humano | ~~**DIVERGE — o port mostra o byte cru, o original mostra byte + 1**~~ **corrigido em 2026-08-12**, ver abaixo |
| a lista de jogadores | montagem, olho humano | bate |
| o estado de habilitação | pixel, 13 controles | **DIVERGE em um: `iguala_nombres`** |

| Time | Barras (px), oráculo e port | |
|---|---|---|
| 2 (Gales) | `64, 53, 75, 75, 75` | idêntico |
| 9 | `75, 64, 75, 75, 75` | idêntico |
| 63 (Manchester, clube de ML) | `104, 75, 97, 97, 97` | idêntico |

**As quinze larguras batem em pixel.** É a prova que faltava: o port calcula a
barra a partir de `Team.bar_*` da camada de dados e o original a partir de
cinco bytes que ele lê da imagem, e os dois desenham o mesmo pixel — nas duas
famílias, seleção e clube de ML.

**Os textos, na montagem lado a lado:** `Nome2` e `Nome3` idênticos nos três;
`Nome1` mostra `?????` no oráculo e os bytes crus no port, que é a divergência
de filtro já registrada acima.

E a comparação achou **dois erros que nenhum teste pegaria**:

1. **A ordem dos campos de nome não é `names[0..2]`.** O port mostrava `WALES`
   em Nome1 e lixo em Nome2. O certo é `names[1]` no primeiro e `names[0]` no
   segundo.
2. **`Nome3` é `abbreviations[0]`, não `names[2]`.** Este só apareceu no clube
   de ML: para Gales os dois caminhos dão `WAL` e o erro passa; para o
   Manchester `names[2]` é `ARAGON` — cortado em `ARA` pelo campo — contra
   `AGN` na tela do original. **Testar uma família só de time não teria pego.**

Os dois compilavam, não quebravam teste nenhum, e estavam errados.

### Os 23 números de camisa — o port mostra um a menos

Time 63 (Manchester), a faixa dos `dorsal1..23` lida das duas capturas:

```text
oráculo  1  5  6  3  2 11  4 16  7 18 10 24 22 27 14 12  8 25 15 19  9 20 17
port     0  4  5  2  1 10  3 15  6 17  9 23 21 26 13 11  7 24 14 18  8 19 16
```

**Cada número do port é o do oráculo menos um**, e o mesmo desconto aparece na
legenda realçada de `MarcaCamisa(1)` (oráculo `1`, port `0`) e no contador
`SPC/Livre` do canto (oráculo `1`, port `0`).

O byte guardado é 0-based, e quem soma é a tela. O outro editor do mesmo jogo
faz igual, e ali está escrito: `legacy/mfc/edDlg.cpp:2877` monta a legenda com
`_itoa(squad_ml[id-64].str_numeri[0]+1, …)`. O `PreencheCamisas` do port
(`../../src/impl/ep2002_mainform.aux.inc`) chama
`IntToStr(NumeroDaCamisa(indice, slot))` sem o `+ 1`.

~~**Não corrigido aqui**: é defeito de comportamento do Pascal, e esta correção
é do instrumento. Precisa de correção própria, com o gate de tela refeito
depois.~~

**Corrigido em 2026-08-12, pela WTE-TASK-26**, que é a dona do grupo de número.
O `+ 1` entrou no `NumeroDaCamisa`, e antes disso a regra foi conferida nos
**dois oráculos**, por caminhos independentes:

- **`wte.exe`** — a rotina do número de camisa (`0x00403f00`) termina em
  `inc eax` nos **três** ramos: `0x00403f65` (o time 48, que tem caminho
  próprio), `0x00403fae` (clube de ML) e `0x0040403f` (seleção). Não é o efeito
  de um ramo só.
- **`newWe2002`**, que é byte-idêntico ao `ed.exe`: soma 1 ao exibir
  (`src/app/TeamView.cpp:195`) e **subtrai 1 ao gravar** (`:468`), nas três
  famílias — seleção com os cinco bits, `ml_teams` e `ml_default`.

E a correção foi conferida contra o número que esta seção já tinha medido na
tela do oráculo, sem abrir janela: os `raw_numbers` do `ml_teams[0]` que o
`dump_estado.pas` carrega da ROM japonesa, mais 1, dão **exatamente** a linha
`oráculo` acima, nos 23. É a terceira ponta de novo — dado, tela do original, e
agora o Pascal.

**A consequência que sai daqui e vale para o resto do grupo:** o que a imagem
guarda é base zero e o que a tela mostra é base um, então
`dorsalClick`/`scroll_dorsalChange`, ao **gravar**, têm de desfazer a soma.
Está anotado no próprio `NumeroDaCamisa`.

### O estado de habilitação — 13 controles medidos, 1 diverge

A régua não é a cor do cinza: gtk2 e Win32 não desenham o mesmo cinza, e exigir
isso reprovaria o port por ser gtk2. A régua é **mudou ou não mudou**, dentro de
cada lado, entre o time 2 (nacional) e o time **95** (`95 Master L. `, o
time-modelo). O par é esse porque `nacional := ItemIndex < 95` — os três times
da conferência de barras, 2, 9 e 63, são **todos** nacionais, e a metade
desabilitada da tela nunca tinha aparecido em medição nenhuma.

`bash wte/tools/compara_tela.sh --habilitacao`, pixels que mudam por controle:

| Controle | O que a Saída diz | Oráculo | Port | |
|---|---|---|---|---|
| `sel_barra0..4` | `.Enabled := nacional` | 219, 214, 226, 322, 219 | 364, 382, 351, 469, 383 | mudam nos dois |
| `track_barra` | `.Enabled := nacional` | 202 | 1633 | mudam nos dois |
| `boton_barras2iso` | `.Enabled := nacional` | 611 | 368 | mudam nos dois |
| `boton_nombres2iso` | `.Enabled := nacional` | 561 | 211 | mudam nos dois |
| `colorear` | `.Enabled := nacional` | 187 | 50 | mudam nos dois |
| `iguala_nombres` | `.Enabled := nacional` | 518 | **0** | **DIVERGE** |
| `etiq_nombre1..3` | `.Enabled := True` sempre | 0 | 0 | **não** mudam nos dois |
| `bandera` | `.Visible := nacional` | 3840 | 0 | pendente da WTE-TASK-32 |
| `home1`, `home2` | `.Visible := nacional` | 2328, 1012 | 2303, 1032 | mudam nos dois |

Três coisas saem daqui:

1. **A assimetria dos rótulos é real.** `edit_nombreN` segue `nacional` e
   `etiq_nombreN` não — o que a Saída afirma e o que ninguém tinha confrontado.
   Os três medem 0 px de mudança nos dois lados.
2. **O port não desabilita o `iguala_nombres`.** Zero pixel de diferença, com o
   oráculo mudando 518. O `.inc` tem a linha
   (`iguala_nombres.Enabled := nacional`), o `.lfm` tem o controle nascendo
   `Enabled = False` como o DFM, e o vizinho `boton_nombres2iso` — mesmo
   `TSpeedButton`, mesmo `Flat = True`, mesmo grupo — acinzenta certo nos dois
   lados. A causa não foi achada, e **não foi corrigida aqui**, pela mesma razão
   dos dorsais: é defeito de comportamento, e pede correção própria.
3. **Sete controles ficaram fora da régua**, e estão nomeados no
   `compara_tela.py` como `fora_da_faixa`: `boton_mcr`, `boton_dialogo_tex`,
   `grabar_memory`, `grabar_camiseta`, `parriba`, `mostrar_estrategia_1`,
   `mostrar_jugador_1` (mais o `banderita1`). Abaixo de y 240 o port **deriva**
   — o gtk2 desenha cada linha um pouco mais alta, e o erro acumulado chega a
   21 px na faixa dos dorsais —, então o retângulo do DFM deixa de nomear o
   controle certo. Medir ali daria número com cara de veredito. Eles seguem por
   olho humano, na montagem da janela inteira.

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
