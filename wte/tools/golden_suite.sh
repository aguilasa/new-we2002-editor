#!/usr/bin/env bash
# golden_suite.sh -- a bateria golden completa. Produto da WTE-TASK-34.
#
#   bash wte/tools/golden_suite.sh [opcoes]
#
#     --rom japonesa|europeia|ambas   (padrao: ambas)
#     --roteiro <nome>               so este, repetivel (padrao: todos com par)
#     --saida <tsv>                  padrao: wte/re/golden.tsv
#     --retomar                      pula o que ja esta registrado no TSV
#     --listar                       nao roda nada; imprime o plano e sai
#
# ## O que ela e, e o que o `golden_check.sh` nao e
#
# O `golden_check.sh` julga UM roteiro. Ate a WTE-TASK-31 a bateria inteira era
# ele mais um operador: 42 invocacoes a mao, e o resultado transcrito para o
# `fase-4-golden.tsv` depois. Duas coisas nao sobrevivem a esse arranjo -- a
# reproducao (a proxima pessoa nao sabe a lista nem a ordem) e a fixture (o
# operador aponta para o que estiver em `work/`).
#
# Esta bateria e o mesmo julgamento, versionado: a lista sai do disco, a ordem
# e a alfabetica, cada par roda `controle` ANTES de `golden`, e o resultado cai
# no TSV linha a linha, enquanto roda.
#
# ## O controle vem antes do teste, e aqui isso e mecanico
#
# Zero divergencia no `golden` pode ser paridade -- ou pode ser que nenhum dos
# dois lados gravou nada. O `controle` (oraculo contra oraculo) mostra que o
# par roteiro+imagem e deterministico. Esta bateria RECUSA registrar um
# `golden` cujo `controle` nao tenha passado na mesma corrida: sem ele, verde e
# vermelho nao significam nada.
#
# ## A fixture e CRIADA, nunca encontrada
#
# A licao esta escrita no Log da primeira passagem da WTE-TASK-31, e custou uma
# corrida de bateria inteira. O `golden-06-textura` reprovou nos dois lados com
# `ERRO: janela 'W11 TE PT' nao apareceu em 30s` -- assinatura de falha de
# TEMPO. Nao era: o roteiro exige que `work/t.bin` seja o arquivo sintetico de
# 5.000 bytes, e `work/` tinha um `t.bin` de 307 MB, copia de ROM deixada por
# outra corrida. O editor engasgava, e o dialogo do fim nunca vinha.
#
# `work/` e rascunho compartilhado e nome de fixture colide com nome de copia
# de trabalho. Por isso cada roteiro DECLARA o que precisa, no cabecalho:
#
#   fixture: t.bin 5000 sintetica       <- a bateria CRIA, deterministica
#   fixture: entrada.mcr 131072 exigida <- a bateria CONFERE o tamanho e ABORTA
#   ambiente: WTE_TEXTURA=work/t.bin    <- exportada, com `work/` resolvido
#   artefato: saida.mcr                 <- passado como `--artefato`
#
# E a guarda que impede a receita de voltar para o comentario: roteiro cujo
# cabecalho MENCIONA `--artefato` ou `WTE_` em comentario e nao tem a chave
# correspondente ABORTA a bateria, com o nome do arquivo.
#
# ## As duas ROMs, e por que a resposta nao e simetrica
#
# O criterio da task diz "nas duas ROMs". A europeia mata o oraculo ao trocar
# de time -- `0x00010001` no lugar do ponteiro de `dorsal1`, porque a carga do
# time escreve alem do fim da tabela de `0x00433580` (`wte/re/crash-causa.md`).
# Oraculo que morre no meio grava MENOS, e o diff sairia menor: um verde ali
# seria mentira, nao paridade.
#
# A bateria nao decide isso por prosa. Ela RODA a europeia e registra o que
# aconteceu, roteiro a roteiro -- o `golden_check.sh` ja reprova com codigo 4
# ao achar `c0000005` no log do oraculo, e esse codigo vira o veredito
# `SEM_ORACULO` no TSV. A diferenca entre "nao medimos" e "medimos e o oraculo
# nao existe daquele lado" e a task inteira.
#
# ## Excecao nomeada: nao ha nenhuma, e isso e afirmacao medida
#
# Um roteiro pode declarar `conhecida: a..b` no cabecalho -- uma faixa de bytes
# que os dois lados divergem DE PROPOSITO, e que o `golden_veredito.py` aceita
# em vez de reprovar. Hoje **nenhum dos 23 declara**, e as 92 corridas da
# WTE-TASK-34 fecharam com zero `REPROVOU`.
#
# Nem sempre foi assim: ate 2026-08-20 dois roteiros declaravam as faixas do
# arranque que o oraculo gravava e o port nao, e a oitava passagem da
# WTE-TASK-27 portou os dois remendos. O `golden_veredito.py` REPROVA faixa
# declarada que nao aparece, entao a ausencia delas hoje e medida, nao omissao.
#
# **Ao acrescentar uma `conhecida:`, abra a entrada em
# `wte/re/divergencias.md` junto.** O `check_divergencias.py` -- que o
# `make -C wte check` roda -- aborta se aparecer faixa sem entrada: excecao no
# golden sem registro e buraco, e e o que a WTE-TASK-35 existe para impedir.
#
# ## Custo
#
# Duas copias da imagem por corrida, apagadas ao fim de cada uma. Com a
# japonesa sao ~586 MB de temporario; com a europeia, ~950 MB. Cada par
# (controle + golden) leva de 2 a 6 minutos. Nao roda em CI: precisa de Wine,
# do `:98` e do binario do Obocaman, que e gitignored.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTE="$(dirname "$AQUI")"
RAIZ="$(dirname "$WTE")"
ROTEIROS="$WTE/tests/roteiros"

