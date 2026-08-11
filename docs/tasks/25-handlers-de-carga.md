---
id: WTE-TASK-25
title: "Handlers de carga — abrir a imagem e popular as telas"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-22", "WTE-TASK-23", "WTE-TASK-24"]
status: pendente
---

# WTE-TASK-25: Handlers de carga

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- **Ordem por dependência, não por endereço.** Estes vêm primeiro porque tudo
  depende deles: sem carga, nenhum handler de edição tem estado para editar.

Estes handlers **leem** a imagem e **não gravam**. O golden test não os mede
diretamente — o que os mede é a tela. Por isso a verificação aqui é dupla:
comparar o que aparece na janela dos dois lados, e comparar o estado interno
contra o dump da WTE-TASK-20.

---

## Objetivo

Implementar o grupo de carga, com spec e verificação por handler.

### Alvos

| Handler | Endereço | Papel |
|---|---|---|
| `boton_dialogo_weClick` | `0x0040bd60` | abre a imagem de CD |
| `lista_equiposChange` | `0x0040cd6c` | carrega o time selecionado |
| `lista_equipos_2Change` | `0x0040e1a8` | segunda lista de times |
| `lista_jugadores_1Change` | `0x0040f8b8` | seleção de jogador |
| `mostrar_jugadorClick` | `0x0040f8d4` | abre a ficha do jogador |
| `mostrar_estrategiaClick` | `0x00410220` | abre a tela de tática |
| `lista_formacionesClick` | `0x00409aa0` | aplica formação predefinida |
| `ComboBoxDrawItem` | `0x0040adec` | owner-draw do combo |
| `FormCreate` / `FormShow` | 18 endereços | inicialização de cada formulário |

São **16 `FormCreate` mais 2 `FormShow`** — não um por formulário:
`ficha_error` e `ficha_error2` não publicam nenhum dos dois. A coluna
`formulario` do `published_methods.tsv` diz qual é qual.

### Duas armadilhas de framework

**`ItemIndex` dispara `OnChange` na LCL.** Se o original dependia de não
disparar (o `SetCurSel` do Win32 não dispara `CBN_SELCHANGE`), a carga de time
entra em recursão ou recarrega duas vezes. A WTE-TASK-13 já deve ter respondido
isso; se não respondeu, responder aqui antes de escrever código.

**`lista_formacionesClick` aplica formação sobre o time selecionado** — é ação
destrutiva disparada por clique em lista. Conferir que ela não roda durante a
carga.

### Verificação

1. **Estado interno** — depois de carregar o time N, o dump da WTE-TASK-20 do
   app tem de bater com o do `we2002_core`.
2. **Tela** — captura dos dois lados, mesmo time selecionado, comparação humana
   dos campos preenchidos (não de pixel). **Restrita aos campos que o grupo de
   carga possui** — ver o ciclo abaixo.
3. ~~**Sem gravação** — provar que nenhum destes escreve na imagem: rodar
   todos, fechar sem salvar, e `cmp` contra a cópia limpa tem de dar zero.~~

**O item 3 está errado, e a medição é que diz.** Abrir a imagem **grava**:
`boton_dialogo_weClick` injeta sete setores vindos de `dat.bin[0x20000..]` a
partir de `0x2e08`, com salto de `0x130` entre um e o seguinte
([`assets.md` §8.2](../../wte/re/assets.md)). São 11.952 bytes em 7 faixas na
ROM japonesa, e são exatamente as sete primeiras `conhecida:` que a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) declarou no roteiro do gate.

O item vira o seu contrário e continua barato: **o grupo grava, e grava só
isso** — nenhuma faixa além das que o oráculo grava pelo mesmo motivo.

### O item 2 tinha um ciclo dentro, e ele foi cortado

*(decisão de 2026-08-11, quarta passagem)*

O critério de tela pedia comparação da janela carregada, e a janela carregada
tem bandeira e uniforme 2D — que são
[WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md). Mas a 32 depende da 27,
que depende da 26, que depende **desta**:

```text
25 ──► 26 ──► 27 ──► 32 ──┐
 ▲                        │
 └────────────────────────┘   pelo criterio de tela da 25
```

Nenhuma passagem quebra isso; é a mesma forma de circularidade que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md), e ela se desfez por decisão,
não por mais uma passagem.

**A conferência de tela cobre o que o grupo de carga produz:** nome do time nos
três campos, as cinco barras de força, os 23 números de camisa, a lista de
jogadores, e o estado de habilitação dos controles que o `nacional` governa.
**Bandeira e uniforme ficam fora, como pendência nomeada da WTE-TASK-32** — e é
lá que a comparação deles tem de aparecer, senão a exclusão daqui vira buraco.

O que a 25 continua devendo, e que **não** foi afrouxado: as três rotinas 2D
(`0x00405270`, `0x004056c8`, `0x00405468`) ficam com veredito `aberto` nas
specs dos handlers que as chamam, com o dono escrito. Handler cujo corpo depende
delas não vira `implementado` aqui.

### Onde mora auxiliar que não é handler

*(decisão de 2026-08-11, quarta passagem)*

`wte/src/impl/` guarda `<unidade>.<handler>.inc`, um por handler, e o
`dfm2lfm.py` aborta em `.inc` órfão. Rotina interna compartilhada — a
`0x0040b188` é chamada por dois handlers — não cabe nesse formato, e foi o que
segurou o Pascal do `lista_jugadores_1Change` mesmo com a spec medida.

**Decisão: `wte/src/impl/<unidade>.aux.inc`**, um por unidade, incluído uma vez
na seção de implementação **antes** dos handlers daquela unidade. Consequências
que a próxima passagem executa:

- o `dfm2lfm.py` passa a reconhecer o sufixo `.aux` e a emitir o `{$I}` dele;
  `.aux.inc` órfão continua abortando, pela mesma razão dos outros;
- o `check_fase2.py` conta as linhas do `.aux.inc` como escritas à mão, junto
  com os demais `.inc` — senão a fração da §4.4 volta a **subir** a cada
  auxiliar escrito, que é a [CORR-WTE-051](/docs/tasks/CORR-WTE-051.md) pela
  terceira vez.

