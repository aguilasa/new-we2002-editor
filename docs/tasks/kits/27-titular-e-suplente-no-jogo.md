---
id: KITS-TASK-27
---

# KITS-TASK-27 — §4.1 no emulador: suplente em campo e a VRAM lida

## Goal

A §4.1 respondida pelo jogo: com um time de pares diferentes jogando de suplente, os retângulos enviados à VRAM são o 2º par do TEX (ou não são), lido pelo `oracle.py --kit` do `looks` ou por opção versionada.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Comando versionado sobe o fork, chega à partida e compara retângulo por retângulo; saída colada
- [x] Controle: o mesmo comando com o time de titular mostra o 1º par
- [x] A §4.1 do plano tem veredito; se o par não for o 2º, uma CORR é aberta contra a fase 5

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.1). É a fase que não pode ser pulada (§7). Começa de save state, não da rota manual.

## Log de Execução

### 2026-10-04 — comparador pronto, partida ausente

**O comparador** é `tools/kits/oracle.py`. Diferente do `oracle.py --kit` do `looks`, ele **não** compara nos retângulos que o TEX declara: numa partida há dois times, e os dois não cabem em (576, 256). Ele despeja a VRAM inteira (1024×512, `dump_vram`), procura cada um dos 11 registros dos 105 TEX em **qualquer** posição, halfword a halfword nos 15 bits que o dump guarda, e diz o conjunto pelo índice do registro achado (0, 1, 2, 3 = conjunto 1; 4, 5, 6, 7 = conjunto 2). Controle embutido: dois dumps a um quadro de distância têm de dar os mesmos achados; registro com menos de 4 valores distintos é marcado como "não nomeia nada". `--png` faz a busca sobre um dump sem emulador.

Rodado sobre o slot 2 (a `LOOKS SET` do `looks`), onde a resposta é conhecida:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
  WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue \
  python3 tools/kits/oracle.py --slot 2 --out work/kits-oracle/looks-2
  control: two dumps a frame apart give the same 6 match(es)
  TEX_A4  record  1 sleeves            set 1  at (576,384)
  TEX_A4  record  2 player palette     set 1  at (0,486), (0,488)
  TEX_A4  record  3 goalkeeper palette set 1  at (0,486), (0,488)
  TEX_A4  record  5 sleeves            set 2  at (576,384)
  TEX_A4  record  6 player palette     set 2  at (0,486), (0,488)
  TEX_A4  record  7 goalkeeper palette set 2  at (0,486), (0,488)
  TEX_A4 wears set 1 and 2
```

Bate com o `looks` (`TEX_A4`, três retângulos enviados). E mostra por que a §4.1 não se responde com esta tela: no `TEX_A4` os dois conjuntos são os mesmos bytes, então todo registro de um aparece também como do outro.

**O que falta é a partida.** Não há save state de partida em lugar nenhum desta máquina: os de WE2002 (`~/.local/share/duckstation/savestates/SLPM-87056_*`, `work/looks-states/`) são as duas `LOOKS SET`, a tela de título e a de cartão de memória (`savestate.py shot` nos dois `.bak`). A task manda começar de save state, não da rota manual. A task fica bloqueada até existir um state de partida, num slot livre (o 3, por exemplo), com:

- um time de conjuntos diferentes (qualquer um das 103 tags do §1.1 cujas imagens diferem; qual time é qual tag não importa, a busca acha a tag) **jogando de suplente** — é o critério 2;
- e, como controle, um time de titular: o mandante da mesma partida serve.

Então, da raiz do repositório:

```
python3 tools/kits/oracle.py --slot 3
```
- **blocked** (2026-10-04): no save state of a match exists (only LOOKS SET, title and memory-card screens: savestate.py shot); the comparator is in 43ba7df. Unblock: save a match state with a team of differing pairs playing in its second kit (home team in its first as control) into a free slot, e.g. 3, then: python3 tools/kits/oracle.py --slot 3

### 2026-10-04 — a partida

O usuário gravou o state no slot 3: **Escócia (1º uniforme) × Dinamarca (2º uniforme)**, com a bola rolando, sobre `work/we2002-english.cue` (o campo `media` do state). Cópia mestra guardada antes de qualquer corrida:

```
$ cp -p ~/.local/share/duckstation/savestates/SLPM-87056_3.sav work/kits-states/
$ sha256sum work/kits-states/SLPM-87056_3.sav
5f392a12f85cc8946228b4a20d3e8289435bb631ce35b14a730d3ceec8592152  work/kits-states/SLPM-87056_3.sav
```

**A primeira corrida mudou a ferramenta.** A busca exata achou paletas e bandeiras dos dois times e **nenhuma página** de uniforme ou de manga: na partida a página não sobe inteira. Linha a linha, as 80 linhas não planas (mais de um valor de 15 bits) do uniforme do conjunto 2 do `TEX_13` estão todas na VRAM, em (640,256), e só 12 de 80 do conjunto 1 do `TEX_01`, em (576,256) — contagem do `oracle.py --lines`, no bloco abaixo do veredito. O `oracle.py` ganhou então a comparação das páginas pela mais próxima (`closest_sets`, numa grade de colunas de 64 halfwords a partir de x 512), e o veredito sai dele:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
  python3 tools/kits/oracle.py --slot 3 --cue $PWD/work/we2002-english.cue --out work/kits-oracle/match-3
  control: two dumps a frame apart give the same 8 match(es)
  TEX_01  record  2 player palette     set 1  at (0,486), (0,490)
  TEX_01  record  7 goalkeeper palette set 2  at (0,488), (0,492)
  TEX_01  record  8 flag               set -  at (704,256)
  TEX_01  record  9 flag palette       set -  at (256,494)
  TEX_13  record  6 player palette     set 2  at (0,487), (0,491)
  TEX_13  record  7 goalkeeper palette set 2  at (0,489), (0,493)
  TEX_13  record  8 flag               set -  at (704,320)
  TEX_13  record  9 flag palette       set -  at (256,495)
  TEX_01: exact records of set 1 and 2
  TEX_13: exact records of set 2
  TEX_01 uniform  at (576,256): set 1 differs in 4746 of 8192 halfwords, set 2 in 5050 -- set 1 nearer
  TEX_01 sleeves  at (576,384): set 1 differs in 2995 of 8192 halfwords, set 2 in 4211 -- set 1 nearer
  TEX_13 uniform  at (640,256): set 1 differs in 7198 of 8192 halfwords, set 2 in 2640 -- set 2 nearer
  TEX_13 sleeves  at (640,384): set 1 differs in 7693 of 8192 halfwords, set 2 in 4093 -- set 2 nearer
```

