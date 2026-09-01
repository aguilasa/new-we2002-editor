---
id: CORR-PES2-009
title: "Correção: o `--check` do `lzss.py` não sabe ficar vermelho — o bug de porte que a própria task nomeia passa verde"
type: correção
category: verificação
status: pendente
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

- [ ] `lzss.py <quatro discos> --check` verde, nomeando os quatro discos
- [ ] **o controle negativo**: com `count = b - 0xB9` (o bug do `k3` assinado)
      numa cópia da ferramenta, o `--check` fica **vermelho** e sai diferente
      de zero
- [ ] `ctest --test-dir build -R pes2_image` verde, com caminhos absolutos
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
