---
id: CORR-LOOKS-048
title: "Correção: ninguém leu o que as barbas `F` e `G` escrevem, e 28 jogadores do disco e 16 renders do corpus são recusados"
type: correção
category: engenharia-reversa
status: done
depends_on: [CORR-LOOKS-046]
origin: LOOKS-TASK-17
severity: medium
done_on: 2026-09-16
done_commit: cf7e0c6
---

# CORR-LOOKS-048: a tela da barba oferece sete, e a tabela sabe cinco

## Problema identificado

A [`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md) separou os dois
números: a **tela** do `FACE` oferece **7** valores, andada letra a letra nos
dois slots, e a **tabela** sabe aplicar **5** — as faixas 0 a 4 dos dois quads
de barba da seção 24. `F` e `G` são recusados como "não medido", o que é
verdade e é honesto. Ela deixou aberta a segunda metade: **o que `F` e `G`
escrevem**.

O custo, medido no disco: **28** dos 1.449 jogadores têm barba `F` (25) ou `G`
(3) — **1,9%**. No corpus de terceiro, **16** dos 50 renders caem nessa
recusa, e são a maior parte das 19 que o `scene.py --corpus` conta; a
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) só
consegue confrontar 31 das 50 enquanto isso estiver aberto.

O que já se sabe descarta a leitura óbvia: **não é uma faixa 5 e 6** da mesma
folha. A [`CORR-LOOKS-038`](/docs/tasks/looks/CORR-LOOKS-038.md) mediu as
faixas de barba — a 0 é o rosto sem barba e as 1 a 4 amostram as entradas que
a cor de barba move —, e a folha não tem faixa de barba além da 4. Pode ser
outra seção, como o `HAIR` era, ou outro par de primitivas.

## Evidência

```text
$ python - (looks.records sobre /SELECT.BIN)
records: 1449
FACE F or G (refused, not measured): 28 (1.9%)
  by value: {'A': 1326, 'C': 55, 'B': 34, 'F': 25, 'E': 6, 'G': 3}

$ python tools/looks/scene.py --corpus <os 50 JPGs>
      31 drawn, 19 refused
      13 x FACE=F is value 5: the screen offers it
       3 x FACE=G is value 6: the screen offers it

$ python tools/looks/confront.py --reach FACE
  FACE on slot 2: … the screen reaches 7 of the 8 value(s) the field holds
  FACE on slot 1: … the screen reaches 7 of the 8 value(s) the field holds
```

A mesma limitação de linha de comando da
[`CORR-LOOKS-047`](/docs/tasks/looks/CORR-LOOKS-047.md): o `--patched` não
recebe o slot.

## Causa raiz

A LOOKS-TASK-14 observou o `FACE` numa janela só — o `v` dos dois quads de
barba da seção 24 — e o que ela não viu mudar ali ficou sem leitura.

## Correção

### Medição

`python tools/looks/oracle.py --patched FACE <SLOT>` nos **dois** slots: andar
os sete valores lendo o arquivo carregado inteiro depois de cada tecla. O que
`F` e `G` mudarem — outra seção, outras primitivas, outra folha — sai da
corrida, não de dedução. Se a corrida disser que `F` e `G` **não mudam nada**
no arquivo, isso também é resposta, e a recusa passa a dizer isso.

### Arquivo: `tools/looks/assembly.py`

O `Effect` do `FACE` ganha o que a medição disser para `F` e `G`, e o `known`
sobe para o que ela alcançar. Se for outra seção, o `FACE` deixa de ser só
`BAND` e passa a escolher como o `HAIR` escolhe; se forem outras primitivas, o
`where` cresce.

### Arquivo: `tools/looks/scene.py`

A varredura de faixas da CORR-LOOKS-038 anda o `known`; se `F` e `G` não forem
faixa, ela tem de continuar andando só as faixas, e dizer isso.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | o slot no `--patched`, se a CORR-LOOKS-047 ainda não o fez |
| `tools/looks/assembly.py` | modificar |
| `tools/looks/scene.py` | modificar, conforme o desfecho |
| `tools/looks/controls.py` | um controle que devolva `F`/`G` à recusa |
| `docs/PLAN-LOOKS-PY.md` | a tabela da §6(c) e o item 3 da definição de pronto |
| `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` | o número de recusas remedido |

## Verificação

- [x] `oracle.py --patched FACE` rodado nos dois slots, a saída no Log
- [x] `F` e `G` desenham com o que escrevem medido — ou a recusa diz, medido,
      que não escrevem nada no arquivo
- [x] `scene.py --corpus` remedido, e o número novo escrito onde o 31/19 está
- [x] os 28 do disco remedidos pelo mesmo critério
- [x] controle negativo vermelho
- [x] `python tools/looks/selftest.py --quiet` verde
- [x] `roms/` intocada, e os dois save states não sobrescritos

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

**`F` e `G` escrevem outra seção, e ela é o gêmeo da cabeça.** Medido nas treze
cabeças que o `HAIR` nomeia e nas duas figuras: `A` a `E` movem os quads de
barba da cabeça que o `HAIR` escolheu, faixa a faixa; `F` e `G` não tocam nela
e escrevem a **seção ímpar logo depois** — `F` põe as linhas do store nos quads
de cabelo dela e deixa a barba na faixa do disco, que é a **5**; `G` move essa
barba uma faixa. O jogo edita a seção que vai mostrar, como faz com o `HAIR`:
para `F` e `G` a figura veste o gêmeo. O `head_pairs` já tinha medido que o que
separa um par é a barba; esta é a leitura.

**Primeira corrida — os dois slots a partir do state (`A1`):**

```text
$ python tools/looks/oracle.py --patched FACE 2        # e o mesmo no slot 1
  FACE on slot 2: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       0  changed: section 24 (4 byte(s), band(s) [0]), section 32 (16 byte(s), band(s) [0, 1, 3, 4])
       1  changed: section 24 (8 byte(s), band(s) [1, 2])
       2  changed: section 24 (8 byte(s), band(s) [2, 3])
       3  changed: section 24 (8 byte(s), band(s) [3, 4])
       4  changed: section 24 (8 byte(s), band(s) [4, 5])
       5  changed: section 25 (6 byte(s), band(s) [0])
       6  changed: section 25 (8 byte(s), band(s) [6, 7])
       7  changed: nothing
       8  changed: nothing
```

O slot 1 deu as mesmas nove linhas. Isso diz **onde** na família `A`, e não nas
outras doze, então o `--patched` ganhou tuplas de partida e passou a imprimir as
primitivas mudadas.

**Segunda corrida — uma tupla por cabeça, só os passos `F` (5) e `G` (6):**

```text
$ python tools/looks/oracle.py --patched FACE 2 A-A1-A-A-A A-B2-A-A-A \
      A-C2-A-A-A A-D2-A-A-A A-E2-A-A-A A-F2-A-A-A A-G1-A-A-A A-I1-A-A-A \
      A-J1-A-A-A A-K1-A-A-A A-L1-A-A-A A-O1-A-A-A A-P1-A-A-A     # 6 min 39 s
  FACE on slot 2 from A-A1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 25 (6 byte(s), band(s) [0])
       6  changed: section 25 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-B2-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 27 (10 byte(s), band(s) [2, 5, 6])
       6  changed: section 27 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-C2-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 31 (10 byte(s), band(s) [2, 5, 6])
       6  changed: section 31 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-D2-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 49 (10 byte(s), band(s) [2, 5, 6])
       6  changed: section 49 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-E2-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 55 (4 byte(s), band(s) [5, 6])
       6  changed: section 55 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-F2-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 53 (10 byte(s), band(s) [1, 5, 6])
       6  changed: section 53 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-G1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 29 (2 byte(s), band(s) [5, 6])
       6  changed: section 29 (8 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-I1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 35 (6 byte(s), band(s) [0])
       6  changed: section 35 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-J1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 37 (1 byte(s), band(s) [5, 6])
       6  changed: section 37 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-K1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 33 (4 byte(s), band(s) [5, 6])
       6  changed: section 33 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-L1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 47 (16 byte(s), band(s) [5, 6])
       6  changed: section 47 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-O1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 45 (4 byte(s), band(s) [5, 6])
       6  changed: section 45 (12 byte(s), band(s) [6, 7])
  FACE on slot 2 from A-P1-A-A-A: 9 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       5  changed: section 51 (4 byte(s), band(s) [5, 6])
       6  changed: section 51 (12 byte(s), band(s) [6, 7])
```

As primitivas que `G` move, uma faixa (16 linhas) além do disco:

```text
A-A1-A-A-A  section 25 primitive 8: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (155, 108)]
A-A1-A-A-A  section 25 primitive 13: clut 0x7809, (u, v) [(174, 96), (172, 108), (164, 96), (164, 112)]
A-B2-A-A-A  section 27 primitive 4: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (155, 108)]
A-B2-A-A-A  section 27 primitive 7: clut 0x7809, (u, v) [(172, 108), (164, 112), (174, 96), (164, 96)]
A-C2-A-A-A  section 31 primitive 0: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (154, 108)]
A-C2-A-A-A  section 31 primitive 3: clut 0x7809, (u, v) [(173, 108), (164, 112), (175, 96), (164, 96)]
A-D2-A-A-A  section 49 primitive 0: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (154, 108)]
A-D2-A-A-A  section 49 primitive 3: clut 0x7809, (u, v) [(173, 108), (164, 112), (175, 96), (164, 96)]
A-E2-A-A-A  section 55 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-E2-A-A-A  section 55 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-E2-A-A-A  section 55 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-F2-A-A-A  section 53 primitive 0: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (154, 108)]
A-F2-A-A-A  section 53 primitive 3: clut 0x7809, (u, v) [(173, 108), (164, 112), (175, 96), (164, 96)]
A-G1-A-A-A  section 29 primitive 9: clut 0x7809, (u, v) [(164, 96), (164, 112), (152, 96), (153, 108)]
A-G1-A-A-A  section 29 primitive 17: clut 0x7809, (u, v) [(174, 96), (174, 108), (164, 96), (164, 112)]
A-I1-A-A-A  section 35 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-I1-A-A-A  section 35 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-I1-A-A-A  section 35 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-J1-A-A-A  section 37 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-J1-A-A-A  section 37 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-J1-A-A-A  section 37 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-K1-A-A-A  section 33 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-K1-A-A-A  section 33 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-K1-A-A-A  section 33 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-L1-A-A-A  section 47 primitive 6: clut 0x7809, (u, v) [(171, 108), (166, 112), (174, 96), (167, 96)]
A-L1-A-A-A  section 47 primitive 7: clut 0x7809, (u, v) [(160, 96), (161, 112), (153, 96), (156, 108)]
A-L1-A-A-A  section 47 primitive 8: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-O1-A-A-A  section 45 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-O1-A-A-A  section 45 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-O1-A-A-A  section 45 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
A-P1-A-A-A  section 51 primitive 7: clut 0x7809, (u, v) [(172, 108), (166, 112), (174, 96), (167, 96)]
A-P1-A-A-A  section 51 primitive 10: clut 0x7809, (u, v) [(160, 96), (161, 112), (152, 96), (155, 108)]
A-P1-A-A-A  section 51 primitive 11: clut 0x7809, (u, v) [(167, 96), (166, 112), (160, 96), (161, 112)]
```

**E o slot 1, as mesmas treze tuplas** (6 min 36 s): comparado linha a linha com
o slot 2 — seções, bytes, faixas e cada primitiva com os quatro cantos —,
**idêntico**:

```text
$ diff <(strip slot-1) <(strip slot-2) && echo "SLOT 1 == SLOT 2 (changed + primitives)"
SLOT 1 == SLOT 2 (changed + primitives)
```

O `media` dos dois states foi conferido de dentro do arquivo (`--check-states`,
na mesma sessão da CORR-LOOKS-047): `C:\games\ps1\work\we2002-english.cue` nos
dois.

### O código

- `layout.py` — `FACE_TWIN_QUADS`, os quads de barba dos treze gêmeos, com a
  origem; e a nota de que os gêmeos das quatro cabeças de `HAIR_QUADS` levam os
  mesmos índices de cabelo (25: 1, 14; 27: 1, 3; 35: 0, 1, 12; 47: 0, 9, 17 —
  lidos no passo `F`).
- `assembly.py` — `FACE_TWIN_FROM = 5`, `FACE_TWINS` por figura (as duas
  medidas), `wears_twin`, `twin_of` e `worn_head` (seção desenhada, seção
  escolhida, faixas). O `edits` endereça `F`/`G` aos quads do gêmeo com faixa
  `passo − 5`; `draw_list` e `sections_of` desenham o gêmeo; o `known` do `FACE`
  subiu para 7, e a recusa "não medido" virou `check_step`, exercitada por um
  `Effect` sintético. O `--check-image` confere que os quads de barba dos treze
  gêmeos estão na faixa 5 do disco e que `F`/`G` vestem o gêmeo nas duas
  figuras.
- `scene.py` — a varredura de faixas da CORR-LOOKS-038 anda só `A` a `E` nos
  dois quads da 24, **e diz isso**; `F` e `G` são varridos nos quads do gêmeo.
- `oracle.py` — `--patched <LINHA> [<SLOT> [<TUPLA> ...]]` e o detalhe por
  primitiva.
- `controls.py` — `assembly-unmeasured-as-unreached` e
  `assembly-table-off-by-one` seguiram para o `check_step`; novo
  `assembly-face-twin-ignored` (desenhar `F`/`G` na cabeça par).
- `ui_check.py` — a tupla de recusa do `looks_ui` era `A-A1-A-F-A`, que agora
  desenha; virou `A-H1-A-A-A`.

### Gates

```text
$ python tools/looks/assembly.py --check-image
  the twins' beard quads sit in band(s): 25 -> [5], 27 -> [5], 29 -> [5], 31 -> [5],
  33 -> [5], 35 -> [5], 37 -> [5], 45 -> [5], 47 -> [5], 49 -> [5], 51 -> [5],
  53 -> [5], 55 -> [5]
  A-A1-A-F-A on figure 0 wears [25]      A-I3-A-G-A on figure 0 wears [35]
  A-A1-A-F-A on figure 1 wears [25]      A-I3-A-G-A on figure 1 wears [35]
