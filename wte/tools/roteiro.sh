#!/usr/bin/env bash
# roteiro.sh -- o driver de roteiro, compartilhado. NAO e executavel: e
# `source`ado pelo `diff_dirigido.sh` (WTE-TASK-19) e pelos dois lados do gate
# golden (WTE-TASK-22).
#
# Existe porque os dois precisavam do MESMO dialeto e da MESMA resolucao de
# janela. Duas copias divergiriam em silencio, e o sintoma seria diff de bytes
# que parece bug do port -- exatamente o modo de falha que este projeto ja pagou
# duas vezes.
#
# ## O dialeto
#
#   > <nome>       espera a janela com esse nome e passa a ser a origem das
#                  coordenadas
#   >~ <W>x<H>     idem, pelo TAMANHO -- para o formulario que troca o proprio
#                  Caption pelo nome do time (com a ROM japonesa, Shift-JIS
#                  vira uma corrida de `?` e nao ha regex estavel)
#   = <marca>      marca de corte; quem usa e o `diff_dirigido.sh`. O gate
#                  golden a ignora, e ignorar e o certo: um roteiro serve aos
#                  dois
#   ~ <seg>        espera
#   espera: <seg>  sobe o limite da PROXIMA janela (o `>` ou `>~` seguinte).
#                  O default e o `ROTEIRO_ESPERA_PADRAO` (30s), dimensionado
#                  para maquina descarregada;
#                  passo que vem logo depois de uma acao cara precisa de mais
#                  (ver o `golden-14-uniforme.txt`). Vale so para a proxima:
#                  espera longa em todo passo esconde app que nao subiu
#   ! clique X Y   clique simples, coordenada RELATIVA a janela alvo
#   ! duplo  X Y   duplo clique
#   ! arrasta X0 Y0 X1 Y1
#                  `mousedown` em (X0,Y0), tres passos ate (X1,Y1), `mouseup`.
#                  Os passos intermediarios sao necessarios: um salto unico nao
#                  gera `OnMouseMove` em gtk2 (CORR-WTE-092)
#   ! tecla  <k>   `xdotool key`
#   ! texto  <t>   `xdotool type` -- CURTO. `xdotool type` usa `XSendEvent` e
#                  embaralha string longa; e por isso que a unidade E: existe
#
# Cabecalho (`alvo:`, `estado:`, `operacao:`, `conhecida:`) e comentario sao
# pulados aqui; quem os le e quem precisa deles.
#
# ## Coordenada e sempre relativa
#
# Sem window manager no `:98` a origem da janela muda a cada corrida. Por isso
# nenhuma linha do roteiro carrega coordenada absoluta, e por isso o `>` vem
# antes do primeiro `!`.
#
# ## O filtro por PID
#
# `roteiro_pid_alvo <pid>` restringe a busca de janela ao processo lancado --
# a terceira guarda da WTE-TASK-22. Sem ele, uma janela esquecida de um teste
# manual e dirigida no lugar da que esta sob teste. Quando o alvo nao publica
# `_NET_WM_PID` (o Wine publica; a LCL/GTK2 tambem), a restricao vira aviso e
# nao filtro -- filtrar por um atributo ausente devolveria zero janela e o
# diagnostico seria "a janela nao apareceu", que manda procurar no lugar
# errado.

ROTEIRO_PID=""          # 0 = sem filtro
ALVO_ID=""; ALVO_X=0; ALVO_Y=0

# `ROTEIRO_FOCO=1` faz o driver dar `xdotool windowfocus` na janela alvo assim
# que ela e resolvida. Vale para o lado PORT e so para ele -- ver
# `golden_run_laz.sh`. Sem gerenciador de janela no `:98` o GTK2 nunca
# considera a janela ativa sozinho, e sem foco nenhuma tecla e entregue; o
# `windowfocus` (que e `XSetInputFocus`) resolve, e o `windowactivate`, que
# precisa de gerenciador, nao.
#
# Fica atras de variavel em vez de ligado sempre porque o lado ORACULO nao
# precisa -- o Wine implementa o proprio foco -- e mexer nele invalidaria o
# controle (original contra original) sem ganho nenhum.
ROTEIRO_FOCO="${ROTEIRO_FOCO:-0}"

