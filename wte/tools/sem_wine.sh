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
# A guarda vem ANTES do comando: se `wine`, `wine64` ou `wineserver` ainda
# responder dentro do namespace, o script RECUSA. Ambiente que so parece
# limpo mede tao pouco quanto nao medir.
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
