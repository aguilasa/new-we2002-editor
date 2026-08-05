#
# Makefile de conveniencia.
#
# Nao substitui o CMake: e um atalho para os presets de CMakePresets.json,
# para os testes e para rodar o editor sobre uma COPIA da imagem de CD.
#
#   make            lista os alvos
#   make run        compila e abre o editor sobre roms/golden-european-deluxe.bin
#   make run-jp     idem, com a imagem japonesa
#   make test       compila e roda os testes unitarios
#
# Variaveis (todas sobrescrevveis na linha de comando):
#
#   PRESET=debug|release|asan|ubsan   preset do CMake                (debug)
#   IMAGE=<caminho.bin>               imagem de CD de origem
#   WORK=<dir>                        onde ficam as copias de trabalho (work/)
#   JOBS=<n>                          paralelismo do build           (nproc)
#   DISPLAY=:99                       display X para a GUI    (herda do shell)
#   ARGS='...'                        argumentos extras para o binario
#
# Ex.: make run PRESET=release IMAGE=roms/japanese-shift-jis.bin
#

# ---------------------------------------------------------------- config ----

PRESET ?= debug
JOBS   ?= $(shell nproc 2>/dev/null || echo 4)
WORK   ?= work
IMAGE  ?= roms/golden-european-deluxe.bin
ARGS   ?=

# preset -> binaryDir, conforme CMakePresets.json
BUILD_DIR_debug   := build
BUILD_DIR_release := build-release
BUILD_DIR_asan    := build-asan
BUILD_DIR_ubsan   := build-ubsan
BUILD := $(BUILD_DIR_$(PRESET))

ifeq ($(BUILD),)
$(error PRESET invalido: '$(PRESET)'. Use debug, release, asan ou ubsan)
endif

BIN   := $(BUILD)/src/app/newWe2002
TESTS := $(BUILD)/tests/we2002_tests

# copia de trabalho: o editor grava IN-PLACE, entao a imagem de roms/
# nunca e aberta diretamente.
COPY := $(WORK)/$(notdir $(IMAGE))

.DEFAULT_GOAL := help
.PHONY: help configure build run run-jp run-99 copy fresh test test-release \
        golden golden-gui install uipreview gen gen-check clean distclean

# ------------------------------------------------------------------ help ----

help:
	@echo 'Alvos:'
	@echo '  build         compila o preset $$(PRESET) (atual: $(PRESET))'
	@echo '  run           compila e abre o editor sobre uma copia de $$(IMAGE)'
	@echo '  run-jp        idem, com roms/japanese-shift-jis.bin'
	@echo '  run-99        run forcando DISPLAY=:99 (validacao visual)'
	@echo '  oracle        abre o ed.exe original sob Wine (runner do Bottles)'
	@echo '  oracle-99     oracle forcando DISPLAY=:99'
	@echo '  fresh         descarta a copia de trabalho e refaz do original'
	@echo '  test          testes unitarios (sem imagem)'
	@echo '  test-release  testes no preset release (pega _FORTIFY_SOURCE)'
	@echo '  golden        golden test headless (core vs ed.exe sob Wine)'
	@echo '  golden-gui    golden test dirigindo a janela Qt'
	@echo '  gen           reexecuta os geradores de codigo'
	@echo '  gen-check     falha se o codigo gerado divergir do commitado'
	@echo '  uipreview     screenshot do diálogo principal sem rodar o app'
	@echo '  install       instala em $$(PREFIX) (default: ~/.local)'
	@echo '  clean         limpa os artefatos do preset atual'
	@echo '  distclean     remove todos os build*/ e a pasta $(WORK)/'
	@echo
	@echo 'Preset atual: $(PRESET)  ->  $(BUILD)/'
	@echo 'Imagem:       $(IMAGE)'
	@echo 'Copia:        $(COPY)'

# ----------------------------------------------------------------- build ----

$(BUILD)/CMakeCache.txt:
	cmake --preset $(PRESET)

configure: $(BUILD)/CMakeCache.txt

