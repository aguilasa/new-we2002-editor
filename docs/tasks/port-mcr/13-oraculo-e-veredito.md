---
id: MCR-TASK-13
title: "O oráculo do Obocaman: o `0x6500`, o nome cheio e o veredito do console"
type: verificação
category: engenharia-reversa
phase: 3
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.5"
status: concluído
---

# MCR-TASK-13: O oráculo, e as três perguntas

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §5.5 e §1.8.
- **Pode ser antecipada** assim que a MCR-TASK-09 fechar: ela precisa do leitor,
  não da UI. E deve ser, porque o veredito muda a tela da MCR-TASK-12.
- O oráculo é o editor do Obocaman por `make wte` — Wine, prefix `win32`, no
  `:98`. Ele **não é oráculo de tudo**: é de três perguntas, e só.
- **O lado do upstream da discordância mora em `lite/fifatomcr/FrmFormation.vb`,
  e só ali.** Medido na MCR-TASK-02: o `25856` (= `0x6500`) não aparece em
  nenhum arquivo da árvore principal `fifatomcr/`, que é a do `<Copyright>`
  citado no plano. Ao citar o que "o upstream diz" sobre o sexto cobrador,
  a referência é esse arquivo — a árvore principal não opina sobre o byte.

---

## Objetivo

Responder com valor medido o que hoje é opinião.

---

## Critério de conclusão

- [x] **A tela já está esperando o veredito, e sabe onde pô-lo.** A MCR-TASK-12
      deixou o `0x6500` em **leitura**, com o rótulo `_open_byte` do
      `tools/mcr/ui/formation_view.py` dizendo as duas leituras e que o byte é
      lido e nunca gravado. Fechado o veredito, o editor entra ali — um campo
      "capitão" (um índice de slot) ou um sexto cobrador ao lado dos cinco —, e
      **o `formation.write` precisa passar a gravar o byte**: hoje ele o pula
      de propósito, com o comentário dizendo por quê. São dois arquivos, e os
      dois estão nomeados aqui para não se descobrir isso relendo a tela.
- [x] **O `0x6500`**: capitão ou sexto cobrador. Experimento discriminante — pôr
      o capitão num slot conhecido e os cinco cobradores em slots distintos,
      salvar, ler os seis bytes. Na fixture eles valem `[7,7,8,7,7]` e `8`, e
      **o valor sozinho não discrimina**.
- [x] **O nome que enche os 10 bytes**: escrever nome de 10 caracteres com
      espaço no fim, salvar, ler de volta. Confirma (ou derruba) a leitura de
      que o campo não é cadeia terminada em NUL.
- [x] **O veredito do console**, ou a razão escrita de ele não ter sido obtido:
      14 dos 17 destinos caem no bloco 3, que o diretório declara livre, e
      ninguém recalcula checksum. Um cartão gravado pelo port aberto no
      DuckStation responde se isso importa.

      **A MCR-TASK-04 já mediu o lado do contêiner**, e o comando que reproduz
      é `python3 tools/mcr/card.py <cartão> --blocks`: na fixture, os blocos
      1 e 2 são a cadeia declarada (16.384 B), o bloco 3 tem **41 bytes
      não-zero** e o diretório o marca `0xA0`, e **os 16 checksums de quadro
      batem** — o cartão está formalmente íntegro *exceto* por esse dado fora
      da cadeia. É esse o estado exato que o console tem de julgar; leve um
      cartão nessa condição ao experimento, não um recém-gravado sem conferir.
- [x] O que for medido volta para a §1.8 e a §5.6 do plano; hipótese descartada
      fica, com o motivo.

---

## Armadilhas

- **Feche qualquer editor aberto no `:98` antes.** Os roteiros acham o diálogo
  pelo tamanho, e janela esquecida é dirigida no lugar da certa.
- **Cópia, sempre** — inclusive do cartão. O `work/entrada.mcr` é fixture.

---

## Log de Execução

**Executado em:** 2026-09-08

### O veredito: `0x6500` é o **capitão**, e a discordância era nossa

Quatro medições independentes, e nenhuma delas precisa do console:

1. **O formulário do oráculo.** O `estrategia.dfm` põe seis marcadores
   (`tirador1..6`) numa grade só, e os seis rótulos acima deles são `SF`, `LF`,
   `RC`, `LC`, `PK` e `CP` — o sexto com `Hint = 'Captain'`.
