---
id: LOOKS-TASK-16
title: "`ui_check.py` — a UI julgada de fora, e o alvo `looks_ui`"
type: implementação
category: verificação
phase: 5
depends_on: ["LOOKS-TASK-15"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4.4"
status: concluído
---

# LOOKS-TASK-16: Os contratos da UI

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4.4 e
  §3.3.
- Molde pronto: o `tools/mcr/ui_check.py` julga a UI **de fora**, por contrato
  legível por máquina, e substitui os pontos que abririam modal.
- **A armadilha do ciclo do `.mcr` vale aqui inteira:** o `mcr_ui` passava com
  a janela sozinha quando faltava a fixture, e imprimia um `note:` que ninguém
  lia. Alvo que passa sem medir é pior do que alvo que pula.

---

- **A janela e os três comandos que o gate dirige já existem**, desde
  2026-09-16 ([`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md)):
  `ui/app.py --smoke`, `--looks <tupla> --screenshot <png>` e
  `--compare <png> <png>`, este último devolvendo quantos pixels diferem e em
  que porcentagem — é o que fecha o segundo critério abaixo sem escrever um
  comparador novo. O `--smoke` e o `--screenshot` **imprimem as contagens** do
  que desenharam (primitivas, texturizadas, superfícies, triângulos): um quadro
  em branco e um boneco escrevem PNG do mesmo tamanho, e só os números separam
  os dois antes de alguém olhar.
- **Medido no dia, para o gate ter piso:** `A-A1-A-A-A` contra `B-A1-A-A-A`
  difere em **47,13%** dos pixels e contra `A-A1-C-A-A` em **17,17%** — a
  cabeça sozinha, 640x640. Duas tuplas iguais dariam 0,00%.
- **Uma tupla pode ser RECUSADA, e isso não é falha da janela.** Três estilos de
  cabelo e os valores de barba acima de `E` saem como recusa da tabela de
  montagem, com a mensagem dela e **saída 2**. O gate tem de distinguir recusa
  de queda: `--smoke` e `--screenshot` saem 0, recusa sai 2, e falta de venv ou
  de imagem sai 77.
- **Peças cinza são esperadas**, e o gate não pode julgá-las como quadro
  errado: 237 das 593 primitivas da figura inteira amostram páginas que não
  estão no `DAT2D.BIN` — são o uniforme, que mora nos 105 `TEX_*.BIN`.

---

## Objetivo

`tools/looks/ui_check.py` mede o que a janela realmente fez, e pula quando não
pode medir.

---

## Critério de conclusão

- [x] O gate roda `--smoke` e `--screenshot`, e **julga o PNG**: tamanho, e que
      ele não é quadro em branco. Ele **decodifica o PNG por conta própria**,
      em `zlib` e `struct`, com os cinco filtros da spec — nem PIL nem Qt. Três
      tuplas medidas: 640x640, 15 a 19 cores, e a cor mais comum cobrindo
      38,47%. Quadro em branco é uma cor só, e o controle que zera os
      triângulos o produz.
- [x] Duas tuplas visivelmente diferentes produzem **imagens diferentes** —
      `B-A1-A-A-A` difere da referência em **47,13%** dos pixels (piso 40%) e
      `A-A1-C-A-A` em **17,17%** (piso 12%). E a mesma tupla duas vezes difere
      em **0,00%**, que é o que faz os dois números acima significarem alguma
      coisa.
- [x] Sem venv ou sem display, **pula com 77** e a mensagem nomeia o que falta.
      Medido nos dois caminhos que esta máquina alcança: sem
      `WE2002_LOOKS_IMAGE`, e a partir de uma árvore sem `work/venv-looks`
      acima dela.
- [x] **Não existe caminho em que o alvo passe sem ter medido.** As quatro
      faltas saem 77 antes de qualquer julgamento, e não há `note:` nenhum: ou
      ele julgou uma figura, ou pulou.
- [x] Achado o venv por busca para cima, como o `mcr/ui_check.py` faz — e por
      um motivo que esta task pagou: toda árvore plantada mora numa
      profundidade diferente.

---

## Log de Execução

**Executado em:** 2026-09-16 — **CONCLUÍDA**.

### O que se aprendeu, e é o achado da task

**Vermelho pela causa errada é tão inútil quanto verde pela causa errada.** A
primeira corrida do gate anunciou **3 de 3 controles vermelhos**, e os três
tinham morrido antes de desenhar um pixel: o `atlas.py` alcança `tools/pes2/`
de lado, a cópia plantada levava só `tools/looks/`, e o processo caía em
`ModuleNotFoundError: No module named 'lzss'`. O `controls.py` deste mesmo
ciclo já copiava as duas pastas, com a razão escrita no docstring — e mesmo
assim o erro se repetiu, o que diz que a lição não estava onde quem escreve um
plantio novo a lê. Agora está: virou a armadilha **27** do perfil.

O conserto tem duas metades, e a segunda é a que vale: copiar o que a árvore
alcança, e fazer o `measure()` devolver **`broke` separado de `bad`**. "Não
rodou" e "rodou e o juiz reprovou" são coisas diferentes, e só a segunda é
guarda exercitada.

### O gate não pergunta ao réu

O `--compare` do `app.py` existe e responde, mas é **o código sob teste**. Se
ele fosse o juiz de "duas tuplas desenham diferente", quebrá-lo deixaria o gate
verde — é o defeito que a CORR-MCR-018 mediu no outro ciclo, o juiz comparando
a conversão consigo mesma. Então o `ui_check.py` **conta os pixels duas vezes**,
com dois pedaços de código que não compartilham nada, e exige que os dois
números batam. O terceiro controle negativo é exatamente esse: com o `if` do
`_compare` desligado, a corrida fica vermelha por **desacordo**, não por
desenho.

### As corridas, e o que elas mediram

```text
$ python tools/looks/ui_check.py          (com WE2002_LOOKS_IMAGE apontada)
  A-A1-A-A-A, figure 0: 593 primitive(s), 356 textured, 5 surface(s), 1186 triangle(s)
  window up, off the desktop at -32000,-32000
  A-A1-A-A-A: 640x640, 15 colour(s), the commonest covers 38.47%
  A-A1-C-A-A: 640x640, 19 colour(s), the commonest covers 38.47%
  B-A1-A-A-A: 640x640, 18 colour(s), the commonest covers 38.47%
  A-A1-A-A-A vs B-A1-A-A-A (SKIN):  193050 of 409600 (47.13%), floor 40.0%, app.py --compare says 193050
  A-A1-A-A-A vs A-A1-C-A-A (H.COL):  70336 of 409600 (17.17%), floor 12.0%, app.py --compare says 70336
  A-A1-A-F-A is refused by the table, exits 2 and writes no picture
negative: breaking the tuple reaching the scene reddens the gate -- 0.00%, under the 40.0% floor
negative: breaking the triangles being drawn reddens the gate -- one flat colour
negative: breaking app.py --compare counting pixels reddens the gate -- the gate
          counted 193050 and app.py --compare counted 0
looks_ui: 3 of 3 negative control(s) red
```

Os dois caminhos de pulo que esta máquina alcança, cada um nomeando o que
falta:

```text
$ python tools/looks/ui_check.py          (sem a variável)
skipped: WE2002_LOOKS_IMAGE is not set, and a viewer with no disc has nothing
         to draw -- it names the Japanese data track

$ python <árvore sem work/venv-looks acima>/tools/looks/ui_check.py
skipped: no venv at work\venv-looks\Scripts\python.exe -- the window needs
         PySide6 of its own, and `python -m venv work/venv-looks` then
         `pip install PySide6` is the whole recipe
```

E o alvo pelo `ctest`, com os três listados **pelo nome** — que é a única forma
de ler o número, porque `ctest -R` que não casa nada sai 0 (armadilha 12):

```text
$ cmake -S . -B <fora da árvore> -G Ninja \
      -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
$ ctest --test-dir <build> -R looks
1/3 Test #10: looks_selftest ...................   Passed    10.32 sec
2/3 Test #11: looks_image ......................***Skipped    0.08 sec
3/3 Test #12: looks_ui .........................***Skipped    0.23 sec
100% tests passed out of 3

$ WE2002_LOOKS_IMAGE=<japonesa> ctest --test-dir <build> -R looks
1/3 looks_selftest  Passed  9.30 sec
2/3 looks_image     Passed  0.09 sec
3/3 looks_ui        Passed 29.81 sec
```

**1 passed, 2 skipped numa máquina limpa** — o que a §4.4 prometia para o fim
do ciclo, agora medido.

```text
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 18 file(s), 12609 line(s)
  ..... 37 of 37 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/ui_check.py --check      ->  ui_check.py: 0 failure(s)
$ python tools/check_tasks.py                 ->  123 task(s), ok
```

O `--check` do próprio módulo roda **sem venv, sem display e sem disco**: ele
constrói PNGs em memória e exige que cada juiz reprove o que tem de reprovar —
quadro em branco, tamanho errado, visualizador que ignora a tupla, visualizador
que oscila entre corridas, e `--compare` que discorda. É o que dá caso vermelho
aos juízes numa máquina onde o gate inteiro pularia.

### Problemas encontrados

- **O plantio morria no import** — acima, e virou a armadilha 27 do perfil.
- **A varredura da regra 1 lê `0xFF` como endereço**, e o decodificador de PNG
  usa cinco. Em vez de cinco isenções, um `BYTE` nomeado com uma só — e o
  `-32000` do estacionamento virou `PARKED`, com a razão ao lado.
- **`make looks-venv` não existe.** O docstring citava esse alvo; corrigido
  para a receita de duas linhas da §4.1, que é o que há. Comando inventado num
  gate é pior do que nenhum: quem o roda perde a corrida antes de começar.
- **Fora deste ciclo:** o `pes2_selftest` **falha nesta máquina**, e não é
  desta task — ele lista `/proc/self/fd`, que não existe no Windows
  (`FileNotFoundError: [WinError 3]`). Anotado aqui porque aparece em toda
  corrida de `ctest` sem filtro; o conserto é do ciclo de PES2.

### Arquivos criados/modificados

- `tools/looks/ui_check.py` — **novo**: o decodificador de PNG em stdlib, os
  quatro juízes (`judge_frame`, `judge_repeat`, `judge_pairs`,
  `judge_refusal`), o `measure()` com o `broke` separado, os três controles
  plantados e o `self_check()`
- `tools/looks/selftest.py` — `ui_check` na lista de módulos
- `tests/CMakeLists.txt` — o alvo `looks_ui`, com `SKIP_RETURN_CODE 77`
- `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` — o item do `looks_ui`, que
  esta task fechou: marcado, e com o `if(UNIX AND Python3_FOUND)` do
  enunciado corrigido para o `if(Python3_FOUND)` que a máquina exige. A
  linha vai **na task de destino**, porque quem executar a 19 lê o arquivo
  dela e não este Log
- `docs/PLAN-LOOKS-PY.md` — a §4.4: o `looks_ui` precisa também da imagem, e o
  "1 passed, 2 skipped" deixou de ser promessa
- `docs/prompts/perfil-looks.md` — a linha do `looks_ui` na tabela de gates, o
  número medido e a armadilha 27
- `docs/tasks/looks/progresso.md` — a linha da tabela e o item da Fase 5
