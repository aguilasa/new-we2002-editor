---
id: MCR-TASK-03
title: "A fixture nomeada, o venv e o binding Qt"
type: ferramenta
category: ferramental
phase: 0
depends_on: ["MCR-TASK-01"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §4"
status: concluído
---

# MCR-TASK-03: Fixture, venv e Qt

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §4.
- **O Python desta máquina é duplo, e isso já é armadilha medida:** `python3`
  do `PATH` é o mise 3.13.13, `/usr/bin/python3` é 3.12.3, e o
  `build/CMakeCache.txt` fixou o mise. `apt install python3-pyqt6` instalaria
  para o 3.12 e ficaria **invisível** — o apt termina em verde e o `import`
  continua falhando.
- A fixture existe: `work/entrada.mcr`, 131.072 B, `BISLPM-86600WEW-OPT`, fora
  do git. Cartão de jogo é dado do jogo: **não se versiona**.

---

## Objetivo

Deixar o ambiente reproduzível e registrado, e a fixture nomeada por variável
em vez de por caminho cravado.

---

## Critério de conclusão

- [x] `work/venv-mcr/` com **PySide6** instalado, e no Log: a versão resolvida,
      o `python -VV` do venv e o `pip freeze`. "Instalei PySide6" não é medição.
- [x] A escolha de PySide6 sobre PyQt6 registrada com as duas razões — o Python
      duplo e a licença (LGPL × GPL, num repositório que não pode ser
      licenciado).
- [x] `WE2002_MCR_CARD` é a variável que nomeia a fixture, e nada no código
      cravou `work/entrada.mcr`.
- [x] Alvos `mcr` e `mcr-98` no `Makefile` da raiz, o segundo com a receita de
      `XAUTHORITY` do `:98` que os outros alvos já usam.
- [x] Confirmado que `make fresh` **não** apaga o venv (ele remove quatro
      caminhos nomeados) e que `work/` continua no `.gitignore`.
- [x] Uma corrida de fumaça: `work/venv-mcr/bin/python -c "import PySide6; print(PySide6.__version__)"`.

---

## Armadilhas

- **Não instale nada por `apt` para isto.** Ver o Contexto.
- **A UI roda no `:98`.** `:1` só a pedido explícito do usuário.

---

## Log de Execução

**Executado em:** 2026-09-07

### Resumo do que foi feito

Venv criado com o `python3` do `PATH` (o mise 3.13.13, **não** o 3.12.3 do
sistema), PySide6 resolvido em **6.11.2**, e o `Makefile` da raiz ganhou
`mcr-venv`, `mcr` e `mcr-98`. A fixture passou a ser nomeada por
`WE2002_MCR_CARD`, com default `work/entrada.mcr` no próprio `Makefile` — e os
alvos abrem uma **cópia**, `work/mcr-entrada.mcr`, nunca a fixture.

Duas coisas que a execução ensinou e a task não previa: o `make mcr` precisou de
um `$(wildcard)` para que a guarda do cartão ausente fosse alcançável, e a
fixture é **compartilhada com o ciclo `wte/`**, que sabe regerá-la.

### O venv, medido

```
$ python3 -VV                       # o do PATH, que criou o venv
Python 3.13.13 (main, May 10 2026, 19:26:54) [Clang 22.1.3 ]
$ /usr/bin/python3 -VV              # o do sistema, para o qual o apt instalaria
Python 3.12.3 (main, Jul 15 2026, 23:46:41) [GCC 13.3.0]

$ work/venv-mcr/bin/python -VV
Python 3.13.13 (main, May 10 2026, 19:26:54) [Clang 22.1.3 ]

$ work/venv-mcr/bin/pip freeze
PySide6==6.11.2
PySide6_Addons==6.11.2
PySide6_Essentials==6.11.2
shiboken6==6.11.2

$ work/venv-mcr/bin/python -c "import PySide6; print(PySide6.__version__)"
6.11.2
```

`work/venv-mcr` ocupa **663 MB** (`du -sh`), quase tudo em `PySide6_Addons`. O
pin do alvo é `'PySide6>=6.8'`, como a §4.2 do plano manda; **6.11.2** é o que
o índice resolveu hoje, e é o número que vale citar quando algo parar de
funcionar.

**A corrida de fumaça foi além do `import`**, porque `import` não prova que o
Qt abre janela — e é isso que a MCR-TASK-11 vai precisar. Uma `QApplication`
com um `QLabel` visível no `:98`:

```
QApplication OK, Qt 6.11.2 platform xcb
```

A plataforma resolvida é **xcb**, com `XAUTHORITY` vazio — que é o certo neste
`:98`, levantado sem `-auth`. Nada faltou de biblioteca de sistema: as wheels
trouxeram o que precisavam.

### PySide6 e não PyQt6 — as duas razões

1. **O Python é duplo.** `python3` do `PATH` é o mise 3.13.13 e
   `/usr/bin/python3` é o 3.12.3; `apt install python3-pyqt6` instalaria para o
   3.12 e ficaria invisível para o interpretador que o projeto usa. O apt
   termina em verde e o `import` continua falhando — falha silenciosa, que é o
   pior formato dela. O venv tira o apt da equação inteira.
2. **Licença.** PySide6 é **LGPL**; PyQt6 é **GPL-ou-comercial**. Este
   repositório **não pode ser licenciado** — o código herdado é
   todos-os-direitos-reservados e por isso não há `LICENSE` (ver
   [`../../../NOTICE.md`](../../../NOTICE.md)). Linkar uma dependência GPL num
   repositório nessa posição acrescenta uma obrigação que ele não tem como
   cumprir.

As outras duas razões da §4.2 do plano seguem valendo e foram conferidas: **sem
colisão de ABI** com o Qt6 do sistema que serve ao `newWe2002` em C++ (as
wheels trazem o próprio Qt), e **`make fresh` não apaga o venv**.

### Os alvos do `Makefile`

| alvo | o que faz |
|---|---|
| `mcr-venv` | cria `$(MCR_VENV)` e instala PySide6 — o venv é reproduzível por **comando**, não por prosa num Log |
| `mcr` | copia `$(WE2002_MCR_CARD)` para `$(MCR_COPY)` e abre a UI sobre a cópia |
| `mcr-98` | o mesmo, com `DISPLAY=$(XVFB)` e a receita de `XAUTHORITY` que `run-98`, `oracle-98` e `wte-98` já usam |

Medido:

```
$ make -n mcr-98 | head -1
make --no-print-directory mcr DISPLAY=:98 XAUTH=''
```

`XAUTH` vazio é o valor **correto** aqui, não uma falha: o `ps` procura um
`-auth` que este `:98` não tem, e o `$(if $(XAUTH),...)` do `run` simplesmente
não exporta a variável.

Enquanto `tools/mcr/ui/app.py` não existir, o `mcr` para com mensagem que diz
**qual task o constrói**:

```
ERRO: tools/mcr/ui/app.py ainda nao existe.
      A UI e a MCR-TASK-11; o nucleo, a 04 a 10.
      Ate la o venv ja esta pronto: make mcr-venv
```

### `WE2002_MCR_CARD`, e a cópia

`git grep 'work/entrada.mcr'` fora de `docs/` devolve, deste ciclo, **só** a
linha de default do `Makefile` (`WE2002_MCR_CARD ?= $(WORK)/entrada.mcr`) e a
frase do `CLAUDE.md` — as duas são a **declaração** da variável, não um caminho
cravado. Não há código deste ciclo ainda; quando houver, ele lê a variável.

E o alvo abre **cópia**, como todo editor deste repositório:

```
$ make mcr
>> copiando work/entrada.mcr -> work/mcr-entrada.mcr
$ cmp work/entrada.mcr work/mcr-entrada.mcr && echo identicas
identicas
```

### `make fresh` não apaga o venv — conferido, não suposto

```
$ make -n fresh | head -1
rm -rf 'work/golden-european-deluxe.bin' 'work/oracle-golden-european-deluxe' \
       'work/wte-golden-european-deluxe.bin' 'work/laz-golden-european-deluxe.bin'
```

Quatro caminhos nomeados, nenhum é `work/venv-mcr` nem `work/mcr-entrada.mcr`.
`work/` continua no `.gitignore` (linha 48) e `git status --short` não vê nem o
venv nem a cópia.

### Arquivos criados/modificados

- `Makefile` — os alvos `mcr-venv`, `mcr` e `mcr-98`, a variável
  `WE2002_MCR_CARD` no cabeçalho, e as três linhas de `help`
- `docs/prompts/perfil-mcr.md` — a armadilha 9 (fixture compartilhada) e a
  árvore de `work/` atualizada
- `docs/tasks/port-mcr/progresso.md` — o digest da fixture na tabela "Estado
  medido", e a linha desta task

Fora do git, por decisão: `work/venv-mcr/` (663 MB) e `work/mcr-entrada.mcr`.

### Problemas encontrados

**1. A guarda do cartão ausente nasceu inalcançável.** Escrita como

```make
$(MCR_COPY): $(WE2002_MCR_CARD) | $(WORK)
	@test -s '$(WE2002_MCR_CARD)' || { echo 'ERRO: ...'; exit 1; }
```

ela nunca roda no caso para o qual foi escrita: com o cartão como prerequisito
cru, o make aborta **antes da receita** com

```
make: *** No rule to make target 'work/nao-existe.mcr', needed by 'work/mcr-nao-existe.mcr'.  Stop.
```

— que parece defeito do `Makefile` e não diz o nome da variável a apontar. O
`$(wildcard $(WE2002_MCR_CARD))` resolve os dois lados: existe → prerequisito
de verdade, e a cópia se refaz quando o cartão muda; não existe → lista vazia,
a receita roda, e sai a mensagem útil. Está comentado no lugar, porque sem o
comentário alguém "simplifica" o `wildcard` e restaura o erro feio.

Vale notar que `$(COPY)`, `$(LAZ_COPY)` e `$(WTE_COPY)` têm a mesma forma e a
mesma fragilidade latente — não foram tocados por estarem fora do escopo desta
task, e porque as imagens de `roms/` de fato existem nesta máquina.

**2. A fixture é compartilhada com o ciclo `wte/`, e aquele lado sabe
regerá-la.** `work/entrada.mcr` é apontada aqui por `WE2002_MCR_CARD` e lá por
`WTE_MCR_ENTRADA` e `WTE_MCR_FIXTURE` (`wte/tools/test_dump_mcr.py:341`,
`wte/tests/roteiros/golden-1{2,3}-*.txt`). Nenhum dos dois **escreve** nela,
mas o cabeçalho da `golden-13-roundtrip` manda `cp work/saida.mcr
work/entrada.mcr`, e o `golden_check.sh` produz esse `saida.mcr`. Trocado o
cartão, os números que este ciclo mede — 23/23 dorsais, `[7,7,8,7,7]`, o cp932
dos slots 0 e 20 — passam a ser sobre outro save, e a divergência pareceria bug
do port.

Ancorado com um digest, para que a suspeita seja decidível em uma linha:

```
$ sha256sum work/entrada.mcr
e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546
$ stat -c %s work/entrada.mcr
131072
```

Conferido contra o que o plano registra: magic `MC`, entrada 1 do diretório
`51 00 00 00 00 40 00 00 01 00`, título `BISLPM-86600WEW-OPT`. O digest entrou
na tabela "Estado medido" do `progresso.md` e a armadilha entrou no
`perfil-mcr.md` como item 9 — os dois lugares que toda execução deste ciclo lê
antes de começar.

