---
id: WTE-TASK-30
title: "Handlers dos 13 diálogos auxiliares"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25"]
status: concluído
---

# WTE-TASK-30: Handlers auxiliares

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- O resto dos 96: os handlers dos formulários `ficha_*`, que na maior parte são
  avisos e confirmações. Espera-se que a maioria receba veredito **`trivial`** —
  fecha o formulário, devolve um resultado, não toca a imagem.

**"Espera-se" não é veredito.** Cada um precisa ser olhado; o barato é que
olhar custa pouco quando o handler tem seis instruções.

> **Medido em 2026-08-21, e a expectativa não se confirmou.** Dos 17 handlers
> `auxiliar` que estavam `aberto`, **cinco** são o aviso ou a confirmação que o
> enunciado previa; os outros doze vão de uma chamada de seis bytes a 1.931. E
> **quatro deles escrevem na imagem de CD** — três rotas de gravação que nenhuma
> task anterior tinha visto, mais o preço do time inteiro. Ver o Log de
> Execução no fim deste arquivo.

---

## Objetivo

Fechar os handlers que sobraram, com veredito para cada.

### Alvos

Os `ficha_*`: `about`, `color`, `creditos_equipo`, `dorsal`, `enlaza`, `error`,
`error2`, `info`, `info2`, `info3`, `info4`, `movertodos`, `salida`, `warning`,
`warning_2`.

Handlers repetidos por vários formulários — `BitBtn1Click` (4×),
`BitBtn2Click` (2×), `BitBtn3Click` (3×), `SpeedButton1Click` (3×).

Os outros seis do escopo têm nome parecido mas **não** se repetem — cada um
aparece uma vez só: `SpeedButton2Click`, `Button2Click`, `Image3Click`,
`base_teamClick` (todos de `MainForm`), `botonClick` (`ficha_color`) e
`imagen_urlClick` (`ficha_about`).

**A coluna `formulario` do `published_methods.tsv` é indispensável aqui** — sem
ela, "implementar `BitBtn1Click`" é ambíguo entre quatro formulários.

### O que fica de fora, e por quê

Estes pertencem a `ficha_color`, `jugador`, `MainForm` e `estrategia` mas são
**fórmula**, não diálogo, e são das tasks 29 e 32:

| Handler | Formulário | Dono |
|---|---|---|
| `etiqprecioClick`, `casilla_precioKeyPress` | `jugador` | WTE-TASK-32 (preço) |
| `colorearClick` | `MainForm` | WTE-TASK-29 (render 2D) |
| `gradienteClick`, `oscurecerClick`, `aclararClick`, `lista_col0..3Change`, `colorMouseDown`, `barraChange`, `barra1Change`, `barra2Change` | `ficha_color` | WTE-TASK-29 (render 2D) |
| `malla1MouseDown`, `malla2MouseDown` | `estrategia` | WTE-TASK-29 (render 2D) |

**Um quinto entrou nesta lista depois de medido:** `base_teamClick`
(`MainForm`, `0x00410ff4`) é a **segunda metade da feature de preço** — o preço
do *time inteiro*, num clique, com a mensagem
`Precos dos jogadores calculados!!!!!!!!!!!`. O enunciado o listava entre "os
outros seis" porque foi escrito antes de alguém ler o corpo. O critério que
manda os dois handlers de `jugador` para a
[WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) — *"são fórmula, não
diálogo"* — vale igual para ele. A moldura ficou pronta aqui; a fórmula e a
gravação são da 32, e a linha foi acrescentada ao critério de lá.

Aqui se implementa **a moldura** desses formulários — abrir, fechar, OK/Cancelar
— e as tasks 29 e 32 preenchem o miolo.

### `ficha_enlaza` merece atenção

"Enlaza" = vincula. O `newWe2002` já sabe que os links (`OFS_PLAYER_ATTR_8`) são
o que o `Save` usa para reconstruir as all-star. Um diálogo que edita link **não
é trivial**, mesmo parecendo. Conferir antes de marcar.

### `ficha_movertodos` idem

É a tela de "mover todos os jogadores de cada time com um clique". Toca dados.

### E a resposta dos dois é a mesma, medida

**Nenhum dos dois formulários tem handler nos botões.** O ` Sim` e o `Nao` de
`ficha_enlaza` e de `ficha_movertodos` são `ModalResult = 6` e `ModalResult = 7`
no `.dfm`, sem `OnClick`; os únicos handlers publicados dos dois são
`FormCreate` (e um `FormShow` no `ficha_enlaza`), que a
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) já julgou `trivial` por
serem da forma "cor" do [`wte/re/arranque.md`](../../wte/re/arranque.md).

