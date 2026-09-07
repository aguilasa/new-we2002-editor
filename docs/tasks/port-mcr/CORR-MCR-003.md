---
id: CORR-MCR-003
title: "Correção: o link do `progresso.md` no `correcoes-progresso.template.md` não leva o segmento do ciclo"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-003: o template aponta para o progresso do ciclo raso

## Problema identificado

O critério da MCR-TASK-01 pedia *"os dois `*.template.md` com o segmento de
ciclo nos links de exemplo, … e o `progresso.md` do link é o **ao lado deste
arquivo**"*.

Em `docs/tasks/correcoes-progresso.template.md` a **prosa** ficou certa e o
**link** não:

```markdown
Correções abertas pelo `/revisar` ([`../prompts/02-revisar.md`](/docs/prompts/02-revisar.md))
e fechadas pelo `/corrigir`. O andamento das **tarefas** fica em
[`progresso.md`](/docs/tasks/progresso.md) — o que mora **ao lado deste
arquivo**, na mesma pasta; este arquivo só rastreia correção.
```

O destino é `/docs/tasks/progresso.md` — o ciclo **raso**, hoje o de PES2. Num
ciclo em subpasta o link contradiz a própria frase ao lado dele e aponta para o
progresso de outro ciclo. Todos os demais links do mesmo arquivo já levam o
segmento (`/docs/tasks/<CICLO>/CORR-<PREFIXO>-001.md`), e o instanciado deste
ciclo — `docs/tasks/port-mcr/correcoes-progresso.md` — escreve corretamente
`/docs/tasks/port-mcr/progresso.md`. Só o molde ficou para trás.

## Evidência

O molde:

```
$ grep -n 'progresso.md](' docs/tasks/correcoes-progresso.template.md
3:[`progresso.md`](/docs/tasks/progresso.md) — o que mora **ao lado deste
```

O que sai dele quando o ciclo mora numa subpasta, escrito à mão nesta ocasião:

```
$ grep -n 'progresso.md](' docs/tasks/port-mcr/correcoes-progresso.md
4:[`progresso.md`](/docs/tasks/port-mcr/progresso.md).
```

A conferência de existência de `.claude/rules/links.md` **não pega isto**: os
`*.template.md` estão excluídos dela de propósito, e o destino existe de
qualquer forma — ele só é o arquivo errado.

## Causa raiz

A varredura do template alcançou os links da tabela de exemplo, que ganharam
`<CICLO>/`, e não o link em prosa do cabeçalho.

## Correção

### Arquivo: `docs/tasks/correcoes-progresso.template.md`

Levar o link do cabeçalho à mesma forma dos demais do arquivo:

O destino do link do cabeçalho passa a ser
`/docs/tasks/<CICLO>/progresso.md` — a mesma forma dos demais links do arquivo
—, com a frase ao lado dele intacta:

> `…fica em [progresso.md] apontando para /docs/tasks/<CICLO>/progresso.md — o
> que mora **ao lado deste arquivo**, na mesma pasta…`

*(o alvo está escrito fora da sintaxe de link de propósito: a conferência de
existência de `.claude/rules/links.md` é um `grep` de texto e não distingue
transcrição de link vivo — é o caso que a própria regra prevê para os `CORR-*`
de ciclo vivo.)*

O comentário que já existe logo abaixo (`<!-- `<CICLO>/` nos links some quando o
ciclo e raso… -->`) cobre o caso raso sem texto novo.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/correcoes-progresso.template.md` | modificar |

## Verificação

- [ ] `grep -n 'progresso.md](' docs/tasks/correcoes-progresso.template.md`
      mostra o segmento `<CICLO>/`
- [ ] a conferência de **forma** de link de `.claude/rules/links.md` continua
      sem sítio novo
- [ ] `python3 tools/check_tasks.py` verde e `ctest -R tasks` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

O link do cabeçalho de `docs/tasks/correcoes-progresso.template.md` passou a
levar o segmento do ciclo, como os demais links do mesmo arquivo. A frase ao
lado dele — "o que mora **ao lado deste arquivo**, na mesma pasta" — ficou
intacta, e agora o link concorda com ela; o comentário logo abaixo já cobre o
caso raso, em que o segmento some.

A varredura alcançou o gêmeo: `docs/tasks/progresso.template.md:192` — a linha
de exemplo do "outro projeto no mesmo progresso" — tinha ficado sem o `<CICLO>/`
que as linhas 34 e 35 do mesmo arquivo ganharam na MCR-TASK-01. Mesma classe de
esquecimento, corrigida na mesma passagem.

**Problemas encontrados:**

O `grep` escrito na seção Evidência da CORR (`grep -n 'progresso.md](' …`) sai
vazio: o texto real tem uma crase entre `progresso.md` e o `]`. O padrão que
mede é `progresso.md\`](`. A linha também é a **5**, não a 3. O sintoma em si
está confirmado, e é o descrito.

**Arquivos criados/modificados:**

- `docs/tasks/correcoes-progresso.template.md` — o link do cabeçalho
- `docs/tasks/progresso.template.md` — linha 192 (discrepância da varredura)
