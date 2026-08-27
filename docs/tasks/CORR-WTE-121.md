---
id: CORR-WTE-121
title: "Correção: o port grava três faixas de nome de time diferentes do oráculo, e só a ptbr-remaster expõe"
type: correção
category: paridade
status: pendente
depends_on: []
---

# CORR-WTE-121: três faixas de nome de time que só a régua nova enxerga

## Problema identificado

A bateria golden do `wte/` rodada sobre a `ptbr-remaster.bin` — as 48 corridas
de [`wte/re/golden-ptbr.tsv`](../../wte/re/golden-ptbr.tsv), medidas em
2026-08-27 — deu **46 `PASSOU` e 2 `REPROVOU`**. As duas reprovações são o
**mesmo defeito**: as faixas saem idênticas, byte a byte, nos dois roteiros.

```text
2003945..2003948   4 byte(s)  data  OFS_TEAM_NAME_KANJI_A+17
4599401..4599402   2 byte(s)  data  OFS_TEAM_MIXED_CASE_NAME+805
5652568..5652634  10 byte(s)  data  OFS_TEAM_NAME_6_B+204
```

Os dois roteiros que reprovam — `golden-05-nomes` e
`golden-23-multiplas-edicoes` — são os que **editam nome de time**. Nenhuma das
três faixas está declarada em [`wte/re/divergencias.md`](../../wte/re/divergencias.md).

**O defeito não é da imagem, e não é novo.** Ele está no port desde sempre; o
que faltava era régua capaz de vê-lo. As outras duas ROMs não conseguem:

| ROM | `golden-05-nomes` | `golden-23-multiplas-edicoes` | por quê |
|---|---|---|---|
| japonesa | `PASSOU` | `PASSOU` | o codec transforma katakana em espaço — os campos de nome não exercitam o caminho |
| europeia | `SEM_ORACULO` | `SEM_ORACULO` | o `wte.exe` morre com `0xc0000005` ao trocar de time |
| **ptbr-remaster** | **`REPROVOU`** | **`REPROVOU`** | oráculo vivo **e** nomes latinos: os dois ao mesmo tempo, pela primeira vez |

## Evidência

O `controle` (oráculo contra oráculo) **passou** nos dois pares — 122 s e 144 s
—, então o par roteiro+imagem é determinístico e o oráculo gravou até o fim.
Um `REPROVOU` com `controle` verde é divergência real do port, não oráculo
truncado. Essa distinção é a razão de a bateria ter três palavras em vez de
duas, e aqui ela trabalha.

Nas 48 corridas: **zero `SEM_ORACULO`**, contra 23 na europeia.

```text
>> ptbr/golden-05-nomes           controle: PASSOU (122s)
>> ptbr/golden-05-nomes           golden:   REPROVOU (108s)
>> ptbr/golden-23-multiplas-edicoes controle: PASSOU (144s)
>> ptbr/golden-23-multiplas-edicoes golden:  REPROVOU (132s)
```

O roteiro **não depende do conteúdo da imagem**: ele limpa o campo (`End`,
`shift+Home`, `BackSpace`) e digita a literal `A B-C.DEFG` nos três campos de
nome. O que muda entre as ROMs é o que estava **lá antes** — e é essa sobra que
os dois lados tratam diferente.

## Causa raiz

**Não diagnosticada.** A hipótese que a evidência sustenta, e que a execução
desta CORR precisa confirmar ou derrubar: o oráculo e o port divergem no
**preenchimento da sobra** do campo quando o nome pré-existente é mais longo
que o digitado. Um dos lados zera o resto do bloco, o outro deixa o resíduo.

Três indícios a favor:

- as três faixas são **contíguas dentro de blocos de nome**, e os deslocamentos
  (`+17`, `+805`, `+204`) caem depois do início de cada bloco, não nele;
- a maior tem 10 bytes num bloco que o roteiro preenche com 10 caracteres
  (`A B-C.DEFG`);
- a japonesa passa, e nela o codec já entrega espaço no lugar do resíduo — o
  que apagaria a diferença exatamente como observado.

Confirmar exige comparar os bytes dos dois lados, não só as faixas: dumpar o
bloco antes e depois em cada um.

## Correção

Diagnosticar primeiro, corrigir depois — nesta ordem, e sem inverter:

1. dumpar as três faixas nos dois lados (oráculo e port) na mesma corrida, com
   o conteúdo pré-existente do time 2 da `ptbr-remaster` registrado;
2. achar no `.exe` do Obocaman o handler que grava cada bloco
   (`boton_nombres2isoClick` é o ponto de entrada conhecido do `golden-05`) e
   ler o que ele faz com a sobra;
3. corrigir o port Pascal para reproduzir, **ou** — se o comportamento do
   original for indefinido, como no slot 64 do `newWe2002` — declarar as três
   faixas em `divergencias.md` com a justificativa medida.

**A segunda saída não é atalho.** Ela exige a mesma leitura do `.exe`: declarar
faixa sem saber por que ela diverge é o que o `check_divergencias.py` existe
para impedir.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/we2002_*.pas` ou o handler de nomes do port | modificar — depois do diagnóstico |
| `wte/re/divergencias.md` | modificar — só se a saída for declarar |
| `wte/re/golden-ptbr.tsv` | remedir — as duas linhas têm de virar `PASSOU` |

## Verificação

- [ ] As três faixas têm causa nomeada, com o endereço no `.exe` do Obocaman
- [ ] `bash wte/tools/golden_suite.sh --rom ptbr --roteiro golden-05-nomes` e
      `--roteiro golden-23-multiplas-edicoes` saem `PASSOU` nos dois modos
- [ ] A bateria completa na `ptbr` fecha **48 `PASSOU`**
- [ ] `--rom japonesa` continua 24/24 — a correção não pode quebrar o que passava
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
