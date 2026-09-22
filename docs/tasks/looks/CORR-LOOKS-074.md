---
id: CORR-LOOKS-074
title: "Um código de largura 0 entra na lista de sprites do jogo e não na do Font.run"
origin: CORR-LOOKS-073
severity: low
files: [tools/looks/glyphs.py, tools/looks/oracle.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-074 — Um código de largura 0 entra na lista de sprites do jogo e não na do Font.run

Origin: [CORR-LOOKS-073](/docs/tasks/looks/CORR-LOOKS-073.md)

## Problema identificado

Na passada que desenha (kind 32), o jogo só deixa de chamar o `GsSortSprite`
(`0x8003E8BC`) para o **espaço** (`0x8010C93C`). Um código de largura 0 — `@`,
`^`, `~` nesta fonte — ainda entrega ao GPU um `GsSPRITE` de largura 0. O
`glyphs.Font.run` não põe nada na lista para esse código. Na tela nada aparece
nos dois casos, mas uma comparação de **lista de sprites** (o `oracle.py
--glyphs` conta sprites de fonte) contaria um a mais do lado do jogo.

Hoje é inalcançável: nenhuma string da tela `LOOKS SET` tem `@`, `^` ou `~`
(`screen.json`). Fica registrado para quando o `glyphs.py` servir a outra tela
ou a uma string nova.

## Evidência

Leitura estática do `/SELECTC.BIN` (base `0x800FC000`, igual nos dois discos),
feita na CORR-LOOKS-073 e transcrita no Log dela:

```text
$ sed -n 87,89p docs/tasks/looks/CORR-LOOKS-073.md
passada que desenha (8010c4dc, kind 32 -> jal 8010bb04 com a3=0)
  8010c93c  espaço (32) pula o GsSortSprite (0x8003e8bc); largura 0 não pula
  8010c9c0  lhu v0,192 ; lb v1,14(s1) ; addu v0,v0,v1 ; addu s2,a0,v0   x += w + espaçamento

$ python -c "import sys;sys.path.insert(0,'tools/looks');import glyphs;f=glyphs.Font(glyphs._toy_table());b=bytearray(f.table);b[2*(64-32)+1]=0;print(glyphs.Font(bytes(b)).run('@',(0,0),2,(128,128,128)))"
[]
```

Não medido ao vivo: nenhum quadro do jogo exercita o caso.

## Causa raiz

`Font.run` (`tools/looks/glyphs.py`) pula todo código com `width == 0`, junto
com o espaço (`if char != " " and width`); o jogo só pula o espaço.

## Correção

Decidir, com medição, se vale reproduzir: ou o `Font.run` passa a emitir o
sprite de largura 0 (e a janela ignora sprite vazio ao pintar), ou o `oracle.py
--glyphs` descarta sprite de largura 0 do lado do jogo ao contar, com a
leitura acima como justificativa. Se nenhuma tela alcançar o caso, `rite
mark-stale` com esse motivo é resposta válida.

## Arquivos a criar ou modificar

- `tools/looks/glyphs.py`
- `tools/looks/oracle.py`

## Verificação

Uma string com `@` desenhada no jogo (se alcançável) e pelo `Font.run`: as duas
listas de sprites têm o mesmo tamanho, ou o descarte é explícito e testado.

## Log de Execução
