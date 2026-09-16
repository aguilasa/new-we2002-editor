---
id: CORR-LOOKS-047
title: "Correção: o mapa de cabelo do goleiro não foi medido, e 136 dos 179 goleiros do disco são recusados"
type: correção
category: engenharia-reversa
status: pendente
depends_on: ["CORR-LOOKS-046"]
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

- [ ] `oracle.py --patched HAIR 1` roda e a saída vai para o Log, com o
      `media` do state conferido
- [ ] a figura 1 desenha cada estilo que a medição nomeou, e recusa os que não
      escreveram nada
- [ ] o número de goleiros do disco recusados é **remedido** e escrito onde o
      136 está
- [ ] `confront.py --score` sobre o nosso lado re-renderizado: o slot 1 sem
      `unexplained`
- [ ] controle negativo vermelho
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada, e os dois save states não sobrescritos

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
