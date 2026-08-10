#!/usr/bin/env bash
# golden_check.sh -- O GATE da fase 4: o `wte.exe` contra o app Lazarus.
#
#   bash wte/tools/golden_check.sh <roteiro> [opcoes]
#
#     --modo controle|golden|positivo   (padrao: golden)
#     --roteiro-port <arquivo>          roteiro do lado port, se diferir
#     --imagem <rom>                    padrao: roms/japanese-shift-jis.bin
#     --plantar <offset>                so no modo positivo (padrao: 405228)
#     --manter                          nao apaga o temporario
#
# Nenhum handler da fase 4 entra sem este script verde. Ele vem ANTES dos
# handlers de proposito: sem gate, cada implementacao e opiniao.
#
# ## Os tres modos, e por que o `controle` nao e opcional
#
# | modo | lado A | lado B | o que prova |
# |---|---|---|---|
# | `controle` | oraculo | oraculo | que o par roteiro+imagem e DETERMINISTICO |
# | `positivo` | oraculo | oraculo, com um byte plantado | que o gate DETECTA |
# | `golden` | oraculo | app Lazarus | a pergunta de verdade |
#
# Verde e vermelho nao significam nada sem os dois primeiros. Zero divergencia
# no `golden` pode ser paridade -- ou pode ser que nenhum dos dois lados gravou
# nada; o `controle` mostra que o oraculo grava, e o `positivo` mostra que um
# byte diferente e visto e localizado.
#
# ## As quatro guardas herdadas do `tools/golden_check.sh` do newWe2002
#
# 1. `DISPLAY=:99` fixado aqui dentro, nunca herdado do shell;
# 2. recusa comecar com janela grande ja aberta no `:99`;
# 3. so dirige janela do processo lancado (`_NET_WM_PID`, no `roteiro.sh`);
# 4. `roms/` nunca e alvo -- copia, sempre, e as copias sao apagadas no fim.
#
# ## A imagem e a japonesa, e trocar por habito devolve o travamento
#
# Com a europeia o `wte.exe` morre ao trocar de time: 49.749 violacoes de
# acesso contra 0 (CORR-WTE-044, `wte/re/crash-causa.md`). O lado oraculo
# reprova com codigo 4 se achar `c0000005` no log -- oraculo que morreu no meio
# grava menos, e o diff sairia menor.
#
# ## Custo
#
# Duas copias da imagem por rodada. Com a japonesa sao ~586 MB de temporario;
# com a europeia seriam ~950 MB. Nao roda em CI -- precisa de Wine, do `:99` e
# do binario do Obocaman, que e gitignored.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"

ROTEIRO="${1:?uso: golden_check.sh <roteiro> [--modo controle|golden|positivo]}"
shift || true
MODO=golden
ROTEIRO_PORT=""
IMAGEM="$RAIZ/roms/japanese-shift-jis.bin"
PLANTAR=405228          # dentro da regiao de dados do setor 172, longe do arranque
MANTER=0
while [ $# -gt 0 ]; do
  case "$1" in
    --modo)         MODO="$2"; shift 2 ;;
    --roteiro-port) ROTEIRO_PORT="$2"; shift 2 ;;
    --imagem)       IMAGEM="$2"; shift 2 ;;
    --plantar)      PLANTAR="$2"; shift 2 ;;
    --manter)       MANTER=1; shift ;;
    *) echo "opcao desconhecida: $1" >&2; exit 2 ;;
  esac
done
case "$MODO" in controle|golden|positivo) : ;;
  *) echo "modo desconhecido: $MODO" >&2; exit 2 ;;
esac
[ -n "$ROTEIRO_PORT" ] || ROTEIRO_PORT="$ROTEIRO"

# shellcheck source=roteiro.sh
. "$AQUI/roteiro.sh"
roteiro_display          # guarda 1

for f in "$ROTEIRO" "$ROTEIRO_PORT" "$IMAGEM" \
         "$RAIZ/we-team-editor/we-team-editor.exe"; do
  [ -e "$f" ] || { echo "ERRO: falta $f" >&2; exit 1; }
done