ROM=ambas
SAIDA="$WTE/re/golden.tsv"
RETOMAR=0
LISTAR=0
ESCOLHIDOS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --rom)     ROM="$2"; shift 2 ;;
    --roteiro) ESCOLHIDOS+=("$2"); shift 2 ;;
    --saida)   SAIDA="$2"; shift 2 ;;
    --retomar) RETOMAR=1; shift ;;
    --listar)  LISTAR=1; shift ;;
    *) echo "opcao desconhecida: $1" >&2; exit 2 ;;
  esac
done
case "$ROM" in japonesa|europeia|ambas) : ;;
  *) echo "rom desconhecida: $ROM" >&2; exit 2 ;;
esac

declare -A IMAGEM_DE=(
  [japonesa]="$RAIZ/roms/japanese-shift-jis.bin"
  [europeia]="$RAIZ/roms/golden-european-deluxe.bin"
)
ROMS=()
case "$ROM" in
  ambas) ROMS=(japonesa europeia) ;;
  *)     ROMS=("$ROM") ;;
esac

WORK="$RAIZ/work"
mkdir -p "$WORK"

# ------------------------------------------------------------- cabecalho ----
# Le UMA chave do cabecalho do roteiro. So a linha `chave: ...` fora de
# comentario conta -- `grep` cru casaria a receita em comentario, que e
# exatamente o que esta bateria existe para nao voltar a fazer.
cabecalho() {   # $1 = arquivo, $2 = chave
  sed -n "s/^$2: *//p" "$1"
}

# A guarda: receita em comentario sem a chave correspondente.
confere_declaracao() {   # $1 = arquivo
  local f="$1" nome; nome="$(basename "$f")"
  if grep -qE '^#.*--artefato' "$f" && [ -z "$(cabecalho "$f" artefato)" ]; then
    echo "ERRO: $nome menciona --artefato em comentario e nao tem" >&2
    echo "      a chave 'artefato:' no cabecalho. A bateria le a chave," >&2
    echo "      nao o comentario -- ver o cabecalho do golden_suite.sh." >&2
    exit 1
  fi
  if grep -qE '^#.*WTE_[A-Z_]+=' "$f" && [ -z "$(cabecalho "$f" ambiente)" ]; then
    echo "ERRO: $nome menciona WTE_...= em comentario e nao tem a" >&2
    echo "      chave 'ambiente:' no cabecalho." >&2
    exit 1
  fi
}

# ------------------------------------------------------------- fixtures ----
# `sintetica` a bateria cria; `exigida` ela confere e aborta com a receita.
# Conferir o TAMANHO e o ponto: a falha por fixture errado se disfarca de falha
# por tempo, e foi assim que ela custou uma corrida inteira.
prepara_fixtures() {   # $1 = arquivo do roteiro
  local linha nome tamanho tipo alvo real
  while read -r nome tamanho tipo; do
    [ -n "$nome" ] || continue
    alvo="$WORK/$nome"
    case "$tipo" in
      sintetica)
        python3 - "$alvo" "$tamanho" <<'PY'
