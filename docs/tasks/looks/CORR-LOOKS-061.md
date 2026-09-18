---
id: CORR-LOOKS-061
title: "Correção: o `--against-pose` descarta metade das capturas sem dizer, e o \"96 de 96\" se lê como cobertura inteira"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-LOOKS-061: oito capturas entram, oito somem, e a linha diz oito

## Problema identificado

A [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md) mede o
leitor contra a captura da [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md).
O `oracle.py --poses` grava **16** capturas — oito quadros em cada slot, 192
peças. O `anime.py --against-pose` julga **8**, e não diz que deixou oito de
fora:

```python
tools/looks/anime.py:592
    captures = [one for one in _load_captures(directory)
                if any(piece.get("pair") is not None
                       for piece in one["pieces"])]
```

O filtro é por captura inteira: quem não tem **nenhum** par cai fora antes de
qualquer contagem. Só o caso por peça é reportado — *"0 piece(s) drew before
any unpack stop"* —, e esse zero, ao lado de *"8 capture(s), 96 piece(s)
drawn"*, faz a corrida parecer completa.

Daí saem as frases do Log, do critério de conclusão e da §10.3 (l): **"96 de 96
peças"** e **"90 das 96 matrizes"**. São 96 de **192** capturadas; as outras 96
não foram julgadas nem contadas.

**O descarte em si é defensável** — nas oito capturas de fora o jogo não parou
na instrução de desempacotamento naquela passada, e os ângulos gravados são o
que sobrou do scratchpad, não o que aquele quadro usou. O que falta é **dizer
isso**: um gate que decide sozinho o que não vai medir, em silêncio, é o que a
armadilha 50 do perfil descreve, aplicada à entrada em vez de ao veredito.

## Evidência

Recapturado ao vivo hoje, na árvore de `d9314b2` (as 16 capturas saíram
idênticas às da task, arquivo por arquivo):

```text
$ python tools/looks/oracle.py --poses
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)      # 16 arquivos

$ ls work/looks-pose | wc -l
16

$ python - (contando o campo `pair` de cada captura)
slot1-frame0     12 pieces   pair 12
slot1-frame40    12 pieces   pair  0      <- descartada
slot1-frame60    12 pieces   pair  0      <- descartada
slot1-frame100   12 pieces   pair  0      <- descartada
slot1-frame120   12 pieces   pair  0      <- descartada
slot2-frame40    12 pieces   pair  0      <- descartada
slot2-frame60    12 pieces   pair  0      <- descartada
slot2-frame120   12 pieces   pair  0      <- descartada
slot2-frame140   12 pieces   pair  0      <- descartada
(as outras sete: pair 12)

$ python tools/looks/anime.py --against-pose
  8 capture(s), 96 piece(s) drawn
  96 of 96 carry the angles the file holds at the pair the game read, integer for integer
  0 piece(s) drew before any unpack stop, so no pair names them
  90 matrices of 96 are EXACT, 6 are blends the game made, and 0 are neither
anime --against-pose: 0 failure(s)
```

E o que as descartadas guardam, que é a razão de elas não servirem como estão —
ângulos de scratchpad não reescrito, fora do domínio de 10 bits com sinal
deslocado que o arquivo guarda:

```text
slot1-frame100  peça 0: (48, -4096, 0)     peça 1: (64, -16, -4096)
slot2-frame60   peça 0: (64, -4080, -16)   peça 1: (64, -16, -4080)
```

## Causa raiz

O filtro nasceu para a peça que não para na instrução vigiada (dez variantes
dividem o dispatch) e acabou eliminando a captura inteira, num ponto do código
onde nada conta o que saiu.

## Correção

### Arquivo: `tools/looks/anime.py`

O `_against_pose` conta e **imprime** as capturas postas de lado, com o motivo
— nenhuma parada de desempacotamento naquela passada, ângulos do scratchpad
anterior — e nomeia quais. Duas frases que valem: *"8 de 16 capturas julgadas"*
e *"8 postas de lado: nenhuma parada de desempacotamento"*.

E, se a captura sem par for **esperada** (metade delas, nas duas corridas de
hoje), isso é resíduo nomeado, como o `confront.EXPECTED` faz — com o número
virando falha se mudar: hoje é metade, e uma corrida em que 15 de 16 caiam fora
passaria igualmente verde.

### Arquivo: `tools/looks/oracle.py`

A captura que não vê par nenhum pode dizer isso ao gravar (um campo no JSON),
para o consumidor não ter de inferi-lo da ausência.

### Arquivos: `docs/PLAN-LOOKS-PY.md` (§10.3 (l)) e `docs/tasks/looks/26-o-formato-do-anime-bin.md`

Onde está "96 de 96" e "90 das 96", dizer de quantas capturadas: 96 peças **de
192**, nas oito capturas em que o jogo desempacotou.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/anime.py` | modificar |
| `tools/looks/oracle.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/26-o-formato-do-anime-bin.md` | modificar |

## Verificação

- [ ] `anime.py --against-pose` imprime quantas capturas julgou **e** quantas
      pôs de lado, com o motivo
- [ ] um número de descartadas fora do esperado **reprova**
- [ ] os documentos dizem 96 de 192, não 96 de 96
- [ ] `python tools/looks/selftest.py --quiet` verde, com controle plantado
      para o descarte silencioso
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
