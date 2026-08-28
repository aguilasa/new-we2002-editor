---
id: CORR-WTE-121
title: "Correção: o port grava três faixas de nome de time diferentes do oráculo, e só a ptbr-remaster expõe"
type: correção
category: paridade
status: concluído
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

- [x] As três faixas têm causa nomeada, com o endereço no `.exe` do Obocaman
- [x] `bash wte/tools/golden_suite.sh --rom ptbr --roteiro golden-05-nomes` e
      `--roteiro golden-23-multiplas-edicoes` saem `PASSOU` nos dois modos
- [x] A bateria completa na `ptbr` fecha **48 `PASSOU`**
- [x] `--rom japonesa` continua 24/24 — a correção não pode quebrar o que passava
- [x] `roms/` intocada

## Log de Execução

**Executado em** 2026-08-28.

### A hipótese da CORR estava errada, e o defeito era triplo

A seção "Causa raiz" apostava no preenchimento da sobra do campo — *"um dos
lados zera o resto do bloco, o outro deixa o resíduo"*. **Não é isso.**

A régua que desfez a aposta é barata e não estava na CORR: diferenciar a ROM
virgem contra **cada lado**, em vez de os dois lados entre si. Feito assim, os
dois gravam nos **mesmos dez blocos**, e a diferença aparece separada por
mecanismo:

```text
ROM -> oraculo                      ROM -> port
  1013916..1013922  (7)               1013916..1013922  (7)
  1882884..1882890  (7)               1882884..1882890  (7)
  2003937..2003949 (13)               2003937..2003949 (13)   <- conteudo difere
  2004968..2004974  (7)               2004968..2004974  (7)
  2005364..2005366  (3)               2005364..2005366  (3)
  2830924..2830930  (7)               2830924..2830930  (7)
  4234852..4234854  (3)               4234852..4234854  (3)
  4599396..4599402  (7)               4599396..4599400  (5)   <- 5 chars vs 7
  5651436..5651438  (3)               5651436..5651438  (3)
  5652568..5652570  (3)               5652628..5652634  (7)   <- OUTRO slot
```

São **três** defeitos independentes, e as três faixas da CORR se repartem
entre eles. Nenhum tem a ver com preenchimento de sobra.

### Defeito A — o `MaxLength` do `edit_nombre1` (faixas 1 e 2)

O oráculo aceitava **7** caracteres onde o port aceitava **5**, e o campo
cortava o nome antes de gravar. As duas faixas são o mesmo campo em dois
blocos (`OFS_TEAM_NAME_KANJI` e `OFS_TEAM_MIXED_CASE_NAME`).

O `LimiteDoNome1` tirava o número de `TEAM_NAME_KANJI_LEN`, do `we2002_core`;
o original mede a largura do registro **andando pela imagem**
(`0x00403c0c`, chamado pelo `lista_equiposChange`). Emulada a varredura do
`.exe` contra as tabelas constantes, em 95 times por ROM:

| tabela | japonesa | `ptbr-remaster` | European Deluxe |
|---|---:|---:|---:|
| `TEAM_NAME_LEN_3` (`edit_nombre2`) | 95/95 | 95/95 | 95/95 |
| `TEAM_NAME_KANJI_LEN` (`edit_nombre1`) | 95/95 | **66/95** | **46/95** |

**Isto já estava registrado como divergência deliberada** — a §4 do
[`divergencias.md`](../../wte/re/divergencias.md), *"o `MaxLength` do
`edit_nombre1` na European Deluxe"*, decisão *manter*. A entrada estava errada
em duas coisas: não é só da European Deluxe, e não é limite de tela — é nome do
usuário perdido na imagem. Ela virou **remoção**, no molde da §9.

Os dois `LimiteDoNome*` passaram a medir. O `edit_nombre2` entrou junto embora
bata 285/285 nas três ROMs: o original mede os dois, e a medição prova que a
mudança dele não move byte nenhum hoje.

### Defeito B — o salto de setor da varredura (faixa 3)

Aqui o port gravava no **time errado**: 5652628 (`S.AFRIC`) contra 5652568
(`CHL`) do oráculo, **8 registros** adiante no mesmo bloco.

As duas rotinas de bloco do original — `0x004033bc` (ler `count`) e
`0x00403400` (gravar `count`) — chamam o `0x00403388` depois de **cada** byte,
inclusive o último, e é isso que o `LeDoFluxo` do port faz. **A varredura do
`0x00403c0c` não**: o `call 0x403388` mora no topo de cada laço
(`0x00403c42`, `0x00403c56`, `0x00403cb9`, `0x00403cce`), roda *entre* duas
leituras e nunca depois do byte que encerra o laço — nem o `0` que termina o
nome, nem o não-zero que abre o próximo.

São dois bytes por registro sem teste de fronteira. Um deles caía em
`2072 mod 2352`, o original não pulava os 304 de EDC/ECC, e quem pulava saía
de fase. Modelado o laço byte a byte como o `.exe`, os dez blocos batem
**10/10** com o que o oráculo gravou — antes batiam 9/10.

O `0x00403388` foi lido, não suposto: `ftell`, `idiv 0x930` (2352),
`cmp edx,0x818` (2072), `fseek(+0x130)` (304).

### Defeito C — o terminador incondicional (1 byte)

Consertados A e B, sobrou **um byte**: `5652571`. O slot do time 2 em
`OFS_TEAM_NAME_6` tem largura 4 (`CHL`), o campo trazia `A BC.DE`, e o port
gravava `A BC` onde o oráculo grava `A B` mais o NUL.

