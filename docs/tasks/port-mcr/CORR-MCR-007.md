---
id: CORR-MCR-007
title: "Correção: retraduzir o `card.py` para en-US e fechar a dívida aberta da §3.5"
type: correção
category: processo
status: concluído
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

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

`tools/mcr/card.py` traduzido para en-US de ponta a ponta — as 17 docstrings, os
45 comentários (36 de linha e 9 inline), os 9 valores de `FRAME_STATES` mais o
`"unknown"` do `state_name`, as 20 chaves do `--json`, as 7 mensagens de recusa,
os 20 `print` e os identificadores locais (`falhas`→`failures`,
`tenta`→`attempt`, `recusa`→`refuses`, `nome`→`name`, `detalhe`→`detail`,
`excecao`→`exception`, `trecho`→`fragment`, `achado`→`found`,
`declarados`→`declared`, `sujo`→`dirty`, `sujeira`→`littered`,
`perdido`→`lost`, `laco`→`loop`, `antes`→`before`, `entrada`→`entry`,
`blocos`→`blocks`, `ruins`→`bad`, `rel`→`rep`, `marca`→`mark`), e os quatro
`origin` sintéticos (`<memoria>`→`<memory>`, `<sintetico>`→`<synthetic>`,
`<truncado>`→`<truncated>`, `<sem magic>`→`<no magic>`). A **API pública não
mudou**: `Card`, `DirectoryEntry`, `frame_checksum`, `next_frame`, `chain`,
`find_save`, `bad_checksums`, `stray_blocks`, `write`, `to_bytes`,
`synthetic_card`, `self_check` seguem como estavam.

Os trechos que o `refuses()` casa por substring foram traduzidos **no mesmo
movimento** que as mensagens: `"abaixo de 0x800"`→`"below 0x800"`,
`"passa do fim"`→`"past the end"`, `"negativo"`→`"negative"`,
`"bytes, e um memory card"`→`"bytes, and a PSX memory card"`,
`"nao e um memory card formatado"`→`"not a formatted memory card"`,
`"volta ao quadro"`→`"returns to frame"`, mais o
`state_name.startswith("em uso")`→`startswith("in use")`.

A §3.5 do plano perdeu o parágrafo da dívida aberta e o `perfil-mcr.md` perdeu
a oração da exceção.

**Medições:**

| gate | resultado |
|---|---|
| `--self-check` | **27 checks, 0 failures**, `rc=0`; duas corridas dão saída idêntica (`cmp`) |
| cinco controles negativos replantados | **5/5 vermelhos**, `rc=1`, falhas **2, 8, 1, 1, 1** — as mesmas contagens da corrida original |
| `--blocks` na fixture | blocos `[1, 2]`, 5844 e 6253 bytes não-zero, 41 no bloco 3 marcado fora da cadeia |
| `--json` | 7 chaves de topo, todas em inglês; `declared_size` 16.384, `first_block_offset` 8192 |
| `grep -inE 'quadro|cartao|escrita|recusa|falha' card.py` | vazio |
| Regra 1 (endereço só em `layout.py`) | nenhum dos 17 destinos (`0x5404`…`0x6500`) em `card.py` |
| Regra 3 (núcleo sem Qt) | `import card` não traz `PySide6` |
| `check_tasks.py` / `ctest -R tasks` | `100 task(s), ok` / `1/1 Passed` |
| fixture | digest inalterado, `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546` |

O controle 4 continua falhando **pela mensagem de magic**, que é o
comportamento documentado na MCR-TASK-04: com a checagem de tamanho desligada,
o buffer truncado passa a ser recusado pelo magic, e a asserção é sobre *qual*
recusa dispara.

**Problemas encontrados:**

**Um sítio que a CORR não listava**, achado pela varredura: a
[MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md), linha 47, dizia
que o `card.py` é "a exceção conhecida até a CORR-MCR-007 fechar" e que a
varredura de idioma "nasce sabendo disso". Como a CORR fechou antes daquela
task começar, a varredura nasce **sem lista de exceção** — a linha foi reescrita
nesse sentido.

Junto: a linha da CORR-MCR-007 na tabela do `correcoes-progresso.md` estava
separada da 006 por uma **linha em branco**, o que partia a tabela em duas e
deixava a 007 fora do corpo renderizado. Removida.

A nota datada de 2026-09-07 na MCR-TASK-04 — que preserva em português os
trechos casados pelos cinco controles — **ficou como está**: é evidência da
corrida que aconteceu, não texto a reindexar.

**Arquivos criados/modificados:**

- `tools/mcr/card.py` — tradução para en-US, sem mudança de API nem de
  comportamento
- `docs/PLAN-MCR-PY.md` — §3.5, o parágrafo da dívida aberta
- `docs/prompts/perfil-mcr.md` — a decisão de idioma e a verificação de Fase 1
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — linha 47 (discrepância da
  varredura)
- `docs/tasks/port-mcr/correcoes-progresso.md` — a linha em branco que partia a
  tabela
