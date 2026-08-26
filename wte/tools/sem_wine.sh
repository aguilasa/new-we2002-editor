#!/usr/bin/env bash
# sem_wine.sh -- roda um comando num ambiente SEM Wine e SEM 32 bits.
# Produto da WTE-TASK-40, condicao 3 da definicao de pronto (plano, secao 0).
#
#   bash wte/tools/sem_wine.sh [--listar] -- <comando> [args...]
#
#     --listar   nao roda nada: imprime o que seria mascarado e sai
#
# ## Por que uma ferramenta, e nao um `ldd | grep -v wine`
#
# "O app nao USA Wine" e "o app RODA onde Wine nao existe" sao duas afirmacoes
# diferentes, e so a segunda fecha a condicao 3. A primeira se responde com
# `ldd`; a segunda exige uma maquina sem Wine -- que esta aqui nao e, porque o
# oraculo A depende dele.
#
# A saida e a mesma do `tools/run-sanitized.sh` do `newWe2002`: um
# user+mount namespace sem privilegio, onde os caminhos do Wine ficam cobertos
# por `tmpfs` vazio. So a arvore daquele processo enxerga isso; nada no sistema
# muda, nao precisa de root, e o Wine continua inteiro para a proxima corrida
# do gate golden.
#
# ## O que e mascarado, e por que cada um
#
#   ~/.var/app/com.usebottles.bottles   o runner soda-9.0-1, que E o Wine desta
#                                       maquina (nao ha pacote `wine` no apt)
#   /var/lib/flatpak                    a instalacao do Bottles e os runtimes
#                                       org.winehq.Wine.{gecko,mono}
#   work/wineprefix, work/wineprefix-wte  os dois prefixos deste repositorio --
#                                       a condicao 3 pede que o app nao leia
#                                       nada dali
#   /lib/i386-linux-gnu, /usr/lib/i386-linux-gnu   o stack 32 bits, sem o qual
#                                       o `winex11.drv` de 32 bits nem carrega.
#                                       Mascarar prova a independencia do app
#                                       de 32 bits, que a condicao 3 tambem pede
#
# ## A guarda tem DUAS clausulas, e nesta maquina so a segunda tem trabalho
#
# Ela vem ANTES do comando -- ambiente que so parece limpo mede tao pouco
# quanto nao medir --, e recusa por dois motivos diferentes:
#
#   1. `wine`, `wine64`, `wineserver` ou `winecfg` respondem no `PATH` dentro
#      do namespace. E a clausula que pega uma maquina com o pacote do apt.
#      **Aqui ela e verdadeira antes de mascarar qualquer coisa**: o Wine desta
#      maquina e o runner do Bottles, em `~/.var/app/`, e nunca esteve no
#      `PATH` -- `command -v wine wine64 wineserver winecfg` ja sai 1 fora de
#      namespace nenhum. Ela FICA, porque custa quatro linhas e e o que faz
#      este script valer noutra maquina, que e o caso que a condicao 3 quer
#      sobreviver;
#   2. cada alvo mascarado tem de ficar VAZIO dentro do namespace. **E esta que
#      trabalha aqui**, e e ela que prova que o runner do Bottles sumiu.
#
# **Apagar a segunda desliga a conferencia**, mesmo com a primeira intacta --
# e a primeira e a que parece a protecao, porque nomeia o Wine. A CORR-WTE-120
# nasceu de a prosa creditar a clausula inerte; as duas estao medidas no
# `test_check_nativo.py`, uma recusa por clausula.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

ALVOS=(
  "$HOME/.var/app/com.usebottles.bottles"
  "/var/lib/flatpak"
  "$RAIZ/work/wineprefix"
  "$RAIZ/work/wineprefix-wte"
  "/lib/i386-linux-gnu"
  "/usr/lib/i386-linux-gnu"
)

LISTAR=0
if [ "${1:-}" = "--listar" ]; then LISTAR=1; shift; fi
if [ "${1:-}" = "--" ]; then shift; fi

MASCARAS=()
for a in "${ALVOS[@]}"; do
  if [ -e "$a" ]; then
    MASCARAS+=(--tmpfs "$a")
    [ "$LISTAR" = 1 ] && echo "mascara: $a"
  else
    [ "$LISTAR" = 1 ] && echo "ausente: $a"
  fi
done
[ "$LISTAR" = 1 ] && exit 0

if [ $# -eq 0 ]; then
  echo "uso: bash wte/tools/sem_wine.sh [--listar] -- <comando> [args...]" >&2
  exit 2
fi

command -v bwrap >/dev/null || { echo "ERRO: falta o bwrap" >&2; exit 1; }

# A guarda roda DENTRO do namespace, com o mesmo conjunto de mascaras.
GUARDA='
for w in wine wine64 wineserver winecfg; do
  if command -v "$w" >/dev/null 2>&1; then
    echo "ERRO: $w ainda responde dentro do namespace" >&2; exit 1
  fi
done
for d in '"${ALVOS[*]}"'; do
  if [ -e "$d" ] && [ -n "$(ls -A "$d" 2>/dev/null)" ]; then
    echo "ERRO: $d nao ficou vazio" >&2; exit 1
  fi
done
'

exec bwrap --dev-bind / / "${MASCARAS[@]}" \
  /bin/bash -c "$GUARDA"'
echo ">> ambiente sem Wine: guarda passou"
exec "$@"' _ "$@"
