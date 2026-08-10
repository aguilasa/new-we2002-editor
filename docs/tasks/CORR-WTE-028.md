---
id: CORR-WTE-028
title: "Correção: `conferir_vereditos()` guarda a coluna `Original`, não o veredito"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-028: o dicionário de vereditos do `check_fase2.py` guarda a coluna errada

## Problema identificado

`wte/tools/check_fase2.py:216-241`, `conferir_vereditos()`. A docstring diz
"Um veredito escrito por formulario, na tabela do `re/visual.md`", o retorno é
anotado `dict[str, str]` e o chamador nomeia o resultado `vereditos`. O que ele
guarda, porém, é o **grupo 2** da regex — a coluna `Original` da tabela do
`visual.md`, que vale `sim` ou `DFM`. O veredito é o grupo 3, e é descartado:

```python
m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$", linha)
if m and m.group(1) in formularios:
    achados[m.group(1)] = m.group(2).strip()   # <- Original, não Veredito
```

O cabeçalho da tabela em `wte/re/visual.md` é
`| Formulário | Original | Veredito |`, então o grupo 2 é `Original`.

Não é falso-verde hoje: o `montar()` só usa `len(vereditos)`, e a regex de três
colunas já exige que a célula de veredito exista e seja não vazia — formulário
sem linha, ou linha sem a terceira coluna, continua abortando. O defeito é o
valor guardado, que está errado e é dado morto: no dia em que o `fase-2.md`
imprimir o veredito por formulário, ou em que a conferência passar a olhar o
texto do veredito (vocabulário, ressalva, "sem ressalva"), ela vai medir
`sim`/`DFM` e não vai reclamar de nada.

## Evidência

Linha real do `wte/re/visual.md`:

```
| `MainForm` | sim | **Fundo divergente por handler não implementado** (achado 3). …
```

Grupos da regex de `conferir_vereditos()` sobre ela:

| Grupo | Valor | O que a função chama disso |
|---|---|---|
| 1 | `MainForm` | chave — correto |
| 2 | `sim` | **guardado como "veredito"** |
| 3 | `**Fundo divergente…**` | descartado |

E o teste que cobre a rota, `test_check_fase2.py:113-116`, escreve as linhas
como `| \`{f}\` | sim | sem ressalva |` e só assere a **contagem**
(`| Formulários com veredito visual escrito | **2** |`), então nunca olha o
valor — é por isso que a troca de coluna passou.

## Causa raiz

Índice de grupo trocado na captura, num valor que nenhum chamador lê.

## Correção

### Arquivo: `wte/tools/check_fase2.py`

Guardar `m.group(3)` — o veredito — em vez de `m.group(2)`. A coluna `Original`
não se perde de graça: ela diz se o formulário foi confrontado com captura do
original ou só com o DFM, e é o número que sustenta o item 3 de "O que a fase 2
não prova" (18 do port contra 4 do original). Guardar as duas, e passar a
imprimir a contagem `capturado / só DFM` no `fase-2.md`, transforma esse item
de prosa em número medido.

### Arquivo: `wte/tools/test_check_fase2.py`

Acrescentar assert sobre o **valor**, não só sobre a contagem — é o que teria
pegado isto. Com a árvore sintética do `Base`, `conferir_vereditos()` tem de
devolver o texto `sem ressalva`, e não `sim`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase2.py` | modificar |
| `wte/tools/test_check_fase2.py` | modificar |
| `wte/re/fase-2.md` | modificar (regerado, se a contagem `capturado / só DFM` entrar) |

## Verificação

- [x] `python3 -m unittest discover -s wte/tools -p 'test_*.py'` verde, com o
      assert novo sobre o valor do veredito — **276 testes, OK**
- [x] `python3 wte/tools/check_fase2.py --check` verde
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

`conferir_vereditos()` passou a devolver o par `(origem, veredito)` por
formulário — o grupo 3 da regex, que é o veredito, deixou de ser descartado, e
o grupo 2 deixou de ser chamado pelo nome errado. A docstring explica a troca e
por que ela não era falso-verde ainda.

A coluna `Original` virou número publicado em vez de dado morto: o `fase-2.md`
ganhou a linha `…confrontados com captura do original / só com o DFM` —
medida **4 / 14** —, e o item 3 de "O que a fase 2 não prova" passou a
interpolar os dois números em vez de trazê-los escritos, com a origem dita.
Antes eram `18` e `4` datilografados na prosa; agora saem de contar a tabela.

Guarda nova: valor fora de `sim`/`DFM` na coluna `Original` **aborta**. Sem
ela, um terceiro valor cairia calado no lado "só DFM" e o par publicado
deixaria de ser medida. `**sim**` e `sim` são normalizados para o mesmo valor —
a tabela real do `visual.md` escreve o `ficha_salida` em negrito.

Três testes novos: o assert sobre o **valor** do veredito (`sem ressalva`, não
`sim`), a contagem com negrito e com `DFM` nos dois sentidos, e o aborto do
valor estranho.

**Problemas encontrados:**

Nenhum. O `fase-2.md` foi regerado (143 linhas, 5.945 bytes) e duas execuções
seguidas dão bytes iguais (`md5sum` idêntico).

**Arquivos criados/modificados:**

- `wte/tools/check_fase2.py`
- `wte/tools/test_check_fase2.py`
- `wte/re/fase-2.md` (regerado)