Alternativa descartada: unidade `we2002_*` nova. Esse prefixo é a camada de
dados gerada, e um auxiliar que mexe em controle de formulário não é dado.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (um por handler do grupo) |
| `wte/src/ep2002_*.pas` | modificar (corpo dos stubs) |
| `wte/re/spec/INDICE.md` | regenerar |
| `wte/src/wtemain.pas` | modificar — **remover o andaime `--show`** |

**O `--show` sai com esta task.** Ele existe porque na fase 2 nada navega: os
handlers são stub, e sem ele a
[WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) não conseguiria abrir
formulário para capturar
([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md), problema 3). Quando
a navegação de verdade entrar — que é aqui —, o andaime perde a razão de
existir; sem dono nomeado, ele fica para sempre. `--list` pode ficar, é barato
e não simula comportamento.

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec no gabarito da WTE-TASK-23 — **22 dos 28**
      (2026-08-11); os 18 `FormCreate`/`FormShow` estão todos lá, mais os três
      handlers de lista
- [ ] Estado interno batendo com o `we2002_core` após carga
- [x] Tela conferida contra o original para pelo menos 3 times distintos, nos
      campos que o grupo de carga possui — bandeira e uniforme são pendência
      nomeada da [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md).
      Times 2, 9 e 63 (clube de ML), ROM japonesa, por
      `wte/tools/compara_tela.sh`: as 15 larguras de barra batem em pixel
- [x] Medido **o que** o grupo escreve na imagem, e que não escreve mais que
      isso — 7 faixas, 11.952 B, as mesmas do oráculo
- [x] Comportamento de `OnChange` na carga decidido e testado — a LCL/gtk2
      **não** dispara `OnChange` por atribuição, como o Win32 e ao contrário do
      Qt; remedido a cada build pelo `check_lcl_combo.py`
- [ ] Andaime `--show` removido de `wtemain.pas`, com a navegação real no lugar
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-11 — **parcial**, a tarefa continua em andamento.

- **Resumo do que foi feito:**

  Entrou a **infraestrutura sem a qual nenhum handler da fase 4 pode existir**,
  mais os dois handlers do caminho de abrir imagem.

  O problema que precisava ser resolvido antes de escrever a primeira linha de
  corpo: os 18 `ep2002_*.pas` são saída do `dfm2lfm.py` e dizem **NÃO EDITAR À
  MÃO**, com `make -C wte check` provando isso a cada rodada — e o enunciado
  desta task manda modificá-los. As duas coisas não cabem juntas. A saída foi
  o gerador passar a **referenciar** corpo escrito à mão em vez de emitir stub:
  `wte/src/impl/<unidade>.<handler>.inc` vira `{$I}` logo abaixo da assinatura,
  que continua gerada porque é mecânica. `.inc` órfão aborta o gerador — nome
  errado viraria stub em silêncio, e o sintoma seria "o handler não faz nada".

  **O achado que muda o enunciado:** abrir a imagem **grava**. A task previa
  provar `cmp` = zero para o grupo de carga; o que existe é uma injeção de sete
  setores vindos de `dat.bin[0x20000..]`, sentinela `0xFC` em `0x2e14`, salto
  de `0x130` sobre EDC/ECC. O port passou a fazer o mesmo e as **sete faixas
  saíram do `conhecida:` do roteiro do gate: de 9 divergências declaradas para
  2**. As duas que restam — um byte no setor 817, dois no 855 — continuam sem
  causa medida.

  Efeito colateral previsto e cobrado por teste: o `test_so_teste_consome_a_
  camada` do `check_fase3.py` existia dizendo que a casca não consome a camada
  de dados, e comentava que a WTE-TASK-25 o faria falhar. Falhou. A asserção
  virou de lado e o `fase-3-fechamento.md` foi regerado — o gerador já tinha os
  dois ramos escritos.

- **Arquivos criados/modificados:**
  - `wte/tools/dfm2lfm.py` — o mecanismo de corpo à mão (`le_impl`, `{$I}`,
    `uses` por unidade, `{$PUSH}` por handler em vez de por bloco)
  - `wte/tools/test_dfm2lfm.py` — 6 testes do mecanismo (70 no total, verdes)
  - `wte/src/impl/` — `README.md`, os dois `.inc`, `ep2002_mainform.uses`
  - `wte/src/we2002_estado.pas` — **escrito à mão**: `dat.bin`, injeção,
    `AbreImagem`, o `TDatabase` compartilhado
  - `wte/re/spec/MainForm.FormShow.md`, `MainForm.boton_dialogo_weClick.md`
  - `wte/tests/roteiros/golden-01-arranque.txt` — 9 `conhecida:` → 2
  - `wte/tools/check_fase2.py` — stub **ou** corpo, conta por soma
  - `wte/tools/check_fase3.py`, `test_check_fase3.py` — a asserção invertida
  - regerados: os 18 `.pas`, `fase-2.md`, `fase-3-fechamento.md`, `INDICE.md`

- **Problemas encontrados:**
  1. O `IMPL_DIR` nasceu como global de import e quebrou o
     `test_blob_ausente_...`: os testes trocam `SRC_OUT` por árvore temporária,
     e o global continuava apontando para a árvore real. Passou a ser derivado
     de `SRC_OUT` em tempo de chamada.
  2. O `{$PUSH}{$WARN 5024 OFF}` envolvia o bloco inteiro de stubs. Mantido
     assim, o primeiro corpo de verdade escrito ao lado herdaria o silêncio e
     um parâmetro esquecido passaria. Virou um par por stub.
  3. O cabeçalho gerado afirmava que todo corpo é stub. Vira mentira no dia em
     que deixa de ser; foi reescrito para descrever as duas formas.

