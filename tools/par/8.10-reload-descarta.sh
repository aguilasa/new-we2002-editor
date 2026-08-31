# PARIDADE-FUNCIONAL §8.10, item 3 -- `CMB_RELOAD` depois de editar.
#
# Edita o nome do time, recarrega da imagem, e grava. O que se afirma: a edição
# NÃO chega ao disco -- o `OnReload` relê tudo do arquivo e joga fora o que
# estava em memória.
#
#   CMB_TEAM        142,7,137,12     TXT_TEAM_NAME1  10,31,76,12
#   TXT_TEAM_NAME_KANJI 10,123,76,12 (só para tirar o foco)
#   CMB_RELOAD      145,295,130,15
#
# Os dois `OnReload` são equivalentes e é isso que o item confere:
#   legado  `carica_dabin(); carica_url(); OnSelezioneSquadraV();`
#   port    `db_.Load(...); LoadUrls(); OnTeamSelected();`
#
# **O controle deste item é a cópia sem edição nenhuma.** Um roteiro que
# falhasse em digitar produziria exatamente o mesmo resultado que um `Reload`
# funcionando -- os dois "não gravam a edição". Por isso a evidência tem de
# incluir uma corrida gêmea SEM o `CMB_RELOAD`, mostrando que o mesmo estímulo
# de fato altera o disco quando não se recarrega.

par_click() {   # par_click <x> <y> <w> <h>
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
par_type() {    # par_type <texto> -- `Ctrl+A` não seleciona tudo num CEdit
    xdotool key --clearmodifiers End;        sleep 0.4
    xdotool key --clearmodifiers shift+Home; sleep 0.4
    xdotool key --clearmodifiers BackSpace;  sleep 0.4
    xdotool type --delay 40 "$1";            sleep 0.4
}

# Time: Nation 1 - Ireland. Home antes do Down torna a escolha independente do
# estado inicial.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
xdotool key --clearmodifiers Down;             sleep 1
xdotool key --clearmodifiers Return;           sleep 2

# Edita o 1º nome e tira o foco, para o killfocus gravar em memória.
par_click 10 31 76 12; sleep 1
par_type "RELOAD"
par_click 10 123 76 12; sleep 2

# Recarrega da imagem. `PAR_SEM_RELOAD=1` pula esta linha -- é a corrida de
# controle, a que TEM de sujar o disco.
if [ "${PAR_SEM_RELOAD:-0}" != 1 ]; then
    par_click 145 295 130 15; sleep 3
fi
