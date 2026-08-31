#!/bin/bash
# PARIDADE-FUNCIONAL §8.10 -- itens 1, 2 e 5, LADO DO PORT.
#
#   bash tools/par/8.10-ciclo-port.sh "$PWD" <copia.bin>
#
# Irmão do `8.10-ciclo-oraculo.sh`, e pelo mesmo motivo não é hook de
# `GOLDEN_GUI_EDIT`: mede arranque e encerramento, que o harness não expõe.
#
# O item 1 sobe o app SEM argumento, que é o que faz o `QFileDialog` aparecer --
# o argumento existe só para o golden poder dirigir a janela.
#
# Sempre sobre CÓPIA.
set -u
REPO="$1"
IMG="$2"
export DISPLAY=:98 XAUTHORITY=
APP="$REPO/build/src/app/newWe2002"

# Onde caem as capturas. `work/` é gitignored e é onde o resto do projeto põe
# saída de corrida. O destino era `/tmp/c09` fixo, que ninguém criava: com o
# `import` calado por `2>/dev/null`, nenhuma captura era produzida e nada
# reclamava — o defeito da CORR-WTE-142.
OUT="${PAR_OUT:-$REPO/work/par-8.10}"
mkdir -p "$OUT"

# Captura, e DIZ o que aconteceu. A linha de confirmação só sai com o arquivo
# escrito; a falha sai com a mensagem do próprio `import`, em vez de sumir.
# O `-window <id>` falha com `Resource temporarily unavailable` quando a janela
# está obscurecida por um modal, e o aviso deste roteiro é justamente um modal
# (CLAUDE.md, seção do `:98`). O `-window root` sempre funciona e, sem gerente
# de janelas, mostra a mesma tela -- então ele é a segunda tentativa, e a
# mensagem diz qual das duas produziu o arquivo.
capturar() {    # capturar <window-id> <nome-do-arquivo>
    local err
    if err="$(import -window "$1" "$OUT/$2" 2>&1)"; then
        echo "  captura em $OUT/$2"
    elif err="$(import -window root "$OUT/$2" 2>&1)"; then
        echo "  captura em $OUT/$2 (root: a janela $1 não pôde ser lida)"
    else
        echo "  captura FALHOU ($OUT/$2): ${err:-sem mensagem}"
    fi
}

listar() {
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        echo "    $id $(xdotool getwindowgeometry "$id" | grep -o 'Geometry: [0-9]*x[0-9]*') :: $(xdotool getwindowname "$id" 2>/dev/null)"
    done
}
esperar_titulo() {   # <titulo> <segundos>
    local want="$1" tries="${2:-20}" i id name
    for ((i = 0; i < tries * 2; i++)); do
        for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
            name="$(xdotool getwindowname "$id" 2>/dev/null || true)"
            case "$name" in *"$want"*) printf '%s' "$id"; return 0 ;; esac
        done
        sleep 0.5
    done
    return 1
}
vivo() { kill -0 "$1" 2>/dev/null && echo sim || echo NAO; }

# ---------------------------------------------------------------- item 1
echo "== item 1: cancelar o diálogo de abertura =="
"$APP" >/dev/null 2>&1 &
P=$!
DLG="$(esperar_titulo 'IMAGE CD SELECTION' 25)" || { echo "  diálogo não abriu"; kill $P 2>/dev/null; exit 1; }
echo "  diálogo de abertura apareceu (id $DLG)"
xdotool mousemove --window "$DLG" 200 200; sleep 0.5
xdotool key --clearmodifiers Escape; sleep 2
echo "  janelas logo após cancelar:"; listar
AV="$(esperar_titulo 'WE2002' 6)" && {
    capturar "$AV" port-cancelar.png
    xdotool mousemove --window "$AV" 100 40; sleep 0.3
    xdotool key --clearmodifiers Return; sleep 2
}
sleep 2
echo "  processo ainda vivo? $(vivo $P)"
echo "  janelas ao final:"; listar
kill $P 2>/dev/null; sleep 1

# ---------------------------------------------------------------- itens 2 e 5
echo
echo "== item 2: abrir imagem com tamanho errado =="
"$APP" "$IMG" >/dev/null 2>&1 &
P=$!
AV="$(esperar_titulo 'WE2002' 20)"
sleep 1
capturar "$AV" port-tamanho.png
xdotool mousemove --window "$AV" 100 40; sleep 0.3
xdotool key --clearmodifiers Return; sleep 2
MAIN=""
for id in $(xdotool search --pid "$P" 2>/dev/null); do
    g="$(xdotool getwindowgeometry "$id" 2>/dev/null | grep -o 'Geometry: [0-9]*x[0-9]*')"
    case "$g" in *' 1077x'*) MAIN="$id" ;; esac
done
if [ -n "$MAIN" ]; then
    echo "  CARREGOU MESMO ASSIM -- janela principal $MAIN"
else
    echo "  NAO carregou"; listar
fi

echo
echo "== item 5: Escape fecha =="
xdotool mousemove --window "$MAIN" 300 300; sleep 0.5
xdotool key --clearmodifiers Escape; sleep 3
echo "  processo ainda vivo? $(vivo $P)"
echo "  janelas ao final:"; listar
kill $P 2>/dev/null
