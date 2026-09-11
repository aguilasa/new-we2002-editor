# Makefile do editor de `.mcr` -- roda de dentro de `tools/mcr/`.
#
#   make -C tools/mcr            # a lista de alvos
#   cd tools/mcr && make check
#
# ESTE ARQUIVO E PORTUGUES, e o codigo ao lado dele e ingles. A §3.5 do plano
# poe todo `tools/mcr/**.py` em en-US e deixa de fora o que for Makefile ou
# CMake, onde a regra que vale e o idioma DO ARQUIVO. O Makefile da raiz e
# portugues inteiro e este nasce ao lado do `README.md`, que tambem e -- entao
# portugues. Dizer isso aqui custa duas linhas; descobrir depois custou a
# CORR-MCR-019, que foi exatamente uma troca de idioma nao declarada num
# arquivo vizinho.
#
# ELE NAO DUPLICA O DA RAIZ. O `mcr`, o `mcr-98` e o `mcr-venv` ja moram la, com
# a copia do cartao e a resolucao do XAUTHORITY; aqui eles sao DELEGADOS, nunca
# reimplementados. Duas implementacoes da mesma receita divergem em silencio, e
# este repositorio ja pagou esse preco mais de uma vez. O que e proprio daqui
# sao os alvos que a raiz nao tem: os gates, as varreduras, os subcomandos do
# CLI e os roteiros do oraculo.
#
# LEITURA LE O CARTAO, ESCRITA MEXE NUMA COPIA. Os alvos de leitura (`info`,
# `dump`, `get`, `formation`, ...) apontam para `$(CARD)` direto, porque nao
# gravam. Os que gravam (`set`, `probe`, `ui`) trabalham sobre `$(COPY)`, feita
# pelo alvo `copy`. Um `.mcr` e o save de alguem e nao se regera de lugar
# nenhum.

RAIZ  := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))../..)
WORK  := $(RAIZ)/work
VENV  := $(WORK)/venv-mcr
VPY   := $(VENV)/bin/python
PY    ?= python3
AQUI  := $(RAIZ)/tools/mcr

# O mesmo default do Makefile da raiz, e a mesma variavel: quem exporta
# WE2002_MCR_CARD manda nos dois.
WE2002_MCR_CARD ?= $(WORK)/entrada.mcr
CARD  ?= $(WE2002_MCR_CARD)
COPY  := $(WORK)/mcr-make-$(notdir $(CARD))

# Argumentos dos alvos de campo. `make get SLOT=3 FIELD=speed`
SLOT  ?= 0
FIELD ?= speed
VALUE ?= 17
OUT   ?= $(WORK)/mcr-tela.png
TAB   ?= 0

# A camera do option file, por nome ou por numero 0..8. Os nove nomes moram no
# `options.py`; `camera-set` sem CAMERA= grava esta.
CAMERA ?= normal-mid

# Os quatro cartoes que o alvo `cameras` mede, num diretorio so: o limpo e os
# tres que o jogo salvou com a camera trocada. CARTAO DE JOGO NAO SE VERSIONA,
# mesma regra de roms/, entao sem a variavel o alvo PULA e diz que pulou --
# nunca passa em silencio.
CAMERAS ?= $(WE2002_MCR_CAMERA_CARDS)

XVFB ?= :98
# Recursiva de proposito: o `ps` so roda quando um alvo de GUI e chamado.
# Vazio quando o servidor subiu sem `-auth` -- que e o caso do `:98` deste
# projeto, e ai vazio e o CERTO, nao um erro.
XAUTH_XVFB = $(shell ps -o args= -C Xvfb 2>/dev/null \
             | sed -n 's/.*Xvfb $(XVFB) .*-auth \([^ ]*\).*/\1/p' | head -1)

.DEFAULT_GOAL := help
.PHONY: help check controls sweeps gate gates card copy info dump get set \
        formation numbers names camera cameras camera-set \
        roundtrip probe negative ui ui-98 ui-vazia \
        shot venv \
        oracle-controle oracle-capitao oracle-nome limpa

