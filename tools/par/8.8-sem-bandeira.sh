# PARIDADE-FUNCIONAL §8.8, item 2 -- time SEM bandeira própria.
#
# Carrega tools/par/8.8-prelude.sh antes, com o id no `PAR_TEAM`.
#
# Mede as duas metades do item de uma vez, e imprime o veredito:
#
#   1. as caixas de cor desabilitadas -- captura do diálogo em `PAR_SHOT`
#   2. o export recusado -- `CMD_EXPORT_FLAG` (124,65,44,12) não pode abrir
#      diálogo de arquivo nenhum; tem de subir a caixa
#      `Choose a team (that has "indipendent" flag too) !`
#
# Os ids que interessam são 56 (all-star), 57..63 (seleções) e **69 e 86**
# (clubes de Master League). Os dois últimos passam por OUTRO ramo do
# `OnButtgraf` -- `squad_ml[id-64]` em vez de `squad_nazall[id-1]`
# (`legacy/mfc/edDlg.cpp`; `src/app/Commands.cpp:65` no port) --, e medir
# 57..63 não exercita esse caminho. Ver CORR-WTE-138.
#
#   PAR_SHOT = caminho do PNG de captura. Opcional.
#
# Este roteiro NÃO grava a imagem: ele existe para medir recusa e estado de
# tela. Rodado sob `golden_check.sh`, os dois lados saem `IDENTICAL` contra a
# original a menos das não-idempotências -- o que aqui é o resultado certo, e
# não um falso verde, porque o que se afirma é justamente que nada foi
# exportado nem alterado.

par_extras_fk() {   # janelas que não são a raiz, o MainDialog nem o FlagKitDialog
    local _id _geo
    for _id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        [ "$(( _id ))" = "$(( MAIN ))" ] && continue
        [ "$(( _id ))" = "$(( FK ))" ]   && continue
        _geo="$(xdotool getwindowgeometry "$_id" 2>/dev/null | grep -o 'Geometry: [0-9]*x[0-9]*')"
        case "$_geo" in *' 1280x1024') continue ;; esac
        printf '%s ' "$_id"
    done
}

[ -n "${PAR_SHOT:-}" ] && import -window "$FK" "$PAR_SHOT" 2>/dev/null \
    && echo "par: captura em $PAR_SHOT"

fk_click 124 65 44 12
sleep 3

if xdotool search --onlyvisible --name 'FLAG FILE TO EXPORT' >/dev/null 2>&1; then
    echo "par: VEREDITO team=${PAR_TEAM:-1} -- export ACEITO (abriu o diálogo de arquivo)"
else
    _box="$(par_extras_fk)"
    if [ -n "$_box" ]; then
        echo "par: VEREDITO team=${PAR_TEAM:-1} -- export RECUSADO, com caixa de aviso"
    else
        echo "par: VEREDITO team=${PAR_TEAM:-1} -- export RECUSADO, SEM caixa"
    fi
fi

# Dispensa o que estiver de pé. `Return` só chega à caixa com o ponteiro sobre
# ela -- sem gerente de janelas o foco segue o ponteiro (CLAUDE.md, §:98).
for _i in 1 2 3; do
    _w="$(par_extras_fk)"
    [ -z "$_w" ] && break
    for _id in $_w; do
        xdotool mousemove --window "$_id" 70 40 2>/dev/null || continue
        sleep 0.3
        xdotool key --clearmodifiers Return
    done
    sleep 1.2
done

# Fecha o FlagKitDialog, que é modal nos dois lados: sem isto o clique em
# CMB_WRITE não alcança o diálogo principal (CORR-WTE-137).
fk_click 196 26 36 14; sleep 1.5