# Guarda 2: janela grande ja aberta no :99. Uma sobra de teste manual e dirigida
# no lugar da que esta sob teste, e o resultado e um diff de bytes que parece
# bug do port. O piso e 400x300: o MainForm do wte.exe e 522x475 e o do port
# tem o mesmo tamanho, e nenhum dialogo do app chega perto disso.
if command -v xwininfo >/dev/null 2>&1; then
  while read -r linha; do
    [[ "$linha" =~ ([0-9]+)x([0-9]+)\+ ]] || continue
    if [ "${BASH_REMATCH[1]}" -ge 400 ] && [ "${BASH_REMATCH[2]}" -ge 300 ]; then
      echo "ERRO: ja ha janela grande em $DISPLAY:" >&2
      echo "  $linha" >&2
      echo "  Feche antes ('wineserver -k' para o oraculo). Os dois lados acham" >&2
      echo "  janela por nome e por tamanho, e dirigiriam a errada." >&2
      exit 1
    fi
  done < <(xwininfo -root -children 2>/dev/null | grep -F '": (')
fi

# Guarda 4: `roms/` nunca e alvo. As copias moram em work/, que e a unidade E:
# do prefix -- o dialogo de abrir do original nao engole caminho longo.
WORK="$RAIZ/work"
mkdir -p "$WORK"
A="$WORK/golden-a.bin"
B="$WORK/golden-b.bin"
SAIDA="$(mktemp -d)"
limpar() {
  [ "$MANTER" = 1 ] && { echo ">> temporario mantido: $SAIDA"; return; }
  rm -f "$A" "$B"; rm -rf "$SAIDA"
}
trap limpar EXIT

echo ">> modo $MODO, roteiro $(basename "$ROTEIRO"), imagem $(basename "$IMAGEM")"
echo ">> copiando (roms/ nunca e alvo)"
cp -f "$IMAGEM" "$A"
cp -f "$A" "$B"

echo ">> lado A: oraculo"
bash "$AQUI/golden_run_wte.sh" "$ROTEIRO" "$A" "$SAIDA"

case "$MODO" in
  controle|positivo)
    echo ">> lado B: oraculo de novo (o controle e original contra original)"
    bash "$AQUI/golden_run_wte.sh" "$ROTEIRO" "$B" "$SAIDA"
    ;;
  golden)
    echo ">> lado B: app Lazarus"
    bash "$AQUI/golden_run_laz.sh" "$ROTEIRO_PORT" "$B" "$SAIDA"
    ;;
esac

if [ "$MODO" = positivo ]; then
  # O positivo planta UM byte depois das duas corridas, e nao antes: plantado
  # antes, o editor poderia sobrescrever justamente aquele byte e o teste
  # provaria o contrario do que quer provar.
  echo ">> plantando um byte em $PLANTAR"
  python3 - "$B" "$PLANTAR" <<'PY'
import sys
caminho, pos = sys.argv[1], int(sys.argv[2])
with open(caminho, "r+b") as fh:
    fh.seek(pos)
    b = fh.read(1)
    fh.seek(pos)
    fh.write(bytes([b[0] ^ 0xFF]))
print(f"   {pos}: {b[0]:#04x} -> {b[0] ^ 0xFF:#04x}")
PY
fi

echo ">> comparando"
# O comparador e o do newWe2002 -- os dois projetos nao compartilham build, mas
# compartilham FORMATO: ele le o mesmo Offsets.hpp e a mesma geometria
# MODE2/2352. Copiar as 186 linhas para ca criaria a segunda copia que
# envelhece sozinha.
python3 "$RAIZ/tools/golden_compare.py" --json "$A" "$B" > "$SAIDA/diff.json" || true

set +e
if [ "$MODO" = positivo ]; then
  python3 "$AQUI/golden_veredito.py" "$SAIDA/diff.json" --nenhuma
  codigo=$?
  if [ "$codigo" = 1 ]; then
    echo "OK: o gate DETECTOU o byte plantado."
    exit 0
  fi
  echo "FALHOU: o byte plantado passou despercebido -- o gate nao mede nada." >&2
  exit 1
fi
if [ "$MODO" = controle ]; then
  # O controle e oraculo contra oraculo: os dois gravam os MESMOS bytes, entao
  # a faixa declarada do roteiro nao vale aqui. Ela existe para o `golden`, que
  # compara com o port -- declarar no controle exigiria que a divergencia
  # aparecesse, e ela nao aparece por construcao.
  python3 "$AQUI/golden_veredito.py" "$SAIDA/diff.json" --nenhuma
else
  python3 "$AQUI/golden_veredito.py" "$SAIDA/diff.json" --roteiro "$ROTEIRO"
fi
codigo=$?
set -e
exit "$codigo"