import sys
caminho, n = sys.argv[1], int(sys.argv[2])
# A mesma serie do cabecalho do golden-06-textura, e ela nao e arredondada de
# proposito: 5.000 nao e multiplo de 2.048, entao exercita o bloco parcial.
with open(caminho, "wb") as fh:
    fh.write(bytes((i * 7 + 3) % 251 for i in range(n)))
PY
        echo ">> fixture criada: work/$nome ($tamanho bytes)"
        ;;
      exigida)
        if [ ! -f "$alvo" ]; then
          echo "ERRO: falta a fixture work/$nome ($tamanho bytes)." >&2
          echo "      Ela e produzida por uma corrida do oraculo:" >&2
          echo "        bash wte/tools/diff_dirigido.sh \\" >&2
          echo "             wte/tests/roteiros/27-mcr.txt" >&2
          echo "        cp work/saida.mcr work/$nome" >&2
          exit 1
        fi
        real="$(stat -c%s "$alvo")"
        if [ "$real" != "$tamanho" ]; then
          echo "ERRO: work/$nome tem $real bytes, e a fixture pede $tamanho." >&2
          echo "      work/ e rascunho compartilhado: nome de fixture colide" >&2
          echo "      com nome de copia de trabalho, e o roteiro reprovaria" >&2
          echo "      com cara de falha por TEMPO. Apague e refaca." >&2
          exit 1
        fi
        echo ">> fixture conferida: work/$nome ($real bytes)"
        ;;
      *) echo "ERRO: tipo de fixture desconhecido: $tipo" >&2; exit 1 ;;
    esac
  done < <(cabecalho "$1" fixture)
}

# ------------------------------------------------------------- inventario ----
todos=()
for f in "$ROTEIROS"/golden-*.txt; do
  case "$f" in *.port.txt) continue ;; esac
  nome="$(basename "$f" .txt)"
  [ -f "$ROTEIROS/$nome.port.txt" ] || continue    # sem par nao ha o que julgar
  if [ "${#ESCOLHIDOS[@]}" -gt 0 ]; then
    achou=0
    for e in "${ESCOLHIDOS[@]}"; do
      if [ "$e" = "$nome" ]; then achou=1; fi
    done
    [ "$achou" = 1 ] || continue
  fi
  todos+=("$nome")
done
[ "${#todos[@]}" -gt 0 ] || { echo "ERRO: nenhum roteiro com par" >&2; exit 1; }

for nome in "${todos[@]}"; do
  confere_declaracao "$ROTEIROS/$nome.txt"
done

if [ "$LISTAR" = 1 ]; then
  echo "# plano: ${#todos[@]} roteiro(s) x ${#ROMS[@]} rom(s) x 2 modos"
  for r in "${ROMS[@]}"; do
    for nome in "${todos[@]}"; do
      art="$(cabecalho "$ROTEIROS/$nome.txt" artefato)"
      echo "$r	$nome	${art:-—}"
    done
  done
  exit 0
fi

# ------------------------------------------------------------------ TSV ----
if [ ! -f "$SAIDA" ] || [ "$RETOMAR" != 1 ]; then
  printf 'roteiro\trom\tmodo\tveredito\tsegundos\tdata\n' > "$SAIDA"
fi
ja_tem() {   # $1 = roteiro, $2 = rom, $3 = modo
  [ "$RETOMAR" = 1 ] || return 1
  grep -qP "^$1\t$2\t$3\t" "$SAIDA"
}

HOJE="$(date +%F)"
registra() {   # roteiro rom modo veredito segundos
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$HOJE" >> "$SAIDA"
}