# Nome do arquivo que o roteiro manda digitar no dialogo de abrir. O roteiro
# escreve `E:\@IMAGEM@` e nao o nome literal, porque o gate golden roda o MESMO
# roteiro sobre DUAS copias -- uma por lado -- e cada uma tem nome proprio.
# Roteiro com nome fixo obrigaria dois roteiros, e dois roteiros deixam de ser
# a mesma entrada, que e a condicao de qualquer comparacao valer alguma coisa.
ROTEIRO_IMAGEM="${ROTEIRO_IMAGEM:-dd-run.bin}"

roteiro_display() {
  # `DISPLAY` fixo, e nao herdado: o runner de teste repassa o do shell (`:1`
  # aqui), e as janelas da sessao real derrubam a deteccao. Vale para os dois
  # lados do gate.
  #
  # O ALVO E O `:98` DESDE 2026-08-20, e antes era o `:99`. A troca foi a
  # pedido do usuario: outro projeto da mesma maquina (`World-Of-Football`)
  # mantem uma janela de 1024x768 no `:99`, e a guarda de janela grande do
  # `golden_check.sh` -- que existe justamente para nao dirigir a janela errada
  # -- recusava comecar. `WTE_DISPLAY` move de novo sem editar script nenhum.
  export DISPLAY="${WTE_DISPLAY:-:98}"
  # O cookie, quando houver. O `:98` deste projeto sobe SEM `-auth` e portanto
  # sem cookie -- `XAUTHORITY` vazio e o certo ali. A busca continua porque um
  # servidor levantado por `xvfb-run` tem cookie proprio, e sem apontar para ele
  # o Qt e o Wine morrem com `Invalid MIT-MAGIC-COOKIE-1 key`.
  local xauth alvo
  alvo="${DISPLAY#:}"
  xauth="$(ps -o args= -C Xvfb 2>/dev/null \
    | sed -n "s/.*Xvfb :$alvo .*-auth \\([^ ]*\\).*/\\1/p" | head -1)"
  if [ -n "$xauth" ]; then
    export XAUTHORITY="$xauth"
  else
    # Servidor sem `-auth` nao usa cookie, e herdar o do desktop (o
    # `/run/user/1000/gdm/Xauthority` que o shell traz) so serve para confundir
    # quem depurar depois. Vazio e o certo aqui.
    unset XAUTHORITY
  fi
  xdpyinfo >/dev/null 2>&1 || {
    echo "ERRO: sem $DISPLAY. Suba com:" >&2
    echo "  Xvfb $DISPLAY -screen 0 1280x1024x24 -nolisten tcp &" >&2
    return 1
  }
}

roteiro_pid_alvo() { ROTEIRO_PID="${1:-}"; }

# Da foco a janela alvo, se `ROTEIRO_FOCO=1`. Falha de foco NAO derruba o
# roteiro: um roteiro so de mouse funciona sem foco nenhum, e derrubar por isso
# trocaria um roteiro que roda por um erro que nao importa.
roteiro_foca() {
  [ "$ROTEIRO_FOCO" = 1 ] || return 0
  [ -n "$ALVO_ID" ] || return 0
  xdotool windowfocus "$ALVO_ID" 2>/dev/null || true
  sleep 1
}

_do_pid() {
  # 0 quando a janela pertence ao processo alvo (ou quando nao ha filtro).
  local id="$1" pid
  [ -n "$ROTEIRO_PID" ] || return 0
  pid="$(xdotool getwindowpid "$id" 2>/dev/null)" || return 0  # sem _NET_WM_PID
  [ "$pid" = "$ROTEIRO_PID" ]
}

janela() {
  # "ID X Y" da janela com esse nome. Vazio enquanto ela nao existir.
  local nome="$1" id
  for id in $(xdotool search --onlyvisible --name "$nome" 2>/dev/null); do
    _do_pid "$id" || continue
    eval "$(xdotool getwindowgeometry --shell "$id" 2>/dev/null)" || continue
    echo "$id $X $Y"
    return 0
  done
  return 1
}

