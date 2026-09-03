---
id: CORR-PES2-028
title: "Correção: o fork publica binário próprio, e o AppImage dele traz o servidor MCP"
type: correção
category: ferramental
status: pendente
depends_on: []
---

# CORR-PES2-028: "não publica binário próprio" é falso, e o binário publicado tem o MCP

## Problema identificado

Dois documentos vivos afirmam que o fork não publica binário, e a afirmação
sustentou a conta de custo que decidiu, em 2026-09-02, **não** adotá-lo.

Na §6.14 do [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md):

> O fork tem **3 estrelas e 0 forks** e **não publica binário próprio** — a
> página de releases que o README aponta é a do *upstream*
> `stenzek/duckstation`, que é justamente o build sem o servidor; reconferido
> em 2026-09-02, 12.330 commits na branch `mcp`.

E no critério de conclusão da
[PES2-TASK-32](/docs/tasks/32-poc-do-mcp-do-duckstation.md):

> `sadnescity/duckstation` tem 3 estrelas, 0 forks, 12.330 commits na branch
> `mcp`, e **nenhuma release própria** — a página que o README aponta é a do
> upstream `stenzek/duckstation`, que é justamente o build sem o servidor.

Três dos quatro números batem. O quarto não: o repositório **tem** uma
release própria, com quatorze binários construídos pelo CI dele, entre eles
um `DuckStation-x64.AppImage` de 93 MB — e esse AppImage **carrega o servidor
MCP**.

O que isso muda:

- a premissa de custo estava errada duas vezes. A PES2-TASK-33 já a derrubou
  de "dias" para **107 s de compilação**; o custo real de obter um binário
  com MCP é **um download**;
- o `fork.py recipe` documenta só o caminho de clonar e compilar, que passa a
  ser o caminho caro entre dois;
- a frase "a página que o README aponta é a do upstream" continua verdadeira
  e é justamente o que **enganou**: o README é o do upstream, intocado, e a
  aba de releases do próprio fork nunca foi consultada.

Nada disto reverte decisão nenhuma — o fork já é o binário de trabalho desde
2026-09-03. O que está errado é o fato escrito em dois documentos, e a
receita que só conhece o caminho longo.

## Evidência

A release existe, é do CI do fork, e é de 2026-08-29 — quatro dias antes da
avaliação que disse que ela não existia:

```
$ gh api repos/sadnescity/duckstation/releases --jq 'length'
1
$ gh api repos/sadnescity/duckstation/releases/tags/latest \
    --jq '{tag:.tag_name,name:.name,author:.author.login,published:.published_at}'
{"tag":"latest","name":"Latest Build","author":"github-actions[bot]",
 "published":"2026-08-29T17:20:32Z"}
```

Quatorze ativos, com AppImage de Linux x64:

```
DuckStation-x64.AppImage        93237536
DuckStation-x64-SSE2.AppImage   93229344
DuckStation-arm64.AppImage      85102848
… mais Windows x64/ARM64 e macOS
```

E ele traz o servidor — o mesmo teste de `strings` que a §6.14 usou para
mostrar que o AppImage **oficial** não o tinha:

```
$ gh release download latest --repo sadnescity/duckstation \
      --pattern 'DuckStation-x64.AppImage'
$ ./DuckStation-x64.AppImage --appimage-extract
$ for s in EnableMCPServer MCPServerPort duckstation-mcp memory_scan snapshot_memory; do
      printf "%-18s " "$s"; strings -a squashfs-root/usr/bin/duckstation-qt | grep -cx "$s"; done
EnableMCPServer    1
MCPServerPort      1
duckstation-mcp    1
memory_scan        1
snapshot_memory    1
```

Os outros três números foram reconferidos e continuam certos:

```
$ gh api repos/sadnescity/duckstation --jq '{stars,forks:.forks_count,default:.default_branch}'
{"default":"mcp","forks":0,"stars":3}
$ gh api "repos/…/commits?sha=mcp&per_page=1" -i | grep -oE 'page=[0-9]+>; rel="last"'
page=12330>; rel="last"
```

## Causa raiz

A avaliação leu o **README** do fork — que é o do upstream, intocado, e por
isso aponta para as releases do upstream — e concluiu dali que o fork não
publica nada. A aba de releases do próprio repositório nunca foi consultada,
e é onde o CI dele deposita os quatorze binários a cada push.

## Correção

### Arquivo: `docs/PLAN-PES2-PSX.md`, §6.14

Corrigir a frase nos dois lugares em que a seção a repete, e registrar o que
o erro ensina, que é a parte útil:

```markdown
O fork tem **3 estrelas e 0 forks**, e **publica binário próprio** — o CI dele
deposita quatorze ativos na release `latest`, entre eles um
`DuckStation-x64.AppImage` cujo `duckstation-qt` traz `EnableMCPServer`,
`MCPServerPort` e os nomes de ferramenta do servidor (medido em 2026-09-03).
O **README** dele é o do upstream, intocado, e por isso aponta para as
releases do `stenzek/duckstation`, que são o build sem o servidor: ler o
README e concluir que não há binário do fork foi o engano de 2026-09-02, e o
custo de obtê-lo nunca foi de dias nem de 107 s, mas de um download.
```

### Arquivo: `tools/pes2/fork.py`, `recipe`

Pôr o caminho barato **primeiro**, mantendo a compilação como a alternativa
de quem quer o fonte:

```
Getting the fork -- two ways, cheapest first.

  1. Download the build its own CI publishes (measured 2026-09-03: it
     carries the MCP server):

       gh release download latest --repo sadnescity/duckstation \
          --pattern 'DuckStation-x64.AppImage'

     Confirm before trusting it:
       strings -a <the extracted duckstation-qt> | grep -x EnableMCPServer

  2. Build it -- 107 s on this machine, and what you want if you need the
     source: [a receita atual, sem mudança]
```

A conferência por `strings` é parte da receita, não enfeite: a release é
reconstruída a cada push, e nada garante que o próximo build ainda traga o
servidor.

### Arquivo: `docs/tasks/32-poc-do-mcp-do-duckstation.md`

O critério de conclusão diz "nenhuma release própria". Anotar a correção
datada ao lado, como o Log já faz com os 45 bytes — a task está concluída, e
o que se corrige é o registro, não o resultado.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-PES2-PSX.md` | modificar |
| `tools/pes2/fork.py` | modificar |
| `docs/tasks/32-poc-do-mcp-do-duckstation.md` | modificar |

## Verificação

- [ ] `grep -rn "não publica binário próprio\|nenhuma release própria" docs/ | grep -v concluidos`
      só devolve menção histórica datada
- [ ] `python3 tools/pes2/fork.py recipe` imprime os dois caminhos, o de
      download primeiro, com a conferência por `strings`
- [ ] `python3 tools/pes2/fork.py --self-check` verde — os dois casos que
      cobram a receita (nomear a licença e o diretório de instalação)
      continuam passando
- [ ] `ctest --test-dir build -R pes2_selftest` verde
- [ ] nada do fork versionado; o AppImage baixado não fica no repositório

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
