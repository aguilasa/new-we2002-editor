---
id: MCR-TASK-11
title: "A casca Qt: janela, elenco e ficha em leitura"
type: implementação
category: ui
phase: 3
depends_on: ["MCR-TASK-10"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §3"
status: concluído
---

# MCR-TASK-11: A UI em leitura

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §3 (Regra 3) e
  §4.3.
- O upstream tem duas abas — `PLAYERS` e `FORMATION` — e uma terceira janela de
  opções que é do raspador dele, fora do escopo.
- **A UI não conhece endereço.** Ela importa `model`, `domains` e `glossary`, e
  mais nada; o `selftest` recusa o contrário.
- **Roda no `:98`.** `make mcr-98`.

---

- **Três campos têm mais valores do que o upstream deu nomes**, medido na
  MCR-TASK-08: `beard_style` e `beard_colour` guardam 3 bits (8 valores) e ele
  nomeia 7; `foot` guarda 2 bits (4) e ele nomeia 3. O índice extra **não é
  ilegal** — é anônimo. O `domains.label()` devolve `domains.UNNAMED` (`"?"`)
  nesse caso e **levanta** só quando o valor está fora da faixa do campo; a
  tela precisa distinguir as duas coisas, senão um cartão legítimo vira erro.

---

## Objetivo

Abrir um cartão e mostrar o que o núcleo já lê, sem gravar nada.

---

## Critério de conclusão

- [x] **`ui/app.py --smoke` abre a janela, deixa o Qt pintar um quadro e sai
      com 0, sem esperar por ninguém.** É o contrato que o alvo `mcr_ui` já
      chama: o `tools/mcr/ui_check.py` da MCR-TASK-10 resolve o venv, resolve o
      `XAUTHORITY` do `:98` como o `make run-98` faz, e roda **exatamente essa
      linha**. Antes desta task ele pulava com 77 dizendo "app.py does not
      exist yet (MCR-TASK-11)"; **desde 2026-09-08 ele passa** — o `app.py`
      existe e responde a `--smoke`. A pressão funcionou porque a linha estava
      aqui, no arquivo de destino, e não só no Log da task anterior.
- [x] **A Regra 3 é varrida, não prometida.** O `selftest.py` lê cada
      `tools/mcr/ui/*.py` e recusa `import layout`, `import card` e
      `import mcrio` (e as formas `from X import`). Enquanto a pasta não
      existia ele **pulava dizendo isso**; com ela no lugar a varredura passou a
      valer sem ninguém religar nada, e ganhou caso vermelho próprio — o
      controle `ui-imports-an-address`.

- [x] Janela com a lista dos 23 jogadores, rotulada `[GK] Nome`. **O rótulo é
      nosso, não do upstream** — o `ListBoxMcR` dele nasce com
      `Player1..Player23` no designer e cada linha é substituída pelo **nome
      cru**, sem posição e sem número de vaga (`Frmmcr.vb`, os 23
      `Items.Insert`). Medido na MCR-TASK-11; a posição vem do `domains`,
      que é a tabela dele, mas a forma da linha é decisão deste port.
- [x] Ficha do jogador em leitura: posição, aparência, físico, os 16 atributos
      (exibidos 12..19), dorsal, pé e chuteira.
- [x] Aba de formação desenhando os 10 de linha por X e Y — com os fatores de
      tela (`X*7`, `Y*2`) **na UI**, nunca no núcleo — e o papel de cada um.
- [x] Nome em cp932 aparecendo correto na tela, inclusive o katakana.
- [x] **Nenhum caminho de gravação ligado** nesta task: abrir é seguro por
      construção.
- [x] **Toda a UI em en-US** — título de janela, aba, rótulo, cabeçalho de
      coluna, tooltip e mensagem. A regra é a §3.5 do plano e vale para o texto
      que o usuário lê, não só para o identificador.
- [x] Captura de tela no `:98` anexada ao Log.

---

## Log de Execução

**Executado em:** 2026-09-08

### Resumo do que foi feito

`tools/mcr/ui/` com os cinco módulos que o plano previa — `app.py`,
`main_window.py`, `squad_view.py`, `player_form.py`, `formation_view.py`, 518
linhas —, e o alvo `mcr_ui` **passou de pulado a verde**: `ctest -R mcr` agora
é **3 de 3**, sem skip.

Duas coisas que a execução resolveu e o critério não previa: **a UI precisava
de uma porta**, porque a Regra 3 lhe proíbe o carregador; e **o rótulo da lista
não é o do upstream**, que não rotula nada.

### A porta: como a UI abre um cartão sem quebrar a Regra 3

A Regra 3 proíbe `tools/mcr/ui/**.py` de importar `layout`, `card` e `mcrio` —
e `mcrio.load()` é justamente quem abre um cartão. A janela ficaria sem
carregador.

A saída é uma porta no `model.py`, que a UI **pode** importar:

```python
def load(path) -> Save:
    import mcrio
    return mcrio.load(path)
```

O import é **adiado de propósito**: o `mcrio` importa o `model` no topo, então
importá-lo de volta no escopo do módulo é ciclo. A validação continua sendo a
do `mcrio` — tamanho, magic e a entrada do diretório —, porque escrever um
segundo carregador, mais fraco, para a tela é exatamente como uma janela acaba
lendo um cartão que o gate teria recusado. Está registrado na Regra 3 do plano,
e a MCR-TASK-12 recebeu a linha: a gravação precisa da **porta
correspondente**, não de um gravador próprio da tela.

### A Regra 3, agora com caso vermelho

A varredura existia desde a MCR-TASK-10 e nunca tinha tido o que varrer — ela
**pulava** dizendo que a pasta não existia. Com a pasta no lugar, virou
controle:

```
$ python3 tools/mcr/controls.py --only ui-imports-an-address
  RED    ui-imports-an-address      ui/main_window.py :: module scope
controls: 1 of 1 red
```

E o vermelho nomeia o defeito, não só o número:

```
FAIL  Rule 3: the UI imports no core module that knows an address
      ['ui/main_window.py:26: mcrio']
```

São **16 controles, 16 vermelhos**. O `ui-below-the-sweep`, aberto pela
[CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md) quando a pasta ainda não
existia, continua vermelho ao lado dele — um cobre a varredura que **desce**, o
outro a que **proíbe**.

Para o controle rodar, o `selftest.py` passou a aceitar `--self-check`, que é
como o motor de controles invoca todo módulo. Ele **implica `--fast`**, e não é
atalho: um selftest que replanta dentro de um sandbox já plantado seriam
dezesseis árvores de dezesseis.

### O rótulo da lista é nosso, e o upstream não rotula nada

O critério dizia "rotulada como o upstream (`[GK] Nome`)". Medido: o
`ListBoxMcR` do Zetaprog nasce com `Player1..Player23` no designer
(`Frmmcr.designer.vb:2247`) e cada linha é substituída pelo **nome cru** —
`ListBoxMcR.Items.Insert(m, txtplayername.Text)`, uma vez por jogador. Sem
posição, sem número de vaga.

`[GK] Nome` é decisão deste port, e vale a pena: vinte e três nomes em katakana
numa coluna, sem mais nada na linha, não deixam achar o goleiro. A posição sai
do `domains`, que é a tabela **dele**; a forma da linha é nossa, e o
`squad_view.py` diz isso no próprio docstring. Critério corrigido.

### Os fatores de tela, na única casa que podem ter

`X*7` e `Y*2` estão no `ui/formation_view.py` e em nenhum outro lugar —
armadilha 7 do perfil. O número saiu do upstream, não de estimativa:
`FrmFormation.vb:1517` escreve `PicP1.Left = 9 * 7` e a linha seguinte
`PicP1.Top = 41 * 2`, contra um `PictureBox2` de **353x192**
(`FrmFormation.Designer.vb:1224`). O rótulo de cada marcador fica seis unidades
de Y abaixo dele (`lblPic1.Top = 47 * 2` contra `PicP1.Top = 41 * 2`), e o
mesmo deslocamento está aqui.

### O cp932 na tela

Os nomes japoneses aparecem inteiros, com katakana meia-largura e o ponto
médio: `[GK] P･ジｮｰﾙズ`, `[SH] ｶｰﾑ･ﾛﾚﾝｿﾝ`. É o `text.py` da MCR-TASK-07 chegando
à tela sem nada no meio — nenhuma transliteração, nenhum `KanjiToAscii`, que é
o que apagaria tudo isso em silêncio.

### As capturas, no `:98`

```
$ Xvfb :98 -screen 0 1280x1024x24 -nolisten tcp &
$ make mcr-98 ARGS=--smoke
>> copiando work/entrada.mcr -> work/mcr-entrada.mcr
>> work/venv-mcr/bin/python tools/mcr/ui/app.py work/mcr-entrada.mcr   (DISPLAY=:98)
smoke: window up, card loaded, platform xcb

$ DISPLAY=:98 XAUTHORITY= work/venv-mcr/bin/python tools/mcr/ui/app.py \
    work/mcr-entrada.mcr --tab 0 --screenshot work/mcr-ui-players.png
$ DISPLAY=:98 XAUTHORITY= work/venv-mcr/bin/python tools/mcr/ui/app.py \
    work/mcr-entrada.mcr --tab 1 --screenshot work/mcr-ui-formation.png
```

As duas PNG ficam em `work/`, que é gitignored como todo o resto do diretório —
o comando acima é o que as reproduz. A aba **Players** mostra os 23 com
`[POS] Nome`, a ficha do slot 0 com os dois dorsais lado a lado (tabela e
registro), aparência com rótulo e os dezesseis atributos em 12..19. A aba
**Formation** desenha os dez marcadores com o papel de cada um — CB-L, CB-R,
CB-C, LB, RB, DH-C, OH-L, OH-R, CF-L, CF-R —, os cobradores em ordem de
cobrador e o `0x6500` com a dúvida escrita ao lado.

O `--screenshot` usa `QWidget.grab()`, que pinta fora da tela: a janela sai
inteira mesmo com um modal por cima, que é o defeito que o `import -window`
tem contra o `ed.exe` (seção do `CLAUDE.md`).

### Nenhum caminho de gravação, por construção

Todo valor da ficha é um `QLabel`. Não há widget editável, não há ação Save, e
não há chamada que alcance `Save.write` — abrir é seguro **por construção**, não
por cuidado. A MCR-TASK-12 recebeu a linha dizendo que é essa garantia que ela
perde, e que a substituta tem de ser medida.

### Os gates da fase

| gate | resultado |
|---|---|
| `ctest -R mcr` | **3 de 3 passed**, nenhum skip — o `mcr_ui` era pulado e agora roda |
| `make test` | **10 de 10** |
| `ui_check.py` | `ok: the UI came up on :98 and exited cleanly` |
| `controls.py` | **16/16 vermelhos**, incluindo o novo `ui-imports-an-address` |
| `selftest.py` | 0 falhas em 12 módulos + regras de desenho + controles |
| Regra 1 (`layout.py --rule1`) | 0 endereços fora de `layout.py`, com a `ui/` na varredura |
| Regra 3 | 0 ofensores; `PySide6` ausente do núcleo |
| idioma (`glossary.py`) | **0 queixas**, com a `ui/` incluída |
| `check_tasks.py` | 100 task(s), ok |
| fixture | `sha256 e53f4895…c47546`, intacta; a UI abre `work/mcr-entrada.mcr` |

### Arquivos criados/modificados

- `tools/mcr/ui/app.py` — **novo**, a entrada, `--smoke`, `--screenshot`, `--tab`
- `tools/mcr/ui/main_window.py` — **novo**, as duas abas, o menu e a barra
- `tools/mcr/ui/squad_view.py` — **novo**, a lista e a ficha
- `tools/mcr/ui/player_form.py` — **novo**, o registro em `QLabel`
- `tools/mcr/ui/formation_view.py` — **novo**, o campo e os dois fatores de tela
- `tools/mcr/model.py` — `load()`, a porta da UI
- `tools/mcr/controls.py` — o controle `ui-imports-an-address`
- `tools/mcr/selftest.py` — `--self-check`, que implica `--fast`
- `Makefile` — a guarda do `mcr` não promete mais uma task futura
- `docs/PLAN-MCR-PY.md` — a porta do `model.load()` na Regra 3 da §3.3
- `docs/prompts/perfil-mcr.md` — o `mcr_ui` passou a verde; a `ui/` na estrutura
- `docs/tasks/port-mcr/12-ui-gravacao.md` — três linhas: a porta de gravação, a
  garantia estrutural que se perde, e os fatores de tela
- `docs/tasks/port-mcr/progresso.md` — a linha desta task e o checklist

### Problemas encontrados

**1. A UI ficaria sem carregador.** Detalhado acima: a Regra 3 proíbe
justamente o módulo que abre cartão. O import adiado no `model.py` é a saída, e
o comentário no lugar diz por que ele é adiado — senão alguém "arruma" o import
para o topo e descobre o ciclo em outro dia.

**2. O rótulo de altura e idade saía duas vezes.** `Height 191 191`: as tabelas
de `HEIGHT` e `AGE` do `domains` são construídas a partir do bias e suas
entradas **são** os números, então anexar o rótulo repete o valor. A ficha passou
a anexar o rótulo só quando ele diz algo que o número não diz.

**3. O rótulo do jogador mais baixo do campo saía cortado.** O Y máximo da
fixture é 87, o rótulo fica em `(87 + 6) * 2 = 186` e o campo tem 192 de altura
— o texto passava da linha de fundo. O upstream não percebe porque os rótulos
dele são controles soltos no formulário e podem transbordar do `PictureBox`;
aqui tudo é pintado dentro de um widget só. A **superfície de desenho** ficou
mais alta que o campo, com o campo no topo dela. Os dois fatores continuam
intactos: o que mudou foi quanto espaço o desenho ganha, não onde um jogador
está.