assembly --check-image: ok

$ python tools/looks/scene.py --check-image
      FACE F is section 25's own beard quads, 0 band(s) on: they sample 6 of them: [2, 5, 12, 13, 14, 15]
      FACE G is section 25's own beard quads, 1 band(s) on: they sample 5 of them: [2, 12, 13, 14, 15]
scene --check-image: ok

$ python tools/looks/scene.py --corpus          # era 31 drawn, 19 refused
      47 drawn, 3 refused
       2 x hair style H1 wrote nothing to either model file ...
       1 x '0' has 1 part(s) and a tuple has 5 ...

os 28 jogadores do disco com barba F ou G: 26 desenham, 2 recusam pelo H1
  (A-H1-H-G-C, D-H1-B-F-B); nenhum recusa mais pela barba.
  No disco inteiro, figura 0: 45 recusas, todas de H1 (29), M1 (10) e N1 (6).

$ work/venv-looks/Scripts/python tools/looks/ui/app.py --compare A-A1-A-E-A.png A-A1-A-F-A.png
A-A1-A-E-A.png vs A-A1-A-F-A.png: 22133 of 409600 pixel(s) differ (5.40%)
$ ... --compare A-A1-A-F-A.png A-A1-A-G-A.png
A-A1-A-F-A.png vs A-A1-A-G-A.png: 11335 of 409600 pixel(s) differ (2.77%)
  (olhadas: F desenha o bigode, G a barba no queixo; janela em -32000)

