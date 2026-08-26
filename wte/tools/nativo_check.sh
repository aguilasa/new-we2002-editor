#!/usr/bin/env bash
# nativo_check.sh -- a CONDICAO 3 da definicao de pronto, medida.
# Produto da WTE-TASK-40. Ver o plano, secao 0.
#
#   bash wte/tools/nativo_check.sh --imagem <copia.bin> [--prefixo <dir>]
#                                  [--saida <tsv>] [--manter]
#
# ## A afirmacao que ele mede, e a que ele NAO mede
#
# "O app nao USA Wine" e "o app RODA onde Wine nao existe" sao duas coisas. A
# primeira e um `ldd`; a segunda precisa de uma maquina sem Wine, e esta nao e
# -- o oraculo A depende dele. O `sem_wine.sh` fabrica essa maquina num
# namespace, e este script mede o app la dentro.
#
# As sete medidas, todas com veredito no TSV:
#
#   1. formato        o binario INSTALADO e ELF 64-bit x86-64
#   2. ldd-wine       nenhuma biblioteca com `wine`/`bottles` no caminho
#   3. ldd-32         nenhuma biblioteca de 32 bits (`i386`, `lib32`)
#   4. guarda         dentro do namespace, `wine`/`wine64`/`wineserver` somem
#   5. janela         a janela principal abre, com o titulo e a geometria certos
#   6. carga          N teclas `Down` produzem N `lista_equiposChange` no trace
#   7. maps           o processo VIVO nao mapeia nada de Wine nem de 32 bits
#
# A 6 e o que separa "abriu" de "funciona": janela vazia abriria igual. O trace
# e lido do arquivo que o proprio app escreve, com `WTE_TRACE_FILE`.
#
# ## O prefixo e INSTALADO, nao o `build/`
#
# A WTE-TASK-38 mediu que o binario de `wte/build/` morria fora dali (o log de
# trace resolvia `<exe>/../re/`, que nao existia), e a WTE-TASK-39 consertou a
# resolucao. Medir o `build/wte` aqui mediria o caminho que ja e caso especial;
# quem o usuario recebe e a arvore instalada, e e ela que este script instala,
# povoa com os assets e roda.
#
# ## Cuidado com a imagem
#
# COPIA, sempre -- o app grava in-place. O script RECUSA imagem que esteja
# dentro de `roms/`.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"
SLUG=we2002Lazarus
TITULO='W11 Team Editor PT by chagas_michel! [Lazarus]'
GEOMETRIA=522x475
TECLAS=3

IMAGEM=""
PREFIXO=""
SAIDA="$WTE/re/nativo.tsv"
MANTER=0
while [ $# -gt 0 ]; do
  case "$1" in
    --imagem)  IMAGEM="$2"; shift 2 ;;
    --prefixo) PREFIXO="$2"; shift 2 ;;
    --saida)   SAIDA="$2"; shift 2 ;;
    --manter)  MANTER=1; shift ;;
    *) echo "opcao desconhecida: $1" >&2; exit 2 ;;
  esac
done
[ -n "$IMAGEM" ] || { echo "ERRO: falta --imagem <copia.bin>" >&2; exit 2; }
[ -f "$IMAGEM" ] || { echo "ERRO: nao existe: $IMAGEM" >&2; exit 2; }
case "$(readlink -f "$IMAGEM")" in
  "$RAIZ/roms/"*)
    echo "ERRO: $IMAGEM esta em roms/. O app grava in-place -- copie antes." >&2
    exit 2 ;;
esac

# shellcheck source=/dev/null
. "$AQUI/roteiro.sh"
roteiro_display

TMP=""
if [ -z "$PREFIXO" ]; then
  TMP="$(mktemp -d)"; PREFIXO="$TMP/prefixo"
fi
TRACE="$(mktemp -d)/trace.log"
APP_PID=""
limpa() {
  [ -n "$APP_PID" ] && kill "$APP_PID" 2>/dev/null || true
  pkill -f "$PREFIXO/bin/$SLUG" 2>/dev/null || true
  [ "$MANTER" = 1 ] || { [ -n "$TMP" ] && rm -rf "$TMP"; }
  rm -rf "$(dirname "$TRACE")"
}
trap limpa EXIT

FALHAS=0
registra() {   # medida valor veredito
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$SAIDA"
  printf '%-12s %-9s %s\n' "$1" "$3" "$2"
  [ "$3" = ok ] || FALHAS=$((FALHAS + 1))
}

printf 'medida\tvalor\tveredito\n' > "$SAIDA"

# ------------------------------------------------------------- instalacao ----
echo ">> instalando em $PREFIXO"
make -C "$WTE" install PREFIX="$PREFIXO" >/dev/null
BIN="$PREFIXO/bin/$SLUG"
[ -x "$BIN" ] || { echo "ERRO: o install nao produziu $BIN" >&2; exit 1; }

