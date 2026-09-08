---
id: CORR-MCR-021
title: "Correção: a tabela \"Estado medido\" do ciclo ficou em 16/16 controles enquanto a ferramenta imprime 20 de 20 — a task de fechamento não a reconciliou"
type: correção
category: processo
status: concluído
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

- [x] `grep -n "16/16" docs/tasks/port-mcr/progresso.md` sai vazio
- [x] o que a linha cita é a última linha de `python3 tools/mcr/controls.py`,
      palavra por palavra
- [x] `python3 tools/mcr/controls.py` continua **20 de 20 vermelhos**, com e
      sem fixture, e o `--self-check` do `controls.py` continua verde
- [x] se a varredura for escrita: com um `16/16` plantado num doc do ciclo,
      `controls.py --self-check` sai `rc=1` nomeando o arquivo e a linha
- [x] `WE2002_MCR_CARD=… ctest -R 'tasks|mcr'` = **4 de 4**
- [x] `python3 tools/check_tasks.py` verde
- [x] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução

**Executado em:** 2026-09-08

**Resumo do que foi feito:**

O sintoma reproduziu exato: a linha 159 dizia `16/16 vermelhos … quinze por
substituição literal`, e `controls.py` imprime
`controls: 20 of 20 red (19 substitutions, 1 new file)`, com
`len(controls.CONTROLS) == 20`.

Fiz as **duas** metades da CORR, e a segunda é a que fecha. A linha do
`progresso.md` passou a citar a última linha do comando **palavra por palavra**
em vez de repetir um número — quem rodar compara duas frases iguais, não um
número solto contra outro. E o `controls.py --self-check` ganhou a varredura:
`count_sweep()` lê os documentos **vivos** do ciclo e recusa qualquer
`N/N red` ou `N/N vermelhos` que não bata com `len(CONTROLS)`. É a forma da
`layout.address_monopoly()` e da `glossary.sweep()` — uma varredura que recusa,
no lugar de uma convenção que alguém tem de lembrar.

**Só os documentos vivos são varridos**, e a escolha é deliberada: um Log de
task que diz "15/15 vermelhas" é o registro do que **aquela** corrida mediu, e
reescrevê-lo falsificaria a evidência — o ciclo já trata citação datada assim.
O que não pode envelhecer é o estado que o leitor toma como atual: a tabela
"Estado medido" do `progresso.md` e o perfil, que é o que os comandos leem
antes de rodar qualquer coisa. Documento ausente é **pulado**, não acusado: os
sandboxes plantados pelo `plant()` carregam `tools/mcr` e pouco mais, e uma
queixa ali seria sobre o sandbox.

**Problemas encontrados:**

**1. A varredura achou uma segunda cópia velha, no arquivo cujo conserto foi
justamente parar de copiar.** O perfil, na linha que a
[CORR-MCR-017](/docs/tasks/port-mcr/CORR-MCR-017.md) escreveu como exemplo do
"hoje", dizia `controls: 16 of 16 red (15 substitutions, 1 new file)` — velha
pelas mesmas quatro tasks. Ela **fica**, porque citar a linha inteira é o que
torna a divergência visível; o que mudou é que agora ela é conferida por
máquina, e o parágrafo diz isso.

**2. O meu próprio comentário fez o módulo falhar na varredura de idioma.** Eu
escrevi "Estado medido" em inglês corrente para nomear a tabela, e `medido`
está no dicionário do `glossary.py`: `controls.py:223`, uma queixa, `selftest`
com 2 falhas. Reescrito como "the *measured state* table of the cycle's
progress file". É a §3.5 pegando exatamente o que ela existe para pegar, num
comentário sobre documentos em português.

**3. Uma falha de `mcr_card` que não reproduziu, e que não sei explicar.** Na
primeira corrida de `ctest -R 'tasks|mcr'` depois do conserto ele saiu
`***Failed` em 0,07 s — não é estouro de tempo, o limite é 600 s. Rodado
sozinho na sequência, passou; e em **seis** corridas seguidas da mesma seleção,
4 de 4 todas as vezes. Não capturei a saída daquela corrida — o `grep` que
escrevi descartou tudo menos as linhas de resumo —, então não tenho evidência
para atribuir causa, e prefiro registrar isso a inventar uma. Fica anotado: se
voltar, a primeira coisa é `--output-on-failure`.

**Medições:**

| gate | número |
|---|---|
| `controls.py`, com e sem cartão | **20 of 20 red (19 substitutions, 1 new file)**, idêntico |
| a linha citada nos dois documentos | bate **palavra por palavra** com a saída (1 ocorrência em cada) |
| `controls.py --self-check` | **8 checks** (eram 6), `0 failure(s)` |
| a varredura, antes do conserto | **2** queixas: `progresso.md:159` e `perfil-mcr.md:161` |
| o caso vermelho da varredura | com `16/16 vermelhos` plantado numa cópia, ela acusa e **nomeia o arquivo** |
| `grep -n "16/16" progresso.md` | **vazio** |
| `selftest.py` | `0 failure(s)` sobre 12 módulos |
| `glossary.py` / `layout.py --rule1` | **0** queixas / **0** endereços |
| `ctest -R 'tasks\|mcr'` | **4 de 4**, em 6 corridas — uma sétima, a primeira, teve a falha do item 3 |
| `make test` | **10/10** |
| `check_tasks.py` | `100 task(s), ok` |
| fixture / `roms/` | `sha256 e53f4895…c47546`, intocada; `roms/` sem alteração |

**Arquivos criados/modificados:**

- `tools/mcr/controls.py` — `LIVE_DOCS`, `count_sweep()`, os dois checks novos
  (a varredura e o caso vermelho dela)
- `docs/tasks/port-mcr/progresso.md` — a linha dos controles aponta para a saída
- `docs/prompts/perfil-mcr.md` — o exemplo atualizado, e a frase que diz que
  agora há varredura (varredura de discrepância)
