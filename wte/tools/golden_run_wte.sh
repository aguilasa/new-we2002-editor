#!/usr/bin/env bash
# golden_run_wte.sh -- o lado ORACULO do gate: dirige o `we-team-editor.exe`
# sob Wine 32-bit por um roteiro, sobre a copia que lhe derem.
#
#   bash wte/tools/golden_run_wte.sh <roteiro> <copia.bin> [dir-de-saida]
#
# Nao copia imagem e nao compara nada: quem faz isso e o `golden_check.sh`.
# Aqui so se dirige a janela e se recusa a mentir sobre o resultado.
#
# ## A imagem e fixa do lado do oraculo, e o motivo e medido
#
# Com `roms/golden-european-deluxe.bin` o `wte.exe` morre ao trocar de time --
# 49.749 violacoes de acesso contra **0** com `roms/japanese-shift-jis.bin`. A
# causa nao e a imagem "certa" no sentido de release: e um ponteiro global
# (`0x004335e4`) que a carga do time sobrescreve com dado de uma tabela
# vizinha, e o valor passa no teste de nulo que a rotina de realce faz
# (CORR-WTE-044, `wte/re/crash-causa.md`).
#
# Consequencia: quem chamar este script com a europeia esta medindo o
# travamento, nao a operacao. O `golden_check.sh` fixa a japonesa; aqui se
# **avisa** quando a copia nao tem o tamanho dela, porque este script tambem e
# util a mao.
#
# ## `c0000005` e falha do lado do oraculo -- nunca silenciada
#
# Esta provado que ESTE caminho e imune com a japonesa, nao que a imagem
# inteira seja. Entao o script varre o log do Wine no fim e reprova se achar
# violacao de acesso: um oraculo que morreu no meio grava menos do que deveria,
# e o diff sairia menor -- verde por ausencia de trabalho.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$(dirname "$AQUI")")"

ROTEIRO="${1:?uso: golden_run_wte.sh <roteiro> <copia.bin> [saida]}"
COPIA="${2:?falta a copia da imagem}"
SAIDA="${3:-$(dirname "$COPIA")}"

WINE_BIN="${WINE_BIN:-/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin}"
PREFIX="$RAIZ/work/wineprefix-wte"
WORK="$RAIZ/work"
LOG="$SAIDA/wine-oraculo.log"

# shellcheck source=roteiro.sh
. "$AQUI/roteiro.sh"
roteiro_display

[ -f "$ROTEIRO" ] || { echo "ERRO: falta $ROTEIRO" >&2; exit 1; }
[ -f "$COPIA" ]   || { echo "ERRO: falta $COPIA" >&2; exit 1; }
[ -x "$WINE_BIN/wine" ] || { echo "ERRO: loader Wine 32-bit em $WINE_BIN" >&2; exit 1; }
case "$COPIA" in
  "$RAIZ/roms/"*) echo "ERRO: $COPIA esta em roms/ -- o editor grava in-place" >&2
                  exit 1 ;;
esac

TAM_JAPONESA=307187664
if [ "$(stat -c%s "$COPIA")" != "$TAM_JAPONESA" ]; then
  echo "AVISO: a copia nao tem o tamanho de roms/japanese-shift-jis.bin." >&2
  echo "       Com a europeia o wte.exe morre ao trocar de time (49.749" >&2
  echo "       violacoes de acesso contra 0) -- wte/re/crash-causa.md." >&2
fi

# O `wte.exe` so digere caminho curto no dialogo de abrir: `xdotool type` usa
# `XSendEvent` e embaralha string longa. Por isso a unidade E: aponta para
# work/, e o roteiro digita `E:\<nome>`.
mkdir -p "$WORK" "$SAIDA"
ln -sfn "$WORK" "$PREFIX/dosdevices/e:"
case "$(dirname "$(readlink -f "$COPIA")")" in
  "$(readlink -f "$WORK")") : ;;
  *) echo "ERRO: a copia tem de morar em work/ -- e a unidade E: do prefix" >&2
     exit 1 ;;
esac

matar_oraculo() {
  env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
  # O `-k` so PEDE; quem ESPERA e o `-w`, que volta quando o servidor daquele
  # prefix realmente saiu. Sem ele o lado B era lancado sobre um prefix ainda
  # em desmontagem, e o `Abre` do roteiro seguinte podia levar mais que os 30s
  # da espera -- a falha intermitente que a CORR-WTE-080 mediu. O `timeout`
  # existe para o gate nao pendurar se o servidor travar: 30s e muito mais do
  # que ele leva, e passar direto e melhor que nao voltar nunca.
  timeout 30 env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -w \
    >/dev/null 2>&1 || true
}
# Mesma razao do lado port: corrida que falha no meio nao pode deixar janela
# viva no `:99`. A guarda 2 do `golden_check.sh` recusaria a proxima corrida --
# e recusar e o certo, mas o custo e uma rodada perdida.
trap matar_oraculo EXIT
matar_oraculo
sleep 1

echo ">> oraculo: lancando o wte.exe"
(
  cd "$RAIZ/we-team-editor"
  env DISPLAY="$DISPLAY" WINEPREFIX="$PREFIX" WINEARCH=win32 \
      WINEDEBUG="${WINEDEBUG:-+seh}" \
      ${XAUTHORITY:+XAUTHORITY="$XAUTHORITY"} \
    setsid "$WINE_BIN/wine" we-team-editor.exe
) >"$LOG" 2>&1 &
LANCADO=$!

# Terceira guarda: so janela deste processo. O `wine` de 32 bits reexecuta e a
# janela nasce num neto, entao o PID que interessa e o do processo que publica
# `_NET_WM_PID` -- descoberto pelo nome, dentro da arvore recem-lancada.
sleep 3
PID_ALVO="$(pgrep -n -f 'we-team-editor.exe' || true)"
[ -n "$PID_ALVO" ] && roteiro_pid_alvo "$PID_ALVO"
echo ">> oraculo: pid $PID_ALVO (lancador $LANCADO)"

# O roteiro digita `E:\@IMAGEM@`; cada lado abre a SUA copia.
ROTEIRO_IMAGEM="$(basename "$COPIA")"
roteiro_executa "$ROTEIRO"

sleep 2
matar_oraculo
sleep 2

if grep -qE 'code=c0000005|EXCEPTION_ACCESS_VIOLATION' "$LOG"; then
  n="$(grep -cE 'code=c0000005|EXCEPTION_ACCESS_VIOLATION' "$LOG")"
  echo "ERRO: o oraculo teve $n violacao(oes) de acesso -- ele morreu no meio," >&2
  echo "      entao gravou menos do que deveria e o diff sairia menor." >&2
  echo "      Log: $LOG" >&2
  exit 4
fi
echo ">> oraculo: fim, sem violacao de acesso"