# Os assets do Obocaman NAO sao instalados (WTE-TASK-38) -- quem os poe la e o
# usuario, e e o candidato 3 da busca do `wte_datafiles`. Aqui o script faz o
# papel do usuario, para medir justamente esse candidato.
if [ -f "$RAIZ/we-team-editor/data/dat.bin" ]; then
  cp -r "$RAIZ/we-team-editor/image" "$RAIZ/we-team-editor/data" \
        "$PREFIXO/share/$SLUG/"
else
  echo "ERRO: faltam os assets em $RAIZ/we-team-editor/" >&2
  exit 1
fi

# ----------------------------------------------------------------- estatico --
formato="$(file -b "$BIN")"
case "$formato" in
  *"ELF 64-bit"*x86-64*) registra formato "ELF 64-bit x86-64" ok ;;
  *) registra formato "$formato" FALHOU ;;
esac

libs="$(ldd "$BIN")"
n_wine="$(printf '%s\n' "$libs" | grep -ciE 'wine|bottles' || true)"
n_32="$(printf '%s\n' "$libs" | grep -ciE 'i386|lib32' || true)"
n_libs="$(printf '%s\n' "$libs" | grep -c '=>' || true)"
[ "$n_wine" = 0 ] && registra ldd-wine "0 de $n_libs bibliotecas" ok \
                  || registra ldd-wine "$n_wine com wine/bottles" FALHOU
[ "$n_32" = 0 ]   && registra ldd-32 "0 de $n_libs bibliotecas" ok \
                  || registra ldd-32 "$n_32 de 32 bits" FALHOU

# ----------------------------------------------------------------- dinamico --
# A guarda do `sem_wine.sh` e a medida 4: ele RECUSA se `wine` ainda responder
# dentro do namespace, entao um `sem_wine.sh -- true` que sai 0 ja a mede.
if bash "$AQUI/sem_wine.sh" -- true >/dev/null 2>&1; then
  registra guarda "wine/wine64/wineserver ausentes" ok
else
  registra guarda "o namespace nao ficou sem Wine" FALHOU
fi

echo ">> abrindo o app sob o namespace, em $DISPLAY"
bash "$AQUI/sem_wine.sh" -- env DISPLAY="$DISPLAY" \
     XAUTHORITY="${XAUTHORITY:-}" WTE_TRACE_FILE="$TRACE" \
     "$BIN" "$IMAGEM" >"$(dirname "$TRACE")/app.log" 2>&1 &
APP_PID=$!

if ID="$(espera_janela "$(printf '%s' "$TITULO" | sed 's/[][\\.*^$]/\\&/g')" 40)"; then
  geo="$(xdotool getwindowgeometry "$ID" | sed -n 's/.*Geometry: //p')"
  [ "$geo" = "$GEOMETRIA" ] \
    && registra janela "$geo, titulo conferido" ok \
    || registra janela "geometria $geo, esperada $GEOMETRIA" FALHOU
else
  registra janela "nao apareceu em 40s" FALHOU
  ID=""
fi

if [ -n "$ID" ]; then
  xdotool windowfocus "$ID" 2>/dev/null || true
  sleep 1
  for _ in $(seq "$TECLAS"); do xdotool key --window "$ID" Down; sleep 1; done
  sleep 2
  n_carga="$(grep -c 'lista_equiposChange' "$TRACE" || true)"
  [ "$n_carga" = "$TECLAS" ] \
    && registra carga "$n_carga cargas de time para $TECLAS teclas" ok \
    || registra carga "$n_carga cargas para $TECLAS teclas" FALHOU

  # O processo VIVO: `ldd` mede o que o linkeditor pediu, `maps` mede o que o
  # processo abriu -- inclusive o que ele carregasse por `dlopen`.
  vivo="$(pgrep -f "$PREFIXO/bin/$SLUG" | head -1)"
  if [ -n "$vivo" ]; then
    n_maps="$(grep -ciE 'wine|bottles|i386|lib32' "/proc/$vivo/maps" || true)"
    [ "$n_maps" = 0 ] \
      && registra maps "0 mapeamentos de Wine ou 32 bits" ok \
      || registra maps "$n_maps mapeamentos suspeitos" FALHOU
  else
    registra maps "o processo nao estava vivo para medir" FALHOU
  fi
fi

echo
if [ "$FALHAS" = 0 ]; then
  echo ">> condicao 3: as 7 medidas passaram. Registro em ${SAIDA#$RAIZ/}"
else
  echo ">> condicao 3: $FALHAS medida(s) reprovaram. Ver ${SAIDA#$RAIZ/}" >&2
fi
exit "$FALHAS"
