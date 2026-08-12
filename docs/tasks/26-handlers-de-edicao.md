---
id: WTE-TASK-26
title: "Handlers de edição — nomes, números, atributos, mover jogador"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25"]
status: pendente
---

# WTE-TASK-26: Handlers de edição

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- Editam o estado **em memória**. A gravação é a WTE-TASK-27. A separação é de
  propósito: assim o golden test da 27 mede gravação, não edição, e uma
  divergência aponta para um lado só.

---

## Objetivo

Implementar o grupo de edição, com spec por handler.

### Alvos

| Grupo | Handlers | Endereços |
|---|---|---|
| nomes | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick`, `casilla_nombreKeyPress` | `0x0040d36c`, `0x0040d3c4`, `0x0040d41c`, `0x0040d43c`, `0x00408af8` |
| números | `dorsalClick`, `dorsalMouseDown`, `scroll_dorsalChange`, `casilla_dorsalKeyPress` | `0x00410a74`, `0x00410ddc`, `0x00402b58`, `0x00408b50` |
| atributos | `barrhabScroll`, `barrhab_bisScroll` | `0x00407a88`, `0x00407bb4` |
| barras | `sel_barraClick`, `track_barraChange` | `0x0040c9d0`, `0x0040ca10` |
| mover jogador | `paderechaClick`, `paizquierdaClick`, `parribaClick`, `pabajoClick`, `paderecha2Click`, `paizquierda2Click`, `paderechaeizquierdaClick`, `flechasapaClick` | `0x0040e5e8` … `0x00408088` |
| tática | `bolaMouseDown`, `bolaMouseMove`, `bolaEndDrag`, `campoMouseMove`, `rectanguloDragOver`, `rectanguloDragDrop`, `relojTimer` | `0x00408f00` … `0x00409ba4` |

`paderechaeizquierdaClick` é a novidade da v0.98 — "mover todos os jogadores de
cada time com um clique". `ficha_movertodos` é a tela dela.

**São 28 handlers, e a tabela acima está completa** — conferido em 2026-08-12
contra a coluna `grupo` do
[`published_methods.tsv`](../../wte/re/published_methods.tsv). O grupo `edicao`
tem 44 linhas lá; as 16 de diferença carregam na coluna `nota` o dono fora
desta task: **11 do `ficha_color`** mais `colorearClick` e os dois
`mallaNMouseDown` são da
[WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md), e
`casilla_precioKeyPress` com `etiqprecioClick` são da
[WTE-TASK-30](/docs/tasks/30-preco-do-jogador.md). Os 28 restantes são
exatamente os seis grupos acima (5 + 4 + 2 + 2 + 8 + 7).

### O que a spec tem de capturar aqui, e que a de carga não tinha

**Validação.** Estes handlers recusam entrada, e a regra da recusa é o que
importa. A WTE-TASK-05 já mapeou as mensagens de erro para os handlers que as
referenciam — a mensagem é o atalho para a regra. Exemplo já visto:

```
Numero do uniforme invalido ([33 ... 99] somente na Mastere
```

**Truncamento.** Todo campo de texto tem tamanho máximo no formato. O original
é C++Builder com buffer fixo; o comportamento de estouro (trunca? recusa?
corrompe o vizinho?) entra na spec, porque o Pascal não vai reproduzi-lo por
acidente. Isto alimenta a WTE-TASK-36.

**Ordem de evento.** `OnKeyPress` filtra caractere; a gravação no modelo
acontece onde? A WTE-TASK-13 mediu a ordem — usar a medição, não supor.

### Verificação

Estes não gravam. A verificação é: editar pela tela nos dois lados, **então**
gravar nos dois, e o golden test da WTE-TASK-22 compara. Uma edição por rodada,
para que a divergência tenha uma causa só.

**E o segundo verbo não tinha dono nesta task** *(medido em 2026-08-12)*. Quem
grava é o grupo da [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), que
`depends_on` esta — as barras editadas aqui só chegam à imagem pelo
`boton_barras2isoClick` (`0x0040cab8`), os nomes pelo `boton_nombres2isoClick`,
e assim por diante. É a mesma forma de circularidade que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) e que a decisão de 2026-08-11
desfez para o critério de tela da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md). Como as outras duas, **não
se desfaz por mais uma passagem** — se desfez por decisão.

### Decisão do usuário, 2026-08-12: esta task fecha por pixel; o byte é da 27

Cada handler de edição tem duas metades de verificação, e elas medem coisas
diferentes:

| régua | o que julga | quem executa |
|---|---|---|
| **pixel** — `compara_tela.sh` | o efeito na tela: largura de barra, número de camisa, texto do campo | **esta task** |
| **byte** — `golden_check.sh` | que a edição chega ao byte certo da imagem | **[WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md)** |

**Nenhuma das duas substitui a outra**, e é por isso que a segunda tem de ter
dono escrito em vez de sumir: pixel igual dos dois lados não prova que os dois
estão editando o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
WTE-TASK-25, onde comparar port com oráculo teria passado igual se **ambos**
estivessem lendo o time errado.

A metade excluída virou linha de critério de conclusão da WTE-TASK-27, na forma
"cada gravação com uma edição de tela do grupo da 26 antes". Exclusão sem dono
nomeado é buraco, e este projeto já pagou por isso na 25.

**Alternativas descartadas:** implementar o par de gravação junto com cada
edição fura o escopo da 27 e devolveria duas causas possíveis a cada golden
vermelho; fundir 26 e 27 numa task só perderia a separação que faz uma
divergência apontar para um lado só, que é a razão de as duas existirem
separadas (primeiro parágrafo do Contexto).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/edicao-*.sh` | criar |

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec, incluindo regra de validação — **2 de 28**
      (2026-08-12)
- [ ] Comportamento de truncamento documentado por campo
- [ ] ~~Golden verde para cada edição, uma por rodada~~ **Reescrito em
      2026-08-12** (ver "Decisão do usuário" acima): **conferência de tela verde
      para cada edição, uma por rodada**, pelo `compara_tela.sh`. O golden por
      byte da mesma edição é critério da
      [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), porque só ela tem
      como levar a edição ao disco
- [ ] Limpeza de campo usando `End`/`shift+Home`/`BackSpace`, nunca `ctrl+a`
- [ ] Nenhuma medição sobre `roms/` diretamente
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-12 — **primeira passagem, parcial.** A tarefa
  continua `⬜ Pendente`: 2 dos 28 handlers têm spec e Pascal.

- **Resumo do que foi feito:**

  Duas coisas, e a segunda vale mais que a primeira.

  **O grupo das barras — `sel_barraClick` e `track_barraChange`.** São os dois
  menores do grupo (61 e 166 bytes), foram lidos inteiros, e o que eles
  revelaram organiza a fase 4: **existe um buffer de edição, e ele não é
  cache**. Os cinco bytes das barras não vão da imagem para a tela; vão para
  `0x00434592`, e é dali que sai a largura. Três handlers o tocam — a carga
  enche (`0x0040cf79`), o `track_barraChange` grava (`0x0040caa1`), e o
  `boton_barras2isoClick` **lê para gravar na imagem** (`0x0040cb3d`).

  Sem esse buffer no port, editar mudaria o pixel e a gravação escreveria o
  valor velho — e o golden acusaria a **gravação** por um defeito que é da
  edição. Entrou como `BarrasEmEdicao` no `.aux.inc`, separado de
  `Jogo.teams[].bar_*`. A coincidência dos quatro endereçamentos virou guarda
  no [`check_barras.py`](../../wte/tools/check_barras.py), junto com a
  conferência de que `11*v + 9` é **a mesma sequência de bytes** na carga e na
  edição — se divergirem, uma barra carregada e uma editada com o mesmo valor
  deixam de ter a mesma largura, e a comparação de tela passa a medir a coisa
  errada sem avisar.

  **A dívida sem dono da WTE-TASK-25 fechou: `TControl::SetEnabled` é
  virtual.** A 25 encerrou registrando que o símbolo tem **zero** `call rel32`
  na `.text` e que não há escrita direta em `FEnabled` — e por isso a seção
  Saída da spec do `lista_equiposChange` desceu de `disassembly lido` para
  `nao medido`, e depois só até `observacao de tela`. A resposta estava nos
  bytes do próprio handler: o original carrega o VMT em `[obj]` e chama
  `call DWORD PTR [reg+0x64]` — três vezes só ali (`0x0040ce9b`, `0x0040cee9`,
  `0x0040d05c`). Chamada virtual não deixa `call rel32`; **a busca procurava a
  forma errada.**

  O slot é medido, não afirmado: o valor exportado de
  `@Controls@TControl@SetEnabled$qqro` aparece a `0x64` bytes do início do VMT
  em **108 classes** do `vcl60.bpl`, com o nome de cada uma lido de
  `[vmt - 0x2c]` — entre elas `TRadioButton`, `TComboBox`, `TStaticText` e
  `TImage`, que são as que o `MainForm` instancia. Virou conferência de build
  no `sonda_dorsal.py --check`, que já era o tool que fala `.bpl`. A seção
  Saída voltou a `disassembly lido`.

- **O achado que desbloqueia o resto da task: o teclado chega ao port.**

  O `golden_run_laz.sh` **reprovava com código 5** qualquer roteiro com
  `! tecla` ou `! texto`, apoiado na medição da
  [WTE-TASK-13](/docs/tasks/13-trace-de-eventos.md) de que o GTK2 sem
  gerenciador de janela nunca se considera ativo. Metade desta task — os cinco
  `KeyPress` de nome, os de número, e o critério "limpar campo com `End` /
  `shift+Home` / `BackSpace`" — só existe por tecla. Com aquela recusa de pé,
  ela **não tinha gate nenhum**.

  A medição de 2026-08-09 da WTE-TASK-13 vale para o que ela testou (`xdotool
  key` sem foco, e `key --window`, que usa `XSendEvent` e o GTK2 descarta) e
  não para o caso que faltava: `xdotool windowfocus` é `XSetInputFocus` e não
  precisa de gerenciador. Foi assim que o `compara_tela.sh` da WTE-TASK-25
  passou a trocar de time com `Down` — a evidência já estava na árvore,
  contradizendo a recusa, e ninguém tinha cruzado as duas.

  Remedido por este caminho, pelo próprio harness: com `ROTEIRO_FOCO=1`,
  **3 `! tecla Down` produzem 3 disparos de `lista_equiposChange`** no
  `port-trace.log`. O driver ganhou o foco atrás de variável, ligada **só** no
  lado port — mexer no lado oráculo invalidaria o controle sem ganho, porque o
  Wine implementa o próprio foco. A recusa saiu, e no lugar dela ficou o
  registro do porquê: ela era a resposta certa para o que se sabia, e o que
  mudou não foi o port, foi a pergunta ter sido refeita.

- **Escopo conferido, e ele bate:** os 28 handlers desta task são as 44 linhas
  `grupo = edicao` do `published_methods.tsv` menos as 16 que já trazem dono na
  coluna `nota` (14 da WTE-TASK-32, 2 da WTE-TASK-30). A tabela de alvos do
  enunciado não divergia — só não dizia isso.

- **Arquivos criados/modificados:**
  - `wte/re/spec/MainForm.sel_barraClick.md`, `MainForm.track_barraChange.md`
    — as duas specs, `disassembly lido` nas seis seções
  - `wte/src/impl/ep2002_mainform.sel_barraClick.inc`, `.track_barraChange.inc`
  - `wte/src/impl/ep2002_mainform.aux.inc` — `BarrasEmEdicao`
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — a carga passa pelo
    buffer
  - `wte/tools/check_barras.py` — o buffer nos quatro handlers, o `11*v + 9`
    idêntico nos dois lados, a âncora do `sel_barraClick` contra o `campos.tsv`
  - `wte/tools/sonda_dorsal.py` — `TControl.SetEnabled = VMT[0x64]`
  - `wte/tools/roteiro.sh` — `ROTEIRO_FOCO`, e a lápide de `roteiro_usa_teclado`
  - `wte/tools/golden_run_laz.sh` — a recusa fora, o foco ligado
  - `wte/tests/roteiros/golden-01-arranque.port.txt` — as duas justificativas
    que caducaram
  - `wte/re/spec/MainForm.lista_equiposChange.md` — a Saída de volta a
    `disassembly lido`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 88,5% → **87,8%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos nesta passagem:**
  - `make -C wte check` — **rc 0**
  - `lazbuild wte/wte.lpi` — compila
  - `golden_check.sh --modo controle` — **PASSOU: byte-idêntico**
  - `golden_check.sh --modo positivo` — **detectou** o byte plantado em 405228,
    com o offset (`OFS_SQUAD_NUMBERS_NATIONAL+512`)
  - `golden_check.sh --modo golden` — **PASSOU**, só as duas faixas declaradas
    (`1921862`, `2012984..2012985`). Repetido depois de mexer no `roteiro.sh`

- **Problemas encontrados:**
  1. **O `Xvfb` do `:99` morreu no meio da passagem outra vez**, e outra vez o
     `golden_check.sh` falhou com **saída vazia e código 1** — o `set -e` o
     derruba no primeiro `xdotool`, antes de qualquer mensagem. É a mesma
     ocorrência da nona passagem da WTE-TASK-25, e continua sem causa. O
     achado de ferramenta continua de pé e continua não executado: **um script
     que depende do `:99` devia dizer "não há `:99`" antes de tentar dirigir
     janela.** Restaurado como estava (`Xvfb :99 -screen 0 1280x1024x24
     -nolisten tcp`, sem `-auth`).
  2. O padrão `mov eax,[ebx+imm32]` casava **duas** vezes no
     `sel_barraClick` — a âncora e a `track_barra` logo abaixo. A guarda exige
     casamento único, então reprovou em vez de ler o campo errado; o padrão
     passou a incluir o `sub esi,eax` que só a âncora tem. Mesma forma do
     problema 1 da terceira passagem da WTE-TASK-25.
  3. A guarda do slot de VMT foi testada contra o erro plantado antes de
     entrar: com `SLOT_SETENABLED = 0x60` ela devolve 2 e diz que **0 classes**
     casaram. Sem isso ela seria "guarda testada contra o erro errado", que a
     WTE-TASK-25 já pagou.

- **O que falta para esta task fechar:**
  - **26 dos 28 handlers**, sem spec: os 5 de nome, os 3 de número que sobram
    (`dorsalClick`, `dorsalMouseDown`, `scroll_dorsalChange`,
    `casilla_dorsalKeyPress`), os 2 de atributo, os 8 de mover jogador e os 7
    de tática;
  - **a régua de byte**, que depende da
    [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) — ver a seção
    "Verificação" acima. É decisão, não passagem;
  - **a régua de pixel para edição**: o `compara_tela.sh` leva os dois lados ao
    mesmo time e mede as cinco larguras, mas não edita nada. Estender é o que
    fecha `track_barraChange`, e é o próximo passo barato;
  - o comportamento de truncamento por campo, que alimenta a
    [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md);
  - **como a `TTrackBar` responde ao clique na trilha nos dois widgetsets.** O
    `PageSize` do comctl32 sob Wine e o do GTK2 podem não ser o mesmo, e a
    faixa é curta (`Max = 9`): um clique que ande 2 de um lado e 1 do outro
    produziria divergência de tela que não é do handler. Medir antes de
    escrever roteiro de edição de barra.

---

- **Executado em:** 2026-08-12 — **segunda passagem, ainda parcial.**

- **Resumo do que foi feito:**

  A decisão do usuário sobre a régua, executada — e com ela o primeiro par de
  handlers de edição **conferido contra o original**.

  **A régua de pixel para edição existe:** `compara_tela.sh --edicao`. Ela leva
  os dois lados ao time 2, marca `sel_barra1` ("Defesa") e clica na trilha da
  `track_barra`. Medido, ROM japonesa:

  | | oráculo | port |
  |---|---|---|
  | as cinco larguras, em px | `64, 75, 75, 75, 75` | `64, 75, 75, 75, 75` |
  | `defesa`, valor do jogo | 4 → **6** | 4 → **6** |
  | as outras quatro contra o `we2002_core` | 4 de 4 exatas | 4 de 4 exatas |

  **As duas metades importam, e por razões diferentes.** As quatro não editadas
  continuarem ancoradas no dump mostra que a edição não respingou; a editada
  ter mudado mostra que houve edição — sem isso, "os dois lados concordam"
  passaria com a tela intacta, que é o par que a
  [WTE-TASK-20](/docs/tasks/20-round-trip-headless.md) ensinou a exigir. Do
  lado do port o script ainda exige do trace 1 `sel_barraClick` e o número
  previsto de `track_barraChange`.

  **O número que precisava ser medido antes de o roteiro existir era o passo do
  clique**, e ele fecha: clique na trilha não arrasta o cursor, **pagina**, e o
  `PageSize` do comctl32 sob Wine e o do `TTrackBar` da LCL sobre gtk2 são
  código diferente numa faixa curta (`Max = 9`). **Os dois andam +2 por
  clique** — 4 → 6 → 8, larguras 53, 75, 97. Se tivessem divergido, o roteiro
  de edição mediria divergência que não é do handler.

  E o valor esperado **não é literal no script**: sai do dump da camada de
  dados mais o passo. O único número escrito à mão é o passo, que é o que foi
  medido.

- **Duas coisas que a medição mostrou de graça:**

  1. **`Position :=` dispara `OnChange` na LCL.** A carga de time faz
     `track_barra.Position := ...`, e isso reentra no `track_barraChange` — que
     regrava o mesmo valor e redesenha a mesma largura, então é inofensivo,
     mas está na conta que o script confere. É a pergunta que o
     [`check_lcl_combo.py`](../../wte/tools/check_lcl_combo.py) respondeu para
     `TComboBox` (**não** dispara), com resposta oposta para `TTrackBar`.
  2. **As coordenadas de clique não são as mesmas nos dois lados abaixo de
     certa altura.** A `track_barra` do oráculo aceita clique em y 190..200 e a
     do port em y 199..207: o gtk2 desenha uma borda de 6 px que o Wine não
     desenha — o mesmo `(6, 6)` que o `calibra()` do `compara_tela.py` já
     media —, e a diferença cresce descendo a janela. `y = 200` é a
     intersecção, verificada nos dois. Vale para todo roteiro de edição desta
     task: **controle no rodapé do formulário pode não ter coordenada comum**,
     e nesse dia a saída é o `calibra()`, não o chute.

- **A decisão (b) alcançou o vocabulário de veredito, e tinha de alcançar.**
  `implementado` dizia "spec, Pascal, **golden** verde". Com a régua de byte
  morando na 27, nenhum handler de edição poderia ser `implementado` — nem os
  conferidos —, e o veredito passaria a medir a ordem das tasks em vez do
  estado do handler. Passou a dizer "a régua da task do handler verde", com uma
  tabela nomeando qual é qual por grupo, no
  [`GABARITO.md`](../../wte/re/spec/GABARITO.md). A metade por byte não sumiu:
  virou linha de critério de conclusão da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), com o par
  gravação × edição escrito.

  Os dois handlers foram de `aberto` para `implementado`. O índice vai a
  **3 `implementado`** de 96.

