---
id: CORR-LOOKS-069
title: "Dizer quantos sprites estáticos foram amostrados, não 14"
origin: LOOKS-TASK-36
severity: low
files: [tools/looks/oracle.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-069 — Dizer quantos sprites estáticos foram amostrados, não 14

Origin: [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md)

## Problema identificado

O `oracle.py --scenery --write` imprime "359 pixel(s) of 14 sprite(s)", e o
Log da task cita a frase. Só 13 sprites trazem amostra: a barra é inteira
transparente (armadilha 91) e não tem nenhuma. O número é o de sprites
estáticos achados, não o de amostrados.

## Evidência

Revisão da LOOKS-TASK-36 em 2026-09-21, contando os sprites com `samples` em
`work/looks-scenery/slot{1,2}.json`:

```text
$ python -c (conta sprites com "samples" em work/looks-scenery/slot{1,2}.json)
1 142 sprites; 13 with samples; 359 samples
2 142 sprites; 13 with samples; 359 samples
Counter: plate 4, shirt boxes 4, title 4, bar 1, icon 1  (= 14 static)
```

## Causa raiz

(hipótese) A mensagem em `tools/looks/oracle.py:2188` divide pelo número de
sprites estáticos, e não pelo dos que deram ao menos uma amostra.

## Correção

`tools/looks/oracle.py`, perto da linha 2188: imprimir os sprites que têm
amostra e nomear os que não têm (a barra).

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`

## Verificação

`python tools/looks/oracle.py --scenery --write` deve dizer "of 13 sprite(s)"
e nomear a barra como não amostrada, batendo com a recontagem acima.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-21, HEAD `36d1aaed`: **reproduzida**.

```text
1 142 sprites; 13 with samples; 359 samples
2 142 sprites; 13 with samples; 359 samples
1 with samples key: 14 nonempty: 13 empty: [(None, [66, 53], [96, 12])]
2 with samples key: 14 nonempty: 13 empty: [(None, [66, 53], [96, 12])]
oracle.py:2188-2190: print("    the static sprites sampled: %d pixel(s) of %d sprite(s), ..." % (..., len(samples)))
_static_samples: out[index] = [...] roda para todo sprite estático, e guarda [] para a barra transparente
```

Execução em 2026-09-21, sobre HEAD `efc9d071` (a `print` estava então em
`oracle.py:2188`, já depois das amostras de seta da CORR-LOOKS-068).

**Causa raiz confirmada.** `_static_samples` grava uma entrada para todo sprite
estático — `[]` para a barra, cujo recorte é inteiro transparente (armadilha
91) — e a mensagem contava `len(samples)`, as chaves, não as que têm amostra.
O JSON escrito não muda: a barra continua com `samples: []`, que é o que diz
que ela foi considerada e não deu pixel.

**Correção.** A frase saiu para `_say_static_samples(sprites, samples)`, que
conta só os sprites com amostra e nomeia cada um sem nenhuma, pelo grupo de
`sprites.group_of`, o ponto e o tamanho.

Antes (triagem acima): `359 pixel(s) of 14 sprite(s)`. Depois:

```text
$ python tools/looks/oracle.py --scenery --write
  -- slot 2 --
    the static sprites sampled: 359 pixel(s) of 13 sprite(s), each the colour the game's frame shows there
    not sampled: the bar at (66, 53), (96, 12) -- no opaque texel on screen
    wrote C:\github\new-we2002-editor\work\looks-scenery\slot2.json
  -- slot 1 --
    the static sprites sampled: 359 pixel(s) of 13 sprite(s), each the colour the game's frame shows there
    not sampled: the bar at (66, 53), (96, 12) -- no opaque texel on screen
    wrote C:\github\new-we2002-editor\work\looks-scenery\slot1.json
oracle --scenery: 0 problem(s) over 2 slot(s)
```

Bate com a recontagem da Evidência: 13 com amostra, 359 amostras, a barra em
`(66, 53)` de `96×12` a única vazia, nos dois slots.

Gates: `selftest.py` → `looks_selftest: 0 failure(s)` (97 de 97 controles
vermelhos); `cli.py check` → `11 ok, 0 failed`; `ui_check.py` → `16 of 16
negative control(s) red`.

Varredura: "of 14 sprite" só aparece no Log de Execução da LOOKS-TASK-36
(`36-os-sprites-estaticos.md:132`), que é registro do que a ferramenta
imprimiu naquele dia — não foi reescrito.
