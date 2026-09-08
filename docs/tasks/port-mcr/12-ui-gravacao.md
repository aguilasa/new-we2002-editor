---
id: MCR-TASK-12
title: "Gravação pela UI: ficha, formação e dorsais"
type: implementação
category: ui
phase: 3
depends_on: ["MCR-TASK-11"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §3"
status: concluído
---

# MCR-TASK-12: A UI em gravação

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §3 e §5.1.
- **O gate da MCR-TASK-10 é pré-requisito duro.** Gravação pela tela sem gate é
  a combinação que perde cartão do usuário.
- **O veredito do `0x6500` (MCR-TASK-13) muda o que esta tela desenha**: se for
  capitão, há um campo "capitão"; se for o sexto cobrador, há seis cobradores.
  Descobrir depois é refazer a tela.

---

## Objetivo

Editar e gravar pela janela, com a garantia de que o arquivo gravado continua
passando no round-trip.

---

## Critério de conclusão

- [x] **A porta da UI é o `model`, e a gravação precisa da segunda.** A Regra 3
      proíbe `tools/mcr/ui/**.py` de importar `layout`, `card` e `mcrio`, e o
      `selftest` varre por isso — o controle `ui-imports-an-address` fica
      vermelho quando alguém tenta. A MCR-TASK-11 abriu a primeira porta,
      `model.load()`, que delega ao `mcrio` por import adiado (o `mcrio`
      importa o `model` no topo, então o caminho contrário só funciona dentro
      da função). A gravação precisa da porta correspondente — `model.store()`
      ou equivalente —, com as recusas do `mcrio` intactas: nada de um
      gravador próprio da tela, que é como uma janela grava um cartão que o
      gate teria recusado.
- [x] **Nada na tela de leitura grava, e isso é estrutural.** Todo valor da
      ficha é um `QLabel`; não há widget editável nem sinal que alcance
      `Save.write`. Ao tornar a tela editável, o que se perde é essa garantia
      por construção — então a substituta tem de ser medida, não prometida.
- [x] **`X*7` e `Y*2` moram só no `ui/formation_view.py`.** Arrastar um
      jogador no campo tem de converter de volta (dividir) **na UI**, e o que
      chega ao modelo são as unidades do cartão. A armadilha 7 do perfil é
      exatamente isto: os fatores no núcleo matam o round-trip.

- [x] Edição de ficha, de dorsal, de papel e de posição no campo (arrastar),
      todas indo para o modelo e de lá para os bytes.
- [x] **Gravar sempre em cópia por padrão**; sobrescrever o original exige
      confirmação explícita.
- [x] O arquivo gravado pela UI passa no `mcr roundtrip` — a tela não pode
      produzir cartão que o núcleo recuse.
- [x] Uma edição medida ponta a ponta: mudar um atributo pela tela muda
      exatamente os bytes previstos, e nada mais.
- [x] O `0x6500` desenhado conforme o veredito da MCR-TASK-13, ou ausente se
      ela ainda não tiver fechado. **Ela não fechou**, então o byte ficou em
      leitura: um rótulo que diz as duas leituras e que ele é lido e nunca
      gravado, e nenhum editor. A linha que diz onde o editor entra quando o
      veredito sair foi escrita **na MCR-TASK-13**.
- [x] Captura de tela no `:98`, antes e depois, anexada ao Log.
- [x] Diálogo, confirmação e mensagem de erro da gravação **em en-US**, como o
      resto da UI (§3.5).

---

## Log de Execução

**Executado em:** 2026-09-08

### Resumo

A tela passou a gravar, e a parte que custou não foi tornar a ficha editável —
foi **substituir a garantia que isso destrói**. A MCR-TASK-11 podia escrever
"nada aqui grava" e estar certa por construção: todo valor era um `QLabel`, e
não havia sinal que alcançasse `Save.write`. Com combos e spin boxes na tela
essa frase vira promessa, e o que ficou no lugar são três coisas medidas: o
alcance de cada editor vem do próprio `attributes.Field` (`low`..`high`), então
valor fora de faixa é **inalcançável**, não recusado adiante; a edição vai para
o **modelo**, nunca para o arquivo, então fechar sem gravar continua seguro por
construção; e existe **uma** porta de gravação, que o `selftest` varre.

Três lições, e as duas primeiras se repetem de tasks anteriores num contexto
novo:

1. **A varredura da porta de gravação precisa tokenizar.** A primeira versão
   contava `model.store(` por texto e acusava o `player_form.py` e o
   `squad_view.py` — que só **explicam nas próprias docstrings** que quem grava
   é a janela. É a mesma escolha que o `layout.address_monopoly()` já fazia
   pelo motivo oposto ao da `glossary.sweep()`, e agora há três varreduras sobre
   a mesma árvore com regras diferentes sobre os mesmos tokens.
2. **Modal em gate é travamento, não falha.** Um `QMessageBox` roda o próprio
   laço de eventos: uma recusa durante `--smoke` ou `--write-probe` ficaria
   parada até o timeout de 120 s e o alvo reportaria "não saiu" em vez de dizer
   a razão. Daí o `MainWindow.headless`, que faz a recusa **levantar**.
3. **Quem mede não é quem julga.** A Regra 3 mantém `layout` e `mcrio` fora de
   `ui/`, então o `app.py --write-probe` **relata** em JSON o que fez e não
   afirma nada sobre byte; quem confere localidade, round-trip e releitura é o
   `ui_check.py`, que pode importar os dois. A separação não foi elegância: sem
   ela a tela precisaria de um endereço para dizer se acertou.

O `mcr_ui` deixou de ser só "a janela subiu". Ele agora abre uma **cópia** da
fixture num diretório temporário, muda um atributo pelo spin box, grava com o
Save padrão, muda nome/dorsal/papel/cobrador e **arrasta um marcador com
`QMouseEvent` de verdade** (press, move, release — para exercitar detecção de
alvo, deslocamento de pega e a divisão pelos dois fatores), grava de novo, e
então confere. Medido nesta corrida: um atributo pela tela move **1 byte**, em
`0x0590d`, dentro dos 12 do registro do jogador 0 — o mesmo byte que o
`--edit-probe` da MCR-TASK-09 mediu pela linha de comando; o arraste levou o
jogador de linha 1 de `[11, 32]` para `[14, 43]` **em unidades do cartão**; e
os dois cartões gravados passam nas duas formas do round-trip.

### Arquivos criados/modificados

- `tools/mcr/mcrio.py` — `copy_target()`, a política de cópia por padrão, e os
  três checks dela
- `tools/mcr/model.py` — `store()` e `copy_target()` (a porta de saída, com
  import adiado como a de entrada), `Player.set_number()` e `Player.set_name()`,
  e o check que grava em arquivo e relê da **cópia** em disco
- `tools/mcr/ui/main_window.py` — a única chamada de `model.store`, o menu de
  gravação (cópia por padrão, "salvar como", sobrescrever com confirmação),
  o marcador de não gravado, o `closeEvent` e o `headless`
- `tools/mcr/ui/player_form.py` — a ficha editável, com o alcance vindo do campo
- `tools/mcr/ui/squad_view.py` — a linha da lista acompanha a edição
- `tools/mcr/ui/formation_view.py` — o arraste, `to_card_x`/`to_card_y`,
  os dez combos de papel e os cinco cobradores
- `tools/mcr/ui/app.py` — `--write-probe`, que dirige os widgets e relata
- `tools/mcr/ui_check.py` — o juiz do probe: localidade, round-trip, releitura
- `tools/mcr/selftest.py` — a varredura tokenizada da porta de gravação
- `tools/mcr/controls.py` — três controles novos (19/19 vermelhos), e o
  `model-half-number` reapontado para `Player.set_number`
- `tests/CMakeLists.txt` — o comentário do `mcr_ui` dizia que ele pulava por
  causa da MCR-TASK-11
- `docs/PLAN-MCR-PY.md` (§3.3), `docs/prompts/perfil-mcr.md` (Fase 3),
  `docs/tasks/port-mcr/{13,14}-*.md` (as duas pendências encaminhadas),
  `docs/tasks/port-mcr/progresso.md`

Fora do git, para o registro: `work/mcr-ui-12-before-formation.png`,
`work/mcr-ui-12-after-players.png` e `work/mcr-ui-12-after-formation.png`,
capturadas no `:98`. O comando que as reproduz:

```sh
export DISPLAY=:98
export XAUTHORITY=$(ps -o args= -C Xvfb \
  | sed -n 's/.*Xvfb :98 .*-auth \([^ ]*\).*/\1/p' | head -1)
PY=work/venv-mcr/bin/python
mkdir -p work/mcr-t12 && cp work/entrada.mcr work/mcr-t12/before.mcr
$PY tools/mcr/ui/app.py work/mcr-t12/before.mcr \
  --screenshot work/mcr-ui-12-before-formation.png --tab 1
$PY tools/mcr/ui/app.py work/mcr-t12/before.mcr --write-probe work/mcr-t12
$PY tools/mcr/ui/app.py work/mcr-t12/full.mcr \
  --screenshot work/mcr-ui-12-after-players.png --tab 0
$PY tools/mcr/ui/app.py work/mcr-t12/full.mcr \
  --screenshot work/mcr-ui-12-after-formation.png --tab 1
```

### Gates medidos

| gate | resultado |
|---|---|
| `WE2002_MCR_CARD=$PWD/work/entrada.mcr ctest --test-dir build -R mcr` | **3 de 3 passed**, nenhum pulado |
| `ctest -R mcr` sem a variável | 1 passed, 1 skipped (`mcr_card`), `mcr_ui` passa com a janela sozinha |
| `mcr_ui` com cartão | `one attribute moved 1 byte(s) at ['0x590d'], inside slot 0's record at 0x05904`; arraste `[11, 32] -> [14, 43]`; os dois cartões passam nas formas 1 e 2 |
| `make test` | **10 de 10** |
| `python3 tools/mcr/controls.py` | **19 de 19 vermelhos** (18 substituições, 1 arquivo novo) |
| `python3 tools/mcr/selftest.py` | 0 falhas em 12 módulos + regras de desenho + controles |
| `python3 tools/mcr/layout.py --rule1` | 0 endereços fora de `layout.py` |
| `python3 tools/mcr/glossary.py` | 0 queixas |
| `python3 tools/check_tasks.py` | 100 tasks, ok |
| `sha256sum work/entrada.mcr` | `e53f4895…c47546` — a fixture não foi tocada |

### Problemas encontrados

- **`model-half-number` virou controle quebrado.** `Save.set_number` passou a
  delegar a `Player.set_number`, e a linha `p.shirt_number = number` que o
  controle substituía deixou de existir — o `controls.py --self-check` acusou
  `matched 0x` na hora, que é exatamente o caso que o perfil manda tratar como
  **controle quebrado e não como vermelho**. Reapontado para a linha nova.
- **A varredura textual da porta de gravação acusava a prosa** (ver a lição 1).
- O comentário do `mcr_ui` no `tests/CMakeLists.txt` ainda dizia que o alvo
  pulava por causa da MCR-TASK-11, que fechou ontem. Corrigido, e passou a
  registrar que sem `WE2002_MCR_CARD` o alvo passa sem medir gravação.
