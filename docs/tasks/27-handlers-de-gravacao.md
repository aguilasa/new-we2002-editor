---
id: WTE-TASK-27
title: "Handlers de gravação — escrever na imagem de CD"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-26"]
status: pendente
---

# WTE-TASK-27: Handlers de gravação

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4 e §6.
- **O grupo mais arriscado do projeto.** É onde o app toca 474 MB de imagem
  in-place, e é o único grupo que o golden test mede diretamente e sem
  ambiguidade.

Vêm por último de propósito: dependem de carga e edição estarem certas.

---

## Objetivo

Implementar as seis gravações, cada uma com golden verde antes de passar para a
seguinte.

### Alvos

| Handler | Endereço | O que grava |
|---|---|---|
| `boton_nombres2isoClick` | `0x0040d534` | nomes na imagem |
| `boton_barras2isoClick` | `0x0040cab8` | barras/atributos |
| `boton_tex2isoClick` | `0x0040de18` | textura |
| `boton_mcr2isoClick` | `0x0040c46c` | dados vindos de `.mcr` — **ver WTE-TASK-31** |
| `grabar_camisetaClick` | `0x0040ee80` | camisa — **ver WTE-TASK-32** |
| `grabar_memoryClick` | `0x0040f69c` | escreve `.mcr` (saída, não a imagem) |

Dois deles são **compartilhados com a Fase 5**: `boton_mcr2isoClick` depende do
parser de `.mcr` e `grabar_camisetaClick` do render 2D. Aqui se implementa a
**gravação** — onde e como os bytes vão para a imagem; a *origem* dos bytes é
das tasks 31 e 32. Se a ordem incomodar, inverta: nada impede fazer a 31/32
antes, desde que o golden desta task rode depois.

### Regras que não podem ser violadas

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; preservar é o
  comportamento correto.
- **Fronteira de setor.** Os offsets pulam cabeçalho de setor manualmente
  (2352 = 24 + 2048 + 280). Se um round-trip falhar, é a primeira suspeita.
- **Cópia, sempre.** Cada rodada de golden usa duas cópias de ~474 MB.

### O diff de controle vem antes

Como na WTE-TASK-19: gravar **sem editar nada** nos dois lados e registrar o que
muda de graça. O `Save` reconstrói as all-star a partir dos links, e o
`Load`+`Save` do original não é idempotente (troca os dois primeiros cobradores
de cada clube de ML). Sem esse controle, toda medição vem contaminada.

### Critério

**Byte-idêntico** entre `wte.exe` e o app Lazarus, nas duas ROMs, para cada
operação. Divergência que sobreviver à análise vira **divergência deliberada**
com registro (WTE-TASK-35) — nunca "aceita e esquecida".

### A metade da WTE-TASK-26 que esta task herdou

