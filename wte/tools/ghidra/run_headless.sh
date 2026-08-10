#!/usr/bin/env bash
# Refaz o projeto Ghidra do zero -- WTE-TASK-24.
#
# O banco do Ghidra NAO e versionado: fica em `work/ghidra/`, que o .gitignore
# cobre. Isso e decisao, nao descuido -- e um banco binario de centenas de MB
# que muda a cada analise. O que fica versionado e ESTE script mais o
# `apply_names.py`, que juntos reconstroem o projeto inteiro em um comando.
#
#   bash wte/tools/ghidra/run_headless.sh              # importa e analisa
#   bash wte/tools/ghidra/run_headless.sh --decompile <simbolo>
#
# O `--decompile` imprime a assinatura recuperada de UMA funcao. Serve de prova
# da convencao (§8.1) e de ferramenta de consulta na fase 4.
#
# LIMITE: a saida do decompilador responde PERGUNTA. Ela nunca vai para
# `wte/re/spec/` nem para Pascal -- recuperacao de especificacao, nao
# transcricao (PLAN-WTE-LAZARUS §2, §8.10).
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
GHIDRA="${GHIDRA_HOME:-$HOME/.local/opt/ghidra_12.1.2_PUBLIC}"
PROJ="$RAIZ/work/ghidra"
NOME=wte
EXE="$RAIZ/we-team-editor/we-team-editor.exe"

# A convencao Borland nao e configurada depois: ela vem do compiler spec
# escolhido NA IMPORTACAO. O x86borland.cspec ja traz __fastcall = EAX, EDX,
# ECX como prototipo DEFAULT, entao ela vale para TODAS as funcoes -- que e o
# que o criterio da task pede. Ver borland_cc.md ao lado.
PROCESSOR="x86:LE:32:default"
CSPEC="borlandcpp"

[ -x "$GHIDRA/support/analyzeHeadless" ] || {
  echo "ERRO: Ghidra nao esta em $GHIDRA (aponte GHIDRA_HOME)." >&2; exit 1; }
[ -f "$EXE" ] || {
  echo "ERRO: $EXE nao existe. A pasta we-team-editor/ e do usuario," >&2
  echo "      como roms/, e nao e versionada." >&2; exit 1; }

mkdir -p "$PROJ"

if [ "${1:-}" = "--decompile" ]; then
  [ $# -ge 2 ] || { echo "uso: $0 --decompile <simbolo>" >&2; exit 1; }
  exec "$GHIDRA/support/analyzeHeadless" "$PROJ" "$NOME" \
    -process "$(basename "$EXE")" -noanalysis \
    -scriptPath "$RAIZ/wte/tools/ghidra" \
    -postScript decompile_one.java "$2" \
    -readOnly
fi

"$GHIDRA/support/analyzeHeadless" "$PROJ" "$NOME" \
  -import "$EXE" \
  -processor "$PROCESSOR" -cspec "$CSPEC" \
  -overwrite \
  -scriptPath "$RAIZ/wte/tools/ghidra" \
  -postScript apply_names.java "$RAIZ"
