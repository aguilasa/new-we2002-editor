---
id: CORR-PES2-020
title: "Correção: a conferência antes da gravação nunca foi vista ficando vermelha"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-PES2-020: A guarda de "conferir antes do disco" não é exercitada

## Problema identificado

O `rewrite_image` do `asset_write.py` faz a conferência que o critério da
PES2-TASK-29 exige — descomprimir o que acabou de comprimir e comparar, antes
de qualquer escrita, sem flag para desligar:

```python
back, _ = lzss.decompress(blob, 0)
if back != packed:
    raise Refused("the recompressed stream does not decompress to what "
                  "was compressed -- refusing to write it")
```

Mas **nada a exercita**. O `cmd_check` mostra em vermelho a guarda de
orçamento (o `TITLE.BIN` entrada 0, 22 bytes acima) e em verde as outras
quatro; a conferência de round-trip só é atravessada em verde, e um verde que
nunca pôde ser vermelho não é evidência — é decoração.

É a mesma lição que a [CORR-PES2-009](/docs/tasks/CORR-PES2-009.md) já cobrou
neste ciclo, quando o `--check` do `lzss.py` passou verde com o bug do `k3`
assinado reintroduzido.

## Evidência

O critério da task: *"Toda entrada regravada é descomprimida e comparada antes
de ir ao disco — sem exceção, sem flag para desligar."* Marcado `[x]`.

A saída do gate, com as guardas que ele de fato exercita:

```
-- open and save, no edit --        SAVE OK
-- the budget refusing --           refused: … 22 B over budget      ← vermelho
-- the negative control --          NEGATIVE CONTROL OK
-- a palette colour, …              1 sector(s) differ … [4711]
WRITE CHECK OK
```

Nenhuma linha prova que a comparação `decompress(compress(x)) == x` recusaria
alguma coisa.

## Causa raiz

A guarda foi escrita e nunca teve um caso que a fizesse disparar, porque
disparar exige um compressor defeituoso — e não há como injetar um sem um
ponto de injeção.

## Correção

### Arquivo: `tools/pes2/asset_write.py`

Dar à conferência um ponto de injeção que só o teste usa, e exercitá-la:

1. `rewrite_image(..., _codec=lzss)` — parâmetro privado, com o módulo real
   como padrão, para o `check` poder passar um objeto cujo `compress` devolve
   bytes que não descomprimem de volta.
2. No `cmd_check`, um caso que passa esse codec quebrado e **exige** o
   `Refused`. Se a guarda sumir do código, o `check` fica vermelho.

Alternativa igualmente válida, se o parâmetro incomodar: mutar um byte do
`blob` entre o `compress` e o `decompress` dentro de um caso de teste dedicado,
e afirmar a recusa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/asset_write.py` | modificar |

## Verificação

- [ ] o `check` tem um caso que faz a conferência recusar, e o imprime
- [ ] remover as três linhas da conferência deixa o `check` **vermelho**
- [ ] `ctest --test-dir build -R pes2` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito:** `rewrite_image` ganhou o parâmetro privado
`_codec=lzss`, e o `cmd_check` um caso que lhe passa um compressor cuja saída
**não** volta ao original — `lzss.compress` com um byte do primeiro literal
invertido — exigindo o `Refused`.

Medido, na ordem em que o `check` imprime:

```
-- the verification before the disk, made to refuse --
  refused: the recompressed stream does not decompress to what was
           compressed -- refusing to write it
```

E o critério que importa, a guarda tendo de ser necessária: **removendo as três
linhas da conferência, o `check` fica vermelho** —

```
$ (sem as tres linhas)  → WRITE CHECK FAILED
$ (restaurado)          → WRITE CHECK OK
```

**Problemas encontrados:** nenhum. O ponto de injeção é privado e tem o módulo
real como padrão, de modo que nenhum caminho de produção passa por ele; quem
o usa é só o `check`.

**Arquivos criados/modificados:** `tools/pes2/asset_write.py`.