2. **O experimento dirigido**, que é o critério desta task. Com as seis colunas
   da `malla2` em seis linhas distintas, o `.mcr` exportado sai com
   `0x614F=0, 0x6140=1, 0x6122=2, 0x6113=3, 0x6131=4` e **`0x6500=5`**. O
   `cmp -l` contra o cartão do controle acusa **exatamente** esses seis bytes
   da família (mais oito de Y, ver abaixo) e nada mais.
3. **O fonte do upstream.** Em `lite/fifatomcr/FrmFormation.vb` o valor gravado
   em `25856` sai de um local chamado **`CP`**, ao lado de `SF`, `LF`, `RC`,
   `LC` e `PK` nos cinco endereços de cobrador — as mesmas seis siglas do
   oráculo, que é outro autor e outra linguagem.
4. **O readme do Obocaman**, que o `wte/re/mcr.md` já citava: a v0.98 consertou
   *"the problem with the **captain and kickers** when loading from .mcr
   files"*. O autor separa os dois.

**"Sexto cobrador" foi leitura nossa, tirada da posição** — sexto de um grupo
de seis — e não de rótulo nenhum. O `wte/re/mcr.md` já hesitava, chamando o
campo de "cobrador 5 (o capitão)".

### Dois achados que o experimento entregou de brinde

- **Qual cobrador é qual.** A tabela de endereços dizia "cobrador 0..4" e mais
  nada. Na ordem de `layout.KICKER_ADDRESSES` eles são **SF, LF, RC, LC, PK**.
- **O domínio é o onze inicial, não o elenco.** A `malla2` mede 144×176 com
  passo 24×16 — seis colunas por **onze** linhas —, então o que um cobrador e o
  capitão guardam é `0..10`. A MCR-TASK-12 oferecia `0..22` na tela, **errado
  por um fator de dois**. Corrigido aqui, com o número saindo da geometria
  medida em `wte/re/zonas.md` e não de chute.

### O nome que enche os dez bytes

`ABCDEFGHI` mais um espaço, digitado no `casilla_nombre` (`MaxLength = 10`) e
exportado: o slot 0 volta como `41 42 43 44 45 46 47 48 49 20` — **dez bytes
não-zero, décimo byte `0x20`, sem terminador**. Confirma a §1.6 e a leitura de
que o campo não é cadeia terminada em NUL, que os slots 5 e 20 da fixture já
sugeriam. O espaço vai por `! tecla space` e não no fim do `! texto`: espaço no
fim de linha de roteiro não sobrevive à leitura, e é justamente o décimo byte
que se mede.

### O veredito do console: **não obtido**, e a razão é medida

A fixture é um save chamado `BISLPM-86600WEW-OPT`. As três imagens de `roms/`
declaram `cdrom:SLPM_870.56` e escrevem `BISLPM-87056WEW-OPT` — mesmo sufixo
`WEW-OPT`, que é por que todos os offsets batem, e **código de produto
diferente**. Um jogo de PSX acha o save dele pelo nome, então este cartão é
invisível para os discos desta máquina. Renomear a entrada do diretório é
exatamente a escrita abaixo de `0x800` que o port recusa (armadilha 3).

O caminho que resta está escrito na §5.6 do plano e é alcançável: subir
`roms/golden-european-deluxe.cue` ou `roms/ptbr-remaster.cue` no DuckStation —
as duas são `SLPM-87056` e as duas têm `.cue`, ao contrário da
`japanese-shift-jis.bin` — com um cartão **vazio**, deixar o jogo criar o
próprio `BISLPM-87056WEW-OPT`, editar esse cartão com o port e botar de novo.
A §5.6 já dizia que **a definição de pronto da v1 não depende disso**.

### O que o port passou a fazer

- `formation.py` **grava** o `captain` (era `open_slot_byte`, lido e nunca
  gravado), com o controle `formation-captain-not-written` exigindo o vermelho
  — 20 de 20.
- `layout.py` chama o destino de `CAPTAIN`, não mais `CAPTAIN_OR_SIXTH_KICKER`.
- A tela ganhou o campo `CP` ao lado dos cinco, os cinco ganharam os rótulos
  medidos (`SF LF RC LC PK`) e os seis passaram a `0..10`. O `--write-probe`
  edita o capitão e o `ui_check.py` exige o valor de volta do disco.

  **O `0..10` das seis caixas virou orientação, não recorte, na
  [CORR-MCR-020](/docs/tasks/port-mcr/CORR-MCR-020.md).** Como o domínio vem da
  grade do editor de terceiro e não do formato, um cartão de outra release pode
  cair fora dele legitimamente — e um `QSpinBox` limitado a 10 mostrava **10**
  para um cartão que guarda 15, calado, enquanto o núcleo preservava o byte e o
  round-trip continuava em zero. As caixas passaram a aceitar o byte inteiro e
  a marcar com sufixo visível o valor que a grade não oferece.