- **O que falta para esta task fechar:**
  - `lista_equiposChange`, `lista_equipos_2Change`, `lista_jugadores_1Change`,
    `mostrar_jugadorClick`, `mostrar_estrategiaClick`, `lista_formacionesClick`,
    `ComboBoxDrawItem`, `MainForm.FormCreate` e os 16 `FormCreate`/`FormShow`
    dos `ficha_*` — 26 dos 28 do grupo;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a decisão medida sobre `OnChange` disparar em `ItemIndex` na LCL;
  - a remoção do `--show` — que só pode sair **depois** da navegação real,
    senão os 17 formulários deixam de ser alcançáveis;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`);
  - quais controles recebem `$00ffb676` no `FormShow`.

---

- **Executado em:** 2026-08-11 — **segunda passagem, ainda parcial.**

- **Resumo do que foi feito:**

  Fechou a linha "`FormCreate` / `FormShow` — 18 endereços" da tabela de alvos.
  Os 18 têm spec, 15 têm Pascal, e o que sobrou aberto sobrou com a razão
  escrita.

  **A ferramenta que faltava era o mapa de campos, e ele quase saiu errado.**
  Todo handler do `.exe` referencia controle por deslocamento
  (`mov eax,[ebx+0x33c]`), e a derivação barata seria a ordem dos `object` no
  `.dfm`. Medido: essa regra acerta **73 de 440** campos — no `MainForm`,
  **zero de 116**. A ordem do `.dfm` é a de criação, a dos campos é a da
  declaração no `.h`, e o C++Builder não as mantém em sincronia. O mapa certo
  vem da *published field table* que o VMT aponta em **-56**, irmã da published
  method table da WTE-TASK-04 e viva pelo mesmo motivo: sem ela o formulário
  não carrega. Está em [`dump_campos.py`](../../wte/tools/dump_campos.py) →
  `wte/re/campos.tsv`, e é o que torna legível todo o resto da fase 4.

  **Os 18 não são todos triviais, e a medição é que diz.**
  [`dump_arranque.py`](../../wte/tools/dump_arranque.py) casa o corpo de cada um
  contra um padrão de bytes e os separa em quatro formas: **11** são uma
  chamada só a `TControl::SetColor` sobre a própria instância, **1** é um `ret`
  vazio (`ficha_about`), **1** é `BitBtn2.SetFocus` (`ficha_enlaza.FormShow`,
  que foca o botão *Não* — a fase 6 pede isso, e aqui já vem do original), e
  **5** são compostos. Padrão que deixe de casar vira `composto` sozinho, nunca
  classificação errada em silêncio.

  Com isso o **achado 3 da WTE-TASK-12 fechou**: a hipótese "é o `FormCreate`
  que pinta" estava certa, e a heurística de 6 formulários era piso — são
  **13**. O `MainForm` é a exceção: quem o pinta é o `FormShow`, e os três
  alvos de `$00ffb676` estavam na lista de pendências desta task — são o
  próprio `MainForm`, o `cuadro_dialogo_we` e o `grupo_barras`. Medidos e
  implementados; a janela do port deixou de ser cinza.

  `MainForm.FormCreate` monta as seis pastas de asset, e bate com o que a
  WTE-TASK-08 já tinha medido pelo lado do consumo.

  **A fração da §4.4 estava sendo medida com uma população só.** O mecanismo de
  `src/impl/*.inc` da primeira passagem tirava o corpo do `.pas` gerado (que
  encolhe) e o punha num `.inc` que o `check_fase2.py` não contava — então a
  fração **subia** a cada handler implementado. Com os 303 na conta ela cai de
  95,9% para **93,0%**, que é o número honesto, e daqui em diante cai de novo a
  cada corpo escrito. É o erro da [CORR-WTE-051](/docs/tasks/CORR-WTE-051.md)
  outra vez, e por isso agora há guarda: o `check_fase2.py` **reprova** se a
  frase da §4.4 do plano não trouxer a fração medida no dia.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_campos.py` + `wte/re/campos.tsv`, `wte/re/campos.md` — o
    mapa de campos, com três conferências que abortam
  - `wte/tools/dump_arranque.py` + `wte/re/arranque.tsv`, `wte/re/arranque.md`
    — a classificação dos 18, com o decodificador x86 do `dump_units.py`
    copiado (o `MainForm.FormShow` só tem outro handler 64 KB adiante)
  - `wte/re/spec/` — 17 specs novas: 14 `trivial`, 1 `implementado`, 2
    `aberto`; `MainForm.FormShow.md` atualizada
  - `wte/src/impl/` — 15 `.inc` novos e 13 `.uses`
  - `wte/src/we2002_estado.pas` — `RaizDosAssets`, `ResolveDiretorios` e as
    seis pastas de asset
  - `wte/tools/check_fase2.py` + `test_check_fase2.py` — os `.inc` na conta,
    a guarda da §4.4, 2 testes novos (19 no total)
  - `wte/tools/dfm2lfm.py` — o `{$I}` no comentário de cabeçalho virava
    `Warning: (2005) Comment level 2` nas 18 unidades
  - `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/visual.md` achado 3
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Problemas encontrados:**
  1. A ordem do `.dfm` **não** é a ordem dos campos. Descoberto porque o
     `MainForm.FormCreate` sairia guardando `dorsal4`, `dorsal22` e `dorsal23`
     em global — leitura que parece plausível e é falsa. O certo é `bandera`,
     `home1`, `home2`, e a diferença só apareceu ao ler a field table.
  2. O `extent` por "até o próximo handler publicado" mede 64.684 bytes para o
     `MainForm.FormShow`. Sem o decodificador de instrução, o inventário dele
     traria código de outra função.
  3. A guarda do `spec_index.py` pegou um `__fastcall` que eu tinha escrito em
     prosa, na spec do `ficha_about`. Ela está certa: a proibição é de token,
     não de intenção.
  4. `conferir_plano` rodava antes das outras conferências e sequestrava a
     mensagem de erro dos testes de árvore quebrada — passou para o fim.

- **O que falta para esta task fechar** *(revisado)***:**
  - os 9 handlers de carga que sobram: `lista_equiposChange`,
    `lista_equipos_2Change`, `lista_jugadores_1Change`, `mostrar_jugadorClick`,
    `mostrar_estrategiaClick`, `lista_formacionesClick`, `ComboBoxDrawItem`,
    `boton_dialogo_texClick`, `boton_mcrClick` — 19 dos 28 do grupo têm spec;
  - `ficha_color.FormCreate` e `estrategia.FormCreate` estão medidos e
    `aberto`: o corpo depende de onde mora o estado do editor 2D, que é decisão
    da WTE-TASK-26 e da 32, não desta;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a decisão medida sobre `OnChange` disparar em `ItemIndex` na LCL;
  - a remoção do `--show`, que só sai depois da navegação real;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`).

---

- **Executado em:** 2026-08-11 — **terceira passagem, ainda parcial.**

- **Resumo do que foi feito:**

  Especificação do handler central — `MainForm.lista_equiposChange`, 1.536
  bytes, o segundo maior do formulário — mais os dois irmãos de lista. O grupo
  vai de 19 para **22 de 28** com spec.

  **O resultado que vale é a equivalência dos dois oráculos, e ela é barata.**
  Ao trocar de time o original não usa offset: usa uma conta, com endereço
  lógico convertido para físico setor a setor, `2352 * (t div 2048) + (t mod
  2048) + 0x1e8178`, com `t = 0x45ff0 + 5*índice`. Essa conta leva o time 0
  para **2328184**, que é exatamente a `OFS_TEAM_BARS` que o `we2002_core` já
  conhece. Conferido byte a byte contra o `dump_estado.pas` sobre uma cópia da
  ROM japonesa: os índices 0, 1 e 62 batem com `teams[i].bar_*`, e 63 e 94 com
  `ml_teams[i-63].bar_*`. Ou seja **os 95 itens da lista são os 63 `teams`
  seguidos dos 32 `ml_teams`**, contíguos na imagem, e o port pode ler a camada
  de dados em vez de reabrir o arquivo. É o método da §4.2 funcionando: o diff
  diz *onde*, o core diz *o que aquilo significa*.

  Isso virou guarda de build, não nota de rodapé: o
  [`check_barras.py`](../../wte/tools/check_barras.py) decodifica as constantes
  do **próprio corpo do handler** e reprova se a conta deixar de cair na
  `OFS_TEAM_BARS`. Ele não abre imagem — a parte que depende de `roms/` fica na
  spec, com o comando; a parte que dá para conferir a cada build fica no
  `make check`.

  **Dois números que a leitura apressada erraria.** O `95` do handler não é o
  número de times: é o índice do item `95 Master L. ` do combo, o modelo que a
  Master League usa ao criar clube — e é por isso que ele desliga barra,
  bandeira, uniforme e nome. E a largura da barra é `11*v + 9`, aritmética
  literal do disassembly, não proporção sobre um máximo; `v = 0` dá 9 px, que é
  a barra vazia do DFM.

  **E o combo não é populado em tempo de execução:** os 96 itens estão no DFM e
  o `.lfm` os carrega verbatim. Era a suspeita natural — "quem enche a lista de
  times?" — e a resposta é "ninguém, ela já vem cheia".

- **Por que o Pascal não foi escrito:**

  O corpo chama quatro auxiliares que não são dele: `0x0040b2d8` (preenche a
  lista de jogadores, com decodificador de nome próprio), `0x00405270` e
  `0x004056c8` (bandeira e uniforme 2D, que são da
  [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md)), e `0x0040b0b4` /
  `0x0040b188`. Escrever metade do corpo faria o `check_fase2.py` contar o
  handler como "com corpo escrito", e o índice afirmaria pronto o que está pela
  metade — que é exatamente a mentira de índice que este projeto já pagou duas
  vezes. Spec medida com veredito `aberto` diz a verdade; `.inc` pela metade
  não diria.

- **Arquivos criados/modificados:**
  - `wte/tools/check_barras.py` — a guarda da aritmética, sem escrever arquivo
    (mesmo contrato do `check_lcl_props.py`)
  - `wte/re/spec/MainForm.lista_equiposChange.md` — a spec grande
  - `wte/re/spec/MainForm.lista_equipos_2Change.md`,
    `MainForm.lista_jugadores_1Change.md`
  - `wte/re/spec/INDICE.md` — regerado
  - `docs/tasks/progresso.md`, este arquivo

- **Problemas encontrados:**
  1. O padrão `add esi,imm32` casava **duas** vezes no corpo — a âncora e o
     `add esi,0x7ff` do arredondamento de sinal. A guarda exige casamento
     único, então ela reprovou em vez de ler a constante errada; o padrão
     passou a incluir o `lea esi,[eax+eax*4]` que vem antes.
  2. A primeira conta à mão da aritmética deu 2327672, 512 bytes abaixo da
     `OFS_TEAM_BARS`, e por um instante pareceu que as duas tabelas eram
     diferentes. Era erro de divisão na conta à mão. O script acertou de
     primeira — mais uma para "todo número vem de ferramenta".

- **O que falta para esta task fechar** *(revisado)***:**
  - `0x0040b2d8`, `0x0040b0b4` e `0x0040b188` medidos, e daí o Pascal dos três
    handlers de lista;
  - os 6 handlers de carga sem spec: `mostrar_jugadorClick`,
    `mostrar_estrategiaClick`, `lista_formacionesClick`, `ComboBoxDrawItem`,
    `boton_dialogo_texClick`, `boton_mcrClick`;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, medidos e `aberto`;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a decisão medida sobre `OnChange` disparar em `ItemIndex` na LCL;
  - a remoção do `--show`;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`).

---

- **Executado em:** 2026-08-11 — **quarta passagem, ainda parcial.**

- **Resumo do que foi feito:**

  As rotinas internas que travavam as três specs de lista, medidas — e a
  medição virou ferramenta, não anotação.

  **A tabela de auxiliares escrita à mão estava curta, e essa é a lição da
  passagem.** A spec do `lista_equiposChange` listava cinco endereços. Medido
  pelo [`dump_auxiliares.py`](../../wte/tools/dump_auxiliares.py), que percorre
  o corpo instrução a instrução e separa chamada interna de importada pelo
  `jmp DWORD PTR ds:<IAT>`, o handler chama **treze**. Parte da diferença é
  rotina de biblioteca que uma lista à mão descartaria de propósito — mas
  `0x004050d0` e `0x0040cbc8` carregam dado do jogo, e essas não estavam sendo
  descartadas: **não estavam sendo vistas**. Tabela de auxiliar à mão erra da
  forma que não aparece: o que falta na lista não é procurado, e a spec fica
  parecendo completa. Vale para toda a fase 4, onde cada handler aberto tem uma
  lista dessas.

  **Os dois oráculos se encontraram mais duas vezes, e as duas viraram guarda
  de build.** `0x00403388` não recebe offset: pergunta ao `ftell` onde está e,
  se `posição mod 2352 = 2072`, avança 304 — 24 de cabeçalho mais 2048 de
  dados, 280 de EDC/ECC mais os 24 do cabeçalho seguinte. É a **mesma
  geometria** que o `we2002_core` tem pré-somada nos `OFS_*`; o original a
  calcula em tempo de execução. E `0x0040cbc8` varre a tabela de offsets a
  partir de `0x004231a0`, que é exatamente onde a
  [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md) a registrou — duas medições
  independentes, o mesmo endereço. As duas afirmações são decodificadas do
  corpo das próprias rotinas a cada `make -C wte check`, como o
  `check_barras.py` da passagem anterior, e a segunda confronta o `offsets.tsv`
  em vez de repetir o número.

  **E o "decodificador de nome" não decodifica.** `0x0040b2d8` indexa duas
  tabelas em `.data` pelo byte lido, e a leitura barata seria "tabelas de
  tradução, como o `KanjiToAscii`". Medido, as duas são **identidade**: a
  rotina copia letra, dígito, `.` e espaço, troca qualquer byte acima de `z`
  por `?` e descarta o resto. Contra o `we2002_core`, que devolve espaço para
  byte desconhecido, é divergência de **tela**, não de gravação — entrada para
  a [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md). A conferência
  aborta se as tabelas deixarem de ser identidade, porque nesse dia a palavra
  "filtro" fica errada.

  `0x0040b188` ficou inteira: apaga a camisa marcada, acha a nova por
  `FindComponent('dorsal' + N)` e a destaca, com os nomes de propriedade vindos
  dos símbolos importados do `vcl60.bpl` em vez de inferência. É a outra
  metade da história da [`crash-causa.md`](../../wte/re/crash-causa.md) — a
  rotina que grava o ponteiro `0x004335e4` sem conferir.

- **Por que o Pascal continua não escrito:**

  Não é mais falta de medição no caso do `lista_jugadores_1Change` — a spec
  dele basta para escrever o corpo. O que falta é **onde mora um auxiliar que
  não é handler**: `wte/src/impl/` guarda um `.inc` por handler, e
  `0x0040b188` é chamada por dois. Inventar uma casa agora, para uma rotina só,
  é decidir por toda a fase 4 com uma amostra; a
  [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) traz mais auxiliares
  compartilhados e decide os dois juntos. Os outros dois handlers de lista
  continuam presos em medição mesmo: `0x00404374` (881 B, a aritmética do nome)
  e `0x00403f00` (328 B, o número de camisa) não foram lidos.

- **Arquivos criados/modificados:**
  - `wte/tools/dump_auxiliares.py` — o descobridor e as três conferências
  - `wte/tools/test_dump_auxiliares.py` — 19 testes, com PE sintético (444 no
    total, verdes)
  - `wte/re/auxiliares.md`, `wte/re/auxiliares.tsv` — 91 rotinas, 47 chamadas
    diretamente pelos 28 handlers do grupo
  - `wte/re/spec/MainForm.lista_equiposChange.md`,
    `MainForm.lista_equipos_2Change.md`,
    `MainForm.lista_jugadores_1Change.md` — a medição, e duas seções que saíram
    de `nao medido` para `disassembly lido`
  - `docs/tasks/progresso.md`, este arquivo

- **Problemas encontrados:**
  1. Os testes de guarda passavam pelo motivo errado. O PE sintético tinha uma
     `.text` de uma página, e `0x00403388` e `0x0040cbc8` caem fora dela: as
     três conferências abortavam com "fora das secoes" em vez da divergência
     plantada, e `assertRaises` não vê diferença. Guarda testada contra o erro
     errado é guarda não testada.
  2. A primeira redação do doc comparava "5 à mão contra 13 medidos" como se
     fossem a mesma população. Não são — parte dos 13 é biblioteca. O texto
     passou a dizer qual é a diferença que importa: as duas que carregam dado
     do jogo.
  3. A descoberta precisa percorrer instrução a instrução, não varrer o byte
     `0xe8`. `mov eax,0x40b2e8` tem um `0xe8` no operando, e a varredura de
     byte inventaria uma chamada com alvo lido do lugar errado. Virou teste.

- **Depois da passagem, duas decisões do usuário** *(2026-08-11)***:**

  O balanço da passagem mostrou que a task não fechava por passagem nenhuma: o
  critério de tela dela dependia da WTE-TASK-32, que depende da 27, que depende
  da 26, que depende desta. As duas decisões estão escritas no enunciado, nas
  seções "O item 2 tinha um ciclo dentro" e "Onde mora auxiliar que não é
  handler", e a metade excluída do critério de tela virou linha de critério da
  [WTE-TASK-32](/docs/tasks/32-camisa-e-bandeira-2d.md) — exclusão sem dono
  nomeado é buraco.

- **O que falta para esta task fechar** *(revisado)***:**
  - `0x00404374` e `0x00403f00` medidos, e daí o Pascal dos três handlers de
    lista;
  - o `.aux.inc` no `dfm2lfm.py` e no `check_fase2.py`, e daí o Pascal do
    `lista_jugadores_1Change`, cuja spec já basta;
  - os 6 handlers de carga sem spec: `mostrar_jugadorClick`,
    `mostrar_estrategiaClick`, `lista_formacionesClick`, `ComboBoxDrawItem`,
    `boton_dialogo_texClick`, `boton_mcrClick`;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, medidos e `aberto`;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a decisão medida sobre `OnChange` disparar em `ItemIndex` na LCL;
  - a remoção do `--show`;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`).

---

- **Executado em:** 2026-08-11 — **quinta passagem, ainda parcial.**

- **Resumo do que foi feito:**

  As duas decisões da quarta passagem, executadas — e a primeira rotina
  compartilhada em Pascal.

  **`wte/src/impl/<unidade>.aux.inc`.** O `dfm2lfm.py` passou a reconhecer o
  sufixo e a emitir o `{$I}` dele **uma vez por unidade, antes dos handlers** —
  em Pascal a ordem de declaração é o que autoriza a chamada. `.aux.inc` órfão
  aborta, como os outros. O `check_fase2.py` já contava `impl/*.inc` por
  wildcard, então as linhas entraram sozinhas na conta de escrito à mão: a
  fração da §4.4 caiu de 93,0% para **92,1%**, e o guard do próprio
  `check_fase2.py` reprovou até o plano trazer o número novo — funcionou como
  desenhado.

  **A pergunta do `OnChange` era real e a resposta é a melhor possível.** O
  Win32 não dispara `CBN_SELCHANGE` em `SetCurSel`; o Qt **dispara**
  `currentIndexChanged` em `setCurrentIndex`, e o `newWe2002` precisou de
  `QSignalBlocker` nas cargas de time por causa disso. Medido em gtk2 com o
  [`test_lcl_combo.pas`](../../wte/tests/test_lcl_combo.pas): **nenhum dos
  cinco casos dispara** — nem `ItemIndex :=`, nem reatribuir o mesmo índice,
  nem `Items.Clear` com item selecionado. A LCL se comporta como o original, e
  os corpos da fase 4 ficam iguais ao que a spec descreve, sem bloqueio de
  sinal. Virou guarda: a resposta é propriedade do widgetset instalado e pode
  virar num upgrade sem que uma linha deste repositório mude.

  **`MarcaCamisa` — o `0x0040b188` — em Pascal.** Nomes de propriedade vindos
  dos símbolos importados do `vcl60.bpl`, não de inferência. Uma preocupação
  levantada e derrubada por medição: os 23 `dorsalN` declaram `Color = clGray`
  e a LCL tem `Transparent = True` por padrão no `TStaticText` — e a marcação é
  feita de cor de fundo, então seria o caso de falhar sem sintoma. Capturado no
  `:99`, o pixel dentro de um `dorsalN` é (128, 128, 128): a cor aparece, não há
  o que compensar.

- **O que ficou por fazer, e por quê:**

  O corpo escrito **ainda não é exercitado por nada**, e isso está dito na
  spec em vez de disfarçado. O combo nasce `Enabled = False` e sem itens; quem
  o povoa é o `lista_equiposChange`, preso em `0x00404374` (881 B, não lido). O
  golden não cobre e não deveria — ele compara bytes da imagem, e o handler não
  grava nada.

  A tentativa de exercitá-lo por programa de console **esbarrou noutra coisa, e
  ela é achado**: criar qualquer um dos 18 formulários (`Tficha_about.Create`,
  não só o `MainForm`) **bloqueia em `poll` na conexão X** quando o programa é
  compilado direto com `fpc`, no mesmo `:99` em que o `wte` construído por
  `lazbuild` cria os 18 sem travar. Descartados por experimento: `cthreads`,
  `RequireDerivedFormResource` e a hipótese de servidor X travado (um
  formulário montado em código, sem `.lfm`, roda). O programa-sonda **não foi
  commitado** — subir um teste que trava é pior que não ter teste.

- **Arquivos criados/modificados:**
  - `wte/tools/dfm2lfm.py` — o `.aux.inc` (`le_impl`, o `{$I}` único, o aborto
    de órfão) e o cabeçalho que descreve as duas formas
  - `wte/tools/test_dfm2lfm.py` — 4 testes do mecanismo (74 no total)
  - `wte/tools/check_lcl_combo.py` + `wte/tests/test_lcl_combo.pas` — a
    medição do `OnChange`, como guarda de build (448 testes no total)
  - `wte/src/impl/ep2002_mainform.aux.inc` — `MarcaCamisa`
  - `wte/src/impl/ep2002_mainform.lista_jugadores_1Change.inc`
  - `wte/src/impl/README.md` — a seção do `.aux.inc`
  - `wte/re/spec/MainForm.lista_jugadores_1Change.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 93,0% → 92,1%
  - regerados: os 18 `.pas`, `fase-2.md`, `INDICE.md`

- **Problemas encontrados:**
  1. O primeiro teste do `.aux.inc` passava pelo motivo errado: procurava a
     cadeia `.aux.inc` no `.pas` gerado, e o **cabeçalho** de toda unidade
     descreve o mecanismo e a cita. Passou a procurar o `{$I}`.
  2. O `Xvfb` da máquina subiu **sem `-auth`** nesta sessão, e o
     `check_lcl_combo.py` exigia o cookie — pulava dizendo que não havia
     `:99`, que é diagnóstico mandando procurar no lugar errado. O cookie
     virou opcional, com as duas formas registradas.
  3. Um `wte` esquecido no `:99` de uma captura de tela ficou vivo depois de
     `kill %1` (o shell não interativo não tem controle de job). É a armadilha
     6 do `progresso.md` chegando por uma porta nova: o processo sobrou de uma
     medição minha, não de um teste.

- **O que falta para esta task fechar** *(revisado)***:**
  - exercitar o corpo do `lista_jugadores_1Change` — depende do
    `lista_equiposChange` ou de resolver o travamento do programa de console;
  - `0x00404374` (881 B) e `0x00403f00` (328 B) medidos, e daí o Pascal dos
    três handlers de lista;
  - os 6 handlers de carga sem spec: `mostrar_jugadorClick`,
    `mostrar_estrategiaClick`, `lista_formacionesClick`, `ComboBoxDrawItem`,
    `boton_dialogo_texClick`, `boton_mcrClick`;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, medidos e `aberto`;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a remoção do `--show`;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`).

---

- **Executado em:** 2026-08-11 — **sexta passagem, ainda parcial.**

- **Resumo do que foi feito:**

  O handler central em Pascal — e **sem ler os 1,2 KB de disassembly que
  pareciam bloqueá-lo**.

  A observação que mudou o custo: `0x00404374` (881 B) faz aritmética para
  achar o nome do jogador e `0x00403f00` (328 B) o número de camisa, e **nós já
  temos os dois**. É o método da §4.2 pela terceira vez nesta task, depois das
  barras e da fronteira de setor: o original calcula endereços que caem em
  bytes cujo lugar já conhecemos por outro caminho — `OFS_TEAM_BARS` para as
  barras, a tabela em `0x004231a0` para os nomes de time (a mesma da
  [WTE-TASK-06](/docs/tasks/06-mapa-de-offsets.md)), e o mesmo elenco para nome
  e número de jogador. O port lê `Jogo`, e as duas rotinas não precisaram ser
  lidas.

  Entraram, no `.aux.inc` do `MainForm`: `BarraDoTime`, `NomeDoTime`,
  `IndiceDoJogador` (com `ResolveMlLink` para clube de ML), `NomeDoJogador`,
  `NumeroDaCamisa`, `PreencheCamisas` (o `0x0040b0b4`) e `PreencheJogadores`
  (o `0x0040b2d8`). E o `lista_equiposChange` inteiro: os três blocos do
  original, na ordem dele.

  **A casca passou a consumir a camada de dados de verdade.** O
  `check_fase3.py` mede isso e o número virou **2** unidades — o
  `we2002_estado.pas` e agora o `ep2002_mainform.pas`. Antes da WTE-TASK-25 era
  zero, e o teste que existia prevendo a própria falha já tinha sido invertido
  na primeira passagem.

- **Dois achados da tentativa de conferir, e o primeiro é uma correção minha:**

  **~~O combo do port não abre por falta de window manager.~~ Errado.** Foi a
  primeira leitura, e ela chegou a entrar em spec e em mensagem de commit antes
  de cair: `xdotool windowfocus` funciona e a lista continua sem abrir. A causa
  está no DFM — **`lista_equipos` nasce `Enabled = False`** (`MainForm.dfm`
  linha 715, e portanto no `.lfm`). Controle desabilitado ignora clique, com ou
  sem gerenciador de janela. O que falta é o port habilitá-lo depois de
  carregar a imagem. Lição: *"não dá para dirigir"* é conclusão sobre o
  ambiente, e eu a tirei sem antes olhar o estado do próprio controle.

  **`TControl::SetEnabled` nunca é chamado — e isso põe em dúvida a spec.** O
  símbolo é importado do `vcl60.bpl` e tem thunk em `0x00422884`; a `.text`
  inteira tem **zero** `call rel32` para ele, e a única referência ao slot
  `0x0043ec1c` do IAT é o próprio thunk. No mesmo bloco de thunks, para
  comparar: `SetText` 78, `GetText` 24, `SetVisible` 14.

  A seção Saída da spec do `lista_equiposChange` lista uma dúzia de
  `.Enabled := verdadeiro` com evidência `disassembly lido` — escrita na
  terceira passagem. Com zero chamadas a `SetEnabled`, ou o original liga esses
  controles por outro caminho (RTTI — `Typinfo` **é** importado —, o `Parent`,
  ou o `TWinControl`), ou aquela leitura foi inferida da tela e rotulada como
  disassembly. A evidência da seção foi **rebaixada para `nao medido`**, e o
  Pascal escrito nesta passagem herda a dúvida: ele reproduz exatamente esses
  `.Enabled :=`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — o handler
  - `wte/src/impl/ep2002_mainform.aux.inc` — os sete auxiliares novos
  - `wte/src/impl/ep2002_mainform.uses` — `we2002_database`, `we2002_types`,
    `StdCtrls`
  - `wte/re/spec/MainForm.lista_equiposChange.md` — o Pascal, o obstáculo
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 92,1% → **89,7%**
  - regerados: os 18 `.pas`, `fase-2.md`, `fase-3-fechamento.md`, `INDICE.md`

- **Problemas encontrados:**
  1. A fração da §4.4 caiu duas vezes na mesma sessão (92,1% e 89,7%), e as
     duas vezes o `check_fase2.py` reprovou até o plano trazer o número. O
     guard escrito na quinta passagem já pagou o próprio custo.
  2. Um `wte` esquecido no `:99` sobreviveu a `kill %1` e a `pkill -f`; só
     `pkill -9` com o caminho completo resolveu. Segunda vez na mesma sessão.

- **O que falta para esta task fechar** *(revisado)***:**
  - **descobrir como o original habilita controle**, e daí quem habilita o
    `lista_equipos` — sem isso o combo do port não é clicável e dois critérios
    não são exercitáveis, e a seção Saída da spec do `lista_equiposChange`
    continua `nao medido`;
  - `lista_equipos_2Change` em Pascal (mesmos auxiliares, já escritos);
  - os 6 handlers de carga sem spec;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, dono na 26/32;
  - a conferência de tela para 3 times e o dump de estado;
  - a remoção do `--show`;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`).

---

- **Executado em:** 2026-08-11 — **sétima passagem, ainda parcial.**

- **Resumo do que foi feito:**

  **O port ficou dirigível, e a primeira conferência de tela aconteceu.**

  O que destravou não foi window manager nenhum: `lista_equipos` nasce
  `Enabled = False` no DFM, e o `FormShow` do port passou a habilitar os três
  combos de time depois de carregar a imagem. Com isso, `xdotool windowfocus`
  seguido de clique e `Down` troca de time — a dropdown não abre de nenhum dos
  dois lados (**no oráculo também não**), e não precisa: `Down` sobre o combo
  focado muda a seleção e dispara o handler, que é como os roteiros 07/08/11
  sempre funcionaram.

  **Time 2 (Gales), ROM japonesa, os dois lados:**

  | Campo | Oráculo | Port | |
  |---|---|---|---|
  | as cinco barras, em px | `64, 53, 75, 75, 75` | `64, 53, 75, 75, 75` | **idêntico** |
  | Nome2 | `WALES` | `WALES` | idêntico |
  | Nome3 | `WAL` | `WAL` | idêntico |
  | Nome1 | `?????` | bytes crus | o filtro, já registrado |

  As larguras batem nas cinco. É a prova que faltava: o port calcula a barra a
  partir de `Team.bar_*` e o original a partir dos cinco bytes que ele lê da
  imagem, e os dois desenham o mesmo pixel. O `?????` do oráculo é o filtro de
  nome medido na quarta passagem aparecendo na tela — byte acima de `z` vira
  `?`.

  **E a comparação achou um erro que nenhum teste pegaria:** a ordem dos campos
  de nome **não** é `names[0..2]`. O port mostrava `WALES` em Nome1 e lixo em
  Nome2; o certo é `names[1]` no primeiro campo e `names[0]` no segundo.
  Compilava, não quebrava nada, e estava trocado.

- **O que não vale, e por quê:**

  Dois times a mais foram tentados e **descartados**: os dois lados receberam
  número diferente de `Down` — o port chegou a `78 Ajax` e depois a
  `95 Master L. ` enquanto o oráculo estava noutro índice. Medida de tela só
  vale com o índice conferido nos dois lados, e o roteiro ainda não faz isso.
  Reportar aquilo como divergência do port teria sido pior que não medir.

  Fica um resultado de graça: o port em `95 Master L. ` mostrou as cinco barras
  com 9 px, que é o que a spec descreve para o ramo não-nacional.

- **O que continua sem resposta:**

  **Como o original habilita controle.** `TControl::SetEnabled` tem zero
  `call rel32` na `.text`, e não há uma única escrita direta em `FEnabled`
  (offset `0x58` do `TControl`, lido do `vcl60.bpl` pelo mesmo caminho do
  `sonda_dorsal.py`). O port habilita por **observação de tela** — o oráculo
  aceita o combo depois da carga, e sem isso não há como dirigir. Está anotado
  no `.inc` e na spec, e mantém a seção Saída como `nao medido`.

- **Arquivos criados/modificados:**
  - `wte/src/impl/ep2002_mainform.FormShow.inc` — habilita os três combos
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — a ordem dos nomes
  - `wte/re/spec/MainForm.lista_equiposChange.md` — a conferência de tela
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 89,7% → **89,5%**
  - regerados: os 18 `.pas`, `fase-2.md`

- **Problemas encontrados:**
  1. Comparar tela sem confirmar o índice nos dois lados produz divergência
     falsa. Dois dos três times mediram lixo por isso.
  2. O `wineserver -k` não derrubou o `we-team-editor.exe`; foi preciso
     `kill -9` no processo. Terceira vez na sessão que um processo de medição
     sobra no `:99`.

- **O que falta para esta task fechar** *(revisado)***:**
  - conferência de tela para mais 2 times, com o índice confirmado dos dois
    lados — é o roteiro que precisa de ajuste, não o port;
  - `lista_equipos_2Change` em Pascal (auxiliares já escritos);
  - os 6 handlers de carga sem spec;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, dono na 26/32;
  - o dump de estado contra o `we2002_core` depois de carga;
  - a remoção do `--show`;
  - como o original habilita controle, e as duas faixas de arranque sem causa.

---

- **Executado em:** 2026-08-11 — **oitava passagem, ainda parcial.**

- **Resumo do que foi feito:**

  O aparato de conferência de tela, e com ele o critério dos 3 times fechado.

  `compara_tela.sh` leva os dois lados ao mesmo índice e `compara_tela.py`
  mede. A divisão é deliberada: **as cinco barras são medidas em pixel e
  reprovam se divergirem**; os campos de texto saem numa montagem lado a lado,
  para olho humano, porque os dois lados usam fontes diferentes e comparar
  texto por pixel seria exigir o que nem deveria bater — o próprio enunciado
  desta task pede comparação humana ali.

  A barra é o alvo certo da parte medida: a largura é `11*v + 9` com `v` vindo
  do dado, então é **número do jogo virado pixel**. Time errado, vetor errado
  ou campo errado mudam a largura.

  **O índice deixou de ser suposto.** Foi o que invalidou duas das três
  medições da sétima passagem. Agora cada time é uma execução nova dos dois
  lados, o `Down` vai um a um, e do lado do port o número de disparos do
  `lista_equiposChange` sai do `trace.log` e **tem de bater** com o pedido —
  senão o script reprova antes de comparar.

  **Times 2, 9 e 63 (clube de ML): as 15 larguras batem em pixel.** Nas duas
  famílias, seleção e Master League.

- **Os dois erros que a conferência achou:**

  1. **A ordem dos campos de nome não era `names[0..2]`** — o certo é
     `names[1]` no primeiro campo e `names[0]` no segundo.
  2. **`Nome3` é `abbreviations[0]`, não `names[2]`.** Este só apareceu no
     clube de ML: para Gales os dois caminhos dão `WAL` e o erro passa
     despercebido; para o Manchester `names[2]` é `ARAGON`, que o campo corta
     em `ARA`, contra `AGN` na tela do original. **Testar uma família só de
     time não teria pego** — é o argumento para o terceiro time ser de outra
     família, e não o terceiro índice qualquer.

  Os dois compilavam e não quebravam teste nenhum.

- **Arquivos criados/modificados:**
  - `wte/tools/compara_tela.py` + `test_compara_tela.py` — a medição e 10
    testes com imagem sintética (458 no total)
  - `wte/tools/compara_tela.sh` — o roteiro dos dois lados, com a guarda de
    **processo** vivo que o `golden_check.sh` não tem
  - `wte/src/impl/ep2002_mainform.aux.inc` — `AbreviaturaDoTime`
  - `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — os três campos
  - `wte/re/spec/MainForm.lista_equiposChange.md`
  - `docs/PLAN-WTE-LAZARUS.md` §4.4 — 89,5% → **89,3%**

- **Problemas encontrados:**
  1. O ícone laranja do botão `Sobre...` cai na faixa X das barras e entrou
     como sexta banda na primeira medição, desalinhando os cinco valores. A
     largura mínima de 9 px — que é a barra vazia, `11*0 + 9` — separa os dois.
  2. O time 63 mede 104 px, que dariam `v = 8,64`, e barra do jogo é inteira.
     **Os dois lados medem o mesmo 104**, então não é defeito do port; o
     comparador passou a devolver `?` em vez de imprimir `8,63636` como "valor
     do jogo".

- **O que falta para esta task fechar** *(revisado)***:**
  - `lista_equipos_2Change` em Pascal — os auxiliares já existem, e agora há
    como conferir na tela;
  - os 6 handlers de carga sem spec, com os `mostrar_*` escopados em navegação;
  - a remoção do `--show`, depois deles;
  - o dump de estado contra o `we2002_core` depois de carga por tela;
  - `ficha_color.FormCreate` e `estrategia.FormCreate`, dono na 26/32;
  - como o original habilita controle, e as duas faixas de arranque sem causa.

