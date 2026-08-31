# PARIDADE-FUNCIONAL §8.8, item 3 -- exportar a bandeira (.b2002) e o
# uniforme 1 (.m2002).
#
# Carrega tools/par/8.8-prelude.sh antes, com um time que TENHA bandeira
# própria (PAR_TEAM=1). Num time sem, os dois lados recusam com
# `Choose a team (that has "indipendent" flag too) !` -- que é o item 2.
#
#   CMD_EXPORT_FLAG 124,65,44,12    CMD_EXPORT_KIT1 55,174,44,12
#
#   PAR_B / PAR_M            caminho DIGITADO. No oráculo tem de ser caminho
#                            Windows (`Z:` é a raiz do Linux no prefix do
#                            Wine); no port, POSIX.
#   PAR_B_FILE / PAR_M_FILE  caminho CONFERIDO pela guarda, sempre POSIX.
#                            Opcionais: sem eles vale o digitado, que é o caso
#                            do port. O `stat` roda no Linux e não enxerga
#                            `Z:\tmp\...`, então no oráculo os dois têm de ser
#                            dados -- a guarda acusaria "nao saiu" num export
#                            que aconteceu.
#
# ---------------------------------------------------------------------------
# ESTE ROTEIRO JÁ FOI UM FALSO VERDE, E AS TRÊS GUARDAS ABAIXO SÃO O CONSERTO.
#
# Em quatro corridas idênticas ele deu quatro resultados -- duas saindo
# `gui: gravado` com a imagem `IDENTICAL` contra a original, isto é, dizendo ter
# gravado sem ter gravado (CORR-WTE-137). O que faltava:
#
#   1. FECHAR O MODAL. O FlagKitDialog é modal nos dois lados; com ele de pé o
#      clique em CMB_WRITE não alcança o diálogo principal e o `Save()` não
#      roda. Os irmãos `8.8-cores-teto.sh` e `8.8-b2002-importar.sh` já
#      terminavam no "Close"; este não. É a mesma armadilha que a §8.7 pagou na
#      CORR-WTE-131 -- dois lados que NÃO gravam produzem imagens idênticas, e
#      o golden sai verde sem ter medido nada.
#   2. CONFERIR O EFEITO. Sem guarda, corrida que não exportou é indistinguível
#      de corrida que exportou. Agora o roteiro exige o arquivo com o tamanho
#      exato (41 e 40, de `FLAG_FILE_BYTES` = 8+1+32 e `KIT_FILE_BYTES` = 8+32
#      em `src/app/FlagKitDialog.cpp`) e SAI COM ERRO se ele não vier.
#   3. ESPERAR JANELA, NÃO DORMIR. O diálogo de arquivo do port é o do portal
#      GTK, em processo separado, e demora mais que o `CFileDialog` do oráculo;
#      com `sleep` fixo o caminho era digitado antes de a janela existir. Os
#      títulos são os MESMOS nos dois lados (`lpstrTitle` em
#      `legacy/mfc/graf.cpp:731` e `:652`, os `QStringLiteral` do port), então a
#      espera serve aos dois.
# ---------------------------------------------------------------------------

# par_espera_janela <título> -- volta assim que a janela existir; 10 s de teto.
par_espera_janela() {
    local _i
    for _i in $(seq 40); do
        xdotool search --onlyvisible --name "$1" >/dev/null 2>&1 && return 0
        sleep 0.25
    done
    return 1
}

# par_confirma <título> -- Return até a janela sumir. Retentativa, não
# contagem: o oráculo costuma precisar de dois (o primeiro fica no campo de
# nome), o port de um.
par_confirma() {
    local _i
    for _i in $(seq 6); do
        xdotool key --clearmodifiers Return; sleep 1.2
        xdotool search --onlyvisible --name "$1" >/dev/null 2>&1 || return 0
    done
    return 1
}

# par_exige_arquivo <caminho> <bytes> -- a guarda que faltava. Falha ALTO: sai
# com erro, para o harness parar em vez de seguir e dizer que gravou.
par_exige_arquivo() {
    local _i _n
    for _i in $(seq 20); do
        _n="$(stat -c %s "$1" 2>/dev/null || echo -1)"
        [ "$_n" = "$2" ] && return 0
        sleep 0.5
    done
    echo "par: $1 nao saiu com $2 bytes (tem ${_n:--}) -- export nao aconteceu" >&2
    exit 1
}

