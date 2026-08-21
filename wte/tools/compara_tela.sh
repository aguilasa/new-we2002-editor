#!/usr/bin/env bash
# compara_tela.sh -- dirige os dois lados ate o MESMO time e compara a tela.
#
#   bash wte/tools/compara_tela.sh <indice> [<indice> ...]
#   bash wte/tools/compara_tela.sh --habilitacao
#
#     WTE_TELA_IMAGEM=<rom>   padrao: roms/japanese-shift-jis.bin
#     WTE_TELA_SAIDA=<dir>    onde ficam as capturas (padrao: work/tela)
#
# O dump da camada de dados e gerado uma vez, da mesma imagem, e confrontado
# com a largura invertida de cada barra. E a terceira ponta da conferencia: sem
# ela, os dois lados poderiam estar desenhando o mesmo pixel do time errado.
#
# Da WTE-TASK-25, criterio "tela conferida contra o original para pelo menos 3
# times distintos". Quem MEDE e o `compara_tela.py` ao lado; este script leva
# os dois lados ao mesmo estado, que e a parte que erra.
#
# ## Por que o indice e confirmado, e nao suposto
#
# Na setima passagem eu comparei tres times e so um valia: os dois lados
# receberam numero diferente de `Down` -- o port foi parar em `78 Ajax` -- e as
# outras duas medidas eram lixo com cara de divergencia do port. Aqui:
#
#  1. cada time e uma execucao NOVA dos dois lados, sem acumular tecla;
#  2. o `Down` vai um a um, com espera, em vez de rajada;
#  3. do lado do port o numero de disparos do `lista_equiposChange` sai do
#     `trace.log` e tem de bater com o pedido. Do lado do oraculo nao ha trace,
#     e por isso o roteiro parte sempre do combo recem-focado.
#
# ## As guardas
#
# Herdadas do `golden_check.sh`, mais uma que ele nao tem: **processo** vivo,
# nao so janela. Tres vezes na sessao de 2026-08-11 sobrou um `wte` ou um
# `we-team-editor.exe` no `:99` depois de uma medicao de apoio, e processo
# solto dirige a janela errada do mesmo jeito que janela solta.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

export DISPLAY="${WTE_DISPLAY:-:98}"   # fixado aqui, nunca herdado -- regra do repo
IMAGEM="${WTE_TELA_IMAGEM:-$RAIZ/roms/japanese-shift-jis.bin}"
SAIDA="${WTE_TELA_SAIDA:-$RAIZ/work/tela}"
WINE_BIN="${WINE_BIN:-/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin}"
PREFIX="$RAIZ/work/wineprefix-wte"
WORK="$RAIZ/work"
BIN="$WTE/build/wte"
TRACE="$WTE/re/trace.log"

# ## Os dois recortes, e por que sao dois
#
# **`topo`** -- 520x240 do canto superior esquerdo. E o recorte MEDIDO: e onde
# moram as cinco barras, cuja largura e `11*v + 9` e portanto numero do jogo
# virado pixel. Ele nao cresce, e isso e deliberado: `banderita1` (y 339) e
# laranja e entraria na deteccao de banda, que ja achou barra a mais duas vezes.
#
# **`cheia`** -- a janela inteira. E o recorte da MONTAGEM, para o olho humano,
# e e o que o criterio da WTE-TASK-25 pede alem das barras: os 23 numeros de
# camisa (`dorsal1..23`, y 432) e a `lista_jugadores_1` (y 392) caem fora dos
# 240 px de altura do `topo`, e ficaram tres passagens sem ser olhados. Ele
# tambem e a entrada do modo `--habilitacao`.
#
# Bandeira e uniforme 2D (x 232..312, y 36..168) estao dentro dos dois e
# divergem por decisao, nao por defeito: sao da WTE-TASK-29. Quem os exclui e o
# `compara_tela.py`, por nome de controle, e nao o corte por altura -- foi o
# corte por altura que escondeu os dorsais.
REC_W=520
REC_H=240

# O time nacional de prova e o time-modelo, para o modo `--habilitacao`. O
# `nacional` do handler e `indice < 95`, entao 2, 9 e 63 sao TODOS nacionais:
# a metade desabilitada da tela nunca aparecia nas tres medidas de barra.
IDX_NACIONAL=2
IDX_MODELO=95

