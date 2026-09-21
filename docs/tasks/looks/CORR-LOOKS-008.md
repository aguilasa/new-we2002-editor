---
id: CORR-LOOKS-008
title: "Correção: o `BASE` é derivável e nunca é derivado — `require_base()` não tem chamador nenhum"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-03
severity: medium
done_on: 2026-09-14
done_commit: c4bc075
---

# CORR-LOOKS-008: o `BASE` é derivável e nunca é derivado — `require_base()` não tem chamador nenhum

## Problema identificado

O critério da task diz: *"Os dois `BASE` são **derivados do cabeçalho e
conferidos** contra a constante, não apenas cravados"*. O `derive_base()` e o
`require_base()` fazem exatamente isso, e são bons — mas **nenhum comando os
roda sobre os arquivos reais**. Os únicos chamadores estão no `self_check()` do
próprio `layout.py`, e todos sobre vetores **sintéticos** de 520 bytes.

O que existe hoje, comando a comando:

| comando | o que faz com o `BASE` |
|---|---|
| `layout.py --check` | deriva de três cabeçalhos inventados |
| `layout.py --sweep` | nada |
| `iso_source.py --check` | nada (leitor de mentira, sem cabeçalho) |
| `iso_source.py --check-discs` | lê os quatro arquivos reais e **não deriva base nenhuma** |

O `--check-discs` é o único que abre os discos, e passa ao lado: confere
digest e não toca no cabeçalho. Resultado: as duas constantes de `BASE` são
**cravadas na prática**. A derivação existe como capacidade e não como
verificação.

Isso não é hipótese: os números do Log — 2 e 18 palavras de cabeçalho, os dois
`BASE`, os 642/1.703 words de bit alto, os 24/240 que caem dentro, os alvos de
8 a 112 e de 72 a 1.712 — saíram de um script da sessão de execução, que não
ficou. Esta revisão só pôde reconferi-los **escrevendo outro script**, que
também não fica. É o que a regra do repositório proíbe: número em doc vem de
ferramenta guardada.

E o custo é concreto. `derive_base()` é o método que a §1.2 usa e que a Fase 2
vai reusar para achar o boneco na RAM; se ele quebrar numa mudança de regex, de
endianness ou de fatiamento, o `--check` continua verde — os vetores sintéticos
são construídos para casar com o algoritmo — e só a Fase 2 descobre, longe
daqui.

## Evidência

Chamadores fora do `layout.py`:

```
$ grep -rn "require_base\|derive_base" tools/ --include=*.py | grep -v layout.py
(vazio)
```

E dentro dele, só o `self_check()` sobre `b"\x00" * 512` mais oito bytes de
cabeçalho inventado.

Que a derivação **funciona** sobre os arquivos reais, esta revisão mediu — com
script próprio, que é o problema:

```
/BIN/EDT_MOD.BIN     len=36072 header= 2 words base=0x8011C000 const=0x8011C000 match=True
   header targets min=8 max=112
   high-bit words=642  of which inside file under base=24
/BIN/MODEL.BIN       len=64800 header=18 words base=0x8016E800 const=0x8016E800 match=True
   header targets min=72 max=1712
   high-bit words=1703  of which inside file under base=240
```

Todos os números do Log batem. **O defeito não é o valor, é não haver comando
que o reproduza** — e a segunda testemunha que o Log cita, essa sim, é
versionada e confere:

```
$ MSYS_NO_PATHCONV=1 python tools/pes2/lzss.py roms/japanese-shift-jis.bin --file /BIN/MODEL.BIN -v
  /BIN/MODEL.BIN            64800 B  header  18 w -> stream at    72  ...
```

## Causa raiz

A derivação foi escrita como função e exercitada só em sintético; o comando que
lê os discos reais confere digest e não chama `require_base()`.

## Correção

### Arquivo: `tools/looks/iso_source.py`

O `_check_discs()` já tem os bytes na mão. Para cada arquivo de
`layout.GEOMETRY_FILES`, chamar `layout.require_base()` e imprimir o que saiu —
palavras de cabeçalho, base derivada, constante, e o veredito. Uma linha por
arquivo, no mesmo formato das outras:

```
  base     /BIN/EDT_MOD.BIN      2 words -> 0x8011C000 (constant 0x8011C000) ok
  base     /BIN/MODEL.BIN       18 words -> 0x8016E800 (constant 0x8016E800) ok
```

`WrongBase` conta como falha e o comando sai com código != 0, como já faz com
`WrongDisc`.

Vale fazer o mesmo do lado **inglês**: a geometria é byte a byte idêntica, logo
a base derivada tem de ser a mesma nos dois discos — é uma asserção de graça,
sobre bytes que o comando já leu.

### Arquivo: `docs/PLAN-LOOKS-PY.md` §4.5 (ou §1.2, onde o método mora)

