---
id: KITS-TASK-09
---

# KITS-TASK-09 — `cli.py info/export` e o confronto 1: `tex.py` contra `bin_archive.py export`

## Goal

A CLI faz `info` e `export` só pela fachada, e os dois decodificadores concordam imagem por imagem e paleta por paleta nas 105 tags.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/selftest.py`
- `tools/kits/core/api.py`

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kits/cli.py` só mostra `core.api` e a biblioteca padrão
- [ ] `cli.py survey` passa pela fachada: `api.py` expõe o levantamento (`survey_image`) e a forma esperada (quantas imagens e quantas CLUTs), e `grep -nP "^from core import (?!api)" tools/kits/cli.py` sai vazio
- [ ] Confronto 1 roda como opção versionada e imprime 105 de 105 tags iguais (6 imagens e 5 paletas cada); colado no Log
- [ ] Controle: um pixel alterado no lado do `tex.py` derruba o confronto (vermelho no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

Da [CORR-KITS-001](/docs/tasks/kits/CORR-KITS-001.md): o subcomando `survey`, entregue na KITS-TASK-01 antes de a fachada existir, importa `core.survey` direto e lê `survey_mod.EXPECTED_SHAPE`/`KIND_IMAGE`. Esta task o passa para trás de `core/api.py`, com as constantes de forma vindo de lá.

Da KITS-TASK-02: `texture.tables` (do `looks`) e `bin_archive.entries` (de `tools/pes2`) discordam sobre `/BIN/DATSEL2.BIN` — o primeiro acha nele registro sobre (576,256)/(608,256), o segundo não (`atlas.py --elsewhere` contra `cli.py rects ... 576,256 608,256`). Não é TEX, mas é o mesmo tipo de pergunta: vale saber qual leitor está certo antes de declarar os dois decodificadores concordes.

## Log de Execução
