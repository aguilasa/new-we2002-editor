#!/bin/bash
# PARIDADE-FUNCIONAL §8.10 -- itens 1, 2 e 5, LADO DO ORÁCULO.
#
#   bash tools/par/8.10-ciclo-oraculo.sh "$PWD" <copia.bin>
#
# NÃO é um hook de `GOLDEN_EDIT`, e não podia ser: os itens 1 e 5 são sobre o
# arranque e o encerramento do editor, e o `golden_run.sh` já entrou pelo
# diálogo de abertura e já sai gravando. Este roteiro sobe o `ed.exe` ele mesmo,
# duas vezes, e mede o que acontece na tela.
#
# Usa o prefix persistente `work/wineprefix` -- o mesmo do `make oracle`, e
# nunca uma bottle existente: `ed.cpp:75` chama
# `COleObjectFactory::UpdateRegistryAll()`, que escreve no registry.
#
# Sempre sobre CÓPIA. O `roms/` não é alvo de ferramenta nenhuma.
set -u
REPO="$1"
IMG="$2"
WINE_BIN="${WINE_BIN:-/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin}"
export DISPLAY=:98
export XAUTHORITY=
export WINEDEBUG=-all
export WINEPREFIX="$REPO/work/wineprefix"
[ -d "$WINEPREFIX" ] || { mkdir -p "$WINEPREFIX"; "$WINE_BIN/wineboot" -i >/dev/null 2>&1; }

win_path() { printf 'Z:%s' "$(echo "$1" | sed 's#/#\\#g')"; }

janela_por_titulo() {   # <titulo> <segundos>
    local want="$1" tries="${2:-30}" i id name
    for ((i = 0; i < tries * 2; i++)); do
        for id in $(xdotool search --name '.*' 2>/dev/null); do
            name="$(xdotool getwindowname "$id" 2>/dev/null || true)"
            [ "$name" = "$want" ] && { printf '%s' "$id"; return 0; }
        done
        sleep 0.5
    done
    return 1
}
principal() {           # janela > 500x400
    xwininfo -root -children 2>/dev/null |
        awk '$0 ~ /[0-9]+x[0-9]+\+/ { match($0, /([0-9]+)x([0-9]+)\+/, m)
             if (m[1] > 500 && m[2] > 400) { print $1; exit } }'
}
vivo() { pgrep -f 'ed\.exe' >/dev/null 2>&1 && echo sim || echo NAO; }

matar() { "$WINE_BIN/wineserver" -k >/dev/null 2>&1; sleep 2; }

# ---------------------------------------------------------------- item 1
echo "== item 1: cancelar o diálogo de abertura =="
matar
( cd "$REPO/Debug" && "$WINE_BIN/wine64" ed.exe >/dev/null 2>&1 ) &
DLG="$(janela_por_titulo 'IMAGE CD SELECTION' 40)" || { echo "  diálogo não abriu"; matar; exit 1; }
echo "  diálogo de abertura apareceu (id $DLG)"
xdotool windowfocus "$DLG" 2>/dev/null
xdotool key --clearmodifiers Escape; sleep 2
AVISO="$(janela_por_titulo 'ed' 8)" && {
    import -window "$AVISO" /tmp/c09/ora-cancelar.png 2>/dev/null
    echo "  aviso apareceu; captura em /tmp/c09/ora-cancelar.png"
    xdotool windowfocus "$AVISO" 2>/dev/null
    xdotool key --clearmodifiers Return; sleep 2
}
sleep 2
echo "  ed.exe ainda vivo? $(vivo)"
echo "  janela principal? $(principal | head -1 || echo nenhuma)"
matar

# ---------------------------------------------------------------- item 2 e 5
echo
echo "== item 2: abrir imagem com tamanho errado =="
( cd "$REPO/Debug" && "$WINE_BIN/wine64" ed.exe >/dev/null 2>&1 ) &
DLG="$(janela_por_titulo 'IMAGE CD SELECTION' 40)" || { echo "  diálogo não abriu"; matar; exit 1; }
xdotool windowfocus "$DLG" 2>/dev/null
xdotool mousemove --window "$DLG" 378 445 click 1; sleep 1
xdotool type --delay 15 "$(win_path "$IMG")"; sleep 1
xdotool key Return; sleep 2
AVISO="$(janela_por_titulo 'ed' 12)" && {
    import -window "$AVISO" /tmp/c09/ora-tamanho.png 2>/dev/null
    echo "  aviso de tamanho apareceu; captura em /tmp/c09/ora-tamanho.png"
    xdotool windowfocus "$AVISO" 2>/dev/null
    xdotool key --clearmodifiers Return; sleep 2
}
MAIN="$(principal | head -1)"
if [ -n "$MAIN" ]; then
    echo "  CARREGOU MESMO ASSIM -- janela principal $MAIN"
    import -window "$MAIN" /tmp/c09/ora-carregado.png 2>/dev/null && echo "  captura em /tmp/c09/ora-carregado.png"
else
    echo "  NAO carregou"
fi

echo
echo "== item 5: Escape fecha =="
xdotool mousemove --window "$MAIN" 300 300; sleep 0.5
xdotool key --clearmodifiers Escape; sleep 3
echo "  ed.exe ainda vivo? $(vivo)"
echo "  janela principal? $(principal | head -1 || echo nenhuma)"
matar