# ## O modo `--edicao`, da WTE-TASK-26
#
# Os dois modos acima carregam e comparam. Este **edita** e compara: e a regua
# de PIXEL do grupo de edicao, e a unica que essa task tem -- a de byte depende
# das gravacoes da WTE-TASK-27, e a divisao esta escrita no enunciado das duas.
#
# A barra e o alvo certo outra vez, e agora por um motivo a mais: a largura e
# `11*v + 9` na carga E na edicao (a mesma sequencia de bytes nos dois lugares
# do binario, conferido pelo `check_barras.py`), entao uma barra editada para
# `v` fica exatamente do tamanho de uma barra carregada com `v`. O que se mede
# depois do clique e o valor do jogo, nao um efeito visual.
#
# ### As coordenadas, e por que estas
#
# Medidas no `:99`, nos dois lados, em 2026-08-12:
#
# | controle | coordenada | como se sabe |
# |---|---|---|
# | `sel_barra1` ("Defesa") | (30, 112) | dispara `sel_barraClick` uma vez no trace do port |
# | trilha da `track_barra` | (190, 200) | dispara `track_barraChange` nos dois; a barra muda de 53 para 75 px |
#
# O `y = 200` nao e chute: a `track_barra` do oraculo aceita clique em
# y 190..200 e a do port em y 199..207 -- o gtk2 desenha uma borda de 6 px que
# o Wine nao desenha (e o mesmo `(6, 6)` que o `calibra()` do
# `compara_tela.py` mede), e a diferenca cresce ate a base da janela. **200 e a
# interseccao**, e foi verificada nos dois.
#
# ### O passo do clique bate nos dois widgetsets, e isso precisava ser medido
#
# Clique na trilha nao arrasta o cursor: pagina. O `PageSize` do comctl32 sob
# Wine e o do `TTrackBar` da LCL sobre gtk2 sao codigo diferente, e a faixa
# aqui e curta (`Max = 9`): um passo de 2 de um lado e 1 do outro produziria
# divergencia de tela que NAO e do handler. Medido antes de escrever este modo:
# **os dois andam +2 por clique** (4 para 6 para 8, largura 53, 75, 97).
IDX_EDICAO=2
SEL_BARRA1_X=30 ; SEL_BARRA1_Y=112
TRILHA_X=190    ; TRILHA_Y=200
# Quantos cliques na trilha. Com o time 2, `bar_defence` vale 4 e cada clique
# soma 2: um clique leva a 6, longe do teto de 9, e portanto longe de medir
# saturacao em vez de passo.
TRILHA_CLIQUES=1

# ## O modo `--nomes`, da WTE-TASK-26
#
# O segundo grupo de edicao a ganhar regua de tela. Ele exercita os TRES
# filtros de tecla dos campos de nome e o encadeamento de foco entre eles, e
# faz isso com uma sequencia so.
#
# ### Por que este texto, e nao outro
#
# `A B-C.DEFG`. Os tres filtros nao sao iguais, e o texto foi escolhido para
# que a diferenca APARECA na tela:
#
# | campo | aceita | do texto sobra | e o campo corta em |
# |---|---|---|---|
# | `edit_nombre1` | ` `, `.`, #8, `0-9`, `A-Z`, `a-z` | `A BC.DEFG` | `A BC.D` (6) |
# | `edit_nombre2` | idem | `A BC.DEFG` | `A BC.DE` (7) |
# | `edit_nombre3` | #8 e alfanumerico -- **nem espaco nem ponto** | `ABCDEFG` | `ABC` (3) |
#
# Um texto so de letras passaria identico pelos tres e a regua nao mediria
# filtro nenhum: mediria digitacao. O `-` e recusado pelos tres, o `.` e o
# espaco separam o terceiro dos outros dois.
#
# ### O texto anterior media tinta, nao truncamento (CORR-WTE-061)
#
# Ate 2026-08-18 este texto era `AB-C.D E`, e o corte do `edit_nombre1` caia
# EXATAMENTE num espaco: `ABC.D ` e `ABC.D` sao o mesmo desenho. A regua leu
# **cinco** onde o limite e **seis**, e esse 5 virou literal no port e numero
# em tres documentos. O texto de agora poe glifo visivel nos tres cortes -- e
# eles caem em posicoes diferentes, entao um campo com o limite do outro
# tambem aparece.
#
# O limite dos dois primeiros e POR TIME, medido do lote de `0x004231a0`; os
# valores acima sao os do `IDX_EDICAO`. Ver `wte/re/truncamento.md`.
#
# ### O `Return` faz parte do teste
#
# `edit_nombre1KeyPress` e `edit_nombre2KeyPress` movem o foco para o campo
# seguinte quando a tecla e #13; o terceiro nao encadeia. A sequencia digita nos
# tres SEM clicar entre eles: se o encadeamento nao funcionar, os campos 2 e 3
# ficam vazios e a comparacao acusa.
NOMES_TEXTO='A B-C.DEFG'
# Coordenadas absolutas, derivadas do `.lfm` somando `Left`/`Top` pela cadeia de
# pais -- o formulario raiz fora, porque o `Left`/`Top` dele e posicao de tela.
# Os dois lados usam as MESMAS: desde que a WTE-TASK-26 tirou o
# `Application.Scaled`, a janela do port tem o tamanho de projeto, igual a do
# oraculo sob Wine.
NOMBRE1_X=422  ; NOMBRE1_Y=74