*(decisão do usuário, 2026-08-12)*

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) edita **em memória** e não
grava; o critério dela dizia "editar pela tela nos dois lados, então gravar nos
dois, e o golden compara". O segundo verbo é desta task — as barras editadas lá
só chegam à imagem pelo `boton_barras2isoClick`, os nomes pelo
`boton_nombres2isoClick` —, e a 27 `depends_on` a 26. Circularidade da mesma
forma que a [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desfez para o gate.

**A 26 passou a fechar por conferência de tela e esta task herdou o byte.** Na
prática: cada uma das seis gravações roda o golden **duas** vezes —

1. **gravar sem editar** (o diff de controle da seção acima);
2. **editar pela tela, com um handler do grupo da 26, e então gravar.**

A segunda é a que julga a edição e a gravação juntas. Sem ela, a edição fica
verificada só por pixel, e pixel igual dos dois lados não prova que os dois
escreveram o **mesmo byte do modelo** — os dois poderiam desenhar a mesma
largura a partir de campos diferentes. É a lição da terceira ponta da
[WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md).

Par mínimo por gravação, quando existir handler de edição correspondente:

| gravação | edição que a exercita (WTE-TASK-26) |
|---|---|
| `boton_barras2isoClick` | `sel_barraClick` + `track_barraChange` |
| `boton_nombres2isoClick` | `edit_nombre1/2/3KeyPress`, `iguala_nombresClick` |
| `grabar_memoryClick` | os de número (`dorsalClick`, `scroll_dorsalChange`) |

`boton_tex2isoClick`, `boton_mcr2isoClick` e `grabar_camisetaClick` não têm par
na 26 — a origem dos bytes deles é das tasks 31 e 32, como já diz a seção de
alvos.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (6) |
| `wte/src/ep2002_*.pas` | modificar |
| `wte/tools/roteiros/gravacao-*.sh` | criar (6) |

---

## Critério de conclusão

- [x] Diff de controle medido e registrado antes de qualquer edição
      — 2026-08-18, em [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
      gerado. Gravar sem editar **muda** 22 bytes: katakana virando ASCII
- [ ] As seis com spec e com golden verde nas duas ROMs
- [ ] **Cada gravação que tem par na WTE-TASK-26 rodada também com uma edição
      de tela antes** — herdado da 26 em 2026-08-12; ver a seção acima. É o
      único critério do projeto que julga edição e gravação juntas
- [ ] EDC/ECC preservados — provado, não presumido
- [ ] Nenhuma divergência sem veredito escrito
- [x] `roms/` intocada em todas as rodadas — vale por passagem, e a de
      2026-08-18 rodou toda sobre cópia em `work/`
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-18 — **primeira passagem, parcial.** A tarefa
  continua `⬜ Pendente`: nenhuma das seis gravações foi implementada. O que
  fechou foi a primeira linha do critério, o **diff de controle** — e ele
  mudou o desenho de todo roteiro de gravação que vier depois.

- **Resumo do que foi feito:**

  Três coisas, e a segunda vale mais que as outras duas juntas.

  **O diff de controle está medido e registrado.** Carregar um time e mandar
  gravar sem tocar em campo nenhum **não** é neutro nesta imagem: a ROM
  japonesa guarda o nome do time em latino no primeiro bloco e em katakana de
  meia largura nos demais, e o editor lê o campo da tela — que veio do bloco
  latino — e o grava em **todos**. Vinte e dois bytes mudam de graça, em três
  trechos, e são katakana virando ASCII. Reproduzir isso é obrigação: um port
  que "preservasse" o katakana divergiria do oráculo em toda gravação de nomes,
  e o golden acusaria a gravação por um defeito que seria de fidelidade.

  A medição é a sessão `27-gravacao-controle` do `diff_dirigido.sh`, e o
  registro é gerado — [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md),
  do novo [`gravacao_controle.py`](../../wte/tools/gravacao_controle.py), que
  **não mede nada sozinho**: cruza as duas réguas já versionadas. Os offsets
  desta medição são a seção `Bytes tocados` das seis specs que vêm, e
  copiá-los à mão de dois TSV seria a forma conhecida de o número envelhecer
  calado.

  **O clique não grava — quem grava é o `fseek` seguinte.** O `wte.exe` escreve
  pela saída bufferizada do runtime C. A primeira medição desta passagem disse
  que o `boton_barras2iso` **não tocava a imagem**, e o TSV de uma sessão
  anterior (`09-areas-com-time`) dizia o mesmo desde 2026-08-10. Estava errado
  nos dois: ele grava 5 bytes, que ficam no buffer até algo depois procurar
  noutro ponto do mesmo arquivo.

  Medido com um par de sondas de **uma** variável de diferença, agora
  versionadas — [`27-descarga-sem.txt`](../../wte/tests/roteiros/27-descarga-sem.txt)
  e [`27-descarga-com.txt`](../../wte/tests/roteiros/27-descarga-com.txt),
  iguais linha a linha, e o `-com` troca de time depois do clique: **zero**
  escrita no `-sem`, os 5 bytes em 2328184 no `-com`. O
  `test_gravacao_controle.py` compara os dois corpos e exige que o resultado
  medido continue oposto, como o `test_analisar_crash.py` faz com o par 07/08.

  Duas consequências, e as duas são armadilha de gate:

  1. **roteiro que termina numa gravação mede um oráculo truncado** — o harness
     encerra com `wineserver -k` e o buffer se perde. Se o port gravar direto,
     o golden acusaria o *port* por bytes que o oráculo nunca escreveu;
  2. **marca de corte antes da descarga credita a faixa à ação seguinte.** Na
     primeira corrida os 5 bytes das barras apareceram como se fossem dos
     nomes — atribuição errada, em silêncio, num TSV que parecia medido.

  Por isso cada bloco do `golden-02-gravacao.txt` termina com uma troca de time
  e só então a marca. Refeita a corrida, a atribuição fecha: barras 5 bytes,
  nomes 8 faixas.

  **A primeira régua não tinha porta automática, e ninguém tinha notado.** A
  [CORR-WTE-047](/docs/tasks/CORR-WTE-047.md) deu ao `cmp` um `--fundir-cmp`
  porque o `cmp.tsv` morria em `/tmp`; o **trace** tinha a mesma doença e
  chegava ao `io-medido.tsv` a mão, o que é indistinguível de não chegar quando
  alguém esquece. As 75 faixas desta sessão não entrariam sozinhas. Entrou
  `--fundir-io`, simétrico, chamado pelo `diff_dirigido.sh`.

- **O que a passagem NÃO fez, e é o resto da task:**
  - as seis gravações continuam sem spec e sem Pascal. O
    `boton_nombres2isoClick` foi lido até o ponto de se saber que ele valida os
    três campos de nome antes de gravar (vazio em 1 e 2, menos de 3 letras em
    3) e que endereça oito faixas; isso ainda **não** é spec;
  - o par edição+gravação (o critério herdado da WTE-TASK-26) não rodou: sem
    gravação implementada não há o que comparar;
  - EDC/ECC preservados continua **presumido**, não provado.

- **A ROM europeia não hospeda este grupo, e agora está medido aqui.** O mesmo
  roteiro sobre `roms/golden-european-deluxe.bin` morre na troca de time —
  49.749 violações de acesso, o número que a
  [CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) já tinha medido — e a caixa de
  confirmação da gravação nunca aparece. O critério "nas duas ROMs" da task
  herda esse limite; ele não é omissão desta passagem.

- **Arquivos criados/modificados:**
  - `wte/tests/roteiros/golden-02-gravacao.txt` — o roteiro do controle
  - `wte/tests/roteiros/27-descarga-{sem,com}.txt` — o par de sondas
  - `wte/tools/gravacao_controle.py`, `wte/tools/test_gravacao_controle.py`
  - `wte/re/gravacao-controle.md` — gerado
  - `wte/tools/analisar_io.py` (`--fundir-io`), `wte/tools/test_analisar_io.py`
  - `wte/tools/diff_dirigido.sh` — funde as duas réguas
  - `wte/re/io-medido.tsv`, `wte/re/cmp-medido.tsv`, `wte/re/offsets-novos.md`
  - `wte/tools/README.md`, `wte/tests/roteiros/README.md`
  - `docs/tasks/progresso.md`, e esta task

- **Gates medidos:** `golden_check.sh --modo controle` **PASSOU: byte-idêntico**
  e `--modo positivo` **detectou** o byte plantado em 405228, os dois sobre o
  roteiro final; `make -C wte check` rc 0, com **590 testes** OK; `lazbuild`
  rc 0. As duas réguas do `diff_dirigido.sh` fecham nas três sessões novas
  (12/12, 9/9, 9/9). `roms/` intocada — todas as corridas sobre cópia em
  `work/`.

- **Problemas encontrados:** o descrito acima — a leitura de que o
  `boton_barras2iso` "não grava" era artefato de buffer, e sobreviveu por oito
  dias num TSV versionado porque nada exercia a descarga. Foi preciso desmontar
  a atribuição do próprio instrumento antes de confiar em qualquer número desta
  task.