O aviso do enunciado continua certo e o dono é outro: **quem toca dados é o
chamador**, não a janela. `trivial` aqui não é preguiça: é que a janela
realmente não faz nada além de devolver um resultado.

**Mas os dois chamadores não estão no mesmo estado, e a primeira escrita desta
seção juntou os dois numa frase só** — corrigido pela
[CORR-WTE-086](/docs/tasks/CORR-WTE-086.md):

- **`ficha_movertodos` — medido.** O `paderecha2Click` abre o modal e só segue
  com `mrYes`, e o lote roda no `MoveTodosOsJogadores` do
  [`ep2002_mainform.aux.inc`](../../wte/src/impl/ep2002_mainform.aux.inc), onde
  o `if ficha_movertodos.ShowModal <> mrYes then` está escrito;
- **`ficha_enlaza` — não medido, e o dono não é o `pabajoClick`.** Aquele
  handler não menciona vínculo nem na spec nem no `.inc`. Quem alcança o modal
  é o
  [`MainForm.mostrar_jugadorClick`](../../wte/re/spec/MainForm.mostrar_jugadorClick.md),
  que continua **`aberto`** — e é ali, não aqui, que a rota de vínculo será
  fechada.

Duas coisas ficam por medir do lado do `ficha_enlaza`, e é bom que estejam
escritas: **qual condição** faz o `mostrar_jugadorClick` abrir o modal (a spec
diz "quando o jogador escolhido é de clube de Master League", sem endereço de
teste), e **o que o chamador faz com o `mrYes`** — que rotina desvincula, e
quantos bytes ela toca.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar |
| `wte/src/ep2002_*.pas` | modificar |

---

## Critério de conclusão

- [x] Todo handler restante com veredito escrito
- [x] Handlers de nome repetido resolvidos pelo formulário dono
- [x] `ficha_enlaza` e `ficha_movertodos` analisados, não presumidos triviais
- [x] A moldura dos formulários das tasks 29 e 32 pronta
- [x] Nenhum `trivial` atribuído sem ter olhado o código
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-21

- **Resumo do que foi feito:**

  Os 17 handlers `auxiliar` que faltavam ganharam spec medida por disassembly, e
  **onze fecharam com corpo**: cinco `trivial` (o ` Ok` do `ficha_dorsal`, o
  `Cancela` do `jugador` e os três `?`/`Sobre...` que só abrem um modal), quatro
  `implementado` (os dois banners de URL, e o `Original`/`Cancela` do editor de
  cor), um `nao portado` e a moldura do `base_teamClick`. O `dfm2lfm.py` foi
  reexecutado, o `lazbuild` compila, e o gate golden fechou **com o controle
  antes**: `golden-03-barras` e `golden-08-dorsal-mcr`, controle byte-idêntico
  nos dois e golden byte-idêntico nos dois — o `golden-08` importava porque é
  ele que clica no ` Ok` do `ficha_dorsal`, que deixou de ser stub nesta task.

  **O que se aprendeu, e é o achado que vale mais que os onze corpos: este
  grupo não é de "avisos e confirmações".** Quatro dos handlers escrevem na
  imagem de CD, e três dessas rotas não estavam em documento nenhum:

  | handler | o que grava | dono hoje |
  |---|---|---|
  | `ficha_color.BitBtn3Click` | 383 B do bloco de cor do time, via `0x004051A4` | **ninguém** |
  | `jugador.BitBtn3Click` | o jogador (`0x00404820`) e o número (`0x00404048`) | **ninguém** |
  | `estrategia.BitBtn3Click` | as duas cores de radar e a tática | **ninguém** |
  | `MainForm.base_teamClick` | 1 byte de preço por jogador, 23 por clique | WTE-TASK-32 |

  A [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) contava seis
  gravações; medido, são **nove**. Nenhuma das três primeiras podia ser
  implementada aqui: cada uma exige roteiro golden novo dos dois lados, com
  controle antes, e a régua do [`GABARITO.md`](../../wte/re/spec/GABARITO.md)
  para gravação é byte. As três ficaram `aberto` **com spec completa e
  justificativa escrita**, que é o que a
  [WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) vai encontrar — e **elas
  precisam de dono nomeado antes que a 31 rode**, porque a 31 é fechamento e
  não implementa.

  Outros dois `aberto` são dívida herdada, não trabalho desta task:
  `jugador.BitBtn1Click` chama a `0x0040756C`, que o port tem como
  `PreencheFicha` mas dentro do `.aux.inc` do `MainForm` — alcançá-la de
  `ep2002_jugador` fecharia ciclo de `uses`, e a saída é mover a rotina para
  unidade neutra, como a `wte_render2d` já fez uma vez; `estrategia.BitBtn1Click`
  chama a `0x0040A0B4`, que **não está portada** e cuja ausência já segurava o
  `mostrar_estrategiaClick` e o `estrategia.FormCreate`. Portar aquela rotina
  fecha três `aberto` de uma vez.

  Três correções de documento saíram da medição, e as três são de leitura
  errada, não de número velho:

  1. **A `0x004050D0` não carrega "os campos de nome do time".** Ela carrega o
     **bloco de cor** — bandeira, os dois uniformes, as oito chuteiras, a quarta
     paleta, a forma e o padrão — e o nome é a `0x00404E70`, que ela chama
     antes. A descrição errada estava na tabela `PAPEIS` do `dump_auxiliares.py`
     desde a WTE-TASK-25; corrigida no gerador e o `auxiliares.md` regerado.
  2. **A gravação lê 32 bytes e grava 30** em quatro dos sete blocos de cor. A
     última palavra de cada paleta é carregada e nunca devolvida. Um port que
     gravasse 32 mudaria bytes que o original nunca mudou.
  3. **A forma da bandeira é lida de um offset e gravada em cinco.** A carga usa
     `[0x004331E8]`, o do meio; a gravação percorre `[0x004331E0 + i*4]`,
     `i` de 0 a 4. O byte mora replicado na imagem.

  E uma armadilha nova para a §4.4 do plano: **implementar handler derruba a
  fração de gerador pelas duas pontas.** O stub `REStub` que ele substitui era
  saída de gerador — cinco linhas com `{$PUSH}`/`{$POP}` viram duas com `{$I}`
  —, então o numerador cai junto com a subida do denominador. Doze corpos de uma
  vez levaram 9.416 → 9.374 geradas e 6.476 → 6.816 à mão. O
  `check_fase2.py --check` pegou, como foi desenhado para pegar.