- **Arquivos criados/modificados:**
  - `wte/tools/compara_tela.sh` — o modo `--edicao`, o `edita_barra` comum aos
    dois lados, as duas exigências de trace, o valor esperado vindo do dump
  - `wte/tools/compara_tela.py` — `--editada N=V`, `confere_editada`, a barra
    editada fora da conferência contra o dump
  - `wte/re/spec/GABARITO.md` — a régua por grupo
  - `wte/re/spec/MainForm.sel_barraClick.md`, `MainForm.track_barraChange.md` —
    `implementado`, com a medição
  - `docs/tasks/26-handlers-de-edicao.md`, `docs/tasks/27-handlers-de-gravacao.md`
    — a decisão, nos dois lados
  - `wte/re/spec/INDICE.md` — regerado

- **Gates medidos:** `make -C wte check` rc 0; `compara_tela.sh --edicao` rc 0.

- **Problemas encontrados:**
  1. **`pkill -f "wte/build/wte"` mata o próprio shell** que roda o comando —
     o padrão casa a linha de comando do `zsh` que o executa. O sintoma foi
     uma série de comandos terminando em código 1 sem saída nenhuma, que
     parecia o `:99` caindo de novo. Os scripts do repositório não sofrem
     disso (o `limpa()` do `compara_tela.sh` roda dentro do próprio script,
     que morre junto e por último), mas medição de apoio à mão sofre. Prefira
     `pgrep -x wte` / `kill <pid>`.
  2. Primeira estimativa da coordenada da trilha (`y = 196`) veio de olhar uma
     captura ampliada e **errou por 11 px** no lado port: o clique caía acima
     do controle e nada acontecia, sem erro. Trocado por varredura — clicar em
     vários `y` e ver qual dispara o handler no trace.
  3. `sel_barra0` nasce `Checked = True` no `.dfm`, então clicar nele **não**
     dispara `OnClick`. A primeira tentativa de exercitar o `sel_barraClick`
     mediu zero disparo e parecia defeito do port. O rádio de prova passou a
     ser o `sel_barra1`.