# Uma corrida. Devolve o veredito por eco; nunca aborta a bateria -- roteiro que
# reprova e RESULTADO, e a tabela existe para registra-lo.
corre() {   # $1 = roteiro, $2 = rom, $3 = modo
  local nome="$1" rom="$2" modo="$3" art inicio fim codigo
  art="$(cabecalho "$ROTEIROS/$nome.txt" artefato)"
  local -a extra=()
  if [ -n "$art" ]; then extra+=(--artefato "$art"); fi

  # As variaveis do cabecalho, com `work/` resolvido para caminho absoluto --
  # o port recebe caminho, e caminho relativo dependeria do CWD de quem chamou.
  #
  # E elas sao DESEXPORTADAS no fim desta funcao, o que nao e zelo: a bateria
  # roda todos os roteiros no mesmo shell, e variavel que sobra de um vira
  # entrada silenciosa do seguinte. Um `WTE_MCR_ENTRADA` esquecido faria o port
  # importar um cartao no arranque de um roteiro que nao pediu nenhum, e o
  # veredito seria `REPROVOU` acusando o port por um estimulo que o roteiro nao
  # tem. E a mesma familia da fixture achada em vez de criada, um nivel acima.
  local amb
  local -a exportadas=()
  while read -r amb; do
    [ -n "$amb" ] || continue
    export "${amb%%=*}"="$WORK/$(basename "${amb#*=}")"
    exportadas+=("${amb%%=*}")
  done < <(cabecalho "$ROTEIROS/$nome.txt" ambiente)

  inicio=$SECONDS
  set +e
  timeout 900 bash "$AQUI/golden_check.sh" "$ROTEIROS/$nome.txt" \
    --roteiro-port "$ROTEIROS/$nome.port.txt" \
    --imagem "${IMAGEM_DE[$rom]}" \
    --modo "$modo" "${extra[@]}" >"$LOGDIR/$nome.$rom.$modo.log" 2>&1
  codigo=$?
  set -e
  fim=$((SECONDS - inicio))

  if [ "${#exportadas[@]}" -gt 0 ]; then unset "${exportadas[@]}"; fi

  case "$codigo" in
    0) echo "PASSOU $fim" ;;
    # 4 e a recusa do lado oraculo por violacao de acesso: o `wte.exe` morreu
    # no meio e gravou menos. Nao e divergencia do port -- e ausencia de
    # oraculo, e a tabela precisa dizer isso com outra palavra.
    4) echo "SEM_ORACULO $fim" ;;
    124) echo "ESTOUROU_TEMPO $fim" ;;
    *) echo "REPROVOU $fim" ;;
  esac
}

LOGDIR="$(mktemp -d)"
echo ">> logs desta corrida: $LOGDIR"
echo ">> ${#todos[@]} roteiro(s), ${ROMS[*]}, saida $SAIDA"

for rom in "${ROMS[@]}"; do
  [ -f "${IMAGEM_DE[$rom]}" ] || { echo "ERRO: falta ${IMAGEM_DE[$rom]}" >&2; exit 1; }
  for nome in "${todos[@]}"; do
    prepara_fixtures "$ROTEIROS/$nome.txt"

    if ja_tem "$nome" "$rom" controle; then
      echo ">> $rom/$nome controle: ja registrado"
      ctrl=PASSOU
    else
      read -r ctrl seg <<<"$(corre "$nome" "$rom" controle)"
      registra "$nome" "$rom" controle "$ctrl" "$seg"
      echo ">> $rom/$nome controle: $ctrl (${seg}s)"
    fi

    # O controle vem antes do teste, e isto e o mecanismo -- nao a boa vontade
    # de quem roda. Controle vermelho torna o `golden` daquele par ilegivel:
    # se o par roteiro+imagem nao e deterministico, um `golden` verde nao
    # distingue paridade de "os dois lados fizeram nada".
    if [ "$ctrl" != PASSOU ]; then
      registra "$nome" "$rom" golden NAO_APLICAVEL 0
      echo ">> $rom/$nome golden: NAO_APLICAVEL (o controle nao passou)"
      continue
    fi

    if ja_tem "$nome" "$rom" golden; then
      echo ">> $rom/$nome golden: ja registrado"
      continue
    fi
    read -r gold seg <<<"$(corre "$nome" "$rom" golden)"
    registra "$nome" "$rom" golden "$gold" "$seg"
    echo ">> $rom/$nome golden: $gold (${seg}s)"
  done
done

echo
echo ">> bateria encerrada. $(( $(wc -l < "$SAIDA") - 1 )) corrida(s) em $SAIDA"
echo ">> logs em $LOGDIR (nao sao apagados: reprovacao sem log e afirmacao sem prova)"
