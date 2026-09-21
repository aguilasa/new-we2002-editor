---
id: CORR-LOOKS-047
title: "Correção: o mapa de cabelo do goleiro não foi medido, e 136 dos 179 goleiros do disco são recusados"
type: correção
category: engenharia-reversa
status: done
depends_on: [CORR-LOOKS-046]
origin: LOOKS-TASK-17
severity: medium
done_on: 2026-09-16
done_commit: e1561f6
---

# CORR-LOOKS-047: a figura 1 só desenha o `A1`

## Problema identificado

A [`CORR-LOOKS-043`](/docs/tasks/looks/CORR-LOOKS-043.md) fechou o **defeito**:
o goleiro desenhava qualquer estilo de cabelo como `A1`, em silêncio, e agora
**recusa** todo estilo que não seja o da cabeça do disco. Ela mesma escolheu a
saída 1 e deixou a 2 aberta: o `HAIR_MAP` foi medido **só no jogador de
linha**, e o segundo bloco de cabeças do `MODEL.BIN` (74..105), que é do
goleiro, nunca foi andado.

O custo, medido no disco: **179** registros têm posição 0, que o editor chama de
`GK` (`src/app/PlayerSkillsDialog.cpp:21`), e **136** deles têm estilo de cabelo
diferente de `A1`. Três em cada quatro goleiros do jogo saem com saída 2 no
visualizador. A recusa é honesta; a lacuna é grande.

E o que se sabe do segundo bloco torna a medição necessária, não opcional: a
[`CORR-LOOKS-029`](/docs/tasks/looks/CORR-LOOKS-029.md) mediu **24** malhas
distintas nele contra **12** no primeiro, e só **16** das 32 seções amostram a
folha de cabelo. Não é o primeiro bloco repetido, e copiar o mapa do jogador de
linha deslocado de 50 seções é exatamente a suposição plausível que o ciclo
recusa.

## Evidência

```text
$ python - (looks.records sobre /SELECT.BIN)
records: 1449
position values: {0: 179, 1: 271, 2: 176, 3: 174, 4: 145, 5: 187, 6: 289, 7: 28}
position 0 records: 179  not A1: 136

$ <venv>/python tools/looks/ui/app.py --figure 1 --looks A-I3-A-A-A --screenshot …
app: A-I3-A-A-A refuses -- hair style I3 on figure 1: HAIR_MAP was measured on
the outfield player only, and the goalkeeper's heads (MODEL.BIN 74..105) were
never walked …
exit=2
```

E a ferramenta existe mas não alcança o slot pela linha de comando:
`oracle.check_patched(row="HAIR", slot=2)` recebe o slot, e o `main` só repassa
a linha (`--patched <LINHA>`).

## Causa raiz

A LOOKS-TASK-14 mediu o mapa no slot 2 e fechou; o slot 1 ficou como limite de
medição, e a CORR-LOOKS-043 o transformou em recusa sem medi-lo.

## Correção

### Arquivo: `tools/looks/oracle.py`

`--patched <LINHA> [<SLOT>]`, repassando o slot ao `check_patched`. É uma
linha, e é o que torna a corrida repetível por comando e não por script.

### Medição

`python tools/looks/oracle.py --patched HAIR 1`: andar os 32 valores no
goleiro, a partir do `load_state` do slot 1, lendo o arquivo carregado inteiro
depois de cada tecla — a mesma corrida que achou o `HAIR_MAP` no slot 2. E, para
as cabeças que ela nomear, a irmã do `--writes`, que diz **quais quads** recebem
a faixa: sem ela a cabeça certa é desenhada com a janela do disco, que é o que o
`draw_list` já faz para as nove cabeças não medidas do jogador de linha.

### Arquivo: `tools/looks/assembly.py`

Um mapa por figura (`HAIR_MAP` do slot 2, e o do slot 1 ao lado), com o
`head_of` escolhendo pelo número da figura, e o `goalkeeper_head` reduzido ao
que a medição **não** alcançar — estilos que não escreverem nada no slot 1
continuam recusados, com a mesma mensagem que o slot 2 dá ao `H1`. Os números
novos (`HAIR_MAP_SECTIONS`, `HAIR_MAP_SILENT`) ganham par para a figura 1, com
asserção.

### Arquivo: `tools/looks/confront.py`

Re-julgar o slot 1 pelo re-render da CORR-LOOKS-046: `A-I3-A-A-A` e
`A-H1-A-A-A` passam a desenhar, ou continuam recusando com a razão nova.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | modificar — o slot no `--patched` |
| `tools/looks/assembly.py` | modificar — o mapa da figura 1 |
| `tools/looks/controls.py` | um controle que devolva a figura 1 ao mapa do slot 2 |
| `docs/PLAN-LOOKS-PY.md` | §6(c): o mapa do goleiro, e o resíduo que sobrar |
| `docs/tasks/looks/17-confronto-com-o-emulador.md` | o resíduo do goleiro fechado |