- **O que falta para esta task fechar** *(revisado)***:**
  - **26 dos 28 handlers**, sem spec;
  - o comportamento de truncamento por campo (WTE-TASK-36);
  - estender o `--edicao` aos grupos que vierem — cada um precisa da sua
    sequência de cliques medida, como esta precisou.

---

- **Executado em:** 2026-08-12 — **terceira passagem, ainda parcial.** Abertura
  do lote de **número**, pelo defeito que já estava medido e sem dono.

- **Resumo do que foi feito:**

  **O off-by-one dos 23 `dorsalN` acabou.** A
  [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) tinha medido, na tela, que o port
  mostra o byte cru onde o original mostra byte + 1, e deixou o conserto sem
  dono — "é defeito de comportamento, pede correção própria". O dono é este
  lote, e a regra foi conferida nos **dois oráculos** antes de uma linha ser
  escrita:

  - **`wte.exe`:** a rotina do número (`0x00403f00`) termina em `inc eax` nos
    **três** ramos — `0x00403f65` (o time 48, que tem caminho próprio),
    `0x00403fae` (clube de ML), `0x0040403f` (seleção). Não é efeito de um ramo
    só, que é o que uma leitura apressada concluiria olhando um deles;
  - **`newWe2002`**, byte-idêntico ao `ed.exe`: `+ 1` ao exibir
    (`src/app/TeamView.cpp:195`), `- 1` ao gravar (`:468`), nas três famílias.

  E a correção foi verificada **sem abrir janela**: os `raw_numbers` do
  `ml_teams[0]` que o `dump_estado.pas` carrega da ROM japonesa, mais 1, dão
  exatamente os 23 números que a CORR-WTE-057 tinha lido da tela do oráculo.
  Terceira ponta outra vez — dado, tela do original, Pascal.

  **A consequência vale para o resto do lote e está anotada no código:** a
  imagem guarda base zero, a tela mostra base um, então quem **gravar** número
  desfaz a soma.

