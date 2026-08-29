# PARIDADE-FUNCIONAL §8.7, item 4 -- aplicar os 16 presets num time.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMD_TACT1..16 ficam em quatro colunas de quatro:
#   x=131 4-5-1A/B 4-4-2A/B | x=169 4-3-3A/B 3-6-1A/B
#   x=208 3-5-2A/B 3-4-3A/B | x=246 5-4-1A/B 5-3-2A/B
# todos 34x10, nas linhas y=35,48,62,75.
#
# Aplica os dezesseis EM SEQUÊNCIA: o último a ser clicado é o que fica, e o
# que o disco guarda. O valor de medir todos é que qualquer um deles que
# divergisse apareceria -- se um preset intermediário gravasse errado, o
# formato final mudaria junto.
#
#   PAR_SO=<n>  aplica só o preset n (1..16), para isolar um deles
i=1
for x in 131 169 208 246; do
    for y in 35 48 62 75; do
        if [ -z "${PAR_SO:-}" ] || [ "${PAR_SO}" = "$i" ]; then
            par_click "$x" "$y" 34 10; sleep 0.9
        fi
        i=$(( i + 1 ))
    done
done
sleep 1
