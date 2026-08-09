#!/usr/bin/env bash
# capture_forms.sh -- captura os 18 formularios do app Lazarus, um PNG por
# formulario, para a comparacao visual da WTE-TASK-12.
#
# NAO e gerador e NAO entra na bateria de `make -C wte check`: a saida e PNG,
# que nao e byte-estavel entre versoes de GTK e de ImageMagick, e um `--check`
# ali quebraria por causa de atualizacao de biblioteca sem nada ter mudado no
# projeto. O mesmo raciocinio que deixou o `make_icon.py` do newWe2002 fora da
# bateria (ver CLAUDE.md, "Codigo gerado"). O que o script garante e
# reprodutibilidade do ATO, nao do byte.
#
# Fica em `tools/` e nao em `tools/*.py` de proposito: o wildcard do Makefile
# enumera `*.py` e cobraria `--check` de quem entrasse ali.
#
#   bash wte/tools/capture_forms.sh [destino]
#
# Destino padrao: wte/re/visual/lazarus/
#
# Regra do :99 (CLAUDE.md): toda GUI roda no :99, nunca no :1. O script fixa
# DISPLAY=:99 por conta propria em vez de herdar do shell -- herdar foi
# exatamente o que derrubou o golden_check.sh do newWe2002 quando o ctest
# repassava o :1.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
BIN="$WTE/build/wte"
DESTINO="${1:-$WTE/re/visual/lazarus}"

export DISPLAY=:99
# O Xvfb pode ter subido via xvfb-run (com cookie proprio) ou direto (sem
# -auth). Resolver o cookie so quando ele existe; exportar XAUTHORITY vazio
# quebra o caso sem auth.
xauth_file="$(ps -o args= -C Xvfb 2>/dev/null \
  | sed -n 's/.*Xvfb :99 .*-auth \([^ ]*\).*/\1/p' | head -1)"
if [ -n "$xauth_file" ]; then
  export XAUTHORITY="$xauth_file"
fi

if ! xdpyinfo >/dev/null 2>&1; then
  echo "ERRO: nao ha X no :99 (Xvfb fora do ar?)." >&2
  exit 1
fi
test -x "$BIN" || { echo "ERRO: $BIN nao existe -- rode 'make -C wte build'." >&2; exit 1; }

mkdir -p "$DESTINO"

# O sufixo do Caption e divergencia deliberada da WTE-TASK-11; aqui ele e
# util, porque separa janela nossa de qualquer outra coisa no display.
MARCA=' [Lazarus]'

capta_um() {
  local nome="$1" saida="$DESTINO/$nome.png"
  local pid alvo principal id titulo geo w h

  WTE_TRACE_FILE=/dev/null "$BIN" --show "$nome" >/dev/null 2>&1 &
  pid=$!
  # A LCL leva ~1 s para mapear as janelas; 3 s e folga barata.
  sleep 3

  alvo=''
  principal=''
  while read -r id; do
    [ -n "$id" ] || continue
    titulo="$(xdotool getwindowname "$id" 2>/dev/null || true)"
    case "$titulo" in
      *"$MARCA") ;;
      *) continue ;;
    esac
    geo="$(xdotool getwindowgeometry "$id" 2>/dev/null | sed -n 's/.*Geometry: \([0-9]*x[0-9]*\).*/\1/p')"
    w="${geo%x*}"; h="${geo#*x}"
    # Descarta as janelas de servico da LCL (10x10, 1x16, 200x200 fora da tela).
    [ "${w:-0}" -ge 60 ] && [ "${h:-0}" -ge 40 ] || continue
    case "$titulo" in
      *'W11 Team Editor'*) principal="$id" ;;
      *) alvo="$id" ;;
    esac
  done < <(xdotool search --pid "$pid" 2>/dev/null || true)

  # `--show MainForm` mostra so o principal; nos demais o principal aparece
  # junto porque e o formulario principal da LCL, e o alvo e o outro.
  [ -n "$alvo" ] || alvo="$principal"

  if [ -z "$alvo" ]; then
    echo "FALHA: nenhuma janela para $nome" >&2
    kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
    return 1
  fi

  # NAO usar `import -window <id>`. Sem window manager no :99 nao ha
  # empilhamento garantido, e todo formulario que nasce dentro da area do
  # MainForm (544x495 a partir de 132,72 -- quase todos) sai PRETO: o X
  # devolve o conteudo indefinido da regiao obscurecida, sem erro nenhum.
  # E o mesmo sintoma que o CLAUDE.md registra para o modal do ed.exe, com
  # outra causa. A saida e levantar a janela e recortar do root, que sempre
  # tem conteudo.
  xdotool windowraise "$alvo" 2>/dev/null || true
  sleep 1
  geo="$(xdotool getwindowgeometry "$alvo" | sed -n 's/.*Geometry: \([0-9]*x[0-9]*\).*/\1/p')"
  pos="$(xdotool getwindowgeometry "$alvo" | sed -n 's/.*Position: \([0-9]*\),\([0-9]*\).*/\1+\2/p')"
  import -window root -crop "${geo}+${pos//+/+}" +repage "$saida"
  printf '%-24s %-10s %s\n' "$nome" "$geo" "$saida"

  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

for nome in $("$BIN" --list); do
  capta_um "$nome"
done

echo ">> $(find "$DESTINO" -name '*.png' | wc -l) capturas em $DESTINO"
