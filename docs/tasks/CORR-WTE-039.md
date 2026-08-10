---
id: CORR-WTE-039
title: "Correção: o GABARITO diz que o gerador recusa `(int)*(int *)`, e ele aceita"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-039: a marca de decompilado que só existe no texto

## Problema identificado

O [`wte/re/spec/GABARITO.md`](../../wte/re/spec/GABARITO.md), linha 133, lista
o que o `spec_index.py` **recusa** como decompilado colado:

> os nomes que o Ghidra inventa — `undefined4`, `uVar1`, `iVar2`, `local_1c`,
> `param_1`, `DAT_00423…`, `FUN_00401…`, `__fastcall`, `(int)*(int *)`.

O último item não existe no gerador. A tupla `MARCAS_DE_DECOMPILADO`
(`wte/tools/spec_index.py:62-70`) tem sete padrões, e nenhum casa a idiomática
de cast do Ghidra.

O critério de conclusão da WTE-TASK-23 é explícito nesse ponto — "a proibição
de colar decompilado escrita no gabarito — **e verificada pelo gerador**, não
só escrita". Para oito das nove marcas do gabarito ela é verificada; para a
nona, não. E é justamente a marca que sobrevive a uma limpeza superficial: quem
cola um trecho e renomeia `uVar1` para `n` deixa `(int)*(int *)(this + 8)`
intacto, porque parece "só um cast".

## Evidência

Plantando as nove marcas do gabarito contra a tupla do gerador:

```
RECUSA  'undefined4 x;'              ['\\bundefined[0-9]?\\b']
RECUSA  'uVar1 = 2;'                 ['\\b[iuf]Var[0-9]+\\b']
RECUSA  'local_1c = 0;'              ['\\blocal_[0-9a-f]+\\b']
RECUSA  'param_1 + 4'                ['\\bparam_[0-9]+\\b']
RECUSA  'DAT_004231a0'               ['\\b(DAT|FUN|LAB|PTR)_[0-9a-f]{6,}\\b']
RECUSA  'FUN_00401a2e'               ['\\b(DAT|FUN|LAB|PTR)_[0-9a-f]{6,}\\b']
RECUSA  '__fastcall f()'             ['__fastcall\\b']
ACEITA  '(int)*(int *)(param + 8)'   []
ACEITA  '(int)*(int *)(this + 8)'    []
```

O comando, rodado de `wte/tools/`:

```python
import spec_index as s
for t in alvos:
    hit = [m.pattern for m in s.MARCAS_DE_DECOMPILADO if m.search(t)]
    print(f"{'RECUSA' if hit else 'ACEITA'}  {t!r}  {hit}")
```

O [`wte/re/spec/README.md`](../../wte/re/spec/README.md) **não** tem o problema:
ele lista as marcas sem o cast, e está de acordo com o código.

## Causa raiz

A lista do gabarito foi escrita como prosa do que a regra deveria pegar, e a
tupla do gerador foi escrita depois; a nona marca ficou só na prosa.

## Correção

A rota preferida é implementar, não apagar: o cast é a assinatura mais
resistente do decompilado de C++Builder, e o gabarito já promete que ele é
pego.

### Arquivo: `wte/tools/spec_index.py`

Acrescentar o padrão à `MARCAS_DE_DECOMPILADO`. O cast do Ghidra aparece em
mais de uma largura (`(int)`, `(uint)`, `(short)`, `(byte)`) e com espaçamento
variável, então ancore na forma "cast para tipo C seguido de deref de ponteiro
para tipo C":

```python
re.compile(r"\((?:un)?signed |\((?:int|uint|short|ushort|byte|char|long)\)"
           r"\s*\*\s*\((?:int|uint|short|ushort|byte|char|long)\s*\*\)"),
```

Escreva o padrão que os testes provarem — o que importa é que
`(int)*(int *)(this + 8)` seja recusado e que prosa em português com parênteses
não seja.

### Arquivo: `wte/tools/test_spec_index.py`

Estender `test_recusa_nomes_inventados_pelo_ghidra` com o cast, ou abrir um
teste próprio. **Precisa também de um caso negativo**: uma spec legítima que
mencione `(o time)` ou `(int)` em prosa não pode ser recusada — marca nova de
recusa sem teste de falso positivo é a maneira barata de tornar o gabarito
impossível de cumprir.

### Arquivo: `wte/re/spec/GABARITO.md`

Se a decisão for a rota oposta — não implementar —, tirar `(int)*(int *)` da
lista da linha 133 e dizer no texto que a marca de cast é responsabilidade de
quem revisa. Uma das duas coisas, não as duas.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/spec_index.py` | modificar |
| `wte/tools/test_spec_index.py` | modificar |
| `wte/re/spec/GABARITO.md` | modificar (só na rota oposta) |

## Verificação

- [ ] `(int)*(int *)(this + 8)` é recusado, com a mensagem de decompilado
- [ ] Uma spec com `(int)` em prosa portuguesa **não** é recusada
- [ ] `cd wte/tools && python3 -m unittest test_spec_index -v` verde
- [ ] `python3 wte/tools/spec_index.py --check` continua verde (0 com spec, 96
      abertos — nenhuma spec real existe ainda)
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

Rota preferida — implementar, não apagar. `MARCAS_DE_DECOMPILADO` ganhou o
oitavo padrão, com o tipo C do Ghidra extraído para `_TIPO_C` e reusado nas duas
metades:

```python
re.compile(rf"\({_TIPO_C}\)\s*\*\s*\(\s*{_TIPO_C}\s*\*\s*\)"),
```

Exige as **duas** metades adjacentes — cast para tipo C seguido do deref de um
ponteiro para tipo C. É o que separa a marca da prosa: um `(int)` sozinho não
casa.

Dois testes: `test_recusa_o_cast_do_ghidra` (cinco formas em `subTest`, com
espaçamento variável e as larguras `uint`/`ushort`/`byte`/`undefined1`) e
`test_o_cast_do_ghidra_nao_pega_prosa`, que planta numa spec legítima
"O campo `cost` é `(int)` no C++ e `LongInt` no Pascal. O time (int) e o jogador
(char) são lidos juntos, e a barra (5) * (o peso do time) entra no preço. A
lista (int) * 2 posições fica no fim." — e exige que ela seja **aceita**.

O `GABARITO.md` não muda: a linha 133 passa a descrever o que o gerador faz.

Bateria do `wte/tools/`: 298 → 300 testes, verde. `spec_index.py --check` verde
(96 handlers, 0 com spec, 96 abertos). `make -C wte check` rc=0.

**Problemas encontrados:**

O padrão sugerido no corpo desta correção tem um `|` em nível de topo
(`\((?:un)?signed |\((?:int|…)\)…`), que faria a primeira alternativa casar
**sozinha** — qualquer `(unsigned char)` em prosa viraria recusa. Não foi
copiado; o padrão escrito é o que os dois testes provam, como a própria seção
"Correção" manda.

A varredura de discrepância pegou `wte/tools/README.md:49`, que descrevia o
teste como "decompilado colado nas sete formas" — número que esta correção
aposentou. Ajustado na mesma passada.

**Arquivos criados/modificados:**

- `wte/tools/spec_index.py`
- `wte/tools/test_spec_index.py`
- `wte/tools/README.md` (sítio achado na varredura)
