---
id: PES2-TASK-18
title: "`pes2_map.json` — o mapa consolidado"
type: implementação
category: formato
phase: 5
depends_on: ["PES2-TASK-16", "PES2-TASK-17"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 5)"
status: pendente
---

# PES2-TASK-18: O mapa consolidado

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 5, primeiro item, e §4.4.
- **O mapa é o fonte.** A §4.4 é explícita: *"`pes2_map.json` é escrito à mão
  (ou por ferramenta de descoberta) e revisado; os headers, tabelas e código
  de leitura/gravação saem dele por gerador... Nunca o contrário."*
- **É também a primeira condição da definição de pronto** (§0): *"um
  `pes2_map.json` versionado que localize, para cada campo, o conjunto de
  cópias que precisam ser gravadas."*

---

## Objetivo

Um mapa único que cubra tudo que as Fases 2, 3 e 4 fecharam.

### O escopo mínimo, vindo da §0

> nomes de time, abreviações, nomes de jogador, atributos, formações,
> uniformes e bandeiras

Mais o que as tasks acrescentaram: elenco por time, e Master League.

### O que **não** entra

- campo mapeado "por analogia com o WE2002" e nunca verificado (§4.4, §6.9);
- conteúdo do disco. O mapa é **fato sobre o formato** — offset, tamanho,
  tipo. Tabela copiada literalmente de dentro da imagem é conteúdo de jogo
  comercial e cai na regra da §2: **não entra no git.**

Esta segunda distinção é fina e vale explicitar antes de escrever a primeira
linha: `"count": 106` é fato sobre o formato; a lista dos 106 nomes não é.

### Revisão

O mapa é escrito à mão e **revisado** — a §4.4 usa a palavra. A revisão é
contra o disco, pelo validador da PES2-TASK-17 mais um `--check` que
reconfere cada âncora, cada contagem e cada digest, nas **duas** releases.

---

## Critério de conclusão

- [ ] `pes2_map.json` versionado, validado pelo esquema.
- [ ] Toda entidade lógica com **conjunto de cópias** declarado e
      correspondência por conteúdo.
- [ ] `--check` verde nas duas releases: âncora, contagem e digest.
- [ ] Nenhum byte de conteúdo do jogo no arquivo.
- [ ] Lacunas declaradas, com a contagem de quantas são.
- [ ] Registrado no `check_image.py`.

---

## Log de Execução

*(a preencher)*