### Um achado sobre o oráculo, que vale a quem o usar

**Abrir e aceitar a tela de tática no editor do Obocaman derruba em 1 o Y de
oito dos dez jogadores de linha** — `32→31`, `52→51`, `72→71`, `50→49`, `30→29`,
`62→61`, `42→41`, `62→61` —, e deixa os dois extremos (`17` e `87`) parados.
Medido no `cmp -l` entre o cartão do controle e o das seis linhas, numa corrida
em que **nada** foi clicado na `malla1`. O port não faz isso: o round-trip dele
dá 0 bytes nas duas formas. Quem usar aquele editor como oráculo de formação
tem de contar com essa deriva.

### Arquivos criados/modificados

- `tools/mcr/oracle/13-controle.txt`, `13-seis-linhas.txt`, `13-nome-de-dez.txt`
  — os três roteiros, versionados: o controle, o experimento discriminante e o
  nome de dez bytes
- `tools/mcr/layout.py` — `CAPTAIN`, e o comentário com as quatro medições
- `tools/mcr/formation.py` — `captain` no lugar de `open_slot_byte`, gravado, e
  os checks dos dois sentidos
- `tools/mcr/model.py`, `tools/mcr/mcrio.py`, `tools/mcr/cli.py` — o campo novo
- `tools/mcr/ui/formation_view.py` — o campo `CP`, os cinco rótulos medidos e o
  domínio `0..10`
- `tools/mcr/ui/app.py`, `tools/mcr/ui_check.py` — o probe edita o capitão e o
  gate exige o valor de volta. A
  [CORR-MCR-020](/docs/tasks/port-mcr/CORR-MCR-020.md) acrescentou aos dois o
  `--report-formation` e o passo que abre um cartão fora do domínio, com as
  **duas** quebras que o reddenam — o `ui_check.py` passou a plantar quatro,
  não dois
- `tools/mcr/controls.py` — `formation-captain-not-written`
- `wte/tools/dump_mcr.py` + `wte/re/mcr.md` + `wte/re/mcr.tsv` — **o gerador**,
  não o gerado: o campo passou a se chamar `capitao`, e a frase que afirmava
  ser `SLPM-86600` "o mesmo da ROM que o gate usa" foi trocada pelo que se mede
- `docs/PLAN-MCR-PY.md` (§1.8 reescrita, §5.6 e a nota de antecipação),
  `docs/prompts/perfil-mcr.md`, `docs/tasks/port-mcr/progresso.md`

### Gates medidos

| gate | resultado |
|---|---|
| `golden_run_wte.sh` × 3 | **0 violações de acesso** nas três corridas |
| controle × experimento | o `cmp -l` acusa só a família de seis (mais a deriva de Y do oráculo) |
| `WE2002_MCR_CARD=… ctest -R mcr` | **3 de 3 passed** |
| `make test` | **10 de 10** |
| `controls.py` | **20 de 20 vermelhos** (19 substituições, 1 arquivo novo) |
| `selftest.py` | 0 falhas em 12 módulos + regras + controles |
| `layout.py --check` / `--rule1` | 17/17 · 0 endereços fora |
| `glossary.py` | 0 queixas |
| `dump_mcr.py --check` | 2 arquivos em dia; o `we2002_mcr.pas` bate com o layout |
| `check_tasks` | 100 ok |
| fixture | `e53f4895…c47546` intacta; `roms/` só lida |

### Problemas encontrados

- **A imagem de trabalho atravessa as corridas.** O ` Accept` da tela de tática
  grava na imagem de CD, então o cartão do `13-nome-de-dez` já nasceu com os
  seis valores do experimento anterior. Não invalida nada — pelo contrário,
  mostra que os valores sobreviveram a fechar e reabrir o editor e voltaram por
  uma leitura nova da imagem —, mas quem ler o `cmp -l` do nome tem de saber
  disso.
- **A europeia não serve ao oráculo**, e o script avisa: com ela o `wte.exe`
  morre ao trocar de time (49.749 violações contra 0). As três corridas usaram
  `work/wte-japanese-shift-jis.bin`.
