---
id: LOOKS-TASK-22
title: "A tela `LOOKS SET` na janela — doze linhas trocáveis, e o boneco redesenhado a cada troca"
type: implementação
category: ui
phase: 8
depends_on: ["LOOKS-TASK-21"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: concluído
---

# LOOKS-TASK-22: A tela `LOOKS SET` na janela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.4 (1).
- **É o pedido do usuário, e roda sobre a v1 como ela está.** As linhas de cor,
  cabelo, barba e chuteira já andam no `assembly.py`; o boneco ainda sai em
  prateleira até a [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) o montar dentro do mesmo painel.
- **A tabela vem da [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md).** A janela não conhece texto de valor nenhum que o
  `screen.py` não tenha.
- **O que a [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md) entrega, e como adaptou o que esta task
  esperava** (tudo em `tools/looks/screen.json`, lido pelo `screen.load()`):
  - o texto de cada valor de cada linha, com o valor guardado ao lado
    (`values`), para a tupla ir e voltar sem rótulo inventado;
  - as doze linhas **travam** nas pontas e o cursor vertical **dá a volta**
    (`screen.step`, `screen.move`);
  - a ajuda de cada linha, e **`Visual` na caixa ao carregar o state** até a
    primeira tecla (`help_on_load`) — reproduzir isso é fidelidade, não
    defeito;
  - **as regiões estão em pixels do display nativo de 512×240** e em frações
    dele, **não** em frações do quadro capturado: a captura do emulador corta
    overscan conforme a configuração, e fração dela não é o arranjo do jogo;
  - **o alcance da tela é menor que o do campo** em `HEIG` (155..210 de
    148..211), `FACE` e `H.F.COL.` (7 de 8) e `FOOT` (3 de 4). Uma tupla vinda
    de fora com valor fora do alcance não tem texto medido: recusa visível, como
    o `H1`;
  - o título que o objeto de texto recebe é `LOOKS SET`, e o quadro mostra
    `S SET` — **medido em 2026-09-17**
    ([`CORR-LOOKS-054`](/docs/tasks/looks/CORR-LOOKS-054.md)): a fonte do
    título tem glifo para nove caracteres (`AEJSTW12-`), e o que ela não tem
    não desenha nem anda com a caneta. A janela escreve o campo `title` da
    tabela, que é o que a tela desenha; `title_object` e `title_skipped` estão
    ao lado para quem precisar da string inteira.
- **A regra 3 continua:** a `ui/` não conhece endereço nem lê disco; troca de
  valor vira tupla, e a tupla vai ao `scene.py`.
- **Recusa é visível, nunca silenciosa.** `HAIR H1` não foi medido e o
  `assembly` recusa: a janela diz isso na caixa de ajuda e **não** desenha a
  cabeça de outro estilo no lugar — é a falha que o projeto existe para não
  cometer (§0, item 3).
- **Nenhuma janela aparece nos gates** (−32000 no Windows, `:98` no Linux); só
  o `.\make.ps1 looks` abre visível.

---

## Objetivo

O `ui/app.py` abre a tela `LOOKS SET`: as doze linhas com o texto do jogo, o
cursor, a caixa de ajuda, a placa de posição, e o boneco no painel redesenhado a
cada valor trocado — começando dos valores do slot 1 ou do slot 2.

---

## Critério de conclusão

- [x] `tools/looks/ui/looks_set.py` com o arranjo medido na [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md); o
      `ui/app.py` o abre por default, e `--state 1` / `--state 2` carregam os
      valores iniciais, a figura e a placa de cada slot.
- [x] Setas: ↑/↓ movem o cursor, ←/→ trocam o valor, com o travamento e a
      volta que a [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md) mediu; o boneco se redesenha a cada troca.
- [x] Recusa: o valor que o `assembly` recusa aparece na tela e na ajuda, e o
      painel não desenha nada no lugar.
- [x] **O gate julga por tecla:** o `ui_check.py` dirige a janela fora da tela
      com teclas sintéticas do Qt, anda cada linha até as duas pontas, e exige
      que o texto mostrado seja o do `screen.py`, que a tupla enviada ao
      `scene.py` mude e que a ponta trave.
- [x] **Tecla contra tecla com o jogo** (§10.4 (1)): uma sequência de teclas a
      partir do `load_state` nos dois lados, e o texto das doze linhas igual —
      com o controle da mesma sequência duas vezes no jogo.
- [x] Captura da nossa janela ao lado da captura do emulador, olhadas, no Log.
- [x] `.\make.ps1 looks` abre a tela; `-State 1|2` escolhe o slot, e o `help`
      diz os controles.

---

## Log de Execução

**Executado em:** 2026-09-17

### O que se aprendeu

**A janela não decide nada sobre a tela, e é isso que torna o gate mensurável.**
Onde uma tecla leva, como cada valor se chama, qual ponta trava, quando o
cursor dá a volta e o que a caixa de ajuda diz estão no `screen.State`, núcleo
puro escrito sobre o `screen.json` que a [`LOOKS-TASK-21`](/docs/tasks/looks/21-a-tela-medida.md) mediu no jogo; o
`ui/looks_set.py` manda os quatro botões e desenha a resposta. Se o widget
fizesse a própria aritmética, ele e o `screen.py` concordariam **por
construção**, e a comparação do gate não mediria nada.

**E daí sai a armadilha desta task, medida e não suposta** (armadilha 39 do
perfil): janela e tabela concordarem é barato. Com uma mentira plantada na
tabela de uma cópia da árvore — `HEIG=178` escrito `178 CM` — o `looks_ui`
passa **verde** (exit 0, 6 de 6 controles vermelhos) e o `oracle.py --keys` dá
**2 diferenças**, uma contra a tabela e outra contra a janela que acreditou
nela, com o controle do jogo contra si mesmo ainda verde. **Quem julga a tela é
o emulador**; o gate sem emulador cobre a outra metade — que a janela não
inventou nada por cima da tabela.

**Três coisas da tela que a janela reproduz de propósito, e que parecem
defeito:** a caixa de ajuda mostra `Visual` até a primeira tecla (sobra do menu
anterior, armadilha 35); a barra de título escreve `S SET`, porque a fonte do
título não tem glifo para `L`, `O` nem `K` ([`CORR-LOOKS-054`](/docs/tasks/looks/CORR-LOOKS-054.md)); e as doze linhas
**travam** nas pontas enquanto o cursor **dá a volta** nos dois sentidos.

**A recusa é visível e não troca nada de lugar.** `HAIR H1` continua sendo o
texto que o jogo escreve na linha, a caixa de ajuda passa a carregar a frase da
própria tabela de montagem, e o painel fica **vazio** — nenhuma outra cabeça
entra no lugar.

**O que a dupla de capturas mostra, olhada.** No slot 2, depois das mesmas 19
teclas nos dois lados (`work/looks-shots/keys-slot2.png`, do emulador, e
`keys-slot2-window.png`, nossa): as doze linhas, na mesma ordem, com os mesmos
textos (`C TYPE`, `A2 TYPE`, `B TYPE`, `178 cm`), o cursor em `HEIG`, a ajuda
`Height`, a placa `CB`, a camisa `SHIRT N` e o título `S SET` — e o mesmo no
slot 1, com `GK` na placa e o goleiro de 629 primitivas no lugar das 593 do
jogador de linha. O que difere é o que ainda não foi medido, e cada item tem
dono: o boneco montado e vestido (tasks [`27`](/docs/tasks/looks/27-o-boneco-montado.md) e [`30`](/docs/tasks/looks/30-o-uniforme.md) — o nosso ainda é a
prateleira da v1), e o cenário (task [`31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)), para onde foram escritas as
setas `◀ ▶` ao lado do valor, o alinhamento à direita do valor dentro da caixa
do cursor, e as caixas próprias da placa e da camisa.

### Gates, na árvore de `1fb8488`

Tirados **depois** do commit da task, que é a regra do perfil: a árvore anda a
cada edição do próprio arquivo, e número copiado no meio descreve uma árvore
que não existe mais.

```text
# na arvore de 1fb8488
$ python tools/looks/selftest.py
  ..... 71 of 71 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/screen.py --check
screen.py: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 8 module(s), 8 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
  H1 TYPE is refused on the screen: the row keeps the game's text, the help
  box carries the table's sentence, and the panel draws nothing
  the screen walked by key: 24 row(s) to both ends across 2 state(s), the
  cursor past both ends, and every text, help, plate and title is what
  screen.json measured off the game
looks_ui: 6 of 6 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --keys "" 2
  control: the same sequence twice in the game gives the same twelve rows and
  the same help
oracle --keys: 0 difference(s) after 19 press(es), across the game,
screen.json and our window

$ python tools/looks/oracle.py --keys "" 1
  control: the same sequence twice in the game gives the same twelve rows and
  the same help
oracle --keys: 0 difference(s) after 19 press(es), across the game,
screen.json and our window
```

**O vermelho, medido na cópia da árvore com a mentira plantada** (`HEIG=178`
escrito `178 CM` no `screen.json` da cópia):

```text
$ python <copia>/tools/looks/ui_check.py
looks_ui: 6 of 6 negative control(s) red, ...          # exit 0 -- VERDE

$ python <copia>/tools/looks/oracle.py --keys
  control: the same sequence twice in the game gives the same twelve rows ...
  FAIL  HEIG: the game shows '178 cm' and screen.json says a press leaves '178 CM'
  FAIL  HEIG: the game shows '178 cm' and our window shows '178 CM'
oracle --keys: 2 difference(s) after 19 press(es), ...  # exit 1
```

### Arquivos criados/modificados

- `tools/looks/ui/looks_set.py` — **novo**: a tela como widget; arranjo em
  pixels nativos, quatro teclas, recusa na caixa de ajuda, painel vazio quando
  a tupla é recusada.
- `tools/looks/screen.py` — `State` (onde a tela está depois de N teclas),
  `State.layout()` (o arranjo em pixels do display), `parse_keys`,
  `walk_to_end`, e os casos do `self_check` que os exercitam.
- `tools/looks/scene.py` — `Builder` (o disco lido uma vez, uma cena por
  tupla) e as três passagens que dão à `ui/` a tela sem endereço:
  `screen_state`, `screen_press`, `screen_keys`.
- `tools/looks/ui/app.py` — a tela como modo **default**, `--state`, `--keys`
  (teclas sintéticas do Qt), `--scale`, e o relatório que o gate lê.
- `tools/looks/ui_check.py` — o julgamento por tecla: doze linhas às duas
  pontas nos dois slots, o cursor além das duas pontas, a recusa alcançada por
  tecla, e três controles plantados novos.
- `tools/looks/oracle.py` — `--keys [SEQUÊNCIA [SLOT]]`: a mesma sequência no
  jogo (duas vezes, o controle), no `screen.json` e na nossa janela, com a
  dupla de capturas.
- `tools/looks/controls.py` — dois controles novos (`screen-row-walks-past-its-end`,
  `screen-help-honest-from-the-first-frame`).
- `make.ps1` — `looks` passa a abrir a tela; `-State 1|2`; `-Tuple` continua
  abrindo o visualizador de uma tupla; `help` diz os controles.
- `docs/PLAN-LOOKS-PY.md` — §10.4 (1) com o veredito datado.
- `docs/prompts/perfil-looks.md` — armadilha 39 e duas linhas na tabela de
  gates.
- `docs/tasks/looks/31-o-painel-e-o-cenario.md` — as quatro pendências de
  cenário que esta task viu, escritas **na task de destino**.
- `docs/tasks/looks/progresso.md` e este arquivo.

### Problemas encontrados

1. **O relatório da janela foi quebrado por uma vírgula.** O parser do gate
   cortava a linha `screen: slot …, cursor …, help …` por `", "`, e a ajuda
   carrega a frase da recusa, que tem vírgulas — `SyntaxError: unterminated
   string literal` no meio do gate. Corta-se pelos nomes dos campos.
2. **`--looks` tinha default, e um default esconde a pergunta "quem abre por
   quê".** Ele passou a nascer vazio: sem ele abre a tela, com ele o
   visualizador de uma tupla. As linhas que os controles plantados do
   `ui_check.py` citam ficaram intactas de propósito — mexer nelas deixaria os
   três controles vermelhos pela causa errada (armadilha 27).
3. **`QWidget.grab()` não traz o filho OpenGL.** A captura sairia com um buraco
   exatamente onde fica o boneco — e um buraco ali é indistinguível de uma
   recusa, que é a única coisa que esta janela precisa saber mostrar direito.
   O `picture()` compõe o `grabFramebuffer()` do viewer sobre o `grab()`.
4. **O primeiro julgamento por tecla que escrevi media o cursor, não a trava.**
   Ele apertava `Left` com o cursor noutra linha e concluía que a linha
   travava; passaria numa tela cujas linhas não travassem nada. O cursor vai
   para a linha **antes** da caminhada.
5. **Trocar o default de um alvo deixa duas opções órfãs, e elas ficam
   caladas.** Com a tela como default do `.\make.ps1 looks`, `-Figure 1` e
   `--wireframe` **sozinhos** — que antes abriam o visualizador de uma tupla e
   faziam o que dizem — passaram a ser aceitos e ignorados: a tela não tem
   câmera orbital nem prateleira, e o `app.py` engole a opção sem uma palavra.
   O alvo agora **recusa** os dois, dizendo qual é o equivalente na tela
   (`-State 1` é o goleiro) e como chamar o visualizador. Achado por pergunta
   do usuário depois do commit da task, e consertado em `4f5c2e1`.

   **E o primeiro guarda não disparou, pela armadilha do escopo:** dentro de
   uma função, `$PSBoundParameters` é o **da função**, que não declara
   parâmetro nenhum — então `ContainsKey('Figure')` é sempre falso ali. O
   efeito foi o pior possível: a recusa não veio, o alvo abriu com `--visible`
   e **a janela apareceu na tela do usuário**, que é exatamente o que a regra
   do `CLAUDE.md` proíbe. Quem lê `-Figure` agora é o escopo do script.
6. **A cópia da árvore não acha os save states nem o venv.** O `oracle.py` de
   uma cópia resolve `work/` a partir dela, então o controle vermelho precisa
   de `WE2002_LOOKS_STATES` apontado e de uma junção para o venv — e a junção
   se desfaz pelo link, nunca por `rm -rf`, que apagaria o venv de verdade.