- **Arquivos criados/modificados:**

  - `wte/re/spec/` — 17 specs novas: `ficha_dorsal.BitBtn1Click`,
    `ficha_about.imagen_urlClick`, `ficha_color.BitBtn1Click`,
    `ficha_color.BitBtn2Click`, `ficha_color.BitBtn3Click`,
    `ficha_color.SpeedButton1Click`, `jugador.BitBtn1Click`,
    `jugador.BitBtn2Click`, `jugador.BitBtn3Click`,
    `estrategia.BitBtn1Click`, `estrategia.BitBtn3Click`,
    `MainForm.Button2Click`, `MainForm.SpeedButton1Click`,
    `MainForm.SpeedButton2Click`, `MainForm.Image3Click`,
    `MainForm.base_teamClick`, `ficha_error.SpeedButton1Click`
  - `wte/re/spec/INDICE.md` — regerado
  - `wte/src/impl/` — 12 `.inc` novos e 6 `.uses` tocados; o
    `ep2002_mainform.colorearClick.inc` ganhou a foto do slot 0
  - `wte/src/wte_cor.pas` — `GuardaOriginal` e `RestauraOriginal`, o slot 0 que
    faltava
  - `wte/src/ep2002_*.pas`, `wte/forms/*.lfm`, `wte/forms/conversao.md` —
    regerados pelo `dfm2lfm.py`
  - `wte/tools/dump_auxiliares.py` e `wte/re/auxiliares.{md,tsv}` — a correção
    da `0x004050D0`
  - `wte/re/fase-2.md` — regerado
  - `docs/PLAN-WTE-LAZARUS.md` — §4.4 remedida, com a mecânica das duas pontas
  - `docs/tasks/32-preco-do-jogador.md` — o `base_teamClick` acrescentado ao
    escopo e ao critério
  - `docs/tasks/progresso.md`, este arquivo

- **Problemas encontrados:**

  **Três rotas de gravação sem dono.** É o único item aberto que esta task não
  podia fechar sozinha, e ele bloqueava a WTE-TASK-31 — que exige nenhum
  `aberto` e não implementa nada. As três specs estão escritas e dizem
  exatamente o que falta em cada uma. **Resolvido no mesmo dia, a pedido do
  usuário:** virou a [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md), que as
  carrega na ordem `jugador` → `ficha_color` → `estrategia`, cada uma com
  roteiro golden dos dois lados e o controle fechando antes. A terceira leva
  junto o pré-requisito herdado da WTE-TASK-26 — portar a `0x0040A0B4`, que
  enche a tela de tática e destrava mais dois `aberto`.

  O `ficha_error.SpeedButton1Click` abre um `ficha_info2` cujo texto está em
  **inglês** enquanto o resto do app está em português — é a tradução PT-BR que
  não chegou naquele formulário. O port copia os rótulos como estão; traduzir
  mudaria a tela sem o original mudar junto.