help:
	@echo 'Editor de .mcr do WE2002 -- alvos deste diretorio.'
	@echo
	@echo 'Gates:'
	@echo '  check         o gate OBRIGATORIO: selftest.py (12 modulos, 3 regras,'
	@echo '                idioma e os controles plantados). Nao precisa de nada'
	@echo '  controls      planta cada controle negativo e exige o vermelho'
	@echo '  sweeps        idioma (glossary) + endereco fora do layout (--rule1)'
	@echo '  card          cli.py check sobre $$(CARD); pula com 77 sem cartao'
	@echo '  gate          ctest -R mcr, com WE2002_MCR_CARD apontado'
	@echo '  gates         check + controls + sweeps + gate, nessa ordem'
	@echo
	@echo 'Leitura (le $$(CARD), nao grava):'
	@echo '  info          conteiner: tamanho, magic, cadeia, checksums'
	@echo '  dump          os 23 jogadores'
	@echo '  get           um jogador  (SLOT=$(SLOT) FIELD=$(FIELD), FIELD= vazio da a ficha)'
	@echo '  formation     X, Y, papeis, cobradores e capitao'
	@echo '  numbers       os 23 dorsais de 5 bits'
	@echo '  names         os nomes, byte a byte, em cp932'
	@echo '  camera        a camera do option file, e os dois registros'
	@echo '  cameras       o gate da medicao: dois bytes reproduzem os tres'
	@echo '                cartoes que o jogo salvou. Pula sem $$(CAMERAS)'
	@echo '  roundtrip     as duas formas; tem de dar 0 byte'
	@echo
	@echo 'Escrita (sobre $$(COPY), nunca sobre $$(CARD)):'
	@echo '  copy          faz a copia de trabalho'
	@echo '  set           grava um campo   (SLOT= FIELD= VALUE=)'
	@echo '  probe         muda um campo e diz que bytes se moveram'
	@echo '  camera-set    grava a camera  (CAMERA=$(CAMERA)) -- dois bytes:'
	@echo '                o valor e o checksum do registro que o guarda'
	@echo '  negative      as cinco injecoes da §5.2'
	@echo
	@echo 'Interface (delegados ao Makefile da raiz):'
	@echo '  venv          cria $(VENV) com PySide6 -- nunca por apt'
	@echo '  ui            abre a janela sobre uma copia'
	@echo '  ui-98         idem, forcando DISPLAY=$(XVFB)'
	@echo '  ui-vazia      abre a janela SEM cartao -- e o proprio editor abre'
	@echo '                um, pelo botao da tela ou por Ctrl+O'
	@echo '  shot          captura a janela em $$(OUT)  (TAB=0 jogadores, 1 formacao)'
	@echo
	@echo 'Oraculo (editor do Obocaman, sob Wine, no $(XVFB)):'
	@echo '  oracle-controle  exporta sem editar nada -- o par obrigatorio'
	@echo '  oracle-capitao   as seis colunas em seis linhas: o veredito do 0x6500'
	@echo '  oracle-nome      o nome que enche os dez bytes'
	@echo '                   (os tres refazem a imagem de trabalho antes:'
	@echo '                    o Accept do oraculo grava nela, e controle'
	@echo '                    sujo nao e controle)'
	@echo
	@echo '  limpa         apaga as copias e capturas que estes alvos criam'
	@echo '                (a captura e a de $$(OUT); se voce passou OUT= no'
	@echo '                 shot, passe o mesmo aqui)'
	@echo
	@echo 'Cartao:  $(CARD)'
	@echo 'Copia:   $(COPY)'

# ------------------------------------------------------------------ gates ---

check:
	@$(PY) $(AQUI)/selftest.py

controls:
	@$(PY) $(AQUI)/controls.py

sweeps:
	@$(PY) $(AQUI)/glossary.py
	@$(PY) $(AQUI)/layout.py --rule1
	@$(PY) $(AQUI)/layout.py --check
	@WE2002_MCR_CAMERA_CARDS='$(CAMERAS)' $(PY) $(AQUI)/options.py --check

# Sem cartao ele sai 77, que e *skip* e nao falha -- e o `-` deixa o make
# seguir, porque pular nao e erro.
card:
	@-WE2002_MCR_CARD='$(CARD)' $(PY) $(AQUI)/cli.py check

# O `-V` nao e enfeite: sem a variavel o `mcr_ui` passa com a janela sozinha e
# imprime `note: no WE2002_MCR_CARD...`. Le a linha, nao o `Passed`.
gate:
	@test -d '$(RAIZ)/build' || { \
	  echo 'ERRO: $(RAIZ)/build nao existe -- rode `cmake --preset debug` na raiz.'; \
	  exit 1; }
	@WE2002_MCR_CARD='$(CARD)' ctest --test-dir '$(RAIZ)/build' -R mcr -V \
	  | grep -E '^[0-9]+: (smoke|ok|probe|negative|skipped)|tests passed'

gates: check controls sweeps card gate

# --------------------------------------------------------------- leitura ---