# par_extras -- as janelas visíveis que NÃO são a raiz, o MainDialog nem o
# FlagKitDialog. Na prática, o aviso de export.
#
# Identifica por exclusão, e não por faixa de tamanho, de propósito: controle de
# MFC é janela X de verdade, e uma faixa de "caixinha" pega controle em vez de
# caixa -- foi assim que o `dispensa_modal` da §8.9 clicou num controle e o
# oráculo parou de gravar. Medido nesta seção: com o diálogo aberto aparecem no
# máximo quatro janelas nomeadas, e nenhum controle entre elas.
par_extras() {
    local _id _geo
    for _id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        [ "$(( _id ))" = "$(( MAIN ))" ] && continue
        [ "$(( _id ))" = "$(( FK ))" ]   && continue
        _geo="$(xdotool getwindowgeometry "$_id" 2>/dev/null | grep -o 'Geometry: [0-9]*x[0-9]*')"
        case "$_geo" in *' 1280x1024') continue ;; esac
        printf '%s ' "$_id"
    done
}

# par_dispensa_aviso -- tira o aviso da frente antes do próximo clique.
#
# O gesto é MOVER O PONTEIRO SOBRE O AVISO e então mandar `Return` sem
# `--window`. Não é superstição: este X não tem gerente de janelas, o foco de
# teclado segue o ponteiro (PointerRoot), e a caixa que sobe quando o diálogo de
# arquivo morre não recebe foco sozinha. Medido em 2026-08-31, três gestos na
# mesma corrida: com o ponteiro sobre ela o `Return` a fecha e o FlagKitDialog
# sobrevive; sem mover o ponteiro, o `Return` vai para onde o último `fk_click`
# o deixou e a caixa fica de pé.
#
# Com ela de pé, o clique seguinte -- o de `CMD_EXPORT_KIT1` -- acerta a caixa
# em vez do botão, e o segundo export nunca acontece. Era o que deixava o
# roteiro sem `.m2002` em quatro corridas de quatro (CORR-WTE-137).
#
# `xdotool key --window` (XSendEvent) e clique dentro da caixa foram medidos e
# NÃO servem: o primeiro não é entregue, o segundo levou junto o
# FlagKitDialog.
# Teclar UMA vez por rodada e depois ESPERAR, em vez de teclar a cada volta: um
# `Return` a mais enquanto a caixa ainda está sumindo vai para o ponteiro, que
# está sobre o FlagKitDialog, e o fecha -- foi o que produziu
# `o FlagKitDialog sumiu antes de 'SHIRT FILE TO EXPORT'`.
par_dispensa_aviso() {
    local _i _j _w _id
    for _i in 1 2 3; do
        _w="$(par_extras)"
        [ -z "$_w" ] && return 0
        for _id in $_w; do
            # Se o mousemove falhar, a janela já morreu -- e mandar `Return`
            # assim mesmo é perigoso: o ponteiro ficou onde estava, sobre o
            # FlagKitDialog, e a tecla FECHA O DIÁLOGO. Foi o que destruiu o
            # `$FK` entre um export e o outro, com `BadWindow` no clique
            # seguinte.
            xdotool mousemove --window "$_id" 70 40 2>/dev/null || continue
            sleep 0.3
            xdotool key --clearmodifiers Return
        done
        for _j in $(seq 12); do
            [ -z "$(par_extras)" ] && return 0
            sleep 0.5
        done
    done
    echo "par: nao consegui dispensar o aviso de export" >&2
    return 1
}

# par_espera_fk -- devolve o id do FlagKitDialog, esperando por ele.
#
# Uma olhada só não serve: depois que o aviso de export fecha, o Wine repinta e
# a janela do diálogo fica alguns décimos FORA do `--onlyvisible`. Medido em
# 2026-08-31: a mesma corrida, com um `est` de depuração no meio (que custava
# ~1 s), achava a janela; sem ele, `flag_win` voltava vazio e o roteiro
# concluía que o diálogo tinha sumido. Ele não some -- só pisca.
par_espera_fk() {
    local _i _id
    for _i in $(seq 12); do
        _id="$(flag_win)" && [ -n "$_id" ] && { printf '%s' "$_id"; return 0; }
        sleep 0.25
    done
    # Não voltou: REABRIR pelo CMD_FLAG_KIT do diálogo principal.
    #
    # O oráculo fecha o FlagKitDialog ao dispensar o aviso do primeiro export --
    # medido em 2026-08-31, com seis segundos de espera e a janela não volta.
    # Reabrir mantém o estímulo que o item pede (exportar a bandeira e o
    # uniforme do mesmo time) e é o que torna o roteiro repetível; sem isto ele
    # simplesmente não chega ao `.m2002`, que é como ele passou quatro corridas
    # sem produzir o segundo arquivo (CORR-WTE-137).
    par_click 190 173 100 18
    for _i in $(seq 24); do
        _id="$(flag_win)" && [ -n "$_id" ] && { printf '%s' "$_id"; return 0; }
        sleep 0.25
    done
    return 1
}

