# PARIDADE-FUNCIONAL §8.4, item 2 -- altura, idade e número nos dois extremos.
#
# Carrega tools/par/8.4-prelude.sh antes. Estímulo: os valores que o item
# nomeia, um extremo por campo numa corrida (100 e 1 e 0), e a corrida irmã
# faz os altos (999, 99, 99).
#
#   TXT_HEIGHT 55,129,24,13   TXT_AGE 55,144,24,13   TXT_NUMBER 274,131,16,13
sk_click 55 129 24 13;  sleep 1; par_type "${PAR_H:-100}"
sk_click 55 144 24 13;  sleep 1; par_type "${PAR_A:-1}"
sk_click 274 131 16 13; sleep 1; par_type "${PAR_N:-0}"
# tira o foco do último campo e fecha o diálogo
sk_click 55 129 24 13;  sleep 1
xdotool key --clearmodifiers Escape; sleep 2
