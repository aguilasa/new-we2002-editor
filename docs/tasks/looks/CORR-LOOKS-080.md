---
id: CORR-LOOKS-080
title: "Marcar as entregas da Fase 10 das tasks 36, 37 e 38 no progresso"
origin: LOOKS-TASK-38
severity: low
files: [docs/tasks/looks/progresso.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-080 — Marcar as entregas da Fase 10 das tasks 36, 37 e 38 no progresso

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

A lista de entregas da Fase 10 no `progresso.md` do ciclo ainda mostra
`- [ ] Os valores alinhados como no jogo (LOOKS-TASK-38)` com a task em `done`.
O mesmo vale para a 36 e a 37; a 30 e a 31, também `done`, estão marcadas — a
convenção é por task, e três caixas estão atrasadas.

## Evidência

```text
$ sed -n '299,301p' docs/tasks/looks/progresso.md
- [ ] Os sprites estáticos e as setas desenhados do disco ([LOOKS-TASK-36]…).
- [ ] O texto desenhado com os glifos do `EDT_2D.BIN` ([LOOKS-TASK-37]…).
- [ ] Os valores alinhados como no jogo ([LOOKS-TASK-38]…).

$ grep -n "LOOKS-TASK-3[678]" docs/tasks/looks/progresso.md | grep done
| LOOKS-TASK-36 … | done | 2026-09-21 | 2026-09-21 |
| LOOKS-TASK-37 … | done | 2026-09-22 | 2026-09-22 |
| LOOKS-TASK-38 … | done | 2026-09-22 | pending |
```

## Causa raiz

A lista é prosa mantida à mão, **fora** da região gerada pelo Rite, então o
`rite check` não a enxerga. A omissão começou na LOOKS-TASK-36 e cada task
desde então a repetiu.

## Correção

Marcar as três linhas (36, 37, 38) na lista da Fase 10, cada uma com a linha de
resultado que as entradas já marcadas carregam. Como é fora da região
`<!-- rite:begin -->`, a edição à mão é o caminho certo aqui.

## Arquivos

- docs/tasks/looks/progresso.md (linhas 299-301)

## Verificação

Nenhum `- [ ]` sobra na lista da Fase 10 para uma task que a tabela gerada
reporta como `done`.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
$ sed -n '299,301p' docs/tasks/looks/progresso.md
- [ ] Os sprites estáticos e as setas desenhados do disco ([LOOKS-TASK-36]...).
- [ ] O texto desenhado com os glifos do `EDT_2D.BIN` ([LOOKS-TASK-37]...).
- [ ] Os valores alinhados como no jogo ([LOOKS-TASK-38]...).
# a tabela gerada dá as três como done (a 38 já com reviewed_on 2026-09-22)
$ grep -n "rite:begin\|rite:end" docs/tasks/looks/progresso.md
48:<!-- rite:begin tasks -->
91:<!-- rite:end -->      # as caixas estão nas linhas 297-303, FORA da região gerada
```

As duas entradas já marcadas (tasks 30 e 31) trazem uma frase de resultado
medido depois do título; marcar as três novas pede a mesma frase, não só a
caixa.

### O que foi feito

As três linhas (299-301, fora da região gerada) ganharam o `[x]` e a frase de
resultado, no molde das entradas da 30 e da 31. **Todo número saiu do Log de
Execução da própria task**, não do resumo:

| Entrada | Números, e de onde |
| --- | --- |
| 36 | 359 pixels de 14 sprites (`oracle --scenery --write`), 718 amostras dentro de 8 e 14 de 14 controles (`ui_check.py`), `uv` (128,240)/(128,248) e 22 de 64 texels opacos e a CLUT da placa (192,499)/(208,499) (`sprites.py --check-image`), 19 teclas e 11 regiões (`--keys`, `--outside`) |
| 37 | rotina 0xfb04 e tabela de 95 pares em 0x11008, 5.201 bytes de diferença entre os discos (`glyphs.py --check-image` e "De que disco a regra vem"), 134 glifos / 13 espaços / 121 de 121 / 0 sem dono (`oracle --glyphs`), 0 de 16.416 e 2.875 (`confront --outside`) |
| 38 | os modos 0/2/3 e a tabela de saltos em 0x800FC048, o `NAT` em x −80 → −104 ("O que foi feito"), 0 de 16.416 e 0 de 23.472 com 2.875 e 3.075 deslocados (`confront --outside`), as cinco sequências de 19, 10, 47, 32 e 2 teclas (`--keys`) |

Duas coisas ficaram **de fora de propósito**: a contagem de linhas com o ◀ em
x 384, que é da [CORR-LOOKS-079](/docs/tasks/looks/CORR-LOOKS-079.md) e sairia
errada repetida aqui; e os 514 de 23.472 da primeira corrida do `--outside` da
38, que foram defeito corrigido dentro da própria task e não resultado dela.

### O Log de Execução de uma task envelhece, e a revisão dela é que fica certa

Três dos números transcritos estavam **superados por correções do próprio
ciclo**, feitas depois de a task fechar: o log diz o que a corrida imprimiu
**naquele commit**, e não o que a árvore imprime hoje. Conferidos contra o
código em vigor e reescritos:

| Onde | Dizia | Diz, e por quê |
| --- | --- | --- |
| 36 | "359 pixels de **14** sprites" | "359 pixels de **13** sprites — a barra, transparente em todo o seu corte, não dá amostra". [CORR-LOOKS-069](/docs/tasks/looks/CORR-LOOKS-069.md): o `_say_static_samples` conta os sprites **com** amostra e nomeia os sem (`oracle.py:2789-2806`, com a razão no próprio docstring) |
| 37 e 38 | "pixel a pixel" | "**pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal**". [CORR-LOOKS-072](/docs/tasks/looks/CORR-LOOKS-072.md): a comparação conta o pixel cujo maior salto de canal passa de `OUTSIDE_SLACK = 16` (`confront.py:1913`, `2104`, `2148`). **Sem a folga, 11.839 dos 16.416 rótulos divergem** — o fundo da faixa fica a ~6 —, então "pixel a pixel" sozinho afirma mais do que foi medido |

```text
$ grep -n "not sampled\|CORR-LOOKS-069" tools/looks/oracle.py | head -3
2793:    found (CORR-LOOKS-069): the bar is transparent over its whole cut
2805:        print("    not sampled: the %s at %s, %s -- no opaque texel on screen"

$ grep -n "OUTSIDE_SLACK" tools/looks/confront.py | head -3
1913:OUTSIDE_SLACK = 16
1998:    """Pixels of *box* where the two frames differ past `OUTSIDE_SLACK`,

$ sed -n '3122,3125p' docs/PLAN-LOOKS-PY.md
> **pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal** com o quadro do
> jogo (0 de 16.416 nos dois slots, ...). Sem a folga, 11.839 dos 16.416 divergem, ...
```

A lição é do ciclo, não desta correção: **a prosa de resumo se escreve contra a
árvore de hoje**, usando o log da task como ponteiro para o que medir, não como
texto a copiar. As três frases agora batem com o plano e com o perfil, que já
traziam a redação corrigida.

### Verificação

```text
$ sed -n '/^### Fase 10/,/^### Fase 11/p' docs/tasks/looks/progresso.md \
    | grep -oE '^- \[ \].*LOOKS-TASK-[0-9]+' | grep -oE 'LOOKS-TASK-[0-9]+'
LOOKS-TASK-39
LOOKS-TASK-40          # as duas pendentes na tabela gerada -- nada mais sem marcar

$ ... | grep -oE '^- \[x\].*' | grep -oE 'LOOKS-TASK-[0-9]+' | sort -u
LOOKS-TASK-30 LOOKS-TASK-31 LOOKS-TASK-36 LOOKS-TASK-37 LOOKS-TASK-38   # as cinco done

$ git diff --unified=0 docs/tasks/looks/progresso.md | grep -E '^@@'
@@ -299,3 +299,3 @@     # um hunk so, fora da regiao gerada (48-91)
```

### Gates

```text
$ sh <rite> check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```
