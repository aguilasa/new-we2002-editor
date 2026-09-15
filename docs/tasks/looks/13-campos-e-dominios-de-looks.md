---
id: LOOKS-TASK-13
title: "`looks.py` — os doze campos, seus domínios e os rótulos"
type: implementação
category: núcleo
phase: 4
depends_on: ["LOOKS-TASK-09"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.9"
status: concluído
---

# LOOKS-TASK-13: Os campos e seus domínios

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.9.
- **Esta é a task barata do ciclo**, e é de propósito: o lado dos bits já tem
  **quatro implementações concordando** — `src/core/Player.cpp`,
  `src/app/Commands.cpp` (`kHair[32]`, `kSkin[4]`, `kLetters[8]`),
  `tools/mcr/domains.py` e o fonte `en_we2000edit` do Superpack.
- Não é engenharia reversa. É transcrição conferida.

---

- **Dois dos doze campos não entram no render, e isso está medido.** Em
  2026-09-15 a [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md)
  rodou `python tools/looks/oracle.py --fields NAT AGE HEIG` nos dois slots:
  **`NAT` e `AGE` não tocam um único byte** de `EDT_MOD.BIN`, de `MODEL.BIN` ou
  de qualquer TMD — o `AGE` move quatro bytes em toda a RAM. `HEIG` também não
  toca a geometria carregada, mas mexe na lista de display, ou seja **é escala
  na hora de desenhar**. Os três continuam sendo campos do registro e desta
  task; o que mudou é que se sabe quais têm efeito visual.
- **E os rótulos da tela, na ordem em que ela os mostra**, já estão no
  `oracle.ROWS`: `DEFAUL, NAT, SKIN, HAIR, H.COL, FACE, H.F.COL., HEIG, BODY,
  AGE, BOOTS, FOOT`. São **posições de linha**, postas ali para saber quantas
  vezes apertar `Down`; o domínio e o significado de cada um continuam sendo o
  assunto desta task, contra o `src/core/Player.cpp`.

---

- **Dois domínios ganharam testemunha independente**, em 2026-09-15
  ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)): a tabela
  do tutorial do `zeta` enumera **8 tipos de cor de cabelo** (A a H) × **4
  raças** (*blanca, amarilla, canela, negra*), e os endereços que ela dá são os
  que a LOOKS-TASK-10 mediu no disco. Isso é uma **quinta** implementação
  concordando com `kSkin[4]` e `kLetters[8]` — e, ao contrário das outras
  quatro, esta não é código: é endereço de paleta.
- **`FACE` mexe em duas primitivas, não numa.** As primitivas 8 e 13 da seção 24
  do `MODEL.BIN`, passo `+0x10` no `v`, nos dois save states. É o par irmão do
  `HAIR` (primitivas 1 e 14, passo `+0x20`), e os quatro amostram a **mesma**
  imagem do `DAT2D.BIN`, a do offset 3.568.

---