As linhas exatas por conjunto, e qual tag é qual time pela bandeira (o registro 8 pintado com o 9, cores mais comuns fora do preto) — as duas leituras saem do `oracle.py` desde a CORR-KITS-048:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --lines --flags | sed -n '/lines not flat/,$p'
  TEX_01 uniform  set 1 at (576,256):  80 of 128 lines not flat,  12 of them exact
  TEX_01 uniform  set 2 at (576,256):  80 of 128 lines not flat,   0 of them exact
  TEX_01 sleeves  set 1 at (576,384): 128 of 128 lines not flat,   0 of them exact
  TEX_01 sleeves  set 2 at (576,384): 128 of 128 lines not flat,   0 of them exact
  TEX_13 uniform  set 1 at (640,256):  80 of 128 lines not flat,   0 of them exact
  TEX_13 uniform  set 2 at (640,256):  80 of 128 lines not flat,  80 of them exact
  TEX_13 sleeves  set 1 at (640,384): 128 of 128 lines not flat,   0 of them exact
  TEX_13 sleeves  set 2 at (640,384): 128 of 128 lines not flat,   0 of them exact
  TEX_01 flag, black left out: (24, 90, 132) 20 %, (222, 222, 222) 18 %, (33, 90, 132) 8 %
  TEX_01 uniform 1==2 False, sleeves 1==2 False, player palette 1==2 False, goalkeeper palette 1==2 False
  TEX_13 flag, black left out: (140, 33, 41) 46 %, (156, 41, 41) 7 %, (165, 41, 49) 6 %
  TEX_13 uniform 1==2 False, sleeves 1==2 False, player palette 1==2 False, goalkeeper palette 1==2 False
```

`TEX_01` azul e branco, **Escócia**; `TEX_13` vermelho, **Dinamarca**. Nos dois kits os conjuntos diferem nas paletas de jogador e de goleiro e nas imagens, então nenhum achado acima vale para os dois conjuntos ao mesmo tempo.

**Critério 1:** o comando acima. **Critério 2 (controle):** a Escócia, de titular, mostra o 1º par — paleta de jogador exata do conjunto 1, páginas mais próximas do conjunto 1. **Critério 3:** o par do suplente é o 2º, como a fase 5 assumiu; sem CORR. Veredito escrito na §4.1 do plano.

**O achado que a pergunta não previa:** o goleiro da Escócia está na paleta de goleiro do conjunto **2**, com o time no 1. O "`TEX_01: exact records of set 1 and 2`" é isso, e não ambiguidade. O jogo escolhe o uniforme do goleiro à parte; por quê não foi verificado. Registrado na §4.1; o `kit_set` da fase 5 não reproduz essa combinação, e quem decidir se a aba 3D deve oferecê-la é outra task.

As duas tags medidas foram anotadas nas Notas da KITS-TASK-30 (§4.2).
- **pending** (2026-10-04): the match state exists: slot 3, Scotland (1st) x Denmark (2nd), copy in work/kits-states/
- **Closed** — commit `e331474` (2026-10-04): feat(kits): section 4.1 answered in the game -- first team is set 1, second is set 2
  - Files (`git show --name-status e331474`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/28-confronto-3.md`
    - `M docs/tasks/kits/30-tabela-time-tag.md`
    - `M tools/kits/oracle.py`
- **Reviewed** (2026-10-04) at `b615e7d`: CORR-KITS-047, CORR-KITS-048, CORR-KITS-049, CORR-KITS-050
