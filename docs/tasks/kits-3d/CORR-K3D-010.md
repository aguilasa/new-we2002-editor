---
id: CORR-K3D-010
---

# CORR-K3D-010 — Log da K3D-TASK-15 sem os comandos de recorte e da folha de contato

Origin: [K3D-TASK-15](/docs/tasks/kits-3d/15-fechamento-fase-5.md)

## Problem

O Log da [K3D-TASK-15](/docs/tasks/kits-3d/15-fechamento-fase-5.md) diz que as capturas
foram "recortadas na caixa da vista (`940x409+20+169`)" e montadas em
`work/k3d-15/sheet.png`, mas não traz comando para nenhum dos dois passos; só o comando
de captura do `app.py` está escrito. O recorte dá para refazer (o revisor refez com
ImageMagick e obteve 0 px de diferença), mas a folha — grade 2×3, 1434x426, com bordas —
não se reconstrói a partir de nada no repositório nem no Log.

## Evidência

```text
$ grep -nE "convert|magick|montage" docs/tasks/kits-3d/15-fechamento-fase-5.md
(nada; exit 1)
$ identify work/k3d-15/sheet.png
work/k3d-15/sheet.png PNG 1434x426 ...
```

## Root cause

Hipótese: o recorte e a montagem rodaram como passos avulsos de shell, e só o resultado
foi transcrito no Log.

## Fix

No Log de `docs/tasks/kits-3d/15-fechamento-fase-5.md`, acrescentar o comando exato do
recorte (por exemplo `convert work/k3d-15/figF-yawY.png -crop 940x409+20+169 +repage
work/k3d-15/crop-figF-yawY.png`) e o da montagem que produziu `sheet.png` — ou registrar
a folha como avulsa e não reproduzível.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/15-fechamento-fase-5.md

## Verificação

```sh
grep -nE "convert|magick|montage" docs/tasks/kits-3d/15-fechamento-fase-5.md
```

Hoje não imprime nada; depois, os comandos de recorte e da folha, e rodá-los refaz
`work/k3d-15/sheet.png` com `compare -metric AE` igual a 0.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. O `grep` não achava nada (exit 1);
  `identify work/k3d-15/sheet.png` → `PNG 1434x426`.
- Comandos reconstruídos e postos no Log da K3D-TASK-15: recorte com `convert … -crop
  940x409+20+169 +repage` e folha com `montage … -tile 3x2 -geometry 470x205+4+4 -background
  grey20`. Refeitos no scratchpad: `compare -metric AE` = 0 nos seis recortes e na folha. Controle
  sem `-background grey20`: AE = 32784.
- Verificação: o `grep` agora mostra as linhas 62, 67, 68 e 72.
