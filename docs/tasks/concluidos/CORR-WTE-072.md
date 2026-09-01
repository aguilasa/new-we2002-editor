---
id: CORR-WTE-072
title: "Correção: gravacao-controle.md fecha com a premissa que a WTE-TASK-28 refutou"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-072: `gravacao-controle.md` fecha com a premissa que a WTE-TASK-28 refutou

## Problema identificado

O último parágrafo de [`wte/re/gravacao-controle.md`](../../../wte/re/gravacao-controle.md)
— **gerado** por [`wte/tools/gravacao_controle.py`](../../../wte/tools/gravacao_controle.py),
linhas 321-324 — diz:

> **O que ela não alcança:** gravação que escreva **setor inteiro**. Não existe
> nenhuma nesta task — a única do projeto é o `boton_mcr2isoClick`, da
> WTE-TASK-28, e é lá que preservar EDC/ECC deixa de ser consequência e vira
> decisão.

A [WTE-TASK-28](/docs/tasks/concluidos/28-import-de-mcr.md) mediu e **refutou** isso, e
fechou o critério de EDC/ECC exatamente por refutação: o `boton_mcr2iso` grava
sete faixas, todas dentro do payload de 2048 B, e a maior tem 276 bytes. O
handler é "tão comportado quanto os quatro da WTE-TASK-27".

Pior: o mesmo documento **já contém a medição que o desmente**, 170 linhas
acima. A sessão `27-mcr2iso` está entre as 12 que compõem as 164 faixas
conferidas, e o veredito imediatamente anterior é "**Nenhuma toca byte de
EDC/ECC nem de cabeçalho**". O documento afirma as duas coisas.

O texto é literal na prosa do gerador, então o `--check` não o alcança: ele
prova que o `.md` bate com o `.py`, e o `.py` é onde está o engano.

## Evidência

O que o próprio documento conta (linhas 139-152):

```text
Conferidas **164** faixas do `cmp`, em 12 sessões desta task:
...
- `27-mcr2iso` — 16 faixa(s)
...
**Nenhuma toca byte de EDC/ECC nem de cabeçalho.** Cada extremo cai
entre 24 e 2071 do próprio setor
```

O que o mesmo documento afirma 30 linhas depois (linhas 163-167):

```text
**O que ela não alcança:** gravação que escreva **setor inteiro**. Não
existe nenhuma nesta task -- a única do projeto é o `boton_mcr2isoClick`
```

As sete faixas do handler, do `wte/re/cmp-medido.tsv` (as outras nove da
sessão `27-mcr2iso` são a injeção da abertura, presentes em toda sessão):

| início | tamanho | setor | byte no setor |
|---:|---:|---:|---:|
| 388786 | 223 | 165 | 706 |
| 404765 | 14 | 172 | 221 |
| 2180624 | **276** | 927 | 320 |
| 2302816 | 1 | 979 | 208 |
| 2303791 | 27 | 979 | 1183 |
| 2329074 | 5 | 990 | 594 |
| 3067473 | 23 | 1304 | 465 |

Nenhuma passa de 276 bytes; nenhuma sai da faixa 24..2071.

E há uma segunda imprecisão no mesmo parágrafo: a escrita de payload **inteiro**
existe e já está contada — as faixas `14136..16183`, `16488..18535`,
`18840..20887`, `21192..23239` e `23544..25591` são 2048 bytes cada, de 24 a
2071, edge a edge. São a injeção dos sete setores da abertura, e passam pelo
mesmo teste sem tocar EDC/ECC.

## Causa raiz

Parágrafo escrito como previsão em 2026-08-11, quando a WTE-TASK-28 ainda não
tinha medido; a medição chegou e o parágrafo não foi revisitado.

## Correção

### Arquivo: `wte/tools/gravacao_controle.py`

Trocar o parágrafo final (linhas 321-324) pelo resultado medido. Algo na forma:

```python
w("**A conta alcança o projeto inteiro, e isso foi medido depois.** O")
w("enunciado da [WTE-TASK-28](../../docs/tasks/28-import-de-mcr.md) previa")
w("que o `boton_mcr2isoClick` escreveria **setor inteiro**, e que ali")
w("preservar EDC/ECC deixaria de ser consequência e viraria decisão.")
w("Medido, não é: a sessão `27-mcr2iso` já está entre as contadas acima, e")
w("as sete faixas do handler cabem no payload -- a maior tem 276 bytes.")
w("Escrita de payload inteiro existe, mas é a injeção da abertura")
w("(2048 B de 24 a 2071, em cinco setores), e ela também não toca os 280.")
```

Os números do parágrafo novo devem ser **computados** do `cmp-medido.tsv`, não
escritos à mão — é o mesmo defeito que a [CORR-WTE-071](/docs/tasks/concluidos/CORR-WTE-071.md)
abre em outro gerador.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/gravacao_controle.py` | modificar |
| `wte/re/gravacao-controle.md` | regerar (não editar à mão) |

## Verificação

- [x] `python3 wte/tools/gravacao_controle.py --check` verde depois de regerar
- [x] `grep -n 'setor inteiro' wte/re/gravacao-controle.md` não afirma mais que
      a WTE-TASK-28 é exceção — a única ocorrência é a citação da previsão que
      o parágrafo refuta
- [x] `make -C wte check` verde — 644 testes, `OK (skipped=3)`, rc=0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

O parágrafo final do gerador passou a dizer o que foi medido, e a dizê-lo com
número computado do `cmp-medido.tsv`. Três funções novas:

- `faixas_comuns()` — a interseção das faixas de todas as 12 sessões da task,
  que é a injeção da abertura (9 faixas presentes em toda sessão);
- `faixas_proprias(sessao)` — a sessão menos a injeção. Para `27-mcr2iso` dá
  **7**, e a maior tem **276** bytes;
- `payload_inteiro(sessao)` — as faixas de 2048 B começando no byte 24, que na
  `27-mcr2iso` são **5**. Payload inteiro existe, mas é a injeção, e payload
  inteiro ainda é payload: não toca os 280.

**Problemas encontrados:**

Os três testes de `TestCruzamento` apontam as fontes para um diretório
temporário sintético, que não tem a sessão `27-mcr2iso` — o `max()` sobre lista
vazia estourou. O gerador ganhou a guarda: sem a sessão no TSV lido, ele diz
que a conta não foi feita nesta rodada em vez de afirmar assim mesmo, que é o
defeito que esta correção fecha.

**Arquivos criados/modificados:**

- `wte/tools/gravacao_controle.py`
- `wte/re/gravacao-controle.md` (regerado)