janela_geo() {
  # "ID X Y" da janela com esse tamanho `<W>x<H>`. Vence a ULTIMA: o dialogo
  # recem-aberto tem o maior id.
  #
  # A ENUMERACAO NAO PODE PASSAR POR NOME. O `--name '.'` parecia inofensivo --
  # "qualquer janela com nome" --, mas o `xdotool` casa a regex contra o nome
  # ja decodificado, e janela cujo `WM_NAME` e Shift-JIS cru simplesmente nao
  # entra na lista. E exatamente o caso dos tres formularios que trocam o
  # proprio Caption pelo nome do jogador ou do time, que sao os UNICOS que
  # precisam de busca por tamanho. No `:99` o `ficha_dorsal` do port ficava
  # invisivel para o `>~` enquanto o do oraculo aparecia -- sob Wine o nome
  # decodifica, sob gtk2 nao.
  #
  # Com filtro de processo ativo, enumerar por `--pid` resolve e ainda e mais
  # estrito. Sem ele, cai no nome, que e o que sempre foi.
  local w="${1%%x*}" h="${1##*x}" id achou="" lista=""
  if [ -n "$ROTEIRO_PID" ]; then
    lista="$(xdotool search --onlyvisible --pid "$ROTEIRO_PID" 2>/dev/null)"
  fi
  [ -n "$lista" ] || lista="$(xdotool search --onlyvisible --name '.' 2>/dev/null)"
  for id in $lista; do
    _do_pid "$id" || continue
    eval "$(xdotool getwindowgeometry --shell "$id" 2>/dev/null)" || continue
    [ "$WIDTH" = "$w" ] && [ "$HEIGHT" = "$h" ] && achou="$id $X $Y"
  done
  [ -n "$achou" ] || return 1
  echo "$achou"
}

# O default da espera. Variavel para o teste poder encurta-la: sem isso, medir
# que o `espera:` vale SO para a proxima janela custaria 30s de bateria.
ROTEIRO_ESPERA_PADRAO="${ROTEIRO_ESPERA_PADRAO:-30}"

espera_janela() {
  local nome="$1" limite="${2:-$ROTEIRO_ESPERA_PADRAO}" i=0 r
  while [ $i -lt "$limite" ]; do
    if r="$(janela "$nome")"; then echo "$r"; return 0; fi
    sleep 1; i=$((i+1))
  done
  echo "ERRO: janela '$nome' nao apareceu em ${limite}s" >&2
  return 1
}

espera_geo() {
  local geo="$1" limite="${2:-$ROTEIRO_ESPERA_PADRAO}" i=0 r
  while [ $i -lt "$limite" ]; do
    if r="$(janela_geo "$geo")"; then echo "$r"; return 0; fi
    sleep 1; i=$((i+1))
  done
  echo "ERRO: janela $geo nao apareceu em ${limite}s" >&2
  return 1
}

# roteiro_marca -- gancho. Quem quiser cortar log por acao redefine isto ANTES
# de chamar `roteiro_executa`; o padrao nao faz nada, que e o que o gate quer.
roteiro_marca() { :; }

# Diagnostico de espera estourada. As duas falhas mandam procurar em lugares
# diferentes, e ate a WTE-TASK-29 a mensagem era a mesma: se a PRIMEIRA janela
# do roteiro nunca aparece, quem nao subiu foi o app (log do Wine, ou da LCL);
# se uma janela ja tinha sido achada, o app esta vivo e o que nao veio foi o
# dialogo daquele passo.
roteiro_diagnostico() {
  local nome="$1"
  if [ "$ROTEIRO_ACHOU" -eq 0 ]; then
    echo "ERRO: o app nao subiu -- a PRIMEIRA janela do roteiro ('$nome')" >&2
    echo "      nunca apareceu. Procure no log do lado que falhou, e nao no" >&2
    echo "      roteiro." >&2
  else
    echo "ERRO: sem janela '$nome' -- o app esta vivo (janela anterior" >&2
    echo "      achada), mas o dialogo deste passo nao veio. Se ele vem" >&2
    echo "      depois de uma acao cara, o caso e de 'espera:'." >&2
  fi
}

