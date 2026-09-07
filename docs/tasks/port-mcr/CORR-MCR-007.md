---
id: CORR-MCR-007
title: "Correção: retraduzir o `card.py` para en-US e fechar a dívida aberta da §3.5"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-007: o `card.py` é anterior à regra de idioma

## Problema identificado

O dono do repositório determinou, em **2026-09-07**, que **todo o código do
port** seja em **inglês dos EUA** — identificadores, docstrings, comentários,
mensagens de erro, texto de `--help` e do CLI, e rótulo de UI. A §3.5 do
[`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) foi reescrita nesse dia e já diz
isso, com a fronteira no **arquivo**: `tools/mcr/**.py` é inglês de ponta a
ponta, `docs/**` continua em português.

O `tools/mcr/card.py` da
[MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) foi escrito
**antes** dessa decisão, sob a regra anterior ("identificadores em inglês,
docstrings em português"), e está em português. **A task não errou** — cumpriu a
regra que existia no dia. A §3.5 registra o módulo como **dívida aberta** e
única exceção, e aponta para esta correção; enquanto ela não fecha, nenhum
módulo novo herda a exceção.

## Evidência

Medido por `ast`/`tokenize` sobre a árvore commitada:

| natureza | quantidade | exemplo |
|---|---:|---|
| docstrings | 17 | `"""O conteiner do memory card PSX -- diretorio, blocos, quadros e as recusas.` |
| linhas só de comentário | 36 (mais 9 inline, 45 tokens) | `# O primeiro byte que pertence a DADO e nao a estrutura.` |
| valores de estado de quadro | 9 (os 8 de `FRAME_STATES` mais o `"desconhecido"` do `state_name`) | `'em uso, primeiro bloco da cadeia'` |
| chaves do `--json` em português | 15 de 20 | `origem`, `checksums_ruins`, `tamanho_declarado`, `blocos_fora_da_cadeia`, `proximo_quadro` |
| mensagens de recusa (`raise Refused`/`CardError`) | 7 | `f"offset negativo: {offset}"` |
| `print(` do CLI e do `self_check` | 20 | `checksums de quadro: todos batem  (relatado, nunca consertado)` |
| identificadores **locais** em português | `falhas`, `tenta`, `recusa`, `ok`, `nome`, `detalhe`, `excecao`, `trecho`, e o default `origin="<memoria>"` | |

Os identificadores **públicos** já estão em inglês — `Card`, `DirectoryEntry`,
`frame_checksum`, `next_frame`, `chain`, `find_save`, `bad_checksums`,
`stray_blocks`, `write`, `to_bytes`, `synthetic_card`, `self_check`. A API não
muda.

A saída de usuário, hoje:

```
$ python3 tools/mcr/card.py work/mcr-entrada.mcr --blocks
 bloco  estado  bytes nao-zero
    1   0x51     5844
    2   0x53     6253
    3   0xa0       41  <-- fora da cadeia declarada
```

O ciclo é o desalinhado, não o repositório: **25 dos 26** módulos de
`tools/pes2/` já têm docstring em inglês (a exceção é o `faq2md.py`), e o
`newWe2002` traduziu o italiano do `legacy/` nas Fases 3.5 e 5.5, com glossário
e `--check`.

## Causa raiz

O módulo é anterior à decisão de idioma; a regra mudou depois de ele existir.

## Correção

### Arquivo: `tools/mcr/card.py`

Traduzir para en-US **preservando a API pública e o comportamento**: as 17
docstrings, os 45 comentários, os 9 valores de estado, as 15 chaves do `--json`,
as 7 mensagens de recusa, os 20 `print` e os identificadores locais. O conteúdo
técnico não muda — só o idioma; a **razão** escrita em cada comentário é o valor
dele e tem de sobreviver à tradução, não ser encurtada por ela.

**A armadilha do gate:** o `recusa()` do `self_check` casa **substring** da
mensagem (`"abaixo de 0x800"`, `"bytes, e um memory card"`, `"volta ao
quadro"`). Traduzir a mensagem sem traduzir o trecho esperado deixa o gate
**verde por acidente** — o mesmo defeito que o controle negativo 1 desta task
denuncia. Traduza os dois lados no mesmo movimento e **replante os cinco
controles**, exigindo 5/5 vermelhos com as mesmas contagens de falha
(2, 8, 1, 1, 1) pelos trechos novos.

### Arquivo: `docs/PLAN-MCR-PY.md` (§3.5)

Tirar o parágrafo **"Uma dívida aberta"** quando a tradução fechar — ele existe
só enquanto o `card.py` é exceção.

### Arquivo: `docs/prompts/perfil-mcr.md`

Tirar a oração que aponta o `card.py` como única exceção, na decisão de idioma.

### Onde a regra vira gate

A §3.5 manda a mesma varredura que recusa espanhol remanescente recusar também
**português em `tools/mcr/`** — uma lista curta de palavras que só aparecem em
prosa (`quadro`, `cartao`, `escrita`, `recusa`, `falha`). Isso é da
[MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md), que constrói o
`selftest`; esta correção não a antecipa, mas deixa o `card.py` no estado em que
essa varredura fica verde.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/mcr/card.py` | modificar (tradução, sem mudança de comportamento) |
| `docs/PLAN-MCR-PY.md` | modificar (tirar a dívida aberta da §3.5) |
| `docs/prompts/perfil-mcr.md` | modificar (tirar a exceção) |

## Verificação

- [ ] `python3 tools/mcr/card.py --self-check` continua **27 checks, 0 falhas**,
      e duas corridas dão bytes iguais
- [ ] os **cinco controles negativos** da MCR-TASK-04 continuam vermelhos, com
      as contagens de falha 2, 8, 1, 1, 1 — é o que prova que os trechos
      esperados foram traduzidos junto com as mensagens
- [ ] `python3 tools/mcr/card.py work/mcr-entrada.mcr --blocks` reporta os
      mesmos números: blocos `[1, 2]`, 16.384 B declarados, 41 bytes no bloco 3,
      5844 e 6253 nos blocos 1 e 2
- [ ] `grep -inE 'quadro|cartao|escrita|recusa|falha' tools/mcr/card.py` vazio
- [ ] nenhum dos 17 destinos de `wte/re/mcr.md` aparece em `card.py` (Regra 1),
      e `import card` não traz `PySide6` (Regra 3)
- [ ] a §3.5 do plano e o `perfil-mcr.md` não citam mais a exceção
- [ ] `roms/` e `work/entrada.mcr` intocados — o digest continua
      `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