## Verificação

- [x] `oracle.py --patched HAIR 1` roda e a saída vai para o Log, com o
      `media` do state conferido
- [x] a figura 1 desenha cada estilo que a medição nomeou, e recusa os que não
      escreveram nada
- [x] o número de goleiros do disco recusados é **remedido** e escrito onde o
      136 está
- [x] `confront.py --score` sobre o nosso lado re-renderizado: o slot 1 sem
      `unexplained`
- [x] controle negativo vermelho
- [x] `python tools/looks/selftest.py --quiet` verde
- [x] `roms/` intocada, e os dois save states não sobrescritos

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

**A medição respondeu o contrário do que a CORR temia, e é resposta.** Andado
no goleiro, o `HAIR` **não** escreve no segundo bloco de cabeças (74..105):
escreve **as mesmas seções do primeiro bloco, com as mesmas faixas**, valor a
valor, que o `HAIR_MAP` mediu no slot 2. `H1`, `M1` e `N1` também não escrevem
nada no goleiro. E o `--writes` acha **os mesmos quads** nas mesmas quatro
cabeças. Não houve mapa novo a deduzir; houve uma segunda medição que concorda
com a primeira.

O `media` dos dois states conferido de dentro do arquivo antes da corrida:

```text
$ python tools/looks/oracle.py --check-states
  slot 1 (goalkeeper)  1690941 B  sha256 7e335fae60870de4
      media C:\games\ps1\work\we2002-english.cue
  slot 2 (outfield player)  1691623 B  sha256 f5fc6015574c554d
      media C:\games\ps1\work\we2002-english.cue
```

`oracle.py --patched HAIR 1`, só a coluna "changed" de cada passo (a outra
coluna acumula as seções já diferentes do disco):

```text
$ python tools/looks/oracle.py --patched HAIR 1        # 1 min
  window moved off the visible desktop
  slot 1 restored: the goalkeeper, on LOOKS SET
  HAIR on slot 1: 33 value(s); what CHANGED at each press, and what the live /BIN/MODEL.BIN no longer matches on the disc
       0  changed: section 24 (4 byte(s), band(s) [0]), section 32 (16 byte(s), band(s) [0, 1, 3, 4])
       1  changed: section 24 (8 byte(s), band(s) [2])
       2  changed: section 24 (8 byte(s), band(s) [1])
       3  changed: section 26 (8 byte(s), band(s) [0, 1])
       4  changed: section 26 (8 byte(s), band(s) [2])
       5  changed: section 26 (8 byte(s), band(s) [1])
       6  changed: section 26 (8 byte(s), band(s) [5])
       7  changed: section 26 (8 byte(s), band(s) [3])
       8  changed: section 26 (8 byte(s), band(s) [4])
       9  changed: section 30 (8 byte(s), band(s) [0, 1])
      10  changed: section 30 (8 byte(s), band(s) [2])
      11  changed: section 48 (8 byte(s), band(s) [0, 1])
      12  changed: section 48 (8 byte(s), band(s) [2])
      13  changed: section 48 (8 byte(s), band(s) [0])
      14  changed: section 54 (4 byte(s), band(s) [0, 1])
      15  changed: section 52 (8 byte(s), band(s) [0, 1, 3])
      16  changed: section 52 (8 byte(s), band(s) [1])
      17  changed: section 52 (8 byte(s), band(s) [4])
      18  changed: section 28 (2 byte(s), band(s) [0, 1])
      19  changed: nothing
      20  changed: section 34 (6 byte(s), band(s) [0])
      21  changed: section 34 (12 byte(s), band(s) [2])
      22  changed: section 34 (12 byte(s), band(s) [1])
      23  changed: section 36 (1 byte(s), band(s) [0, 1])
      24  changed: section 32 (14 byte(s), band(s) [0, 1, 3, 4])
      25  changed: section 46 (12 byte(s), band(s) [5])
      26  changed: section 46 (12 byte(s), band(s) [6])
      27  changed: section 46 (12 byte(s), band(s) [7])
      28  changed: nothing
      29  changed: nothing
      30  changed: section 44 (4 byte(s), band(s) [0, 1])
      31  changed: section 50 (4 byte(s), band(s) [0, 1])
      32  changed: nothing
```

O passo 0 é o estilo `A1` depois de 32 `Left`: ele reescreve a 24 na faixa 0
e **também** a 32 — resto do que o state tinha carregado antes, a mesma seção
e as mesmas faixas que o `K1` escreve no passo 24. Os passos 1 a 31 são os
estilos `A2` a `P1`, e cada um bate com a linha do `HAIR_MAP`; o 32 é a
trava da ponta (armadilha 14).

`oracle.py --writes HAIR 1` (3 min):

```text
  HAIR on slot 1: 23 of 31 press(es) registered, and 9 of those wrote a quad
      the sections it wrote: [24, 26, 34, 46]
      section 24: primitive 1, primitive 14
      section 26: primitive 1, primitive 3
      section 34: primitive 0, primitive 1, primitive 12
      section 46: primitive 0, primitive 17, primitive 9
```

