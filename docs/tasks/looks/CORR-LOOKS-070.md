---
id: CORR-LOOKS-070
title: "A caixa do cursor no valor do DEFAUL começa em x 396 no jogo, e a tabela a carrega da linha de carga em x 314"
origin: CORR-LOOKS-067
severity: low
files: [tools/looks/oracle.py, tools/looks/screen.py, tools/looks/screen.json]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-070 — A caixa do cursor no valor do DEFAUL começa em x 396 no jogo, e a tabela a carrega da linha de carga em x 314

Origin: [CORR-LOOKS-067](/docs/tasks/looks/CORR-LOOKS-067.md)

## Problema identificado

Com o cursor no **valor** do `DEFAUL` (um `Up` depois da carga), o jogo
desenha a caixa amarela em `(396, 41, 476, 52)`. O `screen.State.cursor_box()`
não mede a caixa por linha: carrega para baixo, pelo `pitch`, a caixa da linha
de carga (`cursor_box_on_load = [314, 53, 476, 64]`), e dá `[314, 41, 476, 52]`.
A janela desenha o que a tabela diz, então sai 82 px mais larga à esquerda. Nenhum
gate compara a caixa do cursor da janela com a do jogo, e o `--keys` compara
texto, ajuda e setas, não a caixa.

Apontado pelo worker da CORR-LOOKS-067 em 2026-09-21; anterior a ela.

## Evidência

```text
$ grep -n "396" docs/tasks/looks/CORR-LOOKS-067.md     # o que o walk da 067 leu da VRAM
116:    Up    -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'

$ python -c "import json,sys; sys.path.insert(0,'tools/looks'); import screen; \
    d=json.load(open('tools/looks/screen.json',encoding='utf-8')); s=screen.State(d,'2'); \
    print('load',s.row,s.cursor_box()); s.press('Up'); print('after Up',s.row,s.cursor_box())"
load NAT [314, 53, 476, 64]
after Up DEFAUL [314, 41, 476, 52]
```

## Causa raiz

(hipótese) `State.cursor_box()` (`tools/looks/screen.py`) supõe que a caixa
tem a mesma largura em toda linha e só desce pelo `pitch`. O walk do `--screen`
mede a caixa na chegada, mas grava só a da linha de carga
(`cursor_box_on_load`); a caixa por linha nunca entra na tabela. Falta saber se
só o `DEFAUL` difere ou se outras linhas também.

## Correção

- `tools/looks/oracle.py`, walk do `--screen --write`: gravar a caixa do cursor
  medida no valor de **cada** linha (como a 067 já faz para o rótulo).
- `tools/looks/screen.py`: `cursor_box()` lê a caixa da linha; `validate` recusa
  linha sem ela.
- Um confronto da caixa no `--keys` (jogo × tabela × janela), com controle
  plantado.
- Regenerar `tools/looks/screen.json` pelo gerador.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`
- `tools/looks/screen.py`
- `tools/looks/screen.json` (gerado)

## Verificação

O comando `python` da Evidência deve dar `after Up DEFAUL [396, 41, 476, 52]`,
e o `oracle.py --keys "Up" 2` deve confrontar a caixa e dar 0 diferença; com a
caixa do `DEFAUL` plantada em x 314, vermelho.

## Log de Execução
