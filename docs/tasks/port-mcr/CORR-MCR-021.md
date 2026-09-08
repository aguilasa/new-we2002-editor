---
id: CORR-MCR-021
title: "Correção: a tabela \"Estado medido\" do ciclo ficou em 16/16 controles enquanto a ferramenta imprime 20 de 20 — a task de fechamento não a reconciliou"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-MCR-021: o número que a CORR-MCR-017 tirou do perfil continuou no progresso

## Problema identificado

A linha 159 do `progresso.md` — dentro da tabela **"Estado medido"**, que é
onde o ciclo guarda o que foi medido contra a fixture — diz:

> | Controles negativos | **16/16 vermelhos**, com e sem fixture: **quinze** por
> substituição literal, um que cria um arquivo uma pasta abaixo.
> `python3 tools/mcr/controls.py` |

A ferramenta que a própria linha manda rodar diz outra coisa:

```
$ python3 tools/mcr/controls.py | tail -1
controls: 20 of 20 red (19 substitutions, 1 new file)
```

Quatro a menos, e o tipo também: **19** substituições, não quinze.

**A MCR-TASK-14 é a task de fechamento**, e o critério dela é reconciliar o que
os documentos afirmam com o que as ferramentas medem. Ela reconciliou seis
seções do plano, o `CLAUDE.md`, o `NOTICE.md` e o perfil, e **atualizou duas
linhas desta mesma tabela** — a de `0x6500` e a de "Cobradores", as duas com o
que a MCR-TASK-13 mediu. A linha dos controles ficou.

**E é exatamente a falha que a [CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md)
previu.** O conserto dela foi fazer o `controls.py` **imprimir** o total por
tipo, e o perfil passou a apontar para a saída em vez de copiar o número:

> `mcr_selftest` … **e os controles negativos, todos exigidos vermelhos** —
> **quantos são, e de que tipo, é o que a última linha do `controls.py`
> imprime**

O `progresso.md` continua copiando. A contagem subiu de 16 para 19 na
MCR-TASK-12 (três controles novos) e para 20 na MCR-TASK-13
(`formation-captain-not-written`), e nenhuma das duas passou por aqui.

O custo é o de sempre para número em prosa: quem revisar o ciclo lê 16, mede
20, e gasta a corrida decidindo qual dos dois está errado — que foi o que esta
revisão fez.

## Evidência

```
$ python3 tools/mcr/controls.py | tail -1
controls: 20 of 20 red (19 substitutions, 1 new file)

$ PYTHONPATH=tools/mcr python3 -c "import controls; print(len(controls.CONTROLS))"
20

$ grep -n "Controles negativos" docs/tasks/port-mcr/progresso.md
159:| Controles negativos | **16/16 vermelhos**, com e sem fixture: quinze por substituição literal, um que cria um arquivo uma pasta abaixo. `python3 tools/mcr/controls.py` |
```

A história dos quatro que faltam, toda ela dentro deste ciclo:

| quando | controle | total |
|---|---|---|
| MCR-TASK-11 | `ui-imports-an-address` | 16 |
| MCR-TASK-12 | `ui-writes-from-two-places`, `model-store-skips-the-model`, `mcrio-copy-target-is-the-original` | 19 |
| MCR-TASK-13 | `formation-captain-not-written` | 20 |

E o perfil, no mesmo dia, já não copia:

```
$ grep -n "controles negativos, todos exigidos" docs/prompts/perfil-mcr.md
142:… quantos são, e de que tipo, é o que a última linha do `controls.py` imprime …
```

Os controles estão **certos** — 20 de 20 vermelhos, com e sem fixture, nesta
revisão. O defeito é só do número escrito ao lado.

## Causa raiz

A CORR-MCR-017 tirou o número copiado do perfil e não do `progresso.md`, que
tem uma cópia própria na tabela "Estado medido".

## Correção

### Arquivo: `docs/tasks/port-mcr/progresso.md`

Aplicar aqui o mesmo conserto que o perfil recebeu — apontar para a saída em
vez de repetir o total:

```markdown
| Controles negativos | **todos vermelhos**, com e sem fixture. Quantos são, e
de que tipo, é o que a última linha do `controls.py` imprime — hoje
`controls: 20 of 20 red (19 substitutions, 1 new file)`, e o número sobe a cada
task que acrescenta um. `python3 tools/mcr/controls.py` |
```

Citar a linha inteira que a ferramenta imprime, e não só o número, é o que
torna a divergência visível na próxima leitura: quem rodar o comando compara
duas frases idênticas, não um número solto contra outro.

### E a varredura que fecha isto de vez

Enquanto o total for prosa em algum lugar, ele envelhece. O barato é o
`controls.py --self-check` ganhar um check que **varre os documentos do ciclo**
atrás de um `N/N ... red` ou `N/N vermelhos` e exige que qualquer número
encontrado bata com `len(CONTROLS)`. É a mesma forma da
`layout.address_monopoly()` e da `glossary.sweep()`: uma varredura que recusa o
que não devia estar ali, em vez de uma convenção que se lembra de atualizar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/progresso.md` | modificar |
| `tools/mcr/controls.py` | modificar (a varredura, opcional mas é o que fecha) |

## Verificação

- [ ] `grep -n "16/16" docs/tasks/port-mcr/progresso.md` sai vazio
- [ ] o que a linha cita é a última linha de `python3 tools/mcr/controls.py`,
      palavra por palavra
- [ ] `python3 tools/mcr/controls.py` continua **20 de 20 vermelhos**, com e
      sem fixture, e o `--self-check` do `controls.py` continua verde
- [ ] se a varredura for escrita: com um `16/16` plantado num doc do ciclo,
      `controls.py --self-check` sai `rc=1` nomeando o arquivo e a linha
- [ ] `WE2002_MCR_CARD=… ctest -R 'tasks|mcr'` = **4 de 4**
- [ ] `python3 tools/check_tasks.py` verde
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