- **O modelo do lote, medido (specs ainda por escrever):**

  - **`dorsalClick`** (`0x00410a74`) não edita nada: sai se
    `lista_equipos.ItemIndex < 0`; extrai o índice do **nome** do componente
    (`Copy(Name, 7, 2)` sobre `'dorsalNN'`, não do `Tag` nem do ponteiro);
    seleciona o jogador em `lista_jugadores_1`; chama a rotina de realce
    (`0x0040b188`, o `MarcaCamisa` que já está em Pascal); posiciona o
    `ficha_dorsal` ao lado do rótulo clicado; e copia o número atual para lá.
  - **A regra de validação que o enunciado desta task pedia é imposta pelo
    widget, não por `if`:** `dorsalClick` chama
    `TScrollBar::SetMax` no `scroll_dorsal` com **99** quando o índice do time é
    > 62 (clube de ML) e com **32** caso contrário. Casa com a mensagem de erro
    que a WTE-TASK-05 mapeou (`[33 ... 99] somente na Master`) e com o clamp em
    32 do `newWe2002`.
  - **`scroll_dorsalChange`** (`0x00402b58`) é uma linha:
    `etiq_dorsal.Caption := scroll_dorsal.Position - Min + 1`. Os
    deslocamentos saíram do `vcl60.bpl` pelo método do `sonda_dorsal.py` —
    `TScrollBar.FMin = 0x20c`, `FMax = 0x210`, `FPosition = 0x214`, deduzidos de
    quais campos `SetMin`, `SetMax` e `SetPosition` tocam. Com `Min = 1` a conta
    é a identidade; o autor escreveu a forma geral.
  - **E a gravação do número não é desta task:** quem leva o valor de volta é o
    `BitBtn1Click` do `ficha_dorsal` (`0x00402b40`), que o
    `published_methods.tsv` põe no grupo `auxiliar` — a
    [WTE-TASK-28](/docs/tasks/28-handlers-auxiliares.md). Mais um par que
    atravessa task, como o das barras com a 27.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.aux.inc` — o `+ 1` em `NumeroDaCamisa`, com
    a evidência dos dois oráculos e o aviso para quem for gravar
  - `wte/re/spec/MainForm.lista_equiposChange.md` — o defeito fechado, com a
    conferência

- **Gates medidos:** `lazbuild` compila; os 23 números do port batem com a
  linha `oráculo` da CORR-WTE-057, conferidos contra o `dump_estado.pas`.

- **O que falta neste lote:** specs e Pascal de `dorsalClick`,
  `dorsalMouseDown`, `scroll_dorsalChange` e `casilla_dorsalKeyPress`; o buffer
  de edição do número em `.data`, se houver (as barras têm um, e a simetria
  sugere que sim); e estender o `--edicao` para medir os 23 rótulos — hoje eles
  só saem na montagem, para olho humano.

---

- **Executado em:** 2026-08-12 — **quarta passagem, ainda parcial.** O lote de
  número, mais um handler do lote de nome que veio de graça.

- **Resumo do que foi feito:**

  Cinco handlers com spec e Pascal: `dorsalClick`, `dorsalMouseDown`,
  `scroll_dorsalChange`, `casilla_dorsalKeyPress` e — porque estava no mesmo
  bloco de disassembly — `casilla_nombreKeyPress`. O grupo vai de **2 para 7 de
  28**; o índice de specs vai a **6 `implementado`** de 96.

  **A resposta à pergunta "onde está o buffer de edição do número" é: não há
  um.** As barras têm `0x00434592` porque a gravação delas é um botão separado.
  O número não: o `dorsalClick` **grava na hora**, quando o modal fecha.

  **E essa é a descoberta que muda a classificação do handler.** `0x00404048` é
  a irmã escritora da rotina de leitura `0x00403f00` — mesmos três ramos, mesma
  aritmética de endereço —, recebe número, time, slot e o arquivo aberto, faz
  `add al,0xff` (o `- 1` da base zero, confirmando de novo a regra da terceira
  passagem) e escreve **aquele trecho**, sem nada parecido com um `Save` do
  banco inteiro.

  É o primeiro handler que o `published_methods.tsv` classifica como `edicao` e
  que grava na imagem. A classificação não está errada — o que ele faz é
  edição, e a gravação é uma chamada no fim —, mas **o par atravessa task**,
  como o das barras. O Pascal escrito faz tudo menos a gravação, e a metade que
  falta está no critério de conclusão da
  [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md). Escrevê-la aqui
  também exigiria a primeira escrita **pontual** do port: o
  `we2002_database.pas` gerado sabe `Save` do banco inteiro, não "escreve estes
  dois bytes aqui".

  **A regra de validação que o enunciado desta task pedia não é um `if`.** É o
  `Max` da barra de rolagem da janelinha: 99 para clube de Master League
  (índice > 62), 32 para seleção. O usuário não digita número inválido porque
  **não há onde digitar** — a escolha é uma barra com faixa fixada na abertura.
  Casa com a mensagem que a WTE-TASK-05 mapeou e com o teto de 32 do
  `newWe2002`.

- **O erro que cometi e que só a semântica cruzada desmentiu:**

  Os deslocamentos de campo do `TScrollBar` saíram errados na primeira leitura.
  Varri os prólogos de `SetMin`/`SetMax`/`SetPosition` atrás de
  `mov reg,[this+disp]` e concluí `FMin = 0x20c`, `FMax = 0x210`,
  `FPosition = 0x214` pela interseção de quais campos cada uma toca. **Com
  esses valores a conta do `scroll_dorsalChange` vira `Position - Min + 1`,
  que com `Min = 1` é a identidade — plausível, e a spec teria fechado assim.**

  O que desmentiu foi o handler vizinho: o `dorsalClick` faz
  `Position := [0x214] - numero + 1`, e só sob `[0x214] = FMax` as duas contas
  se cancelam e o rótulo mostra o número escolhido. Refeita a leitura pelo
  caminho certo — as três não escrevem campo nenhum, são invocações finas do
  mesmo `SetParams(Position, Min, Max)`, e a ordem dos argumentos identifica os
  três: **`FPosition = 0x20c`, `FMin = 0x210`, `FMax = 0x214`**.

  É a armadilha 1 do projeto por outra porta. Interseção de campos tocados é
  heurística, e heurística que "fecha" num caso particular (`Min = 1`) é a que
  passa. Quem decide é a semântica cruzada de dois handlers, não a leitura
  isolada de um.

- **Outros três números que a leitura apressada erraria:**
  1. O índice da camisa sai do **nome** do componente (`Copy(Name, 7, 2)` sobre
     `'dorsalNN'`), não do `Tag` nem do ponteiro.
  2. `dorsalMouseDown` só reage a `mbRight`, e chama o `mostrar_jugadorClick`
     passando **`mostrar_jugador_1`** como `Sender` — é a cadeia do nome que faz
     aquele handler escolher o lado titular, então passar outro botão abriria a
     ficha do time errado.
  3. O título da janelinha é `' ' + nome`: a cadeia em `0x00425077` tem **um**
     caractere. O `Caption = 'Number'` do DFM é de projeto e some no primeiro
     clique.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 5 specs novas (`MainForm.dorsalClick`,
    `MainForm.dorsalMouseDown`, `ficha_dorsal.scroll_dorsalChange`,
    `jugador.casilla_dorsalKeyPress`, `jugador.casilla_nombreKeyPress`)
  - `wte/src/impl/` — os 5 `.inc`, mais `ep2002_mainform.uses` e
    `ep2002_dorsal.uses`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 87,6% → **86,0%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` compila.

