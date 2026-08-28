# PARIDADE-FUNCIONAL §8.1, item 3 -- as 3 abreviações.
#
# Time: Nation 1 - Ireland.
# Estímulo: TXT_TEAM_ABBREV1..3 (10,138 / 10,150 / 10,163, 30x12).
# O limite de 3 é fixo em código (setMaxLength(3)), não vem de tabela por time.
#
# Este arquivo é o trecho de shell que os DOIS hooks recebem sem alteração:
#   GOLDEN_EDIT     -> tools/golden_run.sh (o ed.exe sob Wine)
#   GOLDEN_GUI_EDIT -> tools/golden_gui.sh (o port Qt)
# Ambos exportam $MAIN e definem dlu_x/dlu_y com a mesma conversão do ed.rc.

# clique no centro de um controle, com a geometria em DLU do ed.rc
par_click() {   # par_click <x> <y> <w> <h>
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
# limpa e digita. Ctrl+A NÃO seleciona tudo num CEdit do Win32 (CLAUDE.md):
# usar End, shift+Home, BackSpace, senão os dois lados recebem textos
# diferentes e o diff acusa divergência que não existe.
par_type() {    # par_type <texto>
    xdotool key --clearmodifiers End;        sleep 0.5
    xdotool key --clearmodifiers shift+Home; sleep 0.5
    xdotool key --clearmodifiers BackSpace;  sleep 0.5
    xdotool type --delay 40 "$1";            sleep 0.5
}

# CMB_TEAM 142,7,137,12. O clique abre o popup; Home leva ao primeiro item
# (sem ele, Down significa "o próximo", que depende do estado inicial), e o
# Return CONFIRMA -- sem ele o popup fica aberto e o formulário não troca de
# time. Chega em "Nation 1 - Ireland".
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
xdotool key --clearmodifiers Down;             sleep 1
xdotool key --clearmodifiers Return;           sleep 2

i=1
for y in 138 150 163; do
    par_click 10 "$y" 30 12; sleep 1
    par_type "GA$i"
    i=$((i + 1))
done

# tira o foco do 3º campo para o killfocus gravar
par_click 10 31 76 12; sleep 2      # TXT_TEAM_NAME1