[ $# -ge 1 ] || { echo "uso: $0 <indice> [<indice> ...] | $0 --habilitacao" \
                       "| $0 --edicao | $0 --nomes | $0 --cor | $0 --grade" >&2
                  exit 1; }
MODO=barras
if [ "$1" = "--habilitacao" ]; then
  [ $# -eq 1 ] || { echo "ERRO: --habilitacao nao aceita indice -- o par e" \
                         "$IDX_NACIONAL e $IDX_MODELO, fixados aqui" >&2; exit 1; }
  MODO=habilitacao
  set -- "$IDX_NACIONAL" "$IDX_MODELO"
elif [ "$1" = "--edicao" ]; then
  [ $# -eq 1 ] || { echo "ERRO: --edicao nao aceita indice -- o time e o" \
                         "$IDX_EDICAO, fixado aqui" >&2; exit 1; }
  MODO=edicao
  set -- "$IDX_EDICAO"
elif [ "$1" = "--nomes" ]; then
  [ $# -eq 1 ] || { echo "ERRO: --nomes nao aceita indice -- o time e o" \
                         "$IDX_EDICAO, fixado aqui" >&2; exit 1; }
  MODO=nomes
  set -- "$IDX_EDICAO"
elif [ "$1" = "--grade" ]; then
  # A GRADE DE CORES da WTE-TASK-29 -- o criterio que o `--cor` deixa aberto.
  #
  # O `--cor` mede a paleta COMO ELA VEIO DA IMAGEM: prova que os dois lados
  # leem a mesma fonte, e nao prova nada sobre a aritmetica de cor, porque
  # nenhuma cor foi calculada. Este modo edita antes de medir.
  #
  # ## Por que os TRES botoes, e nao as barras
  #
  # Clicar na trilha de um `TScrollBar` pagina por `LargeChange`, e o passo do
  # comctl32 sob Wine nao e o do gtk2 -- o `--edicao` teve de MEDIR que os dois
  # andavam +2 antes de poder comparar. Os tres botoes nao tem esse problema:
  # cada clique e uma operacao inteira e deterministica, e as tres sao
  # exatamente a aritmetica que a secao 9 do plano poe em risco.
  #
  # A sequencia percorre a faixa cheia (1..16, o default do `FormCreate`):
  #
  #   3x oscurecer  -- tres degraus para baixo em cada canal, com o piso
  #                    mordendo em quem ja estava em zero
  #   1x aclarar    -- um degrau de volta, com o teto de 0xF8 mordendo em quem
  #                    estava saturado. Os dois limites sao assimetricos, e
  #                    3 - 1 <> 2 em toda cor que encostou num deles
  #   1x gradiente  -- interpola as 14 do miolo entre a 1 e a 16, que e onde o
  #                    truncamento do acumulador `Single` aparece
  MODO=grade
  shift
  [ $# -ge 1 ] || set -- 2 9 63
elif [ "$1" = "--cor" ]; then
  # O `--cor` ACEITA indice, ao contrario dos tres de cima: a paleta e por
  # time, e uma so nao provaria que a fonte esta certa -- provaria que ela e
  # constante. Sem argumento vai nos mesmos tres da conferencia de tela.
  MODO=cor
  shift
  [ $# -ge 1 ] || set -- 2 9 63
fi
[ -f "$IMAGEM" ] || { echo "ERRO: $IMAGEM nao existe" >&2; exit 1; }
[ -x "$BIN" ] || { echo "ERRO: $BIN -- rode lazbuild antes" >&2; exit 1; }
[ -x "$WINE_BIN/wine" ] || { echo "ERRO: loader Wine 32-bit ausente" >&2; exit 1; }

# ------------------------------------------------------------------ guardas --
sobra_processo() {
  pgrep -f "$WTE/build/wte" >/dev/null && return 0
  pgrep -f "we-team-editor.exe" >/dev/null && return 0
  return 1
}
if sobra_processo; then
  echo "ERRO: ja ha um wte ou we-team-editor.exe vivo. Feche antes -- os dois" >&2
  echo "      lados acham janela por nome, e o script dirigiria a errada." >&2
  pgrep -af "build/wte|we-team-editor.exe" >&2 || true
  exit 3
fi

mkdir -p "$SAIDA"

# O dump da camada de dados, uma vez por rodada. Sem `fpc` ele nao existe e a
# conferencia contra o dado e PULADA, dizendo isso -- nunca em silencio.
DUMP=""
if command -v fpc >/dev/null; then
  cp "$IMAGEM" "$WORK/tela-dump.bin"
  mkdir -p "$WORK/tela-dump-units"
  if fpc -MObjFPC -Sh -Fu"$WTE/src" -FE"$WORK/tela-dump-units" \
         -FU"$WORK/tela-dump-units" "$WTE/tests/dump_estado.pas" \
         >/dev/null 2>&1; then
    "$WORK/tela-dump-units/dump_estado" "$WORK/tela-dump.bin" \
        > "$SAIDA/estado.txt" 2>/dev/null && DUMP="$SAIDA/estado.txt"
  fi
fi
[ -n "$DUMP" ] || echo ">> AVISO: sem dump da camada de dados -- a tela sera" \
                       "comparada so contra o oraculo"
limpa() {
  pkill -9 -f "$WTE/build/wte" 2>/dev/null || true
  pkill -9 -f "we-team-editor.exe" 2>/dev/null || true
  env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
  sleep 1
}
trap limpa EXIT

geometria() {
  xdotool getwindowgeometry --shell "$1" | grep -E '^(X|Y|WIDTH|HEIGHT)='
}

# recorta <origem.png> <destino.png> <x> <y> <w> <h>
recorta() {
  python3 - "$@" <<'FIM'
import sys
from PIL import Image
src, dst, x, y, w, h = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
Image.open(src).convert("RGB").crop((x, y, x + w, y + h)).save(dst)
FIM
}

descidas() {          # $1 = janela, $2 = quantas
  local i
  for ((i = 0; i < $2; i++)); do
    xdotool key --clearmodifiers --delay 40 Down
  done
}

# edita_barra -- a MESMA sequencia de cliques nos dois lados, e e por isso que
# ela mora aqui e nao dentro de cada `captura_*`. Duas entradas diferentes
# deixariam de ser a mesma entrada, que e a condicao de a comparacao valer.
# Espera `X` e `Y` ja carregados com a origem da janela alvo.
edita_barra() {
  local i
  xdotool mousemove $((X + SEL_BARRA1_X)) $((Y + SEL_BARRA1_Y)) click 1
  sleep 1
  for ((i = 0; i < TRILHA_CLIQUES; i++)); do
    xdotool mousemove $((X + TRILHA_X)) $((Y + TRILHA_Y)) click 1
    sleep 1
  done
  sleep 1
}

# edita_nomes -- a MESMA sequencia nos dois lados, pelo mesmo motivo do
# `edita_barra`. Espera `X` e `Y` ja carregados com a origem da janela alvo.
#
# Limpa com `End`/`shift+Home`/`BackSpace` e NUNCA com `ctrl+a`: num `TEdit` do
# Win32 o `ctrl+a` nao seleciona tudo, e os dois lados receberiam textos
# diferentes -- o diff sairia divergencia do port sem ser.
edita_nomes() {
  xdotool mousemove $((X + NOMBRE1_X)) $((Y + NOMBRE1_Y)) click 1
  sleep 1
  local i
  for ((i = 0; i < 3; i++)); do
    xdotool key --clearmodifiers End;       sleep 0.3
    xdotool key --clearmodifiers shift+Home; sleep 0.3
    xdotool key --clearmodifiers BackSpace;  sleep 0.3
    xdotool type --delay 60 "$NOMES_TEXTO";  sleep 1
    # O `Return` encadeia o foco para o campo seguinte. Depois do terceiro nao
    # ha para onde ir, e manda-lo assim mesmo nao faria mal -- mas mandaria uma
    # tecla a mais para a contagem de disparos, e a contagem e guarda.
    if [ $i -lt 2 ]; then
      xdotool key --clearmodifiers Return; sleep 1
    fi
  done
  sleep 1
}

# Os tres botoes do `ficha_color`, no centro de cada um. As coordenadas saem do
# `.lfm` (`Left`/`Top`/`Width`/`Height`) e sao relativas a janela do MODAL --
# nao ha window manager no :98, entao a origem da janela e a origem do cliente.
OSCURECER_X=308 ; OSCURECER_Y=164
ACLARAR_X=404   ; ACLARAR_Y=164
GRADIENTE_X=356 ; GRADIENTE_Y=164
OSCURECER_N=3
ACLARAR_N=1

# edita_cor -- a MESMA sequencia de cliques nos dois lados, pelo mesmo motivo do
# `edita_barra`. Espera `X` e `Y` ja carregados com a origem do MODAL.
edita_cor() {
  local i
  for ((i = 0; i < OSCURECER_N; i++)); do
    xdotool mousemove $((X + OSCURECER_X)) $((Y + OSCURECER_Y)) click 1
    sleep 1
  done
  for ((i = 0; i < ACLARAR_N; i++)); do
    xdotool mousemove $((X + ACLARAR_X)) $((Y + ACLARAR_Y)) click 1
    sleep 1
  done
  xdotool mousemove $((X + GRADIENTE_X)) $((Y + GRADIENTE_Y)) click 1
  sleep 2
}

# Abre o editor de cor e captura A JANELA DELE, nos dois lados.
#
# `X`/`Y` ja tem a origem da janela principal. O `colorear` fica em (224,184) no
# `.lfm`, 97x25, entao o centro e (272,196).
#
# **A janela capturada e a do editor, e nao a principal.** Comparar a principal
# aqui nao mediria nada: o que muda sao as 16 amostras, que estao no modal. O
# titulo dos dois lados difere -- `Cor  ` no oraculo e `Cor   [Lazarus]` no port
# --, e e de proposito: titulo igual faria o harness dirigir o lado errado, que
# e a armadilha 6 do `progresso.md`.
abre_editor_de_cor() {
  local destino="$1" w
  # A janela principal, guardada ANTES de o modal cobrir a tela -- o modo
  # `--grade` recorta os tres `TImage` dela, e o `X`/`Y` e sobrescrito abaixo.
  MAIN_X=$X ; MAIN_Y=$Y ; MAIN_W=$WIDTH ; MAIN_H=$HEIGHT
  xdotool mousemove $((X + 272)) $((Y + 196)) click 1
  sleep 4
  w=$(xdotool search --name '^Cor' | tail -1)
  [ -n "$w" ] || { echo "ERRO: o editor de cor nao apareceu" >&2; return 4; }
  eval "$(geometria "$w")"
  import -window root "$SAIDA/raw-cor.png"
  recorta "$SAIDA/raw-cor.png" "$destino" "$X" "$Y" "$WIDTH" "$HEIGHT"
  [ "$MODO" = grade ] || return 0

  # ## As duas capturas do `--grade`, e por que uma so nao serve
  #
  # A de cima e o ANTES. Ela nao entra no veredito de igualdade -- entra na
  # guarda: se a cor depois do clique for igual a de antes, os cliques nao
  # chegaram, e "os dois lados concordam" seria concordancia em nao fazer nada.
  # E a mesma guarda que o `--edicao` faz contando disparos no trace, com a
  # diferenca de que aqui ela vale para os DOIS lados, e do oraculo nao ha
  # trace.
  #
  # A janela principal cabe na mesma captura de tela: o `ficha_color` esta em
  # `Top = 281` no `.dfm` e tem 225 px de altura, e os tres `TImage` do render
  # ficam entre y 36 e y 168 -- o modal nao os cobre. Isso e CONFERIDO abaixo,
  # e nao suposto: se um dia as duas janelas se sobrepuserem, o recorte pegaria
  # o modal no lugar da bandeira e passaria por verde.
  recorta "$SAIDA/raw-cor.png" "${destino%.png}-cheia.png" \
          "$MAIN_X" "$MAIN_Y" "$MAIN_W" "$MAIN_H"
  if [ "$Y" -lt $((MAIN_Y + 200)) ]; then
    echo "ERRO: o modal ($Y) sobe acima de y=$((MAIN_Y + 200)) e cobre o" >&2
    echo "      render 2D da janela principal -- o recorte mediria o modal." >&2
    return 4
  fi

  edita_cor
  import -window root "$SAIDA/raw-cor.png"
  recorta "$SAIDA/raw-cor.png" "${destino%.png}-depois.png" \
          "$X" "$Y" "$WIDTH" "$HEIGHT"
  recorta "$SAIDA/raw-cor.png" "${destino%.png}-depois-cheia.png" \
          "$MAIN_X" "$MAIN_Y" "$MAIN_W" "$MAIN_H"
}

# ------------------------------------------------------------------ oraculo --
captura_oraculo() {
  local indice="$1" destino="$2"
  cp "$IMAGEM" "$WORK/tela-oraculo.bin"
  ln -sfn "$WORK" "$PREFIX/dosdevices/e:"
  ( cd "$RAIZ/we-team-editor" \
    && env WINEPREFIX="$PREFIX" WINEARCH=win32 WINEDEBUG=-all \
         setsid "$WINE_BIN/wine" we-team-editor.exe >/dev/null 2>&1 & )
  sleep 8
  local w
  w=$(xdotool search --name '^Abre$' | head -1)
  [ -n "$w" ] || { echo "ERRO: o dialogo Abre do oraculo nao apareceu" >&2; return 4; }
  eval "$(geometria "$w")"
  xdotool mousemove $((X + 315)) $((Y + 304)) click 1; sleep 1
  xdotool type --delay 60 'E:\tela-oraculo.bin'; sleep 1
  xdotool key Return; sleep 4
  w=$(xdotool search --name '^Cuidado$' | head -1)
  if [ -n "$w" ]; then eval "$(geometria "$w")"
    xdotool mousemove $((X + 222)) $((Y + 148)) click 1; sleep 3; fi
  w=$(xdotool search --name '^Sobre\.\.\.$' | head -1)
  if [ -n "$w" ]; then eval "$(geometria "$w")"
    xdotool mousemove $((X + 110)) $((Y + 243)) click 1; sleep 3; fi
  w=$(xdotool search --name 'W11 Team Editor PT by chagas_michel' | tail -1)
  [ -n "$w" ] || { echo "ERRO: janela principal do oraculo nao achada" >&2; return 4; }
  eval "$(geometria "$w")"
  xdotool mousemove $((X + 50)) $((Y + 46)) click 1; sleep 1
  descidas "$w" $((indice + 1)); sleep 3
  [ "$MODO" = edicao ] && edita_barra
  [ "$MODO" = nomes ] && edita_nomes
  if [ "$MODO" = cor ] || [ "$MODO" = grade ]; then
    abre_editor_de_cor "$destino" || { limpa; return 4; }
    limpa
    return 0
  fi
  import -window root "$SAIDA/raw-oraculo.png"
  recorta "$SAIDA/raw-oraculo.png" "$destino" "$X" "$Y" "$REC_W" "$REC_H"
  recorta "$SAIDA/raw-oraculo.png" "${destino%.png}-cheia.png" \
          "$X" "$Y" "$WIDTH" "$HEIGHT"
  limpa
}

# --------------------------------------------------------------------- port --
captura_port() {
  local indice="$1" destino="$2"
  cp "$IMAGEM" "$WORK/tela-port.bin"
  rm -f "$TRACE"
  "$BIN" "$WORK/tela-port.bin" >/dev/null 2>&1 &
  sleep 4
  local w
  w=$(xdotool search --name 'Lazarus' | head -1)
  [ -n "$w" ] || { echo "ERRO: janela do port nao achada" >&2; return 4; }
  eval "$(geometria "$w")"
  # Sem window manager o gtk2 nunca considera a janela ativa sozinho, e sem
  # foco nao ha tecla. `windowfocus` (XSetInputFocus) resolve; o
  # `windowactivate`, que precisa de gerenciador, nao.
  xdotool windowfocus "$w"; sleep 1
  xdotool mousemove $((X + 50)) $((Y + 46)) click 1; sleep 1
  descidas "$w" $((indice + 1)); sleep 2
  [ "$MODO" = edicao ] && edita_barra
  [ "$MODO" = nomes ] && edita_nomes
  if [ "$MODO" = cor ] || [ "$MODO" = grade ]; then
    abre_editor_de_cor "$destino" || { limpa; return 4; }
    # O trace confirma que os cliques VIRARAM handler, e nao so pixel. Do lado
    # do oraculo nao ha trace, e por isso a guarda de mudanca de cor existe
    # tambem -- as duas medem coisas diferentes.
    if [ "$MODO" = grade ]; then
      local esc cla gra
      esc=$(grep -c 'ficha_color.oscurecerClick' "$TRACE" 2>/dev/null || echo 0)
      cla=$(grep -c 'ficha_color.aclararClick' "$TRACE" 2>/dev/null || echo 0)
      gra=$(grep -c 'ficha_color.gradienteClick' "$TRACE" 2>/dev/null || echo 0)
      limpa
      if [ "$esc" -ne "$OSCURECER_N" ] || [ "$cla" -ne "$ACLARAR_N" ] \
         || [ "$gra" -ne 1 ]; then
        echo "ERRO: o port disparou oscurecer/aclarar/gradiente" \
             "$esc/$cla/$gra, esperava $OSCURECER_N/$ACLARAR_N/1 --" >&2
        echo "      os cliques nao chegaram nos botoes." >&2
        return 5
      fi
      return 0
    fi
    limpa
    return 0
  fi
  import -window root "$SAIDA/raw-port.png"
  recorta "$SAIDA/raw-port.png" "$destino" "$X" "$Y" "$REC_W" "$REC_H"
  recorta "$SAIDA/raw-port.png" "${destino%.png}-cheia.png" \
          "$X" "$Y" "$WIDTH" "$HEIGHT"
  # A confirmacao que faltava: quantas vezes o handler disparou de verdade.
  local disparos sel track
  disparos=$(grep -c 'MainForm.lista_equiposChange' "$TRACE" 2>/dev/null || echo 0)
  sel=$(grep -c 'MainForm.sel_barraClick' "$TRACE" 2>/dev/null || echo 0)
  track=$(grep -c 'MainForm.track_barraChange' "$TRACE" 2>/dev/null || echo 0)
  # A evidencia de que o modo exercitou o que a tabela do `check_edicao.py`
  # diz que ele exercita. Sem isto a tabela e palavra: dizer que um modo cobre
  # um handler nao faz o handler disparar, e foi assim que o `dorsalMouseDown`
  # entrou atribuido a um modo que nao clica camisa nenhuma.
  if [ "$MODO" = edicao ] || [ "$MODO" = nomes ]; then
    local ev="$WTE/re/edicao-tela.tsv"
    grep -oE '== [A-Za-z_0-9]+\.[A-Za-z_0-9]+' "$TRACE" 2>/dev/null \
      | sed 's/^== //' | sort | uniq -c \
      | awk -v m="$MODO" '{print m"\t"$2"\t"$1}' > "$ev.$MODO"
    cat "$WTE"/re/edicao-tela.tsv.* 2>/dev/null \
      | sort -u > "$ev.novo" && mv "$ev.novo" "$ev"
    # Os parciais por modo ficam em `.tsv.<modo>` e SAO versionados junto: sem
    # eles, rodar um modo so apagaria a evidencia do outro.
  fi
  local n1 n2 n3
  n1=$(grep -c 'MainForm.edit_nombre1KeyPress' "$TRACE" 2>/dev/null || echo 0)
  n2=$(grep -c 'MainForm.edit_nombre2KeyPress' "$TRACE" 2>/dev/null || echo 0)
  n3=$(grep -c 'MainForm.edit_nombre3KeyPress' "$TRACE" 2>/dev/null || echo 0)
  limpa
  if [ "$disparos" -ne $((indice + 1)) ]; then
    echo "ERRO: o port disparou lista_equiposChange $disparos vez(es) e o" >&2
    echo "      roteiro pediu $((indice + 1)). O indice dos dois lados nao e o" >&2
    echo "      mesmo, e comparar assim produz divergencia falsa." >&2
    return 5
  fi
  if [ "$MODO" = nomes ]; then
    # A conta e MEDIDA e sai do texto, nao de literal: na LCL o `#8` do
    # `BackSpace` e o `#13` do `Return` chegam ao `OnKeyPress`, entao cada
    # campo conta 1 (BackSpace) + ${#NOMES_TEXTO} + 1 (Return), e o terceiro
    # nao leva Return. Se um widgetset deixar de entregar uma dessas duas, a
    # conta muda e a guarda avisa -- que e o ponto: essa entrega e diferenca de
    # plataforma, e diferenca de plataforma calada e o que este projeto mais
    # paga.
    #
    # Derivar em vez de fixar tem motivo proprio: quando a CORR-WTE-061 trocou
    # o texto (o corte do campo 1 caia num espaco e a regua lia um caractere a
    # menos), os literais 10/10/9 derrubaram a corrida por uma razao que nao
    # tinha nada a ver com o que estava sendo medido.
    esperado=$(( 1 + ${#NOMES_TEXTO} + 1 ))
    if [ "$n1" -ne "$esperado" ] || [ "$n2" -ne "$esperado" ] \
       || [ "$n3" -ne $(( esperado - 1 )) ]; then
      echo "ERRO: os filtros de nome dispararam $n1/$n2/$n3, esperava" \
           "$esperado/$esperado/$(( esperado - 1 ))." >&2
      echo '      Se o primeiro estiver certo e os outros zerados, o Return' >&2
      echo "      nao encadeou o foco e so o campo 1 foi digitado." >&2
      return 5
    fi
    return 0
  fi
  [ "$MODO" = edicao ] || return 0
  # Do lado do port da para exigir que os DOIS handlers de edicao tenham
  # disparado -- e sem isto uma tela que nao mudou nada seria lida como
  # "os dois lados concordam". E o par da WTE-TASK-20: concordam, E fizeram
  # alguma coisa.
  if [ "$sel" -ne 1 ]; then
    echo "ERRO: sel_barraClick disparou $sel vez(es), esperava 1 -- o clique" >&2
    echo "      em $SEL_BARRA1_X,$SEL_BARRA1_Y nao chegou no radio." >&2
    return 5
  fi
  # A carga tambem dispara `track_barraChange`, porque `Position :=` dispara
  # `OnChange` na LCL -- medido, e por isso a conta e "uma por troca de time,
  # uma pelo sel_barra, mais os cliques na trilha".
  if [ "$track" -lt $((indice + 2 + TRILHA_CLIQUES)) ]; then
    echo "ERRO: track_barraChange disparou $track vez(es), esperava ao menos" >&2
    echo "      $((indice + 2 + TRILHA_CLIQUES)) -- o clique em $TRILHA_X,$TRILHA_Y nao chegou" >&2
    echo "      na trilha, e a barra nao foi editada em lado nenhum." >&2
    return 5
  fi
}

# --------------------------------------------------------------------- laco --
rc=0
for indice in "$@"; do
  echo ">> time $indice"
  captura_oraculo "$indice" "$SAIDA/time-$indice-oraculo.png"
  captura_port    "$indice" "$SAIDA/time-$indice-port.png"
  [ "$MODO" = habilitacao ] && continue
  extra=()
  [ -n "${DUMP:-}" ] && extra=(--dump "$DUMP")
  if [ "$MODO" = edicao ]; then
    # O valor esperado NAO e literal: sai do dump da camada de dados mais o
    # passo medido do clique. Assim o unico numero escrito a mao aqui e o
    # PASSO, que e o que se mediu -- trocar o time de prova nao exige reescrever
    # nada, e um dump que mude derruba a conferencia em vez de passar.
    [ -n "${DUMP:-}" ] || { echo "ERRO: --edicao precisa do dump (sem fpc" \
                                 "nao ha o que somar ao passo)" >&2; exit 1; }
    base=$(sed -n "s/^teams\[$indice\]\.bar_defence = //p" "$DUMP")
    [ -n "$base" ] || { echo "ERRO: sem bar_defence do time $indice no dump" >&2
                        exit 1; }
    extra+=(--editada "1=$((base + 2 * TRILHA_CLIQUES))")
  fi
  if [ "$MODO" = cor ]; then
    # O veredito da cor nao passa pelas barras nem pela montagem: o que se mede
    # sao as 16 amostras do editor, e elas estao na janela do modal, que e a
    # que a `abre_editor_de_cor` capturou.
    python3 "$AQUI/compara_tela.py" --cor \
        "$SAIDA/time-$indice-oraculo.png" \
        "$SAIDA/time-$indice-port.png" --indice "$indice" || rc=1
    continue
  fi
  if [ "$MODO" = grade ]; then
    python3 "$AQUI/compara_tela.py" --grade --indice "$indice" \
        --antes-oraculo "$SAIDA/time-$indice-oraculo.png" \
        --antes-port    "$SAIDA/time-$indice-port.png" \
        --oraculo       "$SAIDA/time-$indice-oraculo-depois.png" \
        --port          "$SAIDA/time-$indice-port-depois.png" \
        --cheia-antes-oraculo "$SAIDA/time-$indice-oraculo-cheia.png" \
        --cheia-oraculo "$SAIDA/time-$indice-oraculo-depois-cheia.png" \
        --cheia-port    "$SAIDA/time-$indice-port-depois-cheia.png" || rc=1
    continue
  fi
  if [ "$MODO" = nomes ]; then
    # O veredito dos nomes NAO passa pelas barras: o que se mede aqui e o
    # efeito dos tres filtros de tecla, e ele mora nos campos de nome. Rodar o
    # relato das barras aqui daria verde sem olhar para o que a sequencia fez.
    python3 "$AQUI/compara_tela.py" --nomes \
        "$SAIDA/time-$indice-oraculo-cheia.png" \
        "$SAIDA/time-$indice-port-cheia.png" || rc=1
    continue
  fi
  python3 "$AQUI/compara_tela.py" \
      "$SAIDA/time-$indice-oraculo.png" "$SAIDA/time-$indice-port.png" \
      --indice "$indice" --saida "$SAIDA" "${extra[@]}" \
      --cheia-oraculo "$SAIDA/time-$indice-oraculo-cheia.png" \
      --cheia-port    "$SAIDA/time-$indice-port-cheia.png" || rc=1
done

# No modo habilitacao a comparacao e entre os DOIS times, nao entre os dois
# lados de um: o que se mede e qual controle muda de aparencia quando o
# `nacional` vira falso, e se os dois lados mudam o mesmo conjunto.
if [ "$MODO" = habilitacao ]; then
  python3 "$AQUI/compara_tela.py" --habilitacao \
      "$SAIDA/time-$IDX_NACIONAL-oraculo-cheia.png" \
      "$SAIDA/time-$IDX_NACIONAL-port-cheia.png" \
      "$SAIDA/time-$IDX_MODELO-oraculo-cheia.png" \
      "$SAIDA/time-$IDX_MODELO-port-cheia.png" \
      --saida "$SAIDA" || rc=1
fi
exit $rc
