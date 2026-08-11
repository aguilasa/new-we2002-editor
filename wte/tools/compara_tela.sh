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

export DISPLAY=:99          # fixado aqui dentro, nunca herdado -- regra do repo
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
# divergem por decisao, nao por defeito: sao da WTE-TASK-32. Quem os exclui e o
# `compara_tela.py`, por nome de controle, e nao o corte por altura -- foi o
# corte por altura que escondeu os dorsais.
REC_W=520
REC_H=240

# O time nacional de prova e o time-modelo, para o modo `--habilitacao`. O
# `nacional` do handler e `indice < 95`, entao 2, 9 e 63 sao TODOS nacionais:
# a metade desabilitada da tela nunca aparecia nas tres medidas de barra.
IDX_NACIONAL=2
IDX_MODELO=95

[ $# -ge 1 ] || { echo "uso: $0 <indice> [<indice> ...] | $0 --habilitacao" >&2
                  exit 1; }
MODO=barras
if [ "$1" = "--habilitacao" ]; then
  [ $# -eq 1 ] || { echo "ERRO: --habilitacao nao aceita indice -- o par e" \
                         "$IDX_NACIONAL e $IDX_MODELO, fixados aqui" >&2; exit 1; }
  MODO=habilitacao
  set -- "$IDX_NACIONAL" "$IDX_MODELO"
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
  import -window root "$SAIDA/raw-port.png"
  recorta "$SAIDA/raw-port.png" "$destino" "$X" "$Y" "$REC_W" "$REC_H"
  recorta "$SAIDA/raw-port.png" "${destino%.png}-cheia.png" \
          "$X" "$Y" "$WIDTH" "$HEIGHT"
  # A confirmacao que faltava: quantas vezes o handler disparou de verdade.
  local disparos
  disparos=$(grep -c 'MainForm.lista_equiposChange' "$TRACE" 2>/dev/null || echo 0)
  limpa
  if [ "$disparos" -ne $((indice + 1)) ]; then
    echo "ERRO: o port disparou lista_equiposChange $disparos vez(es) e o" >&2
    echo "      roteiro pediu $((indice + 1)). O indice dos dois lados nao e o" >&2
    echo "      mesmo, e comparar assim produz divergencia falsa." >&2
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
