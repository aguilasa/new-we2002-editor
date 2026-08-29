# PARIDADE-FUNCIONAL §8.4, item 4 -- os 10 combos, com mouse E com teclado.
#
# Carrega tools/par/8.4-prelude.sh antes. Os dois caminhos são sinais
# diferentes no Qt e só um deles passa pelo eventFilter, por isso o item pede
# os dois. Cinco combos vão por mouse (clique abre o popup, clique no item) e
# cinco por teclado (Down + Return), para separar os caminhos numa corrida.
#
#   por mouse:   CMB_POSITION 55,28  SKIN 55,42  HAIR_STYLE 55,56
#                HAIR_COLOUR 55,70   BEARD_STYLE 55,84      (todos 37x12)
#   por teclado: BEARD_COLOUR 55,98  BUILD 55,112  BOOTS 55,159
#                FOOT 55,174,50,12   OUT_OF_POSITION 274,90,33,12
for y in 28 42 56 70 84; do
    sk_click 55 "$y" 37 12;              sleep 1
    xdotool key --clearmodifiers Down;   sleep 0.5
    xdotool key --clearmodifiers Return; sleep 0.8
done
for y in 98 112 159; do
    sk_click 55 "$y" 37 12;              sleep 1
    xdotool key --clearmodifiers Down;   sleep 0.5
    xdotool key --clearmodifiers Return; sleep 0.8
done
sk_click 55 174 50 12;                   sleep 1
xdotool key --clearmodifiers Down;       sleep 0.5
xdotool key --clearmodifiers Return;     sleep 0.8
sk_click 274 90 33 12;                   sleep 1
xdotool key --clearmodifiers Down;       sleep 0.5
xdotool key --clearmodifiers Return;     sleep 0.8
xdotool key --clearmodifiers Escape;     sleep 2