# Guarda unica para os alvos que precisam do arquivo. Mensagem que nomeia a
# variavel vale mais do que "No such file".
define exige_cartao
@test -s '$(CARD)' || { \
  echo 'ERRO: cartao nao encontrado ou vazio: $(CARD)'; \
  echo '      aponte WE2002_MCR_CARD (ou CARD=) para um .mcr de 128 KiB;'; \
  echo '      cartao de jogo nao e versionado, como roms/.'; exit 1; }
endef

info:
	$(exige_cartao)
	@$(PY) $(AQUI)/cli.py info '$(CARD)'

dump:
	$(exige_cartao)
	@$(PY) $(AQUI)/cli.py dump '$(CARD)'

get:
	$(exige_cartao)
	@$(PY) $(AQUI)/cli.py get '$(CARD)' $(SLOT) $(FIELD)

formation:
	$(exige_cartao)
	@$(PY) $(AQUI)/formation.py '$(CARD)'

numbers:
	$(exige_cartao)
	@$(PY) $(AQUI)/numbers.py '$(CARD)'

names:
	$(exige_cartao)
	@$(PY) $(AQUI)/text.py '$(CARD)'

camera:
	$(exige_cartao)
	@$(PY) $(AQUI)/options.py '$(CARD)'

# Sem $(CAMERAS) ele imprime `skipped`, nomeia a variavel que falta e sai 0 --
# pular nao e falhar. LEIA A LINHA, nao so o codigo de saida: e a mesma
# armadilha que o `mcr_ui` registra no CLAUDE.md.
cameras:
	@WE2002_MCR_CAMERA_CARDS='$(CAMERAS)' $(PY) $(AQUI)/options.py --check

roundtrip:
	$(exige_cartao)
	@$(PY) $(AQUI)/cli.py roundtrip '$(CARD)'

# --------------------------------------------------------------- escrita ---
#
# O `$(wildcard)` no prerequisito nao e enfeite, e e a mesma licao do Makefile
# da raiz: como prerequisito cru, um cartao inexistente faz o make abortar com
# "No rule to make target" ANTES da receita, e a mensagem que nomeia a variavel
# -- a unica util aqui -- fica inalcancavel justamente no caso para o qual foi
# escrita. Com o wildcard: existe -> prerequisito de verdade, e a copia se
# refaz quando o cartao muda; nao existe -> lista vazia, a receita roda e o
# `test -s` fala.
$(COPY): $(wildcard $(CARD))
	$(exige_cartao)
	@mkdir -p '$(WORK)'
	@echo '>> copiando $(CARD) -> $@'
	@cp --reflink=auto '$(CARD)' '$@'

copy: $(COPY)
	@echo '$(COPY)'

set: $(COPY)
	@WE2002_MCR_CARD='$(CARD)' $(PY) $(AQUI)/cli.py set '$(COPY)' \
	  $(SLOT) $(FIELD) $(VALUE)

probe: $(COPY)
	@$(PY) $(AQUI)/mcrio.py '$(COPY)' --edit-probe $(SLOT) $(FIELD) $(VALUE)

# O `--out` e explicito de proposito. Sem ele o modulo grava numa copia
# `-edited` AO LADO, que e o default certo para quem chama na mao -- mas aqui
# $(COPY) ja e a copia, e encadear uma segunda so esconde o arquivo de quem for
# procura-lo depois.
camera-set: $(COPY)
	@WE2002_MCR_CARD='$(CARD)' $(PY) $(AQUI)/options.py '$(COPY)' \
	  --set '$(CAMERA)' --out '$(COPY)'

negative:
	@$(PY) $(AQUI)/cli.py negative

# ------------------------------------------------------------- interface ---
#
# Delegados: a copia, o venv e o XAUTHORITY ja sao do Makefile da raiz.

venv:
	@$(MAKE) --no-print-directory -C '$(RAIZ)' mcr-venv

ui:
	@$(MAKE) --no-print-directory -C '$(RAIZ)' mcr \
	  WE2002_MCR_CARD='$(CARD)'

ui-98:
	@$(MAKE) --no-print-directory -C '$(RAIZ)' mcr-98 \
	  WE2002_MCR_CARD='$(CARD)'

# A janela vazia, que e o caminho da MCR-TASK-15: quem escolhe o arquivo e o
# usuario, pelo botao da tela ou por Ctrl+O. Delegado como os outros dois --
# com a variavel VAZIA, que e o que faz a raiz nao copiar nem passar cartao.
ui-vazia:
	@$(MAKE) --no-print-directory -C '$(RAIZ)' mcr WE2002_MCR_CARD=

