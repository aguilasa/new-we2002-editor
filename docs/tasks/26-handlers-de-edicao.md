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

**E o segundo verbo não tem dono nesta task** *(medido em 2026-08-12)*. Quem
grava é o grupo da [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md), que
`depends_on` esta — as barras editadas aqui só chegam à imagem pelo
`boton_barras2isoClick` (`0x0040cab8`), os nomes pelo `boton_nombres2isoClick`,
e assim por diante. É a mesma forma de circularidade que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) e que a decisão de 2026-08-11
desfez para o critério de tela da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md), e ela **não se desfaz por
mais uma passagem**.

Enquanto não se decidir, cada handler deste grupo tem duas metades de
verificação e só uma é alcançável:

| régua | o que ela julga | disponível? |
|---|---|---|
| **pixel** — `compara_tela.sh` | o efeito na tela (largura de barra, número, nome) | sim, e é o que fecha `track_barraChange` |
| **byte** — `golden_check.sh` | que a edição chega à imagem certa | **não** até a 27 |

Nenhuma das duas substitui a outra: pixel igual dos dois lados não prova que os
dois estão editando o **mesmo byte do modelo**, e é exatamente a lição da
terceira ponta da WTE-TASK-25.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/edicao-*.sh` | criar |

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec, incluindo regra de validação
- [ ] Comportamento de truncamento documentado por campo
- [ ] Golden verde para cada edição, uma por rodada
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
