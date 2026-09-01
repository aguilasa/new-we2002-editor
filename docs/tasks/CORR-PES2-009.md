---
id: CORR-PES2-009
title: "Correção: o `--check` do `lzss.py` não sabe ficar vermelho — o bug de porte que a própria task nomeia passa verde"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-PES2-009: o gate do codec LZSS é decorativo

## Problema identificado

O perfil do ciclo lista `python3 tools/pes2/lzss.py "<a>" … --check` como o
gate da ferramenta, e o `check_image.py` o roda dentro do `pes2_image`
(`ctest`). Medido: **ele não reprova um decodificador quebrado.**

O `--check` faz duas coisas:

```python
if tally["whole"] == 0:                      # ao menos um contêiner
    ...
for path in paths:
    for off, used, raw in scan(data):        # os blocos que o scan achou
        plain, again = decompress(data, off) # ... redecodificados
        if again != used or len(plain) != raw:
```

O segundo laço **compara `decompress` consigo mesmo**: os blocos vêm de
`scan()`, que os achou decodificando, e a redecodificação é a mesma função
determinística no mesmo offset. Ele nunca discorda. O que sobra de asserção é
"pelo menos um contêiner decodifica no offset do cabeçalho" — e isso continua
verdadeiro depois de estragos muito grandes.

E o texto do `--help` afirma o que o código não faz:

```
--check   assert every container decodes whole, from the offset its own
          header names
```

Medido: **36 contêineres por disco** (3 `partial` + 33 `none`) não decodificam
assim, nos quatro discos, e o `--check` é verde. A afirmação está errada por
construção, não por regressão.

## Evidência

Reintroduzido **exatamente** o bug de porte que a PES2-TASK-26 marca como o
erro a evitar — `while (k3-- >= 0)` com `k3` tratado como não-assinado — numa
cópia da ferramenta no scratchpad:

```python
-                    count = b - 0xB9 + 1           # signed k3, hence the +1
+                    count = b - 0xB9              # BUG: unsigned k3
```

Resultado sobre a mesma imagem `(EsIt)`:

| | íntegro | com o bug |
|---|---:|---:|
| `whole` | 172 | **41** |
| `partial` | 3 | **118** |
| `none` | 33 | **49** |
| blocos | 2.153 | **812** |
| bytes descomprimidos | 24.921.220 | **5.092.275** |
| **`--check`** | `CHECK OK` | **`CHECK OK`, exit 0** |

76% dos blocos do disco deixaram de decodificar e o gate não piscou.

**O `--roundtrip` também não pega este bug, e não é acidente:** o `compress()`
daqui nunca emite o opcode `0xC0..0xFE` — é a assimetria do CARP que a §5c do
`PLAN-FEATURES` mede e o módulo documenta —, então
`decompress(compress(x)) == x` jamais executa o ramo estragado. Os dois gates
que a task entregou são cegos ao mesmo defeito, e por razões diferentes.

## Causa raiz

O `--check` foi escrito para assertar *forma* ("nada regride de `whole`") em
vez de *valor*, porque as contagens diferem entre os quatro discos. Mas
"nada regride" não foi implementado: não há linha de base contra a qual
regredir, e `tally["whole"] == 0` é um limiar que só um decodificador
completamente morto alcança.

## Correção

### Arquivo: `tools/pes2/lzss.py`

O `--check` passa a comparar contra **valor medido**, identificando o disco em
vez de exigir contagem única. Duas formas, e a primeira basta:

1. **Tabela de expectativa por disco**, chaveada por algo que o disco já diz de
   si — o nome do executável de boot que o `tables.boot_executable()` resolve,
   ou o número de contêineres — com os quatro conjuntos que a §1.14(e) do plano
   já publica:

   ```python
   EXPECT = {
       208: ("PES2 (EsIt)",  {"whole": 172, "partial": 3, "none": 33,
                              "blocks": 2153}),
       210: ("PES2 (EnFrDe)", {"whole": 174, "partial": 3, "none": 33,
                              "blocks": 2195}),
       177: ("WE2002 European Deluxe", {"whole": 141, ..., "blocks": 1842}),
       195: ("WE2002 japonês",         {"whole": 159, ..., "blocks": 2027}),
   }
   ```

   Disco desconhecido não reprova — imprime "sem expectativa registrada" e
   segue, como o `pes2_image` já faz com o que lhe falta.

2. **Uma âncora de conteúdo**, barata e independente de disco: o SHA-256 dos
   16.384 bytes do primeiro bloco de `TEX_00.BIN` (offset 48) e dos blocos das
   cinco linhas da §5c. Um decodificador que erra o opcode muda esses bytes
   antes de mudar contagem nenhuma.

