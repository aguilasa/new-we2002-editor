---
id: CORR-LOOKS-061
title: "Correção: o `--against-pose` descarta metade das capturas sem dizer, e o \"96 de 96\" se lê como cobertura inteira"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-26
severity: medium
done_on: 2026-09-18
done_commit: 08ac05f
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

- [x] `anime.py --against-pose` imprime quantas capturas julgou **e** quantas
      pôs de lado, com o motivo
- [x] um número de descartadas fora do esperado **reprova**
- [x] os documentos dizem 96 de 192, não 96 de 96
- [x] `python tools/looks/selftest.py --quiet` verde, com controle plantado
      para o descarte silencioso
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-18

### Resumo do que foi feito

A evidência reproduz em `08ac05f`: `work/looks-pose/` tem **16** capturas, oito
sem par em peça nenhuma, e o `--against-pose` dizia `8 capture(s), 96 piece(s)
drawn` sem uma linha sobre as outras oito.

- **`anime.py`** — o filtro virou `split_captures()`, que devolve as julgadas e
  as postas de lado; o comando imprime `8 of 16 capture(s) judged, 96 piece(s)
  of 192 drawn`, a linha das postas de lado **com o motivo e os nomes**, e
  **reprova** se menos de `JUDGED_FLOOR` (um terço) das capturas carregar par.
  Três casos novos no `self_check()`.
- **`oracle.py`** — a captura grava `"unpacked": <peças com par>`, para o
  consumidor não ter de inferir da ausência. Os 16 arquivos recapturados hoje
  trazem o campo.
- **Plano §10.3 (l), perfil (armadilha 54 e a linha do gate), LOOKS-TASK-26,
  LOOKS-TASK-32 e a linha da Fase 9 do `progresso.md`** — onde se lia "96 de
  96" e "90 das 96", agora se lê de quantas capturadas: **96 de 192**, com as
  oito postas de lado ditas.

**Sobre o piso.** O medido é metade (8 de 16, três corridas: as duas da task e
a de hoje, sempre os mesmos oito quadros). O piso ficou em **um terço**, abaixo
do medido de propósito — a armadilha 49 do próprio perfil diz que limiar
escrito no valor medido transforma variação normal em vermelho. O que ele tem
de pegar é a corrida em que a parada se move e uma ou duas capturas carregam o
veredito inteiro; 15 de 16 fora reprova.

### Gates

```text
$ python tools/looks/oracle.py --poses            # recaptura, 2026-09-18
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)
$ python -c "... campo unpacked"
capturas com campo unpacked: 16 de 16
unpacked=0: slot1-frame40/60/100/120, slot2-frame40/60/120/140

$ python tools/looks/anime.py --against-pose
  8 of 16 capture(s) judged, 96 piece(s) of 192 drawn
  8 set aside -- the pass never stopped at the unpack, so the angles beside
  each piece are the scratchpad's, not that frame's: slot1-frame100,
  slot1-frame120, slot1-frame40, slot1-frame60, slot2-frame120,
  slot2-frame140, slot2-frame40, slot2-frame60
  96 of 96 carry the angles the file holds at the pair the game read, integer
  for integer
  0 piece(s) drew before any unpack stop, so no pair names them
  90 matrices of 96 are EXACT, 6 are blends the game made, and 0 are neither
anime --against-pose: 0 failure(s)

$ python tools/looks/anime.py --check
anime.py: 0 failure(s)
$ python tools/looks/controls.py --only anime-keeps-the-scratchpad-captures
  RED    anime-keeps-the-scratchpad-captures anime.py :: split_captures
$ python tools/looks/selftest.py --quiet
  ..... 82 of 82 controls red
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

As oito postas de lado são **as mesmas** nas três corridas que existem, e os
números do veredito (96/96, 90 exatas, 6 misturas) não mudaram — o que mudou é
a corrida dizer de quanto ela partiu.

`roms/` intocada (leitura pura); os dois states só carregados; nenhum
DuckStation de pé no fim; as capturas são JSON de alguns KB em
`work/looks-pose/`.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `tools/looks/anime.py` — `JUDGED_FLOOR`, `split_captures`, `capture_name`, o
  relatório e a reprovação, mais três casos no `self_check()`
- `tools/looks/oracle.py` — o campo `unpacked` na captura
- `tools/looks/controls.py` — `anime-keeps-the-scratchpad-captures`
- `docs/PLAN-LOOKS-PY.md` §10.3 (l), `docs/prompts/perfil-looks.md`
  (armadilha 54 e a linha do gate), `docs/tasks/looks/26-o-formato-do-anime-bin.md`,
  `docs/tasks/looks/32-o-ciclo-da-caminhada.md`, `docs/tasks/looks/progresso.md`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
