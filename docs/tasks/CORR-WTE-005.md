---
id: CORR-WTE-005
title: "Correção: os streams sintéticos que sustentam \"os 21 TValueType exercitados\" não são versionados"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-005: a cobertura afirmada pelo Log da WTE-TASK-03 não tem rota de volta

## Problema identificado

O Log da [WTE-TASK-03](/docs/tasks/03-extrator-de-dfm.md) afirma:

> Os 21 `TValueType` e as três flags de objeto (`ffInherited`, `ffChildPos`,
> `ffInline`) estão implementados; os que não ocorrem nestes 18 foram
> exercitados contra **streams sintéticos**.

E o critério de conclusão marca `[x]` em:

> Tipo desconhecido aborta com offset, não emite parcial

Os streams sintéticos não estão no repositório. `git ls-files wte` devolve 31
arquivos e nenhum deles é teste do `dfm_extract.py`; `wte/tests/` tem só o
`README.md`, que reserva a pasta para o **lado Pascal** a partir da
WTE-TASK-20.

O que sobra é a afirmação. Metade dos caminhos afirmados — `vaCollection`,
`vaSet`, `vaList`, `vaExtended`, `vaInt64`, `vaNil`, `vaSingle`, `vaDate`,
`vaWString`, o prefixo de flags de objeto e as quatro rotas de aborto — **não
ocorre nos 18 formulários**, então rodar o gerador sobre o `.exe` não os toca.
`--check` verde não diz nada sobre eles.

É a mesma forma da [CORR-WTE-002](/docs/tasks/CORR-WTE-002.md): o valor está
certo, o que falta é a rota de volta. Só que aqui o alvo não é um número num
`.md`, é o guard que o plano chama de armadilha §8 — o extrator que "parece
completo" é o furo principal da fase 1, e ele é exatamente o que esses
caminhos não exercitados protegem.

## Evidência

Nenhum teste versionado:

```
$ git ls-files wte | grep -i test
wte/tests/README.md

$ cat wte/tests/README.md
# `tests/` — testes do lado Pascal
Vazio na fase 0. O primeiro conteúdo real é da **WTE-TASK-20** [...]
```

Nenhum dos tipos raros ocorre nos 18 formulários, medido sobre os streams do
`.exe` — os objetos com byte de flags são **zero** em 459 objetos:

```
RT_RCDATA recursos: 19 | TPF0: 18
objetos: 459 | com byte de flags (0xF0): 0
```

Refeitos à mão nesta revisão, os caminhos respondem como o Log diz — e é
justamente esse trabalho que precisa virar arquivo:

```
tipo-desconhecido: ABORT -> we-team-editor/we-team-editor.exe+4118 (0x1016):
  TEST: Form1 > Left: TValueType desconhecido: 99 (0x63). [...]
truncado:  ABORT -> [...] fim do stream: pedidos 16 bytes, restam 3
sobra:     ABORT -> [...] sobraram 2 bytes depois do fim do formulario
nao-ascii: ABORT -> [...] nome de propriedade com byte fora de ASCII [...]
blob-duplicado: ABORT -> [...] dois blobs disputam o arquivo Form1.Data.bin
flags-objeto: OK -> 'inherited Form1: TForm1 [7]\n  Left = 10\nend\n'
colecao:   OK -> "Items = <\n    item [0]\n      Name = 'x'\n    end>"
extended:  OK -> 'Value = 2.5'   int64: OK -> 'Big = 1099511627776'
```

## Causa raiz

A verificação dos caminhos ausentes dos 18 formulários foi feita em código
descartável, e o repositório não tem onde um teste de ferramenta Python morar.

## Correção

### Arquivo: `wte/tools/test_dfm_extract.py`

Um arquivo, stdlib pura (`unittest`), sem depender do `.exe` — ele monta os
streams em memória. Cobrir:

- **os tipos que os 18 não têm:** `vaList`, `vaExtended`, `vaSet`,
  `vaCollection` (com e sem índice de item), `vaNil`, `vaSingle`, `vaCurrency`,
  `vaDate`, `vaInt64`, `vaUTF8String`, e `vaWString` no caso ASCII;
- **o prefixo de flags de objeto:** `ffInherited`, `ffInline`, `ffChildPos` com
  o inteiro de posição — nenhum ocorre no `.exe`, e o `emit_object` decide entre
  `object`/`inherited`/`inline` por ele;
- **as rotas de aborto**, cada uma conferindo que a mensagem traz o offset
  absoluto: `TValueType` desconhecido, fim de stream, bytes sobrando depois do
  `end` da raiz, byte fora de ASCII em nome de propriedade e em nome de classe,
  `vaWString` não-ASCII, colisão de nome de blob, colisão de nome de formulário;
- **a saída textual** dos casos acima, comparada com a string esperada — é o
  que pega regressão em `quote()`, `fmt_float()` e `emit_value()`.

O `--selftest` embutido no próprio `dfm_extract.py` é alternativa aceitável, e
tem a vantagem de o `make -C wte check` já enumerar `tools/*.py`. Se a rota
escolhida for o arquivo separado, ele **não pode** entrar na bateria como
gerador: o `check` do `wte/Makefile` roda `tools/*.py --check` por `wildcard`, e
um teste sem `--check` quebraria o alvo. Ver a nota do `wte/tools/README.md`.

### Arquivo: `wte/Makefile`

Se a rota for arquivo separado, alvo `test` rodando `python3 -m unittest` sobre
`tools/test_*.py`, e `check` passando a depender dele. Se for `--selftest`, nada
a fazer aqui.

### Arquivo: `wte/tests/README.md`

Uma linha dizendo onde mora teste de **ferramenta Python** — hoje o arquivo diz
"testes do lado Pascal" e não responde a pergunta, que foi o que empurrou a
verificação para o descartável.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_dfm_extract.py` | criar (ou `--selftest` em `dfm_extract.py`) |
| `wte/Makefile` | modificar (se arquivo separado) |
| `wte/tests/README.md` | modificar |
| `wte/tools/README.md` | modificar — registrar a convenção escolhida |

## Verificação

- [ ] O teste roda **sem** o `we-team-editor.exe` presente
- [ ] Todo `TValueType` de 0 a 20 é exercitado por pelo menos um caso
- [ ] As três flags de objeto têm caso, com a palavra-chave textual conferida
- [ ] Cada rota de aborto confere o **offset absoluto** na mensagem, não só que
      levantou `DfmError`
- [ ] `make -C wte check` verde, e o alvo não passa a exigir `--check` de um
      arquivo de teste
- [ ] `python3 wte/tools/dfm_extract.py --check` continua verde
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
