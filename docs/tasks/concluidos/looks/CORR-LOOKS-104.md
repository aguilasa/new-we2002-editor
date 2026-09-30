---
id: CORR-LOOKS-104
title: "C2, D2, F2 e F3 desenham o cabelo do primeiro estilo da família"
origin: LOOKS-TASK-14
severity: medium
files: [tools/looks/assembly.py, tools/looks/layout.py]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-28
done_commit: f5939f3
---

# CORR-LOOKS-104 — C2, D2, F2 e F3 desenham o cabelo do primeiro estilo da família

Origin: [LOOKS-TASK-14](/docs/tasks/concluidos/looks/14-tabela-de-montagem.md)

## Problem

Na linha HAIR, C2 desenha o cabelo de C1, D2 o de D1, F2 e F3 o de F1, e E2
parece D1. Achado em teste manual pelo usuário em 2026-09-28. No jogo, cada
um desses estilos tem franja ou risca próprias.

## Evidência

```text
$ python3 tools/looks/oracle.py --patched HAIR 2
       9  changed: section 30 (8 byte(s), band(s) [0, 1])
            section 30 primitive 0: clut 0x7809, (u, v) [(164, 0), (164, 16), (152, 0), (154, 12)]
            section 30 primitive 1: clut 0x7801, (u, v) [(212, 31), (212, 21), (222, 31), (222, 21)]
            section 30 primitive 2: clut 0x7801, (u, v) [(200, 31), (200, 21), (212, 31), (212, 21)]
            section 30 primitive 3: clut 0x7809, (u, v) [(173, 12), (164, 16), (175, 0), (164, 0)]
      10  changed: section 30 (8 byte(s), band(s) [2])
            section 30 primitive 1: clut 0x7801, (u, v) [(212, 47), (212, 37), (222, 47), (222, 37)]
            section 30 primitive 2: clut 0x7801, (u, v) [(200, 47), (200, 37), (212, 47), (212, 37)]
```

Os estilos 11 a 17 (D1 a F3) mostram o mesmo padrão nas seções 48 e 52: os
quads 1 e 2, com o CLUT da cor de cabelo (coluna 1), reescritos numa faixa só.
`--patched HAIR 1` imprime a mesma coisa, primitiva por primitiva, no goleiro.

## Root cause

Duas lacunas da [LOOKS-TASK-14](/docs/tasks/concluidos/looks/14-tabela-de-montagem.md), as
duas registradas como abertas:

- O `layout.HAIR_QUADS` conhecia os quads de 4 das 13 cabeças, as que o
  breakpoint em `HAIR_QUAD_STORE` pegou. As seções 30, 48 e 52 são gravadas por
  outra instrução, então ficavam com a janela do disco. Todo estilo dessas
  famílias saía igual.
- O `HAIR_MAP` registrava duas ou três faixas para dez estilos (B1, C1, D1, E2,
  F1, G1, J1, K1, O1, P1). O `--patched` dava a faixa de toda primitiva que um
  passo gravava, e o mesmo passo reescreve os quads da **barba** (coluna 9,
  `v` 0..16). As faixas a mais eram as da barba. Separado pela coluna do CLUT,
  cada estilo grava o cabelo numa faixa só, ou em nenhuma.

Além disso, as seções 30, 48 e 52 gravam os cantos em `16·faixa + 15` e
`16·faixa + 5`, e não em `+ 15` e `+ 1` como as quatro conhecidas. O disco
guarda 30/21/30/22, que não é nenhum dos dois.

## Fix

- `layout.HAIR_QUADS`: 30, 48 e 52 → quads (1, 2).
- `layout.HAIR_QUAD_CORNERS`: as linhas de canto por seção, (15, 5, 15, 5) nas
  três. `hair_texcoords()` recebe a seção escolhida e usa as dela.
- `assembly.HAIR_MAP` e `HAIR_MAP_GOALKEEPER`: só a faixa do cabelo. B1 → 0,
  C1 → 1, D1 → 1, F1 → 3. E2, G1, J1, O1 e P1 → nenhuma, porque não gravam
  quad de cabelo e desenham a janela do disco. K1 continua com quatro: a
  reescrita da seção 32 não é passo de faixa, e não é aplicada.
- Contagens do self-check: `HAIR_MAP_MULTI_BAND` 10 → 1 (K1),
  `HAIR_MAP_BANDS_UNMEASURED` 1 → 0, quads em 7 cabeças. Casos novos: os
  cantos de C2 caem em 47/37 e os da seção 24 em 47/33.

## Arquivos a criar ou modificar

- [tools/looks/assembly.py](/tools/looks/assembly.py)
- [tools/looks/layout.py](/tools/looks/layout.py)

## Verificação

```text
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
$ python3 tools/looks/cli.py check | tail -1
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
$ for n in 9 10 11 12 13 14 15 16 17; do python3 tools/looks/oracle.py --keys "Down x2,Right x$n" 2; done
oracle --keys: 0 difference(s) after 11 press(es), ...   (e assim até 19)
```

Montadas lado a lado, as capturas de jogo e janela de C1 a F3 estão em
`work/looks-corr104/hairgrid.png`, fora do git. Cada estilo mostra a franja ou
a risca do jogo, e C2, D2, F2 e F3 deixaram de repetir o primeiro da família.
O que continua diferente é o giro da cabeça no close-up, que é aberto conhecido
do plano (§10.3 (p)).

## Log de Execução

- 2026-09-28 — medido por `--patched HAIR` nos dois slots; corrigido;
  selftest, check-image e a comparação de tela dos nove estilos conferidos.
- **Closed** — commit `f5939f3` (2026-09-28): fix(looks): give C, D, E1 and F their own hair band
  - Files (`git show --name-status f5939f3`):
    - `A docs/tasks/looks/CORR-LOOKS-104.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/assembly.py`
    - `M tools/looks/layout.py`