- **O que fica aberto neste lote, com a razão:**
  - `dorsalClick` — `aberto`: falta a gravação, que é da 27;
  - `casilla_dorsalKeyPress` — `aberto`: o `SetFocus` dele é condicionado a
    `DWORD[0x00433614 + 44*global] <> 0`, e o que essa tabela guarda não foi
    medido. O port foca **sempre**, o que é divergência declarada. Medir sai
    barato quando a ficha do jogador estiver sendo preenchida;
  - os dois `KeyPress` da ficha ainda **não são exercitáveis de verdade**: a
    ficha abre, mas vazia — preenchê-la (`0x00404820`, `0x0040756c`) é o
    obstáculo que os lotes de atributo e de tática também têm pela frente.

---

- **Executado em:** 2026-08-12 — **quinta passagem, ainda parcial.** O lote de
  **nome**: os três `edit_nombreNKeyPress` e o `iguala_nombresClick`. O grupo
  vai de **7 para 11 de 28**; o índice a **9 `implementado`** de 96.

- **Resumo do que foi feito:**

  **Os três campos de nome não são três cópias do mesmo handler**, e a
  diferença estava no tamanho: 88, 88 e **32** bytes. O terceiro é outro
  bicho —

  | | `nombre1` | `nombre2` | `nombre3` |
  |---|---|---|---|
  | aceita | letra, dígito, `.`, espaço | idem | **só alfanumérico** |
  | `Return` | foca `nombre2` | foca `nombre3` | **não faz nada** |
  | teste | faixa a faixa, à mão | idem | `isalnum` da RTL |

  As duas diferenças fazem sentido no dado, e é uma **confirmação
  independente** de um achado da WTE-TASK-25: o terceiro campo é a
  **abreviatura** (`abbreviations[0]`, `MaxLength = 3` no DFM), não `names[2]`.
  A 25 descobriu isso comparando telas de um clube de ML; aqui o mesmo fato
  vem do código, por outro caminho.

  **`iguala_nombresClick`** copia `Nome1` nos outros dois, truncando cada um ao
  que cabe: `Copy(..., 1, global - 1)` no segundo e `Copy(..., 1, 3)` no
  terceiro.

