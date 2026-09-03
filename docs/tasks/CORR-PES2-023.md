---
id: CORR-PES2-023
title: "Correção: o perfil não tem verificações de Fase 0, diz que ela não tem task de trabalho, e conta seis fases onde há oito"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-PES2-023: a Fase 0 não tem verificações escritas no perfil

## Problema identificado

A seção "Verificações específicas por fase" do
[`perfil-pes2.md`](/docs/prompts/perfil-pes2.md) abre assim:

```markdown
As seis fases são as do [`PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §5, e o
quadro de tasks está no [`progresso.md`](/docs/tasks/progresso.md).

**Fases 0 e 1 — infra e diferencial barato — estão fechadas.** Não há task de
trabalho nelas; o que entregaram (o `iso.py`, o round-trip, o controle negativo,
o emulador, as âncoras `OFS_*` e o diff entre releases) é premissa das
seguintes. Revisar uma task que as toque significa conferir que a premissa não
foi quebrada, não reexecutá-las.
```

São três afirmações, e as três estão desatualizadas:

1. **"Não há task de trabalho nelas."** Há **quatro** tasks de Fase 0 no
   quadro — 01, 32, 33 e 34 —, e três delas entregaram ferramenta: a 32 o
   `savestate.py`, a 33 a compilação do fork e o achado do bug de 45 bytes, e
   a 34 o `mcp.py`, o `fork.py` e o `mcp_drive.py`, 1.734 linhas de Python
   novas num commit só. Isso não é "conferir que a premissa não foi quebrada".
2. **Não há lista de verificação para a Fase 0.** O `02-revisar.md` manda, na
   Etapa 3: *"Se o perfil não tiver entrada para essa fase, **diga isso na
   saída** em vez de improvisar — fase sem verificação escrita é achado, e
   vira CORR."* Esta é essa CORR. É o mesmo achado que a
   [CORR-PES2-017](/docs/tasks/CORR-PES2-017.md) cobrou para a Fase 7, e a
   Fase 0 já teve **três** tasks executadas — uma a mais do que a Fase 7 tinha
   quando aquela foi aberta.
3. **"As seis fases"** — a §5 do plano tem **oito**: Fase 0 a Fase 7. A
   contagem envelheceu quando a Fase 7 entrou, em 2026-09-01, e a
   CORR-PES2-017 acrescentou a seção de Fase 7 sem corrigir o número.

## Evidência

As fases do plano:

```
$ grep -n "^### Fase" docs/PLAN-PES2-PSX.md
1304:### Fase 0 — Infra
1381:### Fase 1 — Diferencial barato
1420:### Fase 2 — Inventário de texto
1455:### Fase 3 — O registro de jogador
1470:### Fase 4 — O resto do banco
1477:### Fase 5 — `pes2_map.json` e o leitor
1483:### Fase 6 — Editor
1488:### Fase 7 — Assets do disco
```

As seções de verificação que existem:

```
$ grep -n "^\*\*Fase" docs/prompts/perfil-pes2.md
248:**Fases 0 e 1 — infra e diferencial barato — estão fechadas.**
254:**Fase 2 (tasks 02 a 04) — inventário de texto:**
266:**Fase 3 (tasks 05 a 10) — o registro de jogador:**
278:**Fase 4 (tasks 11 a 16) — o resto do banco:**
286:**Fase 5 (tasks 17 a 21) — mapa e leitor:**
294:**Fase 6 (tasks 22 a 25) — editor:**
303:**Fase 7 (tasks 26 a 31) — os assets do disco:**
```

As tasks de Fase 0 no quadro:

```
$ grep -oE '\| [0-9]+ \|' docs/tasks/progresso.md | grep -c '| 0 |'
4
```

## Causa raiz

O parágrafo foi escrito quando a Fase 0 realmente não tinha task; as quatro
que apareceram desde então — decisões sobre o **ferramental da máquina**, que
é categoria diferente de "infra do disco" — não geraram entrada própria.

## Correção

### Arquivo: `docs/prompts/perfil-pes2.md`

Trocar "As seis fases" por "As oito fases", e substituir o parágrafo de
Fases 0 e 1 por: a Fase 1 continua fechada como está, e a Fase 0 ganha lista
própria. As perguntas saem do que as tasks 32, 33 e 34 mostraram valer:

```markdown
**Fase 1 — diferencial barato — está fechada.** O que ela entregou (as
âncoras `OFS_*` e o diff entre releases) é premissa das seguintes; revisar
uma task que a toque é conferir que a premissa não foi quebrada.

