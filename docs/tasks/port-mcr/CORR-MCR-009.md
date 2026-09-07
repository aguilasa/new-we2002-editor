---
id: CORR-MCR-009
title: "Correção: a tabela de controles da MCR-TASK-06 descreve o defeito em prosa, e duas das cinco contagens não reproduzem"
type: correção
category: verificação
status: pendente
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

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
