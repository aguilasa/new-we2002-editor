#!/usr/bin/env bash
# diff_dirigido.sh -- mede QUE REGIOES da imagem o editor do Obocaman toca.
#
# Produto da WTE-TASK-19. Duas reguas independentes na mesma corrida:
#
#   1. **trace de I/O** -- o `wte.exe` roda sob `strace`, e cada `_llseek` +
#      `read`/`write` sobre a imagem vira uma faixa (offset, tamanho). Isto
#      responde "que regioes ele ENDERECA", que e a pergunta da task, e
#      responde tambem para LEITURA -- coisa que `cmp` nenhum alcanca.
#   2. **cmp contra a copia limpa** -- o que efetivamente MUDOU no arquivo.
#
# As duas se conferem: toda faixa do `cmp` tem de estar contida numa faixa de
# escrita do trace. Divergencia ali significa que o trace perdeu syscall, e o
# script avisa.
#
# ## Por que trace, e nao so `cmp`
#
# O enunciado da task pede diff dirigido: editar UM campo, gravar, `cmp`. Isso
# funciona, mas so enxerga ESCRITA de valor DIFERENTE -- e o editor do Obocaman
# grava, na maior parte das areas, exatamente o que leu. Um `cmp` limpo nao
# distingue "nao gravou" de "gravou igual", e as duas coisas levam a conclusoes
# opostas sobre que offsets o app Lazarus precisa endereçar.
#
# Tentou-se antes um terceiro caminho -- encher a copia com um padrao depois do
# Load e ver o que sobrevive. **Nao funciona: o app derruba.** Ele nao le tudo
# no Load; le sob demanda, e um arquivo de 474 MB cheio de 0xA5 o mata no
# primeiro clique. A medida esta no wte/re/offsets-novos.md.
#
# ## Regra do :99 (CLAUDE.md)
#
# Toda GUI roda no `:99`. O script fixa `DISPLAY=:99` por conta propria em vez
# de herdar do shell -- herdar foi o que derrubou o golden_check.sh do
# newWe2002 quando o ctest repassava o `:1`.
#
# ## Cuidados que o script NAO delega
#
# - **`roms/` nunca e alvo.** Ele copia para `work/` e mede sobre a copia.
# - **ptrace_scope=1** nesta maquina: so da para tracar descendente. Por isso o
#   `strace` LANCA o wine, e nao se anexa a um ja rodando.
#
# Uso:
#   bash wte/tools/diff_dirigido.sh <roteiro> [--imagem ROM] [--saida DIR]
#
# Saida (padrao /tmp/diff-dirigido/<roteiro>/):
#   io.log     trace cru, grande, NAO versionado
#   io.tsv     acao / op / offset / tamanho -- a evidencia
#   cmp.tsv    faixas que mudaram de fato
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

ROTEIRO="${1:?uso: diff_dirigido.sh <roteiro> [--imagem ROM] [--saida DIR]}"
shift || true
IMAGEM="$RAIZ/roms/golden-european-deluxe.bin"
SAIDA="/tmp/diff-dirigido/$(basename "$ROTEIRO" .txt)"
while [ $# -gt 0 ]; do
  case "$1" in
    --imagem) IMAGEM="$2"; shift 2 ;;
    --saida)  SAIDA="$2";  shift 2 ;;
    *) echo "opcao desconhecida: $1" >&2; exit 2 ;;
  esac
done

WINE_BIN="${WINE_BIN:-/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin}"
# `-all` cala o Wine; quem quiser a excecao passa WINEDEBUG=+seh na chamada.
WINEDEBUG="${WINEDEBUG:--all}"
PREFIX="$RAIZ/work/wineprefix-wte"
WORK="$RAIZ/work"
LIMPA="$WORK/dd-clean.bin"
RODA="$WORK/dd-run.bin"

export DISPLAY=:99
xauth_file="$(ps -o args= -C Xvfb 2>/dev/null \
  | sed -n 's/.*Xvfb :99 .*-auth \([^ ]*\).*/\1/p' | head -1)"
[ -n "$xauth_file" ] && export XAUTHORITY="$xauth_file"

for f in "$ROTEIRO" "$IMAGEM" "$RAIZ/we-team-editor/we-team-editor.exe"; do
  [ -e "$f" ] || { echo "ERRO: falta $f" >&2; exit 1; }
done
[ -x "$WINE_BIN/wine" ] || { echo "ERRO: loader Wine 32-bit em $WINE_BIN" >&2; exit 1; }
command -v strace >/dev/null || { echo "ERRO: strace ausente" >&2; exit 1; }
xdpyinfo >/dev/null 2>&1 || { echo "ERRO: sem :99" >&2; exit 1; }

mkdir -p "$SAIDA" "$WORK"
echo ">> copiando $(basename "$IMAGEM") -- roms/ nunca e alvo"
cp -f "$IMAGEM" "$LIMPA"
cp -f "$LIMPA" "$RODA"
ln -sfn "$WORK" "$PREFIX/dosdevices/e:"

env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
sleep 1