Oito das 31 teclas não moveram a célula de valor (armadilha 22), então os
**rótulos** por linha dessa corrida não valem; o que vale é o conjunto de
quads, e ele é exatamente o `layout.HAIR_QUADS` do slot 2.

### O código

- `oracle.py` — `row_and_slot()`: `--patched <LINHA> [<SLOT>]` e
  `--writes <LINHA> [<SLOT>]`, recusando slot que não seja 1 ou 2.
- `assembly.py` — `HAIR_MAP_GOALKEEPER`, escrito linha a linha com o rótulo de
  cada estilo, e `HAIR_MAPS = {0: HAIR_MAP, 1: HAIR_MAP_GOALKEEPER}`;
  `hair_map(figure)` e `head_of(values, figure)`; o `draw_list` e o
  `sections_of` escolhem a cabeça pelo mapa da figura. **`goalkeeper_head` e
  `DISC_STYLE` saíram**: o que a medição não alcançou (`H1`, `M1`, `N1`) é
  recusado pelo `head_of` com a mesma mensagem do slot 2. Os pares
  `HAIR_MAP_GOALKEEPER_SILENT = 3` e `HAIR_MAP_GOALKEEPER_SECTIONS = 13`, com
  asserção, mais a asserção de que as treze seções estão no **primeiro** bloco
  e de que os dois mapas concordam. O `--check-image` confere as três cabeças
  nas duas figuras.
- `controls.py` — `assembly-goalkeeper-draws-any-style` virou
  `assembly-goalkeeper-unmapped`: tira a figura 1 do `HAIR_MAPS`, e o
  `self_check` fica vermelho no `I3` que ela desenha.
- `confront.py` e `layout.py` — só docstring.

### Gates

```text
$ python tools/looks/confront.py --render 1
  slot 1 A-I3-A-A-A: drawn            slot 1 A-H1-A-A-A: refused
$ python tools/looks/confront.py --score
  slot 2: 3 win, 2 ranked, 0 expected, 0 unexplained
  slot 1 A-H1-A-A-A: our side refuses -- ... hair style H1 wrote nothing ...
      A-I3-A-A-A   WIN         by 0.028 over A-A1-A-A-A
  slot 1: 3 win, 2 ranked, 0 expected, 0 unexplained
confront: ok

goleiros do disco (posição 0): 179, recusados por estilo de cabelo: 4
  {'H1': 2, 'M1': 1, 'N1': 1}          # eram 136
  e 6 por qualquer recusa: mais 1 FACE=F e 1 FACE=G, que são da CORR-LOOKS-048

$ python tools/looks/assembly.py --check-image
  the head each tuple wears: A-A1-A-A-A on figure 0 -> [24], A-I3-A-A-A on
  figure 0 -> [34], A-B4-A-A-A on figure 0 -> [26], A-A1-A-A-A on figure 1 ->
  [24], A-I3-A-A-A on figure 1 -> [34], A-B4-A-A-A on figure 1 -> [26]
assembly --check-image: ok
$ python tools/looks/scene.py --check-image          scene --check-image: ok
$ python tools/looks/ui_check.py
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple it was asked for
$ python tools/looks/controls.py --only assembly-goalkeeper-unmapped
  RED    assembly-goalkeeper-unmapped assembly.py :: HAIR_MAPS
$ python tools/looks/selftest.py --quiet
  ..... 53 of 53 controls red
looks_selftest: 0 failure(s)
```

`roms/` intocada (só leitura), os dois save states só carregados — o
`restore_state` copia para o diretório do fork, e nenhum dos dois `.sav` de
`work/looks-states/` foi escrito. O emulador foi encerrado pelas duas corridas;
a janela ficou em −32000 nas duas.

### Problemas encontrados

- **O segundo bloco de cabeças continua sem dono.** Não é do cabelo do goleiro
  — medido —, e "dois blocos, duas figuras" volta a ser a coincidência que o
  `layout.HEAD_RUNS` sempre disse que era. Não abre CORR: nenhuma tupla desenha
  errado por isso, e a pergunta já está escrita lá.
- A primeira linha do `--patched` mostra a seção 32 diferente do disco antes
  de qualquer `K1`: resto do state, não achado.

### Arquivos criados/modificados

- `tools/looks/oracle.py`, `tools/looks/assembly.py`, `tools/looks/controls.py`,
  `tools/looks/confront.py`, `tools/looks/layout.py`
- `docs/PLAN-LOOKS-PY.md` — a linha do goleiro da §5.3 e as duas passagens da
  §6(c), corrigidas no lugar com a data
- `docs/tasks/looks/17-confronto-com-o-emulador.md` — o resíduo fechado
- `docs/tasks/looks/15-visualizador-opengl.md` — a nota do mapa, datada
- `docs/prompts/perfil-looks.md` — o slot no `--patched` e no `--writes`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