- **Dois achados que valem mais que os handlers:**

  1. **O port não põe `MaxLength` em `edit_nombre1` nem em `edit_nombre2`.** O
     original põe, ao carregar a imagem: `edit_nombre1.MaxLength :=
     DWORD[0x00433a10] div 2` e `edit_nombre2.MaxLength := DWORD[0x00433b48] -
     1` (`0x0040cc38` e `0x0040cc48`). No port os dois aceitam texto de
     qualquer tamanho. **Nenhum teste atual pega isso** — é comportamento, não
     pixel —, e o `edit_nombre3` escapa por acaso, porque o `MaxLength = 3`
     dele está no DFM e o `.lfm` herda. É divergência aberta e entrada da
     [WTE-TASK-36](/docs/tasks/36-buffers-e-truncamento.md).
  2. **A global `0x00433b48` não é escrita por `mov` nenhum.** Varri o `.text`
     inteiro atrás de `mov ds:0x433b48,reg` e de `mov DWORD PTR
     ds:0x433b48,imm`: **zero**. Ela é preenchida por outro caminho — ponteiro,
     ou estrutura carregada em bloco. O valor em execução continua por medir, e
     o port usa **19**, tirado do tamanho do campo na camada de dados (`names`
     é `array[0..19] of AnsiChar`). É o método da §4.2 outra vez, mas **sem
     confirmação cruzada** desta vez, e está dito assim na spec.