build: configure
	cmake --build --preset $(PRESET) -j $(JOBS)

# ------------------------------------------------------------------- run ----

# A imagem de origem nunca e tocada: o alvo copia para $(WORK)/ e o editor
# grava sobre a copia. A copia so e refeita se nao existir -- assim as
# edicoes sobrevivem entre execucoes. Use `make fresh` para zerar.
$(COPY): $(IMAGE) | $(WORK)
	@test -s '$(IMAGE)' || { \
	  echo 'ERRO: imagem nao encontrada ou vazia: $(IMAGE)'; \
	  echo '      as imagens ficam em roms/ e nao sao versionadas.'; exit 1; }
	@echo '>> copiando $(IMAGE) -> $@  (~474 MB)'
	@cp --reflink=auto '$(IMAGE)' '$@'

$(WORK):
	@mkdir -p '$(WORK)'

copy: $(COPY)

fresh:
	@rm -rf '$(COPY)' '$(ORACLE_DIR)'
	@$(MAKE) --no-print-directory copy

run: build $(COPY)
	@echo '>> $(BIN) $(COPY)   (DISPLAY=$(DISPLAY))'
	@env $(if $(XAUTH),XAUTHORITY='$(XAUTH)') ./$(BIN) '$(COPY)' $(ARGS)

run-jp:
	@$(MAKE) --no-print-directory run IMAGE=roms/japanese-shift-jis.bin

# Validacao visual: sempre no Xvfb :99, nunca na sessao real do usuario.
# O :99 desta maquina sobe via xvfb-run, com cookie proprio; sem apontar o
# XAUTHORITY para ele o Qt morre com "Invalid MIT-MAGIC-COOKIE-1 key".
# Variavel recursiva: o `ps` so roda quando run-99 e chamado.
XAUTH_99 = $(shell ps -o args= -C Xvfb 2>/dev/null \
             | sed -n 's/.*Xvfb :99 .*-auth \([^ ]*\).*/\1/p' | head -1)

run-99:
	@$(MAKE) --no-print-directory run DISPLAY=:99 XAUTH='$(XAUTH_99)'

# ---------------------------------------------------------------- oraculo ---

# O editor original (MFC, 2002) sob o runner Wine do Bottles. E o oraculo dos
# golden tests -- util para comparar comportamento de tela lado a lado.
#
# Prefix DEDICADO, nunca uma bottle existente: ed.cpp:75 chama
# COleObjectFactory::UpdateRegistryAll(), que escreve no registry do prefix.
# Ele fica em $(WORK)/ e sobrevive entre execucoes (o wineboot so roda uma vez).
#
# ed.exe nao aceita argumento: abre um CFileDialog no OnInitDialog. O filtro
# default dele e literalmente `we2002.bin` (edDlg.cpp:1331), entao a copia do
# oraculo e gravada com esse nome, num diretorio por imagem -- assim ela
# aparece na lista sem trocar o filtro. O alvo tambem imprime o caminho
# Windows, para colar em "File name".

WINE_BIN ?= /home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin
ORACLE_PREFIX ?= $(abspath $(WORK))/wineprefix
ORACLE_DIR    := $(WORK)/oracle-$(basename $(notdir $(IMAGE)))
ORACLE_COPY   := $(ORACLE_DIR)/we2002.bin

.PHONY: oracle oracle-99

$(ORACLE_COPY): $(IMAGE)
	@test -s '$(IMAGE)' || { echo 'ERRO: imagem ausente: $(IMAGE)'; exit 1; }
	@mkdir -p '$(ORACLE_DIR)'
	@echo '>> copiando $(IMAGE) -> $@  (~474 MB)'
	@cp --reflink=auto '$(IMAGE)' '$@'