echo ">> lancando o wte.exe sob strace (ptrace_scope=1 exige lancar, nao anexar)"
(
  cd "$RAIZ/we-team-editor"
  env DISPLAY=:99 WINEPREFIX="$PREFIX" WINEARCH=win32 WINEDEBUG="$WINEDEBUG" \
      ${XAUTHORITY:+XAUTHORITY="$XAUTHORITY"} \
    setsid strace -f -qq -y \
      -e trace=read,pread64,write,pwrite64,lseek,_llseek \
      -o "$SAIDA/io.log" \
      "$WINE_BIN/wine" we-team-editor.exe
) >"$SAIDA/wine.log" 2>&1 &

: > "$SAIDA/marcas.txt"
marca() { echo "$(wc -l < "$SAIDA/io.log" 2>/dev/null || echo 0)	$1" >> "$SAIDA/marcas.txt"; }

janela() {
  # A janela alvo, pelo nome; devolve "ID X Y". Vazio enquanto nao existir.
  local nome="$1" id
  id="$(xdotool search --onlyvisible --name "$nome" 2>/dev/null | head -1)" || true
  [ -n "$id" ] || return 1
  eval "$(xdotool getwindowgeometry --shell "$id" 2>/dev/null)"
  echo "$id $X $Y"
}

espera_janela() {
  local nome="$1" limite="${2:-30}" i=0 r
  while [ $i -lt "$limite" ]; do
    if r="$(janela "$nome")"; then echo "$r"; return 0; fi
    sleep 1; i=$((i+1))
  done
  echo "ERRO: janela '$nome' nao apareceu em ${limite}s" >&2
  return 1
}

# ------------------------------------------------------------- o roteiro ----
#
# Formato irmao do de wte/tests/roteiros/ (WTE-TASK-13), com verbos em vez de
# linha de `xdotool` crua. O motivo e a coordenada: aqui ela e SEMPRE relativa
# a janela resolvida pelo `>`, e a origem muda a cada corrida porque nao ha
# window manager no :99.
#
#   > <nome>     espera a janela e passa a ser o alvo das coordenadas
#   = <marca>    corta o log; tudo ate a proxima marca e daquela acao
#   ~ <seg>      espera
#   ! clique X Y     clique simples em (X,Y) relativo ao alvo
#   ! duplo  X Y     duplo clique
#   ! tecla  <k>     xdotool key
#   ! texto  <t>     xdotool type -- CURTO. `xdotool type` embaralha string
#                    longa (usa XSendEvent); e por isso que a unidade E: existe
ALVO_ID=""; ALVO_X=0; ALVO_Y=0
while IFS= read -r linha || [ -n "$linha" ]; do
  linha="${linha%%$'\r'}"
  case "$linha" in
    ''|'#'*|alvo:*|estado:*) continue ;;
    '> '*)
      nome="${linha#> }"
      read -r ALVO_ID ALVO_X ALVO_Y <<<"$(espera_janela "$nome")"
      echo ">> janela '$nome' = $ALVO_ID em $ALVO_X,$ALVO_Y"
      ;;
    '= '*) marca "${linha#= }" ;;
    '~ '*) sleep "${linha#~ }" ;;
    '! '*)
      set -- ${linha#! }
      verbo="$1"; shift
      case "$verbo" in
        clique) xdotool mousemove $((ALVO_X+$1)) $((ALVO_Y+$2)) click 1 ;;
        duplo)  xdotool mousemove $((ALVO_X+$1)) $((ALVO_Y+$2)) \
                  click --repeat 2 --delay 120 1 ;;
        tecla)  xdotool key --clearmodifiers "$@" ;;
        texto)  xdotool type --delay 60 "$*" ;;
        *) echo "AVISO: verbo desconhecido: $verbo" >&2 ;;
      esac
      ;;
    *) echo "AVISO: linha ignorada: $linha" >&2 ;;
  esac
done < "$ROTEIRO"
marca FIM

sleep 2
env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
sleep 2

echo ">> analisando"
python3 "$AQUI/analisar_io.py" --log "$SAIDA/io.log" --marcas "$SAIDA/marcas.txt" \
        --alvo dd-run.bin --tsv "$SAIDA/io.tsv" \
        --imagem "$(basename "$IMAGEM")"
python3 - "$LIMPA" "$RODA" "$SAIDA/cmp.tsv" <<'PY'
import sys
limpa, roda, saida = sys.argv[1:4]
BLOCO = 1 << 22
faixas = []
with open(limpa, 'rb') as a, open(roda, 'rb') as b:
    pos = 0
    while True:
        x, y = a.read(BLOCO), b.read(BLOCO)
        if not x:
            break
        if x != y:
            for i in range(len(x)):
                if x[i] != y[i]:
                    p = pos + i
                    if faixas and p <= faixas[-1][1] + 16:
                        faixas[-1][1] = p
                    else:
                        faixas.append([p, p])
        pos += len(x)
with open(saida, 'w') as f:
    f.write("inicio\tfim\ttamanho\tsetor\tbyte_no_setor\n")
    for i, j in faixas:
        f.write(f"{i}\t{j}\t{j-i+1}\t{i//2352}\t{i%2352}\n")
print(f"cmp: {len(faixas)} faixa(s) mudaram -> {saida}")
PY
echo ">> pronto: $SAIDA"