# par_abre_export <título> <x> <y> <w> <h> -- clica o botão e espera o diálogo
# de arquivo; se ele não vier, dispensa o que estiver por cima e tenta de novo.
#
# É o conserto da causa raiz da CORR-WTE-137: o clique cai em QUEM ESTIVER POR
# CIMA naquele ponto, e depois de cada export sobe um aviso
# ("Flag exported !" / "Shirt exported !"). Quando o `Return` de dispensa não
# chega a tempo, o clique seguinte acerta a caixa e daí para frente o roteiro
# digita no vazio -- sem que nada detecte. Não dá para dispensar por tamanho de
# janela: controle de MFC é janela X de verdade, e uma faixa de 120..320 px
# pegaria controle em vez de caixa (foi o tropeço do `dispensa_modal` na §8.9).
# Retentar o clique e olhar o efeito é a régua que não erra o alvo.
par_abre_export() {
    local _t
    for _t in 1 2 3; do
        # RE-RESOLVER o FlagKitDialog a cada clique, e por `flag_win`.
        #
        # O id que o prelúdio guardou não sobrevive ao ciclo de export no
        # oráculo: medido em 2026-08-31, logo depois de o aviso ser dispensado
        # o `flag_win` continua achando a janela de 359x315 e um
        # `xwininfo -id "$FK"` no MESMO id falha. Wine recria a janela X do
        # diálogo, e `fk_click` num id velho sai com `BadWindow`, que mata o
        # roteiro sem dizer o que houve.
        FK="$(par_espera_fk)" || {
            echo "par: o FlagKitDialog sumiu antes de '$1'" >&2; return 1; }
        fk_click "$2" "$3" "$4" "$5"
        par_espera_janela "$1" && return 0
        # Nada de `Return` às cegas aqui: sem gerente de janelas ele vai para
        # onde o ponteiro está -- o próprio diálogo -- e o fecha.
        par_dispensa_aviso || return 1
    done
    return 1
}

# --- bandeira: CMD_EXPORT_FLAG -> .b2002, 41 bytes ------------------------
par_abre_export 'FLAG FILE TO EXPORT' 124 65 44 12 || {
    echo "par: 'FLAG FILE TO EXPORT' nao abriu" >&2; exit 1; }
sleep 0.5
xdotool type --delay 40 "${PAR_B:?falta PAR_B}"
sleep 0.8
par_confirma 'FLAG FILE TO EXPORT' || {
    echo "par: 'FLAG FILE TO EXPORT' nao fechou" >&2; exit 1; }
# DISPENSAR O AVISO ANTES DE CONFERIR O ARQUIVO, nesta ordem.
#
# No port o `QFile` é local do `OnExportFlag`/`ExportKit` e só é FECHADO quando
# sai de escopo -- o que acontece depois de o `QMessageBox` retornar. Conferir
# o tamanho com a caixa ainda de pé pega o arquivo com 0 byte, e a guarda
# acusaria "export nao aconteceu" num export que aconteceu. No oráculo tanto
# faz: o `CFile` já fechou quando o `AfxMessageBox` sobe.
par_dispensa_aviso || exit 1
par_exige_arquivo "${PAR_B_FILE:-$PAR_B}" 41

# --- uniforme 1: CMD_EXPORT_KIT1 -> .m2002, 40 bytes ----------------------
par_abre_export 'SHIRT FILE TO EXPORT' 55 174 44 12 || {
    echo "par: 'SHIRT FILE TO EXPORT' nao abriu" >&2; exit 1; }
sleep 0.5
xdotool type --delay 40 "${PAR_M:?falta PAR_M}"
sleep 0.8
par_confirma 'SHIRT FILE TO EXPORT' || {
    echo "par: 'SHIRT FILE TO EXPORT' nao fechou" >&2; exit 1; }
par_dispensa_aviso || exit 1
par_exige_arquivo "${PAR_M_FILE:-$PAR_M}" 40

# --- fechar o modal, como os dois irmãos da seção -------------------------
# Sem esta linha o CMB_WRITE não alcança o diálogo principal e o golden sai
# verde sem ter gravado. É o defeito que originou a CORR-WTE-137.
fk_click 196 26 36 14; sleep 1.5