- **Três domínios já estão medidos na tela, e um deles discorda do
  `Player.cpp`.** Andados de ponta a ponta em 2026-09-15 pela
  [`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md), por
  `python tools/looks/oracle.py --palettes`, lendo o CLUT id na RAM depois de
  cada tecla:

  | campo | valores na tela | bits no `src/core/Player.cpp` |
  |---|---:|---:|
  | `SKIN` | **4** | 2 (`skin_colour`) |
  | `H.COL` | **8** | 3 (`hair_colour`) |
  | `H.F.COL.` | **7** | 3 (`beard_colour`) — oito |

  A terceira linha era o trabalho, e **está respondida**: não há discordância,
  há um valor sem nome. O domínio de `facialhaircolor` é **A..G, sete**, nas
  quatro implementações da §1.9 e no `tools/mcr/domains.py`; os três bits
  guardam oito e o oitavo **ninguém nomeou**. O disco concorda sem ser
  perguntado: nos 1.449 registros a cor de barba chega a **3** e a barba a
  **6**. Índice sem rótulo é lacuna de nomenclatura de terceiro, não defeito —
  e por isso o `looks.label()` devolve `?` em vez de recusar. O que continua
  sem medição é o que o jogo **desenha** com um 7 gravado à força, e isso exige
  escrever no registro do jogador, que este ciclo não faz (§0).
- **Campo desta tela trava nas pontas; não dá a volta.** O quarto `Right` no
  `SKIN` deixa o valor onde o terceiro o pôs. Domínio se mede andando até a
  ponta de baixo e depois até a de cima — contar ciclo aqui acusa falha que não
  houve.
- **`FACE` é a barba, não o rosto.** `FACE` e `H.F.COL.` movem **as mesmas duas
  primitivas** da seção 24 (8 e 13), que amostram a folha de cabelo do offset
  3.568 — e o `Player.cpp` tem `beard_style` e `beard_colour` lado a lado, nos
  bits que sobram ao lado de `hair_style` e `hair_colour`. O rótulo da tela e o
  nome do campo não são a mesma coisa, e aqui é o nome que está certo.

---

## Objetivo

`tools/looks/looks.py`: a tupla de aparência, com domínio e rótulo de cada
campo, e a conversão de e para os 12 bytes.

---

## Critério de conclusão

- [x] Os doze campos da tela representados — e **dez deles guardam alguma
      coisa**: 4 peles, **32 cabelos** (`A1`…`P1`), 8 cores de cabelo, 7 barbas,
      7 cores de barba, 8 corpos, 8 chuteiras, altura a partir de 148, idade a
      partir de 15, e o pé. `DEFAUL` e `NAT` **não são campo**: são as duas
      metades do default por nacionalidade do `data/defaultlook.txt`, e estão no
      `looks.UNSTORED` com a razão escrita.
- [x] Decodificação dos 12 bytes **conferida campo a campo** contra
      `src/core/Player.cpp`, e **mecanicamente**: o `self_check()` lê as
      expressões do `Player::Decode()` daquele arquivo, troca `raw_attributes[`
      por `raw[` e roda as duas implementações sobre 64 blobs. O caso vermelho
      do próprio cross-check está junto: uma expressão entortada de propósito
      tem de ser pega.
- [x] A tupla de texto do corpus (`A-I3-A-F-A`) é lida e escrita. Conferida
      contra os nomes dos 50 JPGs: **49 parseiam e formatam de volta para o
      próprio nome**, e o `0.jpg` recusa com a mensagem certa. E contra as 95
      linhas do `data/defaultlook.txt`, que têm as **mesmas cinco colunas** —
      fixture versionada, então essa parte do gate roda em qualquer clone.
- [x] Os registros no disco são conferidos, e a opinião de terceiro se partiu
      ao meio: o offset **157.164 está certo** — o `OFS_PLAYER_ATTR` deste
      repositório cai no mesmo byte do mesmo arquivo — e a contagem **estava 207
      curta**. São **1.449 × 12 B**, não 1.242, medido pelo `Database::Load` e
      pelo próprio disco.
- [x] `self_check()` com caso vermelho, e dois controles plantados no `controls.py`.

---

## Log de Execução

**Executado em:** 2026-09-15

### Resumo

A task barata do ciclo era transcrição conferida, e a conferência achou duas
coisas: **duas das doze linhas da tela não são campo**, e **a contagem de
registros que o plano trazia estava 207 curta**. O resto bateu.

O `tools/looks/looks.py` entrega os dez campos guardados, com os bits escritos
do jeito que o `src/core/Player.cpp` os escreve, a tupla do corpus nos dois
sentidos, e os registros do `/SELECT.BIN`.

### O cross-check é mecânico, não uma releitura

O `self_check()` abre o `src/core/Player.cpp`, recorta o corpo do
`Player::Decode()`, troca `raw_attributes[` por `raw[` — C e Python escrevem
`>>`, `<<`, `&`, `+` e hexadecimal igual — e **roda as duas implementações lado
a lado** sobre 64 blobs pseudoaleatórios de semente fixa. Nenhum campo diverge.
O caso vermelho do próprio cross-check vai junto: uma expressão entortada de
propósito (`>>1` virando `>>2` no `hair_colour`) tem de ser pega, e é.

Mais duas asserções que valem o que custam: **nenhum par de campos divide um
bit** (varrido, todos contra todos), e **todo valor de todo campo sobrevive ao
`encode`/`decode`** — o domínio inteiro, não uma amostra.

### Dez campos, não doze

`DEFAUL` e `NAT` não guardam nada. São as duas metades do **default look por
nacionalidade**, e a tabela dele já está versionada neste repositório:
`data/defaultlook.txt`, **95 nações**, cujas colunas de aparência são
`SKINCOL;HAIRSTYLE;HAIRCOL;FACEHAIRSTYLE;FACEHAIRCOL` — **exatamente as cinco
da tupla do corpus, na mesma ordem**. Isso fecha um círculo que ninguém tinha
fechado: o `A-I3-A-F-A` dos 50 JPGs e as linhas do `defaultlook.txt` são o
mesmo formato, e a LOOKS-TASK-09 já tinha medido pelo outro lado que `NAT` não
move um byte da geometria.

Como a tabela é versionada, ela virou **fixture do gate**: as 95 linhas são
parseadas no `self_check()`, sem disco e sem Superpack.

### A contagem de registros estava errada, e o offset não

O plano trazia *"`/SELECT.BIN` offset 157.164, 1.242 jogadores × 12 bytes"*, do
`Offsets We2002.txt` do Superpack, marcado como opinião de terceiro. As duas
metades se medem, e só uma sobreviveu:

```text
python tools/pes2/ofs_map.py roms/japanese-shift-jis.bin --markdown
| `OFS_PLAYER_ATTR`   | 2179492 | 157164 |
| `OFS_PLAYER_ATTR_1` | 2180328 | 157696 |
```

O `OFS_PLAYER_ATTR` do `src/core/include/we2002/Offsets.hpp` — offset que os
golden conferem contra o `ed.exe` — resolve para **157.164 do `/SELECT.BIN`**.
Offset confirmado, por uma testemunha que nunca encostou no Superpack.

A contagem, não. O `Database::Load` percorre
`for(i=PLAYERS_NC;i<PLAYERS_TOTAL;i++)`, que é `1911 - 462 = 1449`. E o disco
diz o mesmo sem ser perguntado:

```text
python tools/looks/looks.py --check-image
/SELECT.BIN: 300648 B, 1449 record(s) of 12 from 157164
    the run of plausible heights stops after 1449 record(s); the file has room for 11957
```

Os 1.449 primeiros decodificam para altura entre **155 e 202**; o de índice
1.449 é o primeiro todo zerado. **1.449 × 12 = 17.388 B**, de 157.164 a
174.552.

### O que os 1.449 registros usam

```text
        skin_colour    4 of  4 value(s) used, 0..3
        hair_style    28 of 32 value(s) used, 0..31
        hair_colour    7 of  8 value(s) used, 0..7
        beard_style    6 of  8 value(s) used, 0..6
        beard_colour   4 of  8 value(s) used, 0..3
        height        38 of 64 value(s) used, 155..202
        build          7 of  8 value(s) used, 0..7
        age           22 of 32 value(s) used, 18..40
        boots          8 of  8 value(s) used, 0..7
        foot           3 of  4 value(s) used, 0..2
```

Isso responde a pendência que a LOOKS-TASK-12 encaminhou para cá. **Não há
discordância entre o `Player.cpp` e a tela**: `beard_colour` guarda três bits e
o domínio tem **sete nomes**, nas quatro implementações e no
`tools/mcr/domains.py`. A tela oferecer sete é o esperado; o oitavo índice
existe e ninguém o nomeou. O disco nunca o usa — nem ele nem o oitavo da barba
nem o quarto do pé.

### A tupla, contra o corpus de terceiro

```text
50 .jpg   parsed: 49   refused: 1
    0.jpg -- '0' has 1 part(s) and a tuple has 5
    skin_colour    4 of  4 value(s) covered
    hair_style     9 of 32 value(s) covered
    hair_colour    4 of  8 value(s) covered
    beard_style    6 of  8 value(s) covered
    beard_colour   2 of  8 value(s) covered
```

As 49 formatam de volta para o próprio nome. O `0.jpg` **recusa alto**, que é
o comportamento que a LOOKS-TASK-18 pede no Contexto dela — e a cobertura já
fica medida lá: nove dos trinta e dois cabelos.

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 13 file(s), 8106 line(s)
  controls: 0 failure(s)      ..... 26 of 26 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/looks.py --check            ->  looks.py: 0 failure(s)
python tools/looks/looks.py --check-image      ->  looks --check-image: ok
python tools/looks/skin.py --check             ->  skin.py: 0 failure(s)
python tools/looks/skin.py --check-image       ->  skin --check-image: ok
python tools/looks/texture.py --check          ->  texture.py: 0 failure(s)
python tools/looks/texture.py --check-image    ->  texture --check-image: ok
python tools/looks/atlas.py --check            ->  atlas.py: 0 failure(s)
python tools/looks/atlas.py --check-image      ->  atlas --check-image: ok
python tools/looks/pieces.py --check           ->  pieces.py: 0 failure(s)
python tools/looks/pieces.py --check-image     ->  pieces --check-image: ok
python tools/looks/modelfile.py --check-image  ->  ok
python tools/looks/oracle.py --check           ->  oracle.py: 0 failure(s)
python tools/looks/section.py --check          ->  section: self_check ok
python tools/check_tasks.py                    ->  123 task(s), ok
```

Os dois controles novos são os dois jeitos de perder este resultado sem
sintoma: `looks-cross-check-blind` faz o cross-check incapaz de discordar — e
aí qualquer máscara passa —, e `looks-record-count` repõe o 1.242 do terceiro,
que corta 207 jogadores fora de toda contagem seguinte.

Nenhuma leitura de emulador nesta task. O disco japonês foi lido pela guarda do
`iso_source`; o Superpack foi **lido onde está** — só os nomes dos 50 arquivos
— e nada dele entrou no git. `roms/` só foi lida.

### Arquivos criados/modificados

- `tools/looks/looks.py` — **novo**. `Piece` e `Field` com os bits escritos
  como o `Player.cpp` os escreve, `decode()`, `encode()`, `label()`,
  `parse_tuple()`, `format_tuple()`, `default_looks()`, `records()`,
  `out_of_table()`, `cpp_decoder()`, `disagreements()`, `core_player_count()`,
  o `self_check()` com o caso vermelho do próprio cross-check, e `--check`,
  `--check-image` e `--report`
- `tools/looks/layout.py` — `PLAYER_RECORD_COUNT` de 1.242 para **1.449**, com
  as duas medições e o `OFS_PLAYER_ATTR` escritos ao lado
- `tools/looks/controls.py` — `looks-cross-check-blind` e `looks-record-count`
- `tools/looks/selftest.py` — `looks` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §1.9 com o offset medido, a contagem corrigida, os
  três campos com menos rótulo do que bits, e as duas linhas que não são campo;
  §3.2 com o que o `looks.py` entrega
- `docs/prompts/perfil-looks.md` — duas armadilhas novas (número de terceiro vem
  em par; rótulo de tela não é nome de campo), o gate novo na tabela, e o
  cross-check mecânico nas verificações da Fase 4
- `docs/tasks/looks/14-tabela-de-montagem.md`, `15-visualizador-opengl.md`,
  `18-corpus-dos-cinquenta-renders.md` — os encaminhamentos, escritos nos
  arquivos de destino
- `docs/tasks/looks/progresso.md` — a linha e o checklist

### Problemas encontrados

Um, e é o achado: **1.242 estava errado**. O número vinha em par com um offset
certo, o que é o jeito mais fácil de herdar uma contagem errada — confere-se a
metade barata e leva-se a outra junto. As duas metades se mediam de graça, uma
pelo `ofs_map.py` e a outra pela altura que deixa de ser plausível.
