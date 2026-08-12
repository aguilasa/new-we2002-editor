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