O texto do `--help` passa a dizer o que ele confere de fato.

### Arquivo: `docs/prompts/perfil-pes2.md`

A linha do gate ganha o que se espera ver — o nome do disco reconhecido e as
quatro contagens —, como a linha do `poke.py --self-check` já faz.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/pes2/lzss.py` | modificar |
| `docs/prompts/perfil-pes2.md` | modificar |

## Verificação

- [x] `lzss.py <quatro discos> --check` verde, nomeando os quatro discos
- [x] **o controle negativo**: com `count = b - 0xB9` (o bug do `k3` assinado)
      numa cópia da ferramenta, o `--check` fica **vermelho** e sai diferente
      de zero
- [x] `ctest --test-dir build -R pes2_image` verde, com caminhos absolutos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** O laço tautológico saiu e entraram **duas**
asserções, uma por disco e uma independente de disco.

A **primeira forma** da CORR: `EXPECT`, chaveada pela contagem de contêineres,
com os quatro conjuntos que a §1.14(e) do plano publica. O `--check` diz qual
disco reconheceu e compara `whole`/`partial`/`none`/blocos:

```
CHECK: recognised PES2 (EsIt) by its 208 containers          CHECK OK
CHECK: recognised PES2 (EnFrDe) by its 210 containers        CHECK OK
CHECK: recognised WE2002 European Deluxe by its 177 …        CHECK OK
CHECK: recognised WE2002 Japanese by its 195 containers      CHECK OK
```

**Controle negativo, o que a CORR pede:** com `count = b - 0xB9` numa cópia da
ferramenta no scratchpad, quatro linhas vermelhas e exit 1 —

```
CHECK FAILED: PES2 (EsIt): whole is 41, measured 172
CHECK FAILED: PES2 (EsIt): partial is 118, measured 3
CHECK FAILED: PES2 (EsIt): none is 49, measured 33
CHECK FAILED: PES2 (EsIt): blocks is 812, measured 2153
```

**Problemas encontrados.** Três, os dois primeiros medidos e contra o que a
CORR previa:

1. **A segunda forma da CORR não é independente de disco.** Ela propõe o
   SHA-256 do primeiro bloco de `TEX_00.BIN` @48 como âncora barata "e
   independente de disco". Medido: `(EsIt)` e `(EnFrDe)` batem
   (`1a3d87d33f167794…`, 16.384 B), a **japonesa é outra**
   (`17305ae935ef73f9…`, 5.005 B comprimidos contra 5.145), e a European
   Deluxe **não tem** `TEX_00.BIN` legível — o setor 8415 é Form 2. Seria uma
   quinta constante por disco, não uma âncora.
2. **A primeira forma sozinha deixa um buraco, e ele é o do disco novo.**
   Contagem desconhecida não reprova (é o que a CORR pede, e está certo), mas
   então um decodificador quebrado sobre um quinto disco passa verde de novo —
   exatamente o defeito que esta correção conserta. Entrou
   `check_block_literal()`: um fluxo de 16 bytes construído aqui que exercita
   o opcode `0xC0..0xFE`, o ramo onde o bug do `k3` mora e que nem o
   `--roundtrip` alcança (o `compress()` nunca o emite). Medido, disco fora da
   tabela **e** com o bug:

   ```
   CHECK FAILED: the block-literal opcode does not decode at all: …
   CHECK: 208 containers is no disc on record -- counts not asserted
   CHECK FAILED    exit=1
   ```

3. **A primeira versão da asserção sintética estava errada, e ela mesma
   acusou.** Com o flag byte `0x01` só o primeiro token é comando: o `0xFF`
   terminador é lido como literal e o fluxo corre para fora do fim
   (`input ended mid-token at 16`) — vermelho nos quatro discos íntegros. O
   flag certo é `0x03`, os dois primeiros tokens comando. O comentário
   registra isso, porque é o erro que a próxima asserção escrita à mão repete.

**Gates.** `lzss.py --check` nos quatro discos: `CHECK OK` × 4, exit 0, cada
disco nomeado. Dois controles negativos vermelhos (bug com disco conhecido;
bug com disco fora da tabela). `ctest -R pes2_selftest|pes2_image` 2/2
`Passed`. Os quatro conjuntos de `EXPECT` são os da tabela da §1.14(e) do
plano, remedidos hoje pela ferramenta — não somados à mão. `roms/` intocada.

**Arquivos criados/modificados:**

- `tools/pes2/lzss.py`
- `docs/prompts/perfil-pes2.md`