oracle: $(ORACLE_COPY)
	@test -f Debug/ed.exe || { \
	  echo 'ERRO: Debug/ed.exe ausente -- e o oraculo, precisa ficar no disco.'; \
	  exit 1; }
	@test -x '$(WINE_BIN)/wine64' || { \
	  echo 'ERRO: runner Wine nao encontrado em $(WINE_BIN)'; \
	  echo '      sobrescreva com WINE_BIN=<dir com wine64>'; exit 1; }
	@if [ ! -d '$(ORACLE_PREFIX)' ]; then \
	  echo '>> criando o prefix Wine em $(ORACLE_PREFIX) (primeira vez, demora)'; \
	  mkdir -p '$(ORACLE_PREFIX)'; \
	  env WINEPREFIX='$(ORACLE_PREFIX)' WINEDEBUG=-all \
	    $(if $(XAUTH),XAUTHORITY='$(XAUTH)') \
	    '$(WINE_BIN)/wineboot' -i >/dev/null 2>&1 || true; \
	fi
	@# O CFileDialog abre no CWD, que e Debug/. Um symlink com o nome que o
	@# filtro default espera poe a copia na primeira tela, sem navegar.
	@# So mexe se nao existir ou ja for symlink -- nunca sobrescreve arquivo.
	@if [ ! -e Debug/we2002.bin ] || [ -L Debug/we2002.bin ]; then \
	  ln -sfn '$(abspath $(ORACLE_COPY))' Debug/we2002.bin; \
	else \
	  echo 'AVISO: Debug/we2002.bin existe e nao e symlink -- nao foi tocado.'; \
	fi
	@echo '>> selecione we2002.bin na primeira tela; ele aponta para'
	@echo '   $(ORACLE_COPY)'
	@echo '>> ed.exe   (DISPLAY=$(DISPLAY), prefix $(ORACLE_PREFIX))'
	@cd Debug && env WINEPREFIX='$(ORACLE_PREFIX)' WINEDEBUG=-all \
	  $(if $(XAUTH),XAUTHORITY='$(XAUTH)') '$(WINE_BIN)/wine64' ed.exe; \
	  env WINEPREFIX='$(ORACLE_PREFIX)' '$(WINE_BIN)/wineserver' -k >/dev/null 2>&1 || true

oracle-99:
	@$(MAKE) --no-print-directory oracle DISPLAY=:99 XAUTH='$(XAUTH_99)'

# ----------------------------------------------------------------- testes ---

test: build
	ctest --preset $(PRESET) -E 'golden'

test-release:
	@$(MAKE) --no-print-directory test PRESET=release

# Golden tests: precisam de Debug/ed.exe, Wine e do display :99.
# Feche qualquer editor aberto no :99 antes de rodar.
golden: build
	WE2002_GOLDEN_IMAGE='$(abspath $(IMAGE))' \
	  ctest --preset $(PRESET) -R '^golden$$'

golden-gui: build
	WE2002_GOLDEN_IMAGE='$(abspath $(IMAGE))' \
	  ctest --preset $(PRESET) -R '^golden_gui$$'

# ------------------------------------------------------------- geradores ----

gen:
	python3 tools/extract_legacy_data.py
	python3 tools/port_database.py
	python3 tools/rc2ui.py

# glossary e ui_forms tem --check proprio; extract_legacy_data.py e
# port_database.py nao tem, entao a conferencia deles e reexecutar e ver
# se a arvore ficou suja.
gen-check: build
	ctest --preset $(PRESET) -R 'glossary|ui_forms'
	@$(MAKE) --no-print-directory gen
	@git diff --exit-code -- src/core src/app/ui \
	  || { echo 'ERRO: codigo gerado difere do commitado'; exit 1; }

# ------------------------------------------------------------ utilitarios ---

PREFIX ?= $(HOME)/.local

install:
	@$(MAKE) --no-print-directory build PRESET=release
	cmake --install $(BUILD_DIR_release) --prefix '$(PREFIX)'

uipreview:
	cmake -B build-uipreview -S tools/uipreview
	cmake --build build-uipreview -j $(JOBS)
	DISPLAY=:99 ./build-uipreview/preview_MainDialog /tmp/main.png
	@echo '>> /tmp/main.png'

clean:
	@test -d '$(BUILD)' && cmake --build '$(BUILD)' --target clean || true

distclean:
	rm -rf build build-* '$(WORK)'