$ python tools/looks/assembly.py --corpus        assembly --corpus: ok
$ python tools/looks/looks.py --corpus           looks --corpus: ok
$ python tools/looks/confront.py --render && python tools/looks/confront.py --score
  slot 2: 3 win, 2 ranked, 0 expected, 0 unexplained
  slot 1: 3 win, 2 ranked, 0 expected, 0 unexplained
confront: ok
$ python tools/looks/ui_check.py
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple it was asked for
$ python tools/looks/controls.py --only assembly-face-twin-ignored
  RED    assembly-face-twin-ignored assembly.py :: worn_head
$ python tools/looks/selftest.py --quiet
  ..... 54 of 54 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada (só leitura); os dois save states só carregados.

### Problemas encontrados

- **A primeira corrida do selftest ficou vermelha pela razão certa**: o
  `assembly-table-off-by-one` não casava mais (a linha foi para o
  `check_step`), e o `looks_ui` recusava uma tupla que agora desenha. Os dois
  foram consertados acima.
- **A mesma corrida nomeia os quads de barba das treze cabeças pares** (passos
  1 a 4), que o `FACE` hoje aplica por **índice emprestado** da seção 24
  (`COLOUR BY BORROWED INDEX`). Não entrou aqui: é outra lacuna, a do
  `HEAD_COLOUR_MEASURED`, e o dado está na corrida para quem a fechar.
- Os gêmeos 31, 49 e 53 recebem quads de cabelo no passo `F` (1 e 2) com linhas
  que não são as do store; ficam com a janela do disco, como as cabeças pares
  deles.

### Arquivos criados/modificados

- `tools/looks/layout.py`, `assembly.py`, `scene.py`, `oracle.py`,
  `controls.py`, `ui_check.py`
- `docs/PLAN-LOOKS-PY.md` — o item 3 da definição de pronto e a linha do `FACE`
  na tabela da §6(c), corrigidos no lugar com a data
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — 47 e 3
- `docs/tasks/looks/14-tabela-de-montagem.md` e
  `docs/tasks/looks/17-confronto-com-o-emulador.md` — as notas do alcance da
  barba
- `docs/prompts/perfil-looks.md` — a armadilha 19 (dizia "a tela anda cinco") e
  a linha do `--patched`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