# A captura e propria daqui -- a raiz nao tem alvo para ela. Sempre no $(XVFB),
# e sobre a COPIA: `--screenshot` nao grava no cartao, mas abrir o original
# num alvo que existe para gerar imagem e convidar o proximo alvo a gravar.
shot: $(COPY)
	@test -x '$(VPY)' || { \
	  echo 'ERRO: sem venv em $(VENV) -- rode `make venv`.'; exit 1; }
	@env DISPLAY='$(XVFB)' \
	  $(if $(XAUTH_XVFB),XAUTHORITY='$(XAUTH_XVFB)',) \
	  '$(VPY)' '$(AQUI)/ui/app.py' '$(COPY)' --screenshot '$(OUT)' --tab $(TAB)

# --------------------------------------------------------------- oraculo ---
#
# A IMAGEM E A JAPONESA, e nao por gosto: com a europeia o `wte.exe` morre ao
# trocar de time -- 49.749 violacoes de acesso contra 0 (wte/re/crash-causa.md).
# O `.mcr` de saida se apaga ANTES: o dialogo tem `ofOverwritePrompt`, e um
# arquivo no lugar acrescenta uma caixa que o roteiro nao preve.

WTE_IMAGEM := $(WORK)/wte-japanese-shift-jis.bin
ORACULO_SAIDA := $(WORK)/oraculo-13

# A IMAGEM SE REFAZ A CADA CORRIDA, e isto e o alvo mais importante da secao.
# O ` Accept` da tela de tatica do oraculo GRAVA na imagem de CD, entao uma
# corrida deixa a proxima com os valores da anterior -- e o `oracle-controle`,
# que existe para mostrar o que o jogo gravou, passa a mostrar o que a corrida
# passada editou. Medido em 2026-09-08: rodado sobre a imagem que a MCR-TASK-13
# tinha deixado, o controle devolveu `[0, 1, 2, 3, 4]` e capitao `5` -- os
# valores do EXPERIMENTO, com cara de controle. Controle sujo nao e controle, e
# refazer a copia custa menos de um segundo contra o que custa acreditar nela.
.PHONY: oracle-imagem
oracle-imagem:
	@test -s '$(RAIZ)/roms/japanese-shift-jis.bin' || { \
	  echo 'ERRO: falta roms/japanese-shift-jis.bin -- as imagens nao sao'; \
	  echo '      versionadas; o dono da maquina as mantem.'; exit 1; }
	@mkdir -p '$(WORK)'
	@echo '>> refazendo a imagem de trabalho -> $(WTE_IMAGEM)  (~307 MB)'
	@cp --reflink=auto '$(RAIZ)/roms/japanese-shift-jis.bin' '$(WTE_IMAGEM)'

define roda_oraculo
@mkdir -p '$(ORACULO_SAIDA)'
@rm -f '$(WORK)/$(2)'
@bash '$(RAIZ)/wte/tools/golden_run_wte.sh' '$(AQUI)/oracle/$(1)' \
  '$(WTE_IMAGEM)' '$(ORACULO_SAIDA)'
@$(PY) '$(AQUI)/formation.py' '$(WORK)/$(2)'
endef

oracle-controle: oracle-imagem
	$(call roda_oraculo,13-controle.txt,oraculo-13-controle.mcr)

oracle-capitao: oracle-imagem
	$(call roda_oraculo,13-seis-linhas.txt,oraculo-13-seis.mcr)

oracle-nome: oracle-imagem
	@mkdir -p '$(ORACULO_SAIDA)'
	@rm -f '$(WORK)/oraculo-13-nome.mcr'
	@bash '$(RAIZ)/wte/tools/golden_run_wte.sh' '$(AQUI)/oracle/13-nome-de-dez.txt' \
	  '$(WTE_IMAGEM)' '$(ORACULO_SAIDA)'
	@$(PY) '$(AQUI)/text.py' '$(WORK)/oraculo-13-nome.mcr'

# ----------------------------------------------------------------- limpa ---
#
# So o que ESTES alvos criam. A fixture, o venv, o clone do upstream e a copia
# da imagem japonesa (307 MB, cara de refazer) ficam.

limpa:
	@rm -rf '$(COPY)' '$(OUT)' '$(ORACULO_SAIDA)'
	@rm -f '$(WORK)/oraculo-13-controle.mcr' '$(WORK)/oraculo-13-seis.mcr' \
	       '$(WORK)/oraculo-13-nome.mcr'
	@echo '>> apagados: a copia de trabalho, a captura e as saidas do oraculo'
	@echo '   mantidos: $(CARD), $(VENV)'
	@echo '   a imagem de trabalho ($(WTE_IMAGEM)) se refaz sozinha a cada'
	@echo '   alvo de oraculo, entao nao precisa ser apagada aqui'