**Fase 0 (tasks 01, 32, 33, 34) — o ferramental da máquina:**

A fase não é sobre o disco: ela decide e constrói **com o que** se mede. Ela
foi reaberta duas vezes depois de "fechada", e é por isso que tem lista.

- A ferramenta nova tem `--self-check` que roda **sem** o recurso externo
  (sem emulador, sem imagem), e ele está dentro do `pes2_selftest`?
- O caso de recurso ausente diz o que fazer, ou despeja traceback? "o fork
  não está rodando" contra um `URLError` de `urllib`
- Todo número afirmado sobre a ferramenta externa foi contado **contra ela
  viva**, não contra o fonte dela? O `TOOLS_JSON` do fork declara 99 nomes e
  o `tools/list` devolve 95
- O binário de terceiro ficou **fora** do repositório, e a receita de
  reconstruí-lo é executável em vez de prosa num Log? (licença
  CC-BY-NC-ND-4.0, mesma regra de `roms/`)
- O gate que julga comportamento **diz contra qual binário** correu? São
  dois DuckStation, e eles não desenham a mesma tela
- Uma decisão de máquina (onde o binário mora, `.mcp.json`, configuração do
  emulador) foi **perguntada** ao dono da máquina, e não inventada?
- Toda asserção nova foi vista **ficando vermelha**, e existe um comando
  versionado que a leva ao estado em que ela pode ser exercitada?
```

O último item é o que a [CORR-PES2-024](/docs/tasks/CORR-PES2-024.md) cobra
no `--measure-menu`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [x] `grep -n "^\*\*Fase" docs/prompts/perfil-pes2.md` mostra entrada de
      Fase 0
- [x] `grep -n "seis fases" docs/prompts/perfil-pes2.md` não devolve nada
- [x] as fases da seção batem com `grep "^### Fase" docs/PLAN-PES2-PSX.md`
- [x] `python3 tools/check_tasks.py` continua verde

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-09-03

**Resumo do que foi feito:** as três afirmações desatualizadas foram
substituídas. "As seis fases" virou "As oito fases"; o parágrafo que juntava
Fases 0 e 1 foi partido — a **Fase 1** continua fechada e premissa, e a **Fase
0** ganhou lista própria de sete perguntas, saídas do que as tasks 32, 33 e 34
mostraram valer. O parágrafo da Fase 0 diz por que ela tem lista em vez de
virar premissa como a 1: foi dada por fechada e reaberta duas vezes, e as
tasks que entraram nela entregaram ferramenta.

Dois itens da lista citam a correção que os cobra, como a de Fase 7 já faz:
o do binário aponta para a CORR-PES2-021 (nem a mesma leitura se reproduz
entre dias no mesmo binário), e o do comando versionado até o estado, para a
CORR-PES2-024.

**Problemas encontrados:** a varredura de discrepância puxou **dois documentos
que a CORR não previa**, com a mesma afirmação envelhecida:

- `docs/tasks/progresso.md` (linha 93) — "Não há task de Fase 0 nem de Fase 1
  de trabalho", contradita duas linhas abaixo pelo próprio parágrafo;
- `CLAUDE.md` (linha 669) — "25 tasks nas seis fases do plano"; medido, são
  **34** tasks e o plano tem **oito** fases, das quais sete têm task.

Os dois foram reconciliados em **commit próprio**, como manda o rito.

**Gates:**

- `grep -n "^\*\*Fase" docs/prompts/perfil-pes2.md` → oito entradas, com a
  Fase 0 na linha 253
- `grep -n "seis fases" docs/prompts/perfil-pes2.md` → vazio
- as fases do perfil e as do plano batem (`diff` dos dois `grep` → idêntico)
- `python3 tools/check_tasks.py` → `check_tasks: 85 task(s), ok`

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-pes2.md` | modificado (a abertura de "Verificações específicas por fase") |