- **O `iguala_nombres` continua com o defeito da CORR-WTE-057, e agora com mais
  uma hipótese derrubada.** O port não o desabilita no time-modelo (518 px de
  mudança no oráculo, **0** no port). Comparei o `.lfm` dele com o do vizinho
  `boton_nombres2iso`, que acinzenta certo: mesmo `TSpeedButton`, mesmo
  `Flat = True`, mesmo `Enabled = False` de nascença, os dois com `Glyph`. A
  **única** diferença é `ParentFont = False` mais as propriedades de fonte, o
  que não explica glifo que não acinzenta. Continua sem causa medida, e está
  registrado na spec do `iguala_nombresClick`.

- **Arquivos criados/modificados:**
  - `wte/re/spec/` — 4 specs novas (`edit_nombre1/2/3KeyPress`,
    `iguala_nombresClick`)
  - `wte/src/impl/` — os 4 `.inc`; `TAMANHO_DO_NOME` no `.aux.inc`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 86,0% → **85,2%**
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Gates medidos:** `make -C wte check` rc 0; `lazbuild` compila.

- **Aberto neste lote:** `iguala_nombresClick`, pelo limite não medido e pelo
  defeito de habilitação. Os três `KeyPress` fecham `implementado` — são
  filtros puros, sem estado e sem gravação.
