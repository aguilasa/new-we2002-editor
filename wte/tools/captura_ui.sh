#!/usr/bin/env bash
# captura_ui.sh -- fotografa os formularios dos DOIS lados, no mesmo estado.
#
#   bash wte/tools/captura_ui.sh <roteiro> [<roteiro> ...]
#   bash wte/tools/captura_ui.sh --lado oraculo ui-01-telas
#
#     WTE_UI_IMAGEM=<rom>   padrao: roms/japanese-shift-jis.bin
#     WTE_UI_SAIDA=<dir>    padrao: wte/re/visual/carregado
#
# Produto da WTE-TASK-37. A WTE-TASK-12 conferiu os 18 formularios VAZIOS, com
# o andaime `--show` que a WTE-TASK-25 removeu; aqui eles sao fotografados com
# a imagem carregada e um time selecionado, que e quando os problemas de
# verdade aparecem -- rotulo que so cabia vazio, combo com 63 entradas, cor de
# execucao por baixo do texto.
#
# ## Ele nao mede: ele produz o par
#
# Quem mede e o `check_carregado.py` ao lado, e quem julga e o olho humano --
# a §6 do plano manda **sem tolerancia de pixel**, porque `MS Sans Serif` nao
# esta instalada e gtk2 e Wine substituem por fontes diferentes. Comparar
# pixel a pixel entre os dois widgetsets acusaria divergencia em toda captura
# e nao informaria nada.
#
# ## A imagem e a japonesa, e nao e escolha de gosto
#
# Com a europeia o `wte.exe` morre ao trocar de time -- 49.749 violacoes de
# acesso contra 0 (CORR-WTE-044, `wte/re/crash-causa.md`). Toda foto daqui e
# depois de trocar de time.
#
# ## As guardas
#
# As mesmas do `golden_check.sh` e do `compara_tela.sh`: `DISPLAY` fixado aqui
# (`:98`), processo vivo do lado errado recusa a corrida, e `roms/` nunca e
# alvo -- copia, sempre.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

export DISPLAY="${WTE_DISPLAY:-:98}"   # fixado aqui, nunca herdado
IMAGEM="${WTE_UI_IMAGEM:-$RAIZ/roms/japanese-shift-jis.bin}"
SAIDA="${WTE_UI_SAIDA:-$WTE/re/visual/carregado}"
WORK="$RAIZ/work"
ROTEIROS="$WTE/tests/roteiros"

LADO=ambos
if [ "${1:-}" = "--lado" ]; then LADO="$2"; shift 2; fi
[ $# -ge 1 ] || { echo "uso: $0 [--lado oraculo|port] <roteiro> [...]" >&2
                  exit 1; }
[ -f "$IMAGEM" ] || { echo "ERRO: $IMAGEM nao existe" >&2; exit 1; }

sobra_processo() {
  pgrep -f "$WTE/build/wte" >/dev/null && return 0
  pgrep -f "we-team-editor.exe" >/dev/null && return 0
  return 1
}
if sobra_processo; then
  echo "ERRO: ja ha um wte ou we-team-editor.exe vivo. Feche antes -- os dois" >&2
  echo "      lados acham janela por nome, e a corrida dirigiria a errada." >&2
  pgrep -af "build/wte|we-team-editor.exe" >&2 || true
  exit 3
fi

mkdir -p "$WORK" "$SAIDA/oraculo" "$SAIDA/port"

rc=0
for nome in "$@"; do
  nome="${nome%.txt}"
  ORAC="$ROTEIROS/$nome.txt"
  PORT="$ROTEIROS/$nome.port.txt"
  [ -f "$ORAC" ] || { echo "ERRO: falta $ORAC" >&2; exit 1; }
  [ -f "$PORT" ] || { echo "ERRO: falta $PORT" >&2; exit 1; }

  if [ "$LADO" = ambos ] || [ "$LADO" = oraculo ]; then
    echo ">> $nome: lado oraculo"
    cp "$IMAGEM" "$WORK/ui-oraculo.bin"
    ROTEIRO_FOTO_DIR="$SAIDA/oraculo" \
      bash "$AQUI/golden_run_wte.sh" "$ORAC" "$WORK/ui-oraculo.bin" \
           "$WORK/ui-log" || rc=1
    rm -f "$WORK/ui-oraculo.bin"
  fi

  if [ "$LADO" = ambos ] || [ "$LADO" = port ]; then
    echo ">> $nome: lado port"
    cp "$IMAGEM" "$WORK/ui-port.bin"
    ROTEIRO_FOTO_DIR="$SAIDA/port" \
      bash "$AQUI/golden_run_laz.sh" "$PORT" "$WORK/ui-port.bin" \
           "$WORK/ui-log" || rc=1
    rm -f "$WORK/ui-port.bin"
  fi
done

echo ">> fotos em $SAIDA"
ls -1 "$SAIDA"/oraculo "$SAIDA"/port 2>/dev/null | sed 's/^/   /'
exit $rc
