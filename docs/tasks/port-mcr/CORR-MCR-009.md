---
id: CORR-MCR-009
title: "Correção: a tabela de controles da MCR-TASK-06 descreve o defeito em prosa, e duas das cinco contagens não reproduzem"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-MCR-009: o estímulo dos controles negativos não está versionado

## Problema identificado

O Log da [MCR-TASK-06](/docs/tasks/port-mcr/06-codec-de-atributos.md) registra
cinco controles negativos com o número de falhas que cada um produz. Os
**vereditos** todos reproduzem — 5/5 vermelhos, `rc=1` —, e as três contagens
de blobs divergentes batem **exatamente**: 87.484, 100.000 e 93.748. Mas duas
das cinco **contagens de falha** não reproduzem a partir da descrição:

| controle | Log | remedido nesta revisão |
|---|---:|---:|
| `speed`/`dribbling` trocados no encoder | **4 falhas** | **2 falhas** (87.484 ✓) |
| tirar o `-1` do dorsal no `encode_masks` | 2 falhas | 2 ✓ (100.000 ✓) |
| mover `stamina` um bit | **6 falhas** | **5 falhas** (o `GAP_BITS` denuncia ✓) |
| gravar a partir de buffer zerado | 2 falhas | 2 ✓ (93.748 ✓) |
| `bias=11` no `jump` | 2 falhas | 2 ✓ (os 23 registros divergem ✓) |

A causa não é o módulo: é que **o defeito plantado está descrito em prosa, não
como a edição exata**. "Trocar `speed` e `dribbling` no encoder" tem pelo menos
três leituras — escrever `speed` no lugar de `dribbling`; trocar os dois lados;
trocar também no `encode_stream`, que é dirigido por tabela e onde a troca
mudaria o *decoder* junto. Cada leitura dá uma contagem diferente, e o
`encode_stream` sequer aceita a troca sem virar outro defeito.

É a mesma lição que o ciclo já pagou no `newWe2002` e que o `CLAUDE.md`
registra para os golden: *"verde de golden é asserção sobre um estímulo: sem o
estímulo versionado a corrida não é repetível, e o par verde+faixa vira
lembrança."* Aqui é vermelho em vez de verde, e vale igual — um controle que
não se reproduz deixa de ser controle na primeira vez que alguém tenta repeti-lo.

## Evidência

Os cinco controles replantados numa cópia temporária dentro da árvore, com
`PYTHONPATH` apontando `tools/mcr` (sem isso a cópia não importa `layout` e
morre antes de medir):

```
1) speed/dribbling trocados nos DOIS lados do encode_masks
  FAIL  100,000 blobs: encode_masks(decode_masks(b)) == b  differ=87484
  FAIL  100,000 blobs: the two encoders agree byte for byte  differ=87484
attributes.py: 2 failure(s)

3) Field("stamina", 49, ...) -> Field("stamina", 50, ...)
  FAIL  fields do not overlap and stay inside 96 bits
  FAIL  4 bits belong to no field  gaps=(3, 12, 16, 45, 49)
  FAIL  the gaps are where the measurement puts them  gaps=(3, 12, 16, 45, 49)
  FAIL  100,000 blobs: stream and masks decode the same  differ=87346
  FAIL  the 23 records decode the same both ways  differ at [0..22]
attributes.py: 5 failure(s)

4) r = bytearray(blob) -> r = bytearray(12)
  FAIL  100,000 blobs: encode_masks(decode_masks(b)) == b  differ=93748
  FAIL  100,000 blobs: the two encoders agree byte for byte  differ=93748
attributes.py: 2 failure(s)
```

Tudo o mais que a task afirma remediu exato, e um pedaço foi conferido **fora**
da ferramenta:

- **29 campos**, e o conjunto de `FIELDS` é **idêntico** ao de
  `Player::Decode()` nos dois sentidos;
- as 29 expressões de `Player::Decode` transcritas à mão nesta revisão, num
  decodificador independente, dão **0 divergências em 100.000 blobs** contra o
  `attributes.decode`;
- a tripwire remedida com leitor próprio: `1 + ((raw[3]>>2)&0x1f)` contra a
  tabela de `0x5404` lida como `(5·(j mod 6))` bits num inteiro little-endian
  de 4 bytes por grupo — **23/23**, e a sequência é a mesma que a §1.5
  registra;
- `GAP_BITS = (3, 12, 16, 45)`;
- três das 21 tabelas de peso do upstream lidas direto do
  `lite/fifatomcr/Frmmcr.designer.vb`: `idage` são 32 valores `0..992` =
  `i<<5`, `idskincolor` são `0..3`, `idbodybalance` são `0..448` = `i<<6`.

## Causa raiz

O defeito plantado foi anotado pelo efeito pretendido, não pela substituição
literal que o produz.

## Correção

### Arquivo: `docs/tasks/port-mcr/06-codec-de-atributos.md`

Na tabela dos cinco controles, trocar a descrição pela **edição exata** —
a linha de origem e a de destino —, e reconciliar as duas contagens com o que a
edição escrita produz. Por exemplo, para o primeiro:

```markdown
| `r[6] |= ((v["speed"]-12) << 7) & 0xFF` → `dribbling`, `r[7] |= (v["speed"]-12) >> 1` → `dribbling`, e `r[6] |= (v["dribbling"]-12) << 4` → `speed` (o bug da v4.2, nos dois lados do `encode_masks`) | 🔴 2 falhas, 87.484/100.000 blobs divergindo |
```

