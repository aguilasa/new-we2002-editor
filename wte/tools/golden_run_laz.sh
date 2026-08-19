#!/usr/bin/env bash
# golden_run_laz.sh -- o lado PORT do gate: dirige o app Lazarus por um roteiro,
# sobre a copia que lhe derem.
#
#   bash wte/tools/golden_run_laz.sh <roteiro> <copia.bin> [dir-de-saida]
#
# ## Uma coisa que este lado nao pode, e uma que ele PASSOU a poder
#
# 1. **Teclado chega, desde que se peca foco** -- e ate a WTE-TASK-26 este
#    script afirmava o contrario. A WTE-TASK-13 mediu que nenhuma tecla era
#    entregue e concluiu "o port nao recebe teclado no `:99`"; a conclusao valia
#    para o que ela testou (`xdotool key` sem foco, e `key --window`, que usa
#    `XSendEvent` e o GTK2 descarta) e nao para o caso que faltava. Sem
#    gerenciador de janela o GTK2 nunca se considera ativo **sozinho**, mas
#    `xdotool windowfocus` -- que e `XSetInputFocus` e nao precisa de
#    gerenciador -- resolve, e foi assim que o `compara_tela.sh` passou a
#    trocar de time com `Down` na WTE-TASK-25.
#
#    Remedido na WTE-TASK-26 por este caminho: 3 `Down` sobre a janela focada
#    produzem 3 disparos de `lista_equiposChange` no `port-trace.log`. O driver
#    ganhou `ROTEIRO_FOCO`, ligado aqui e so aqui -- o lado oraculo nao precisa,
#    porque o Wine implementa o proprio foco, e mexer nele invalidaria o
#    controle sem ganho.
#
#    A recusa que existia -- roteiro com `! tecla` reprovava com codigo 5 --
#    saiu. Ela era a resposta certa para "o teclado nao chega": silencio viraria
#    "o port nao gravou", que e a conclusao errada com cara de certa. Com o
#    teclado chegando, ela passou a **bloquear a WTE-TASK-26 inteira**, cujos
#    handlers de nome e numero so existem por tecla.
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
ROTEIRO_FOCO=1          # ver o item 1 do cabecalho -- so o lado port
. "$AQUI/roteiro.sh"
roteiro_display

[ -f "$ROTEIRO" ] || { echo "ERRO: falta $ROTEIRO" >&2; exit 1; }
[ -f "$COPIA" ]   || { echo "ERRO: falta $COPIA" >&2; exit 1; }
[ -x "$APP" ] || {
  echo "ERRO: falta $APP -- rode 'make -C wte build'" >&2; exit 1; }
case "$COPIA" in
  "$RAIZ/roms/"*) echo "ERRO: $COPIA esta em roms/" >&2; exit 1 ;;
esac

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

# `WTE_TEXTURA` atravessa quando o chamador a define. E a mesma afordancia do
# argumento de imagem, pela mesma razao: o `TOpenDialog` do gtk2 nao se dirige
# por coordenada fixa sem gerenciador de janela, entao o roteiro do lado port
# nao tem como escolher arquivo. O oraculo escolhe pelo dialogo; os dois
# terminam com o MESMO arquivo, que e o que a comparacao exige.
echo ">> port: lancando $APP"
env WTE_TRACE_FILE="$SAIDA/port-trace.log" \
  ${WTE_TEXTURA:+WTE_TEXTURA="$WTE_TEXTURA"} \
  setsid "$APP" "$COPIA" >"$LOG" 2>&1 &
sleep 3
PID_ALVO="$(pgrep -n -f "^$APP" || true)"
[ -n "$PID_ALVO" ] && roteiro_pid_alvo "$PID_ALVO"
echo ">> port: pid $PID_ALVO"

roteiro_executa "$ROTEIRO"

sleep 1
matar_port
echo ">> port: fim"
