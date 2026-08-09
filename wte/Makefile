# Build e verificacao do projeto Lazarus (WE2002 Team Editor do Obocaman).
#
# DELIBERADAMENTE SEPARADO do Makefile e do CMake da raiz. O newWe2002 nao
# conhece este diretorio e nao deve passar a conhecer: sao dois produtos, com
# dois ciclos de verificacao. Ver wte/README.md, decisao 2.
#
# `make` sem alvo lista tudo.

LAZBUILD ?= lazbuild
PYTHON   ?= python3

ROOT     := $(abspath $(CURDIR)/..)
LPI      := $(CURDIR)/wte.lpi
BIN      := $(CURDIR)/build/wte

# A pasta do editor do Obocaman e gitignored -- o usuario a mantem, como faz
# com roms/. Ver a decisao 1 do README.
ASSETS_SRC ?= $(ROOT)/we-team-editor

# Os geradores das fases 1 a 3 entram aqui conforme forem existindo. Cada um
# tem de aceitar --check; o alvo `check` roda todos e falha no primeiro que
# divergir do commitado.
#
# Nem todo item da lista e gerador: o `check_lcl_props.py` (CORR-WTE-020) nao
# escreve nada, confere a tabela `PROPRIEDADES` do `dfm2lfm.py` contra as
# secoes `published` da LCL instalada. Entra pela mesma porta porque cumpre o
# mesmo contrato -- `--check`, e sai 2 quando diverge.
#
# `tools/test_*.py` sao testes de ferramenta, nao geradores: nao aceitam
# --check, e sem o filter-out o wildcard os arrastaria para a bateria e
# quebraria o alvo. Eles rodam pelo alvo `test`, do qual `check` depende.
GENERATORS := $(filter-out $(CURDIR)/tools/test_%.py,$(wildcard $(CURDIR)/tools/*.py))
TESTS      := $(wildcard $(CURDIR)/tools/test_*.py)

.PHONY: help build run run-99 assets check test clean distclean

help:
	@echo 'Alvos:'
	@echo '  build      lazbuild wte.lpi -> build/wte'
	@echo '  run        roda o binario no DISPLAY do shell'
	@echo '  run-99     roda no Xvfb :99, resolvendo o XAUTHORITY sozinho'
	@echo '  assets     cria o symlink assets/ -> $(ASSETS_SRC)'
	@echo '  test       unittest de tools/test_*.py (nao precisa do .exe)'
	@echo '  check      test + --check de todos os geradores de tools/'
	@echo '  clean      remove build/'
	@echo '  distclean  clean + remove o symlink assets/'
	@echo
	@echo 'Binario: $(BIN)'

# ----------------------------------------------------------------- build ----

build:
	$(LAZBUILD) $(LPI)

$(BIN): build

# ------------------------------------------------------------------- run ----

run: build
	$(BIN)

# A regra do :99 e obrigatoria neste repositorio -- ver CLAUDE.md. O Xvfb sobe
# via xvfb-run e tem cookie proprio; sem apontar o XAUTHORITY para ele, o GTK
# morre com "Invalid MIT-MAGIC-COOKIE-1 key".
run-99: build
	@xauth_file=$$(ps -o args= -C Xvfb \
	  | sed -n 's/.*Xvfb :99 .*-auth \([^ ]*\).*/\1/p' | head -1); \
	if [ -z "$$xauth_file" ]; then \
	  echo 'ERRO: nao ha Xvfb :99 rodando.'; exit 1; \
	fi; \
	echo ">> DISPLAY=:99 XAUTHORITY=$$xauth_file"; \
	env DISPLAY=:99 XAUTHORITY="$$xauth_file" $(BIN)

# ---------------------------------------------------------------- assets ----

# Symlink de conveniencia, NAO versionado -- decisao 1 do README. O binario
# instalado nao vai depender dele: a resolucao em runtime (WTE-TASK-39) procura
# $WTE_ASSETS_DIR, depois ao lado do executavel, depois o prefixo instalado,
# depois esta arvore de fonte.
assets:
	@test -d '$(ASSETS_SRC)/image' || { \
	  echo 'ERRO: $(ASSETS_SRC)/image nao existe.'; \
	  echo '      O editor do Obocaman nao e versionado (~1 MB de .exe e'; \
	  echo '      198 bitmaps). Coloque a pasta we-team-editor/ na raiz.'; \
	  exit 1; }
	@ln -sfn '$(ASSETS_SRC)' '$(CURDIR)/assets'
	@echo ">> assets -> $$(readlink $(CURDIR)/assets)"
	@echo ">> bitmaps alcancados: $$(find -L $(CURDIR)/assets/image -iname '*.bmp' | wc -l)"
	@test -f '$(CURDIR)/assets/data/dat.bin' \
	  && echo '>> data/dat.bin: ok' \
	  || echo '>> data/dat.bin: AUSENTE'

# ------------------------------------------------------------------ test ----

# Testes das ferramentas Python. Montam os streams em memoria e NAO abrem o
# `.exe`: rodam num clone sem a pasta we-team-editor/. Cobrem o que nenhum
# formulario real alcanca -- os 12 TValueType ausentes dos 18, o byte de flags
# de objeto (zero ocorrencias em 459 objetos) e as rotas de aborto.
test:
	@if [ -z '$(TESTS)' ]; then \
	  echo 'AVISO: nenhum teste de ferramenta em tools/ -- nada medido.'; \
	  exit 0; \
	fi
	@cd '$(CURDIR)/tools' && $(PYTHON) -m unittest discover -p 'test_*.py'

# ----------------------------------------------------------------- check ----

# Gate das fases 1 a 3: nenhum arquivo gerado foi editado a mao. Enquanto nao
# houver gerador, o alvo diz isso em vez de fingir que passou -- alvo verde
# sem nada medido e pior do que alvo ausente.
check: test
	@if [ -z '$(GENERATORS)' ]; then \
	  echo 'AVISO: nenhum gerador em tools/ ainda -- nada medido.'; \
	  echo '       O primeiro chega na WTE-TASK-03 (dfm_extract.py).'; \
	  exit 0; \
	fi
	@rc=0; for g in $(GENERATORS); do \
	  echo ">> $$(basename $$g) --check"; \
	  $(PYTHON) "$$g" --check || rc=1; \
	done; exit $$rc

# ----------------------------------------------------------------- limpa ----

clean:
	rm -rf '$(CURDIR)/build'

distclean: clean
	rm -f '$(CURDIR)/assets'
