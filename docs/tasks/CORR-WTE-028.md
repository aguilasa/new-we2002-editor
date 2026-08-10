---
id: CORR-WTE-028
title: "Correção: `conferir_vereditos()` guarda a coluna `Original`, não o veredito"
type: correção
category: verificação
status: pendente
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

- [ ] `python3 -m unittest discover -s wte/tools -p 'test_*.py'` verde, com o
      assert novo sobre o valor do veredito
- [ ] `python3 wte/tools/check_fase2.py --check` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