Registrar que o `--check-discs` é quem redeixa a derivação — hoje a seção
descreve o método e não diz quem o executa, que é a mesma metade que faltava na
[`CORR-LOOKS-005`](/docs/tasks/looks/CORR-LOOKS-005.md).

### Os números de contexto

Os 642/1.703 e os 24/240 são a **advertência** do `derive_base()` — a razão de
não varrer o arquivo inteiro. Eles vivem hoje só no docstring e no Log. Ou o
`--check-discs` os imprime junto (barato: são duas passadas por arquivo já
lido), ou o docstring diz de onde saíram e como refazê-los. A primeira opção é
melhor: número que a ferramenta imprime não envelhece.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/iso_source.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [x] `python tools/looks/iso_source.py --check-discs <japonês> <inglês>` imprime
      a base derivada dos dois arquivos de geometria, nos dois discos, e sai 0
- [x] uma constante de `BASE` trocada à mão faz o comando sair != 0 (controle
      manual, não commitado)
- [x] `python tools/looks/layout.py --check` e `--sweep` continuam verdes
- [x] `python tools/looks/iso_source.py --check` continua verde
- [x] `roms/` intocada — os dois discos abertos só para leitura

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

O `--check-discs` passou a **derivar** as duas bases dos arquivos reais, nos
dois discos, a cada corrida. Um `_report_bases()` novo no `iso_source.py` chama
`layout.derive_base()` e `layout.require_base()` por arquivo de
`GEOMETRY_FILES`, imprime o veredito, e `WrongBase` conta como falha do mesmo
jeito que `WrongDisc`. O lado inglês reusa a mesma função com o dicionário das
bases já derivadas do lado japonês: geometria idêntica byte a byte tem de
derivar o mesmo número, e divergência sai como
`DIFFERS from 0x… on the other disc`.

Os números de contexto — a advertência do `derive_base()` — são impressos junto,
que era a opção que a CORR preferia:

```
Japanese disc -- everything must be accepted
  accepted /BIN/DAT2D.BIN
  accepted /BIN/EDT_MOD.BIN
  accepted /BIN/MODEL.BIN
  accepted /SELECT.BIN
  base     /BIN/EDT_MOD.BIN      2 words -> 0x8011c000 (constant 0x8011c000) ok
           642 word(s) with the top bit set, 24 of them inside the file under that base
  base     /BIN/MODEL.BIN       18 words -> 0x8016e800 (constant 0x8016e800) ok
           1703 word(s) with the top bit set, 240 of them inside the file under that base
English disc -- geometry accepted, the Japanese-only files refused
  ...
  base     /BIN/EDT_MOD.BIN      2 words -> 0x8011c000 (constant 0x8011c000) ok
  base     /BIN/MODEL.BIN       18 words -> 0x8016e800 (constant 0x8016e800) ok
iso_source --check-discs: ok                                       (exit 0)
```

Os 2, 18, 642, 1.703, 24 e 240 do Log da
[`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) — que saíram
de um script que não ficou — agora saem de comando versionado, e batem.

E o controle, que é o que separa comando de decoração: com
`layout.BASE[MODEL]` trocado para `0x80160000` em memória (nada commitado), o
comando sai **1**:

```
  BASE     /BIN/MODEL.BIN: header derives base 0x8016e800, expected 0x80160000
           -- a different release, a modified image, or not this file at all
iso_source --check-discs: 2 unexpected result(s)                   (rc = 1)
```

São duas ocorrências porque os dois discos derivam, que é o desenho.

**Problemas encontrados:**

A contagem de palavras de bit alto **não pôde** morar no `iso_source.py`: ela
precisa de `0x80000000`, que é endereço, e a regra 1 põe todo endereço no
`layout.py` — o `--sweep` pegaria, e com razão. Virou
`layout.pointer_density(data, base)`, com o porquê no docstring e duas
asserções no `self_check()`. Ou seja, esta CORR tocou um arquivo que a lista
dela não previa, e a razão é a regra 1, não descuido.

A varredura de discrepância puxou o Log da LOOKS-TASK-03: o bloco `Medido:` é
transcrição do script descartado, e **fica** como está — é registro da corrida
que o produziu. O que entrou foi uma frase logo abaixo dizendo que os números
são reproduzíveis desde esta CORR, e por qual comando.

**Arquivos criados/modificados:**

- `tools/looks/iso_source.py` — `_report_bases()` e as duas chamadas no
  `_check_discs()`
- `tools/looks/layout.py` — `pointer_density()` e as asserções dela
- `docs/PLAN-LOOKS-PY.md` — §1.2, quem redeixa a derivação e a advertência medida
- `docs/tasks/looks/03-fonte-de-disco-e-layout.md` — a remissão ao comando
- `docs/tasks/looks/CORR-LOOKS-008.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
