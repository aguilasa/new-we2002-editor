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

.PHONY: help build run run-98 assets check test icon install clean distclean

help:
	@echo 'Alvos:'
	@echo '  build      lazbuild wte.lpi -> build/wte'
	@echo '  run        roda o binario no DISPLAY do shell'
	@echo '  run-98     roda no Xvfb $(XVFB), resolvendo o XAUTHORITY sozinho'
	@echo '  assets     cria o symlink assets/ -> $(ASSETS_SRC)'
	@echo '  test       unittest de tools/test_*.py (nao precisa do .exe)'
	@echo '  check      test + --check de todos os geradores de tools/'
	@echo '  icon       redesenha os 7 PNG de packaging/icons/ (sem --check)'
	@echo '  install    instala em $$(PREFIX) (padrao: /usr/local), com DESTDIR'
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

# A regra do Xvfb e obrigatoria neste repositorio -- ver CLAUDE.md. O alvo e o
# :98 desde 2026-08-20 (antes era o :99, que outro projeto desta maquina
# ocupa); `XVFB=:97 make run-98` move sem editar nada. Servidor que sobe
# via xvfb-run e tem cookie proprio; sem apontar o XAUTHORITY para ele, o GTK
# morre com "Invalid MIT-MAGIC-COOKIE-1 key".
XVFB ?= :98

run-98: build
	@if ! env DISPLAY=$(XVFB) xdpyinfo >/dev/null 2>&1; then \
	  echo 'ERRO: nao ha Xvfb $(XVFB) rodando. Suba com:'; \
	  echo '  Xvfb $(XVFB) -screen 0 1280x1024x24 -nolisten tcp &'; \
	  exit 1; \
	fi; \
	xauth_file=$$(ps -o args= -C Xvfb \
	  | sed -n 's/.*Xvfb $(XVFB) .*-auth \([^ ]*\).*/\1/p' | head -1); \
	echo ">> DISPLAY=$(XVFB) XAUTHORITY=$${xauth_file:-<vazio>}"; \
	env DISPLAY=$(XVFB) XAUTHORITY="$$xauth_file" $(BIN)

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

# --------------------------------------------------------------- instala ----
#
# WTE-TASK-39. O padrao e o do `newWe2002` (as regras `install()` do
# `CMakeLists.txt` da raiz), traduzido para `make` porque aqui nao ha CMake.
#
# ## O binario se chama `wte` na arvore e `we2002Lazarus` instalado
#
# A WTE-TASK-38 escolheu o slug `we2002Lazarus`, e o repasse dela previa
# renomear `wte.lpi`, `wte.lpr` e `build/wte`. **Nao foi feito, e a razao e de
# custo:** o nome `wte` aparece em 3 ferramentas, no `LPI`/`BIN` deste
# arquivo e em prosa de `docs/` -- e nenhum desses leitores e o usuario. Quem
# ve o nome do produto e a barra de tarefas (`Application.Title`, ja trocado),
# o `.desktop` e o `bin/` instalado. Entao a renomeacao acontece no
# `install`, que e onde ela tem consumidor, e o projeto continua sendo `wte`
# para o harness golden, que nao muda de forma por causa de nome.
#
# ## `share/we2002Lazarus/` nasce com um README, nao vazio
#
# E o terceiro candidato da ordem de busca de assets, e os assets nao sao
# redistribuidos (WTE-TASK-38). Diretorio vazio nao explica nada; o
# `packaging/README-assets.txt` diz o que por ali e por que ele nao veio.

PREFIX     ?= /usr/local
DESTDIR    ?=
APPID      := io.github.aguilasa.we2002Lazarus
SLUG       := we2002Lazarus
ICON_SIZES := 16 24 32 48 64 128 256

icon:
	$(PYTHON) '$(CURDIR)/tools/make_icon.py'
	@echo '>> olhe o resultado: o icone e a unica coisa gerada aqui que'
	@echo '   teste nenhum julga.'

install: build
	@test -f '$(CURDIR)/packaging/icons/$(SLUG)-256.png' || { 	  echo 'ERRO: faltam os PNG do icone. Rode: make -C wte icon'; exit 1; }
	install -d '$(DESTDIR)$(PREFIX)/bin'
	install -m 755 '$(BIN)' '$(DESTDIR)$(PREFIX)/bin/$(SLUG)'
	install -d '$(DESTDIR)$(PREFIX)/share/$(SLUG)'
	install -m 644 '$(CURDIR)/packaging/README-assets.txt' 	  '$(DESTDIR)$(PREFIX)/share/$(SLUG)/README.txt'
	install -d '$(DESTDIR)$(PREFIX)/share/applications'
	install -m 644 '$(CURDIR)/packaging/$(APPID).desktop' 	  '$(DESTDIR)$(PREFIX)/share/applications/'
	install -d '$(DESTDIR)$(PREFIX)/share/metainfo'
	install -m 644 '$(CURDIR)/packaging/$(APPID).metainfo.xml' 	  '$(DESTDIR)$(PREFIX)/share/metainfo/'
	@for s in $(ICON_SIZES); do 	  install -d "$(DESTDIR)$(PREFIX)/share/icons/hicolor/$${s}x$${s}/apps"; 	  install -m 644 '$(CURDIR)/packaging/icons/$(SLUG)-'$$s'.png' 	    "$(DESTDIR)$(PREFIX)/share/icons/hicolor/$${s}x$${s}/apps/$(SLUG).png"; 	done
	install -d '$(DESTDIR)$(PREFIX)/share/doc/$(SLUG)'
	install -m 644 '$(ROOT)/NOTICE.md' '$(CURDIR)/README.md' 	  '$(DESTDIR)$(PREFIX)/share/doc/$(SLUG)/'
	@echo '>> instalado em $(DESTDIR)$(PREFIX)'
	@echo '>> os assets do editor original NAO vao no pacote -- veja'
	@echo '   $(DESTDIR)$(PREFIX)/share/$(SLUG)/README.txt'

# ----------------------------------------------------------------- limpa ----

clean:
	rm -rf '$(CURDIR)/build'

distclean: clean
	rm -f '$(CURDIR)/assets'
