---
id: CORR-LOOKS-004
title: "Correção: a LOOKS-TASK-18 se contradiz sobre as 50 tuplas em dois bullets seguidos"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-004: a LOOKS-TASK-18 se contradiz sobre as 50 tuplas em dois bullets seguidos

## Problema identificado

A LOOKS-TASK-01 mediu que a pasta de renders tem **50 arquivos e 49 tuplas** —
o quinquagésimo se chama `0.jpg` — e encaminhou o achado para a
`docs/tasks/looks/18-corpus-dos-cinquenta-renders.md`, que é quem vai contar
cobertura. O encaminhamento entrou como **bullets novos**, e o bullet antigo,
que diz o contrário, **ficou onde estava**:

```markdown
- `MCR\We DB - polipoli\Faces\` tem **50 JPGs**, nomeados pela tupla exata:
  `A-I3-A-F-A` é pele A, cabelo I3, cor A, barba F, cor de barba A.
- **O caminho é relativo a `Superpackv6\We2002\`, não à raiz da coletânea** …
- **São 50 arquivos, mas 49 tuplas.** O quinquagésimo se chama `0.jpg` e não
  tem tupla no nome …
```

O primeiro afirma que os cinquenta são nomeados pela tupla; o terceiro afirma
que quarenta e nove são. A §5.4 do plano — a `fonte_de_verdade` desta task —
foi corrigida na mesma execução e está certa: *"**50 JPGs**, dos quais **49
nomeados pela tupla exata**"*. Só a task ficou dizendo as duas coisas.

O efeito é o que o próprio encaminhamento queria evitar: quem executar a 18 lê
o `## Contexto` de cima para baixo e pode escrever o parser contra o primeiro
bullet — e um parser que exija tupla no nome quebra no `0.jpg`.

## Evidência

Contagem desta revisão:

```
$ ls "C:/games/we2002/Superpackv6/We2002/MCR/We DB - polipoli/Faces/" | wc -l
50
$ ls "…/Faces/" | grep -c '\.jpg$'
50
$ ls "…/Faces/" | head -2
0.jpg
A-A1-A-A-A.jpg
```

| onde | o que diz | certo? |
|---|---|---|
| `docs/PLAN-LOOKS-PY.md` §5.4 | 50 JPGs, 49 nomeados pela tupla | sim |
| `18-…md`, primeiro bullet do Contexto | 50 JPGs "nomeados pela tupla exata" | **não** |
| `18-…md`, terceiro bullet do Contexto | 50 arquivos, 49 tuplas | sim |

## Causa raiz

O achado foi acrescentado por bullet novo em vez de corrigir a frase que ele
desmente.

## Correção

### Arquivo: `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md`

Reescrever o primeiro bullet do `## Contexto` na forma que a §5.4 já usa — 50
JPGs, dos quais 49 nomeados pela tupla exata — mantendo o exemplo
`A-I3-A-F-A`. Os bullets do caminho e do `0.jpg` continuam como estão: eles
detalham, e agora não contradizem nada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` | modificar |

## Verificação

- [ ] nenhuma frase da task afirma que os 50 têm tupla
- [ ] o critério de conclusão continua exigindo veredito escrito para o `0.jpg`
- [ ] `python tools/check_tasks.py` verde
- [ ] a conferência de links do `.claude/rules/links.md` sai vazia

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
