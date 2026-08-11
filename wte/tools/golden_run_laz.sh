#!/usr/bin/env bash
# golden_run_laz.sh -- o lado PORT do gate: dirige o app Lazarus por um roteiro,
# sobre a copia que lhe derem.
#
#   bash wte/tools/golden_run_laz.sh <roteiro> <copia.bin> [dir-de-saida]
#
# ## Duas coisas que este lado nao pode, e as duas sao medidas
#
# 1. **Teclado nao chega.** Sem window manager no `:99` o GTK2 nunca considera
#    a janela ativa, e nenhuma tecla e entregue -- nem `xdotool key` depois de
#    `windowfocus`, nem `key --window` (que usa `XSendEvent`, e o GTK2
#    descarta). Medido na WTE-TASK-13: zero pixel de diferenca e zero linha no
#    trace. O mouse funciona. Entao um roteiro com `! tecla` **reprova aqui**,
#    em vez de rodar e produzir silencio -- silencio viraria "o port nao
#    gravou", que e a conclusao errada com a cara da certa.
#    O `wte.exe` nao sofre disso: o Wine implementa o proprio foco.
#
# 2. **O app abre a imagem pela linha de comando, e nao pelo dialogo.** Este
#    script sempre passou o caminho da copia como argumento; ate a
#    WTE-TASK-25 o app o ignorava, e desde ela o `MainForm.FormShow` carrega
#    dali. O harness nao mudou de forma nenhuma quando isso aconteceu, que era
#    exatamente o ponto. Pelo dialogo nao da: ver o item 1.
#
# ## Por que o titulo tem de ser diferente
#
# Os dois lados rodam no MESMO `:99`. O `wte.lpr` acrescenta um sufixo ao
# `Caption` dos 18 formularios em tempo de execucao exatamente por isto; com
# titulo igual o harness dirigiria o lado errado e o diff pareceria bug do port.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

ROTEIRO="${1:?uso: golden_run_laz.sh <roteiro> <copia.bin> [saida]}"
COPIA="${2:?falta a copia da imagem}"
SAIDA="${3:-$(dirname "$COPIA")}"
APP="${WTE_APP:-$WTE/build/wte}"
LOG="$SAIDA/port.log"

# shellcheck source=roteiro.sh
. "$AQUI/roteiro.sh"
roteiro_display

[ -f "$ROTEIRO" ] || { echo "ERRO: falta $ROTEIRO" >&2; exit 1; }
[ -f "$COPIA" ]   || { echo "ERRO: falta $COPIA" >&2; exit 1; }
[ -x "$APP" ] || {
  echo "ERRO: falta $APP -- rode 'make -C wte build'" >&2; exit 1; }
case "$COPIA" in
  "$RAIZ/roms/"*) echo "ERRO: $COPIA esta em roms/" >&2; exit 1 ;;
esac

if roteiro_usa_teclado "$ROTEIRO"; then
  echo "ERRO: $ROTEIRO usa '! tecla'/'! texto', e o lado port nao recebe" >&2
  echo "      teclado no :99 (WTE-TASK-13). Dirija por mouse, ou instale um" >&2
  echo "      window manager -- e decisao do usuario." >&2
  exit 5
fi

mkdir -p "$SAIDA"
# O app tem de morrer aconteca o que acontecer. Sem isto, uma corrida que falha
# no meio (janela que nao apareceu, roteiro errado) deixa o processo vivo, e a
# proxima corrida bate na guarda 2 do `golden_check.sh` -- ou pior, dirige a
# janela velha. Ja aconteceu na primeira medicao deste gate.
PID_ALVO=""
matar_port() {
  [ -n "$PID_ALVO" ] || return 0
  kill "$PID_ALVO" 2>/dev/null || true
  sleep 1
  kill -9 "$PID_ALVO" 2>/dev/null || true
}
trap matar_port EXIT

echo ">> port: lancando $APP"
env WTE_TRACE_FILE="$SAIDA/port-trace.log" \
  setsid "$APP" "$COPIA" >"$LOG" 2>&1 &
sleep 3
PID_ALVO="$(pgrep -n -f "^$APP" || true)"
[ -n "$PID_ALVO" ] && roteiro_pid_alvo "$PID_ALVO"
echo ">> port: pid $PID_ALVO"

roteiro_executa "$ROTEIRO"

sleep 1
matar_port
echo ">> port: fim"