roteiro_executa() {
  local arquivo="$1" linha nome geo verbo
  ALVO_ID=""; ALVO_X=0; ALVO_Y=0
  ROTEIRO_ESPERA=""; ROTEIRO_ACHOU=0
  while IFS= read -r linha || [ -n "$linha" ]; do
    linha="${linha%%$'\r'}"
    case "$linha" in
      ''|'#'*|alvo:*|estado:*|operacao:*|conhecida:*) continue ;;
      'espera: '*)
        ROTEIRO_ESPERA="${linha#espera: }"
        ;;
      '> '*)
        nome="${linha#> }"
        read -r ALVO_ID ALVO_X ALVO_Y \
          <<<"$(espera_janela "$nome" \
                  "${ROTEIRO_ESPERA:-$ROTEIRO_ESPERA_PADRAO}")"
        ROTEIRO_ESPERA=""
        [ -n "$ALVO_ID" ] || { roteiro_diagnostico "$nome"; return 1; }
        ROTEIRO_ACHOU=1
        roteiro_foca
        echo ">> janela '$nome' = $ALVO_ID em $ALVO_X,$ALVO_Y"
        ;;
      '>~ '*)
        geo="${linha#>~ }"
        read -r ALVO_ID ALVO_X ALVO_Y \
          <<<"$(espera_geo "$geo" \
                  "${ROTEIRO_ESPERA:-$ROTEIRO_ESPERA_PADRAO}")"
        ROTEIRO_ESPERA=""
        [ -n "$ALVO_ID" ] || { roteiro_diagnostico "$geo"; return 1; }
        ROTEIRO_ACHOU=1
        roteiro_foca
        echo ">> janela $geo = $ALVO_ID em $ALVO_X,$ALVO_Y"
        ;;
      '= '*) roteiro_marca "${linha#= }" ;;
      '~ '*) sleep "${linha#~ }" ;;
      '! '*)
        # shellcheck disable=SC2086  # a divisao em palavras E o parser
        set -- ${linha#! }
        verbo="$1"; shift
        case "$verbo" in
          clique) xdotool mousemove $((ALVO_X+$1)) $((ALVO_Y+$2)) click 1 ;;
          duplo)  xdotool mousemove $((ALVO_X+$1)) $((ALVO_Y+$2)) \
                    click --repeat 2 --delay 120 1 ;;
          tecla)  xdotool key --clearmodifiers "$@" ;;
          texto)  xdotool type --delay 60 "${*//@IMAGEM@/$ROTEIRO_IMAGEM}" ;;
          # `arrasta X0 Y0 X1 Y1` -- CORR-WTE-092.
          #
          # O harness so sabia CLICAR ate aqui, e um clique nao exercita
          # handler de `OnMouseDown` que comeca arrasto: o
          # `estrategia.bolaMouseDown` chama `BeginDrag` e desliga a bola, e o
          # que decide a zona final e para ONDE o ponteiro foi antes do
          # `mouseup`.
          #
          # OS PASSOS INTERMEDIARIOS NAO SAO ENFEITE. `mousedown` seguido de um
          # `mousemove` unico e `mouseup` nao produz `OnMouseMove` nenhum em
          # gtk2 -- o servidor entrega um salto, e o widget nunca ve o
          # ponteiro em transito. Tres passos e o minimo que faz os dois
          # widgetsets emitirem movimento; o `--sync` de cada um garante que o
          # servidor processou antes do proximo.
          arrasta)
            local ax=$((ALVO_X+$1)) ay=$((ALVO_Y+$2))
            local bx=$((ALVO_X+$3)) by=$((ALVO_Y+$4))
            xdotool mousemove --sync "$ax" "$ay"
            xdotool mousedown 1
            local i
            for i in 1 2 3; do
              xdotool mousemove --sync \
                $(( ax + (bx-ax)*i/3 )) $(( ay + (by-ay)*i/3 ))
            done
            xdotool mouseup 1
            ;;
          *) echo "AVISO: verbo desconhecido: $verbo" >&2 ;;
        esac
        ;;
      *) echo "AVISO: linha ignorada: $linha" >&2 ;;
    esac
  done < "$arquivo"
}

# REMOVIDA na WTE-TASK-26: `roteiro_usa_teclado`.
#
# Ela devolvia 0 para roteiro com `! tecla`/`! texto`, e o `golden_run_laz.sh`
# a usava para REPROVAR esse roteiro do lado port -- porque a WTE-TASK-13 tinha
# medido que nenhuma tecla chegava ao GTK2 sem gerenciador de janela.
#
# O que faltava naquela medicao era `xdotool windowfocus` antes: ele e
# `XSetInputFocus`, nao precisa de gerenciador, e com ele a tecla chega.
# Remedido na WTE-TASK-26 -- 3 `Down` sobre a janela focada dao 3 disparos de
# `lista_equiposChange` no trace do port. Quem faz isso agora e `ROTEIRO_FOCO`,
# la em cima.
#
# Fica o registro em vez do silencio: a recusa era a resposta certa para o que
# se sabia, e o que mudou nao foi o port, foi a pergunta ter sido refeita.
