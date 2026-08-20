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
# As duas se conferem, e a conferencia e feita de verdade no fim da corrida
# (`analisar_io.py --conferir`): toda faixa do `cmp` tem de estar contida numa
# faixa de escrita do trace. Divergencia ali significa que o trace perdeu
# syscall -- e ja significou duas vezes:
#
#   - a marca era numero de linha, e o `strace` bufferiza o log: `wc -l` no
#     instante da marca fica ATRAS das syscalls que ja aconteceram. Virou
#     relogio (`-tt`);
#   - o parser ignorava syscall partida em `<unfinished ...>` + `<... resumed>`,
#     que sobre a imagem e a MAIORIA delas -- 1.529 numa sessao so.
#
# Os dois passavam despercebidos: o TSV saia com menos faixa e ninguem via.
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
# Toda GUI roda no `:98`. O script fixa `DISPLAY` por conta propria em vez
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
#
# O `cmp.tsv` e fundido em wte/re/cmp-medido.tsv, que E versionado -- ele nao
# se regenera sem Wine, como o io-medido.tsv (CORR-WTE-047).
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

# O driver de roteiro e o mesmo do gate golden (WTE-TASK-22): dialeto, busca de
# janela e a fixacao do `:99` moram em `roteiro.sh`. Duas copias divergiriam em
# silencio, e o sintoma seria diff de bytes com cara de bug do port.
# shellcheck source=roteiro.sh
. "$AQUI/roteiro.sh"
roteiro_display

for f in "$ROTEIRO" "$IMAGEM" "$RAIZ/we-team-editor/we-team-editor.exe"; do
  [ -e "$f" ] || { echo "ERRO: falta $f" >&2; exit 1; }
done
[ -x "$WINE_BIN/wine" ] || { echo "ERRO: loader Wine 32-bit em $WINE_BIN" >&2; exit 1; }
command -v strace >/dev/null || { echo "ERRO: strace ausente" >&2; exit 1; }

mkdir -p "$SAIDA" "$WORK"
# Arquivo que um roteiro manda o `wte.exe` GRAVAR dentro de work/ (que e a
# unidade E: do prefix). Tem de sair antes da corrida: com ele no lugar, o
# TSaveDialog abre a confirmacao de sobrescrita, que nenhum roteiro fixo espera
# -- e a corrida morre esperando a janela seguinte. Custou uma sessao inteira
# na 5a passagem da WTE-TASK-19.
rm -f "$WORK/u.bmp"
echo ">> copiando $(basename "$IMAGEM") -- roms/ nunca e alvo"
cp -f "$IMAGEM" "$LIMPA"
cp -f "$LIMPA" "$RODA"
ln -sfn "$WORK" "$PREFIX/dosdevices/e:"

env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
sleep 1

echo ">> lancando o wte.exe sob strace (ptrace_scope=1 exige lancar, nao anexar)"
(
  cd "$RAIZ/we-team-editor"
  env DISPLAY="$DISPLAY" WINEPREFIX="$PREFIX" WINEARCH=win32 WINEDEBUG="$WINEDEBUG" \
      ${XAUTHORITY:+XAUTHORITY="$XAUTHORITY"} \
    setsid strace -f -qq -y -tt \
      -e trace=read,pread64,write,pwrite64,lseek,_llseek \
      -o "$SAIDA/io.log" \
      "$WINE_BIN/wine" we-team-editor.exe
) >"$SAIDA/wine.log" 2>&1 &

: > "$SAIDA/marcas.txt"
# A marca e RELOGIO, e nao numero de linha. O `strace` bufferiza o arquivo de
# log, entao `wc -l` no instante da marca fica ATRAS das syscalls que ja
# aconteceram -- e a atribuicao "esta faixa e daquela acao" sai errada em
# silencio. Foi assim que sete escritas do arranque viraram duas no TSV
# enquanto o `cmp` continuava mostrando as sete. Com `-tt` cada linha carrega o
# proprio instante, e o corte deixa de depender de quando o buffer foi ao
# disco.
marca() { echo "$(date +%H:%M:%S.%6N)	$1" >> "$SAIDA/marcas.txt"; }

# ------------------------------------------------------------- o roteiro ----
#
# O dialeto e o driver estao em `roteiro.sh`. Aqui so se liga a marca de corte:
# `= <marca>` tem de cortar o log de I/O, e o gancho existe para isto.
roteiro_marca() { marca "$1"; }
roteiro_executa "$ROTEIRO"
marca FIM

sleep 2
env WINEPREFIX="$PREFIX" "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
sleep 2

echo ">> analisando"
# A sessao e o nome do diretorio de saida, e nao o do roteiro: o mesmo roteiro
# roda mais de uma vez com uma variavel trocada (foi assim que a hipotese do
# tamanho caiu -- `06-diff-dirigido` contra `06-truncada`), e as duas corridas
# precisam ficar distinguiveis no `io-medido.tsv`. Sem isso, a imagem seria a
# unica chave, e duas sessoes sobre a MESMA imagem virariam uma tabela so.
python3 "$AQUI/analisar_io.py" --log "$SAIDA/io.log" --marcas "$SAIDA/marcas.txt" \
        --alvo dd-run.bin --tsv "$SAIDA/io.tsv" \
        --imagem "$(basename "$IMAGEM")" --sessao "$(basename "$SAIDA")"
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
python3 "$AQUI/analisar_io.py" --conferir "$SAIDA/io.tsv" "$SAIDA/cmp.tsv"
# A segunda regua tem de deixar rastro versionado, e nao so passar na tela: o
# `cmp.tsv` mora em /tmp e some, e das cinco primeiras sessoes so uma teve o
# numero registrado -- em prosa, no Log de uma passagem (CORR-WTE-047). A
# fusao e pela mesma porta por onde o trace entra no `io-medido.tsv`.
python3 "$AQUI/analisar_io.py" --fundir-cmp "$SAIDA/cmp.tsv" \
        --imagem "$(basename "$IMAGEM")" --sessao "$(basename "$SAIDA")"
# E a PRIMEIRA regua tinha a mesma doenca, sem ninguem ter notado: o `io.tsv`
# tambem mora em /tmp, e chegava ao `io-medido.tsv` a mao. Medido na
# WTE-TASK-27 -- 39 faixas de uma sessao que nao entrariam sozinhas.
python3 "$AQUI/analisar_io.py" --fundir-io "$SAIDA/io.tsv" \
        --sessao "$(basename "$SAIDA")"
echo ">> pronto: $SAIDA"
echo ">> lembre de commitar wte/re/cmp-medido.tsv e wte/re/io-medido.tsv --"
echo ">> eles nao se regeneram sem Wine"
