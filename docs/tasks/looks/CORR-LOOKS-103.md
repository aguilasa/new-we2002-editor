---
id: CORR-LOOKS-103
title: "SKIN recolore só a cabeça, e o corpo fica em A"
origin: LOOKS-TASK-13
severity: medium
files: [tools/looks/assembly.py, tools/looks/layout.py]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-28
done_commit: 1f2286a
---

# CORR-LOOKS-103 — SKIN recolore só a cabeça, e o corpo fica em A

Origin: [LOOKS-TASK-13](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)

## Problem

Trocar SKIN na tela muda a cor da cabeça e mais nada: pescoço, braços e pernas
continuam na pele A em todo valor. No jogo, SKIN recolore o corpo inteiro.
Achado em teste manual pelo usuário em 2026-09-28.

## Evidência

`oracle.py --keys` leva jogo e janela ao mesmo estado; a comparação é das duas
capturas que ele grava.

```text
$ python3 tools/looks/oracle.py --keys "Down,Right x3,Down x5" 2
oracle --keys: 0 difference(s) after 9 press(es), across the game, screen.json and our window
```

A tabela concorda porque só confere o texto das linhas. No painel, com SKIN em
D, o jogo (`work/looks-shots/keys-slot2.png`) mostra pescoço, braços e joelhos
escuros; a janela (`keys-slot2-window.png`) os mostra em A. Com o cursor no
próprio SKIN, no close-up, o pescoço é o que difere.

As duas pontas do SKIN, com o `EDT_MOD.BIN` carregado lido até duas leituras
300 quadros apartadas concordarem (o método do `oracle.py --colour`, apontado
para o corpo):

```text
slot 2: sec 0 moved 5/6, 3 63/78, 4 64/78, 5 16/21, 6 17/21, 7 11/11, 8 10/11
slot 1: sec 11 5/6, 16 16/21, 17 17/21, 18 11/11, 19 10/11
```

Cada número é "movidas / primitivas cujo CLUT no disco é a janela de pele nua
(linha 480, coluna 0)". Nenhuma primitiva fora dessa janela se moveu.

## Root cause

O `Effect` do SKIN em `assembly.py` só endereçava a cabeça (`MODEL.BIN`). A
descrição dele já dizia que o campo "moves the bare-skin primitives of the
figure's own sections as well, which are pieces.SKIN_SECTIONS", e a
[LOOKS-TASK-08](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) mediu essas seções.
O endereçamento ficou só na prosa.

As primitivas de pele nua que não se moveram eram as que a pose não desenhou,
porque o jogo reescreve um CLUT só quando desenha a primitiva. A testemunha são
os pares espelhados: a seção 8 guardou a primitiva 27, e a 7, espelho dela, não
guardou nenhuma.

## Fix

- `layout.SKIN_BODY_SECTIONS`: as doze seções do corpo que o SKIN recolore, 0 e
  3 a 8 do jogador de linha, 11 e 16 a 19 do goleiro.
- `assembly.BARE_SKIN`: em vez de uma lista, uma regra — toda primitiva da
  seção cujo CLUT no disco é a janela de pele nua. O `combine()` aplica o passo
  só a ela.
- Self-check: o SKIN alcança as doze seções, move a primitiva de pele nua e
  deixa a de outro registro.
- `--check-image`: o disco põe pele nua exatamente nessas doze seções, e as
  duas figuras em SKIN D não guardam nenhuma primitiva de corpo em A.

## Arquivos a criar ou modificar

- [tools/looks/assembly.py](/tools/looks/assembly.py)
- [tools/looks/layout.py](/tools/looks/layout.py)

## Verificação

```text
$ python3 tools/looks/assembly.py --check-image | grep -E 'bare skin|SKIN D|check-image'
  EDT_MOD.BIN puts bare skin in section(s) 0, 3, 4, 5, 6, 7, 8, 11, 16, 17, 18, 19
  figure 0 at SKIN D: 0 body primitive(s) still at A
  figure 1 at SKIN D: 0 body primitive(s) still at A
assembly --check-image: ok
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
```

E, de novo com `oracle.py --keys "Down,Right x3,Down x5" 2`, o painel da janela
mostra pescoço, braços e joelhos na pele D, como o do jogo.

## Log de Execução

- 2026-09-28 — reproduzido em tela; medido pelas duas pontas nos dois slots;
  corrigido; self-check, check-image e a comparação de tela verdes.
- **Closed** — commit `1f2286a` (2026-09-28): fix(looks): let SKIN recolour the body, not only the head
  - Files (`git show --name-status 1f2286a`):
    - `A docs/tasks/looks/CORR-LOOKS-103.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/assembly.py`
    - `M tools/looks/layout.py`