A saída comum dos dois modos do codificador faz, sem condição nenhuma:

```text
403bcd:  mov ecx,[ebp+0x14]                 ; o buffer
403bd0:  mov eax,[ebp+0x0c]                 ; o comprimento
403bd3:  mov BYTE PTR [ecx+eax*1-0x1],0x0   ; buffer[comprimento-1] := 0
```

E o gravador (`0x00403dcc`) passa `comprimento` **cheio** ao `0x00403400`, então
o byte forçado é gravado. Só aparece em slot mais estreito que o texto —
quando o texto acaba antes, a cauda já era zero. Por isso 24 corridas
japonesas e 23 europeias nunca o viram.

### Por que nenhuma outra ROM enxergava

A CORR já dizia que a `ptbr-remaster` é a primeira com oráculo vivo **e**
nomes latinos. A execução mostrou o mecanismo: B e C só se manifestam em slot
**estreito**, e A só quando o slot de kanji recebeu nome latino — cujo lixo
depois do terminador encurta a distância até o registro seguinte.

### Um caso especial reconferido, e que continua morto

A spec do handler dizia que `(campo 0, bloco 5, 32º registro)` faz um `seek`
fixo para `0x563f8d`, e chamava a rota de morta. O endereço é
`OFS_TEAM_NAME_6_B + 1`, o que faz o caso *parecer* o do `(campo 1, bloco 5)` —
exatamente o bloco desta correção. **Não é.** O teste em `0x00403c68` é
`test edi,edi` / `cmp [ebp-4],0x5` / `cmp esi,0x1f`, e `edi` é mesmo a linha:
o `lea ecx,[ecx*8+0x433a0c]` com `ecx = edi*39` dá o passo de 312 = 6 × 52 da
linha. A rota continua morta, e a spec ganhou a reconferência.

### Uma divergência vista e **não** consertada

O modo 2 do codificador do original faz `and dl,0x7f` (`0x00403bbc`) antes de
gravar o byte; o port não faz. É inalcançável pelos três filtros de
`KeyPress`, que só deixam passar `[A-Za-z0-9 .-]`, e está fora das faixas
desta CORR. Fica registrada aqui em vez de consertada: mudar rota que nenhuma
régua julga é risco sem ganho.

### Gates

| Gate | Medido |
|---|---|
| `lazbuild wte/wte.lpi` | **0 warnings, 0 errors** |
| `python3 -m unittest` em `wte/tools` | **884 testes, OK** (2 skipped) |
| `make -C wte check` | **rc=0** |
| `golden-05-nomes` ptbr | **PASSOU** — controle 122s, golden 108s |
| `golden-23-multiplas-edicoes` ptbr | **PASSOU** — controle 143s, golden 132s |
| bateria `--rom ptbr` | **48/48 `PASSOU`** |
| bateria `--rom japonesa` | **48/48 `PASSOU`** (24 roteiros × 2 modos) |
| europeia no `golden.tsv` | intocada — 23 `SEM_ORACULO`, 23 `NAO_APLICAVEL`, 2 `PASSOU` |
| `roms/` | intocada; `work/` limpo ao fim |

### Três reprovações que não eram do port

A primeira passagem da bateria `ptbr` deu 45 `PASSOU`, 2 `REPROVOU` e 1
`NAO_APLICAVEL` — as três no fim da corrida, todas com a mesma assinatura:

```text
ERRO: janela 'Abre' nao apareceu em 30s
ERRO: o roteiro nao conseguiu dirigir o oraculo, e o log do Wine esta LIMPO
```

Uma delas era **`controle`** (`golden-25-retorno`), oráculo contra oráculo — o
sinal que o próprio harness usa para dizer "o problema é meu, não do port". O
`load average` da máquina estava em **4,28** com nada do lote rodando, e o
oráculo sob Wine tem 30s para desenhar a primeira janela. Repetidas com a
máquina mais folgada, as três passaram: `golden-25` 100s/87s, `golden-24`
157s/145s.

### Números de ferramenta que a correção moveu

Duas medidas mecânicas mudaram porque o conserto acrescentou linhas escritas à
mão, e as duas foram **regeneradas**, não somadas:

| Onde | Antes | Depois | Quem mede |
|---|---:|---:|---|
| `fase-2.md`, linhas à mão | 9.024 | **9.155** | `check_fase2.py` |
| `PLAN-WTE-LAZARUS.md` §4.4 | 51,2% | **50,8%** | idem, conferido pelo `--check` |
| `golden.md`, relógio | 6.700 s | **6.703 s** | `check_golden.py` |

### Arquivos

| Arquivo | O quê |
|---|---|
| `wte/src/impl/ep2002_mainform.aux.inc` | os três consertos: varredura, limites medidos, terminador |
| `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` | o cabeçalho que dizia "NÃO LÊ A IMAGEM" |
| `wte/re/golden-ptbr.tsv`, `wte/re/golden.tsv`, `wte/re/golden.md` | as 96 corridas remedidas |
| `wte/re/fase-2.md`, `docs/PLAN-WTE-LAZARUS.md` | os números que a ferramenta remede |
| `wte/re/divergencias.md` | a §4 virou registro de remoção |
| `wte/re/spec/MainForm.boton_nombres2isoClick.md` | salto de setor da varredura, terminador, o caso morto reconferido |
| `wte/re/spec/MainForm.lista_equiposChange.md` | a igualdade `TEAM_NAME_KANJI_LEN − 1`, que só valia na japonesa |