Acrescentar também a nota de operação, que custou tempo nesta revisão:

```markdown
> A cópia plantada precisa de `PYTHONPATH` apontando `tools/mcr`: o módulo
> importa `layout`, e fora da pasta ele não resolve — a corrida morre em
> `ModuleNotFoundError` antes de medir qualquer coisa, o que parece defeito do
> controle e não é.
```

### Onde isso deixa de ser prosa

A [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) monta o
`selftest` e o CLI. Se os controles virarem **um subcomando** — plantar,
rodar, exigir o vermelho — em vez de prosa numa tabela, a contagem passa a ser
medida por comando em vez de anotada à mão. Vale uma linha no critério dela; a
decisão de fazê-lo agora ou não é de quem executar a 10.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/port-mcr/06-codec-de-atributos.md` | modificar |
| `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` | modificar (a linha do subcomando de controles) |

## Verificação

- [ ] cada linha da tabela de controles nomeia a substituição literal, e
      replantar exatamente aquilo devolve o número de falhas escrito ao lado
- [ ] `WE2002_MCR_CARD=work/mcr-entrada.mcr python3 tools/mcr/attributes.py
      --self-check` continua **22 checks, 0 falhas**, e duas corridas dão bytes
      iguais
- [ ] sem `WE2002_MCR_CARD` a corrida continua verde, com os checks da fixture
      em `skip`
- [ ] `python3 tools/mcr/attributes.py --upstream-weights work/easy-mcr`
      continua `21/21`
- [ ] `python3 tools/mcr/layout.py --rule1` continua `0`, e importar
      `attributes` não traz `PySide6`
- [ ] `roms/` e `work/entrada.mcr` intocados — o digest continua
      `e53f4895affe075bced499a32ba736d10a20f72b010c9c8c05c1269e77c47546`

## Log de Execução

**Executado em:** 2026-09-07

**Resumo do que foi feito:**

A tabela dos cinco controles da MCR-TASK-06 passou a dizer a **substituição
literal** de cada defeito — linha de origem e de destino — em vez do efeito
pretendido, e as duas contagens que não reproduziam foram reconciliadas com o
que a edição escrita produz: o `speed`/`dribbling` dá **2** falhas (não 4) e o
`stamina` movido dá **5** (não 6). O cabeçalho da seção diz por que a mudança
importa: "trocar dois campos no encoder" tem mais de uma leitura, e cada leitura
dá uma contagem diferente.

Entrou também a nota **"Como replantar"**, e a MCR-TASK-10 ganhou o item de
decidir se o subcomando `negative` planta os controles em vez de descrevê-los —
onde a contagem passa a ser medida por comando em vez de anotada à mão.

`tools/mcr/attributes.py` **não foi tocado**: o defeito era do registro, não do
módulo.

**Medições — os cinco controles replantados da raiz do repositório, com
`PYTHONPATH=tools/mcr` e `WE2002_MCR_CARD=work/mcr-entrada.mcr`:**

| substituição | `rc` | falhas | divergência |
|---|---:|---:|---|
| `speed`/`dribbling` nos dois lados do `encode_masks` | 1 | **2** | 87.484/100.000 |
| `r[3] \|= (v["number"] - 1) << 2` → sem o `-1` | 1 | 2 | 100.000/100.000 |
| `Field("stamina", 49, …)` → `50` | 1 | **5** | `gaps=(3, 12, 16, 45, 49)`, 87.346 |
| `r = bytearray(blob)` → `bytearray(12)` | 1 | 2 | 93.748/100.000 |
| `Field("jump", 82, 3, bias=12)` → `bias=11` | 1 | 2 | 100.000/100.000 |

**5/5 vermelhos.** As três contagens de blob que o Log já trazia — 87.484,
100.000, 93.748 — bateram exatamente, como a CORR afirma.

Os demais gates:

| gate | resultado |
|---|---|
| `attributes.py --self-check` com fixture | **22 checks, 0 falhas**; duas corridas byte-idênticas |
| idem sem `WE2002_MCR_CARD` | 0 falhas, com o check da fixture em `skip` |
| `--upstream-weights work/easy-mcr` | `21/21` |
| `layout.py --rule1` | `0 address(es) outside layout.py` |
| `import attributes` | não traz `PySide6` |
| `check_tasks.py` / `ctest -R tasks` | `100 task(s), ok` / `1/1 Passed` |
| fixture | `e53f4895…`, inalterada |

**Problemas encontrados:**

**Uma armadilha de replantação a mais que a CORR não previa**, e que é irmã da
que a [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md) achou no `layout.py`:
a tabela dizia "numa cópia em `/tmp`", e de `/tmp` a corrida **roda** — mas o
check das 21 tabelas de peso vira `skip  the upstream weight tables (no
work/easy-mcr)` **em silêncio**, e a corrida reporta `0 failure(s)` numa
dimensão que não foi medida. O `PYTHONPATH` que a CORR pede também foi
confirmado: sem ele, `ModuleNotFoundError: No module named 'layout'` antes de
qualquer medição. As duas foram para a nota "Como replantar".

A citação equivalente da MCR-TASK-04 (`/tmp`, para o `card.py`) continua certa
e ficou como está: aquele módulo não importa `layout` nem lê `work/easy-mcr`.

**Arquivos criados/modificados:**

- `docs/tasks/port-mcr/06-codec-de-atributos.md` — a tabela dos cinco controles
  e a nota "Como replantar"
- `docs/tasks/port-mcr/10-selftest-cli-e-gate.md` — o item do subcomando
  `negative`
