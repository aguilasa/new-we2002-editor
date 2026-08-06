---
id: CORR-WTE-013
title: "Correção: o decodificador x86 do dump_units.py é cópia verbatim do dump_strings.py e nenhum teste o alcança"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-013: a cópia do decodificador está livre para divergir da testada

## Problema identificado

O `dump_units.py` carrega uma cópia **byte a byte idêntica** do decodificador de
comprimento de instrução x86-32 do `dump_strings.py` — `_fill()`, `decode()` e
`extent()`. O Log da WTE-TASK-07 registra a escolha e o risco:

> O `dump_units.py` carrega uma cópia verbatim do decodificador x86-32 do
> `dump_strings.py`. A duplicação é a mesma escolha que já vale para o leitor de
> PE — cada gerador de `wte/tools/` roda sozinho —, mas **os dois têm de andar
> juntos se um dia mudarem**.

A duplicação é defensável e não é o problema. O problema é que a
[CORR-WTE-008](/docs/tasks/CORR-WTE-008.md) fixou esse decodificador em teste
— `wte/tools/test_dump_strings.py`, 17 casos, incluindo a conferência contra o
`objdump` — e o teste importa **um** dos dois módulos:

```python
import dump_strings as d  # noqa: E402
```

A cópia do `dump_units.py` não é alcançada por teste nenhum. Nada no
repositório detecta divergência entre as duas: quem corrigir um comprimento de
instrução no módulo testado sai com a bateria verde e a outra cópia errada.

E ela sustenta um veredito. O corpo dos 96 handlers, medido por essa cópia, é o
que separa "chamada dentro de handler" de "chamada em código de RTL" — a
fronteira que decide o único veredito não trivial da WTE-TASK-07:

> o último dos 96 handlers termina em `0x00420f16`, e o sítio está 3141 bytes
> depois disso. A chamada está fora de todo código que o aplicativo escreveu.

Se o `extent()` do `dump_units.py` divergir, o `Comobj` pode passar a ser
reportado como "usado dentro de um handler" sem que nada acuse.

## Evidência

As três funções, comparadas por hash nesta revisão:

```
_fill    strings=070988e14a12 units=070988e14a12 IGUAL
decode   strings=63e2939d002d units=63e2939d002d IGUAL
extent   strings=f27ad1a7bd7b units=f27ad1a7bd7b IGUAL

wte/tools/dump_strings.py | linhas: 1703 | _fill(...) chamadas: 47
wte/tools/dump_units.py   | linhas: 1651 | _fill(...) chamadas: 47
```

Idênticas **hoje**. O que falta é o que mantém assim amanhã:

```
$ ls wte/tools/test_*.py
wte/tools/test_dfm_extract.py
wte/tools/test_dump_strings.py

$ grep -n "^import dump" wte/tools/test_dump_strings.py
52:import dump_strings as d
```

A medida que a cópia sustenta, e que sairia errada em silêncio:

```
0x00421b5b - 0x00420f16 = 0xc45 = 3141
```

## Causa raiz

O teste do decodificador nasceu apontando para o módulo em que ele foi escrito,
e a segunda cópia não estava no escopo daquela correção.

## Correção

### Arquivo: `wte/tools/test_dump_strings.py`

Duas mudanças, ambas pequenas:

1. **Parametrizar os casos de comprimento sobre os dois módulos.** Importar
   `dump_units` ao lado de `dump_strings` e rodar a tabela de (bytes,
   comprimento, classe de fluxo) contra os dois `decode()`. A conferência contra
   o `objdump` não precisa dobrar — ela é cara e já cobre o algoritmo; o que
   dobra é a tabela barata.
2. **Um teste de identidade.** Comparar o texto-fonte de `_fill`, `decode` e
   `extent` entre os dois arquivos e falhar se divergirem, com a mensagem
   dizendo qual das duas mudou e que a outra precisa da mesma mudança. É o
   teste que transforma "têm de andar juntos" de comentário em regra.

O teste de identidade é o que **não** deve ser substituído por "extrair para um
módulo comum": a decisão de cada gerador rodar sozinho está registrada no
`wte/README.md` e vale também para o leitor de PE. Esta correção não a
reabre — só põe uma guarda sobre o preço dela.

### Arquivo: `wte/tools/README.md`

A linha do `test_dump_strings.py` na tabela de testes passa a dizer que ele
cobre os dois geradores, e a nota da duplicação — hoje só no Log da tarefa —
ganha uma frase ali, que é onde quem for escrever o sexto gerador vai olhar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_dump_strings.py` | modificar |
| `wte/tools/README.md` | modificar |

## Verificação

- [x] O alvo `test` do `wte/Makefile` roda a tabela de comprimento contra os
      **dois** módulos — 66 casos × 2, por `subTest(modulo=...)`
- [x] Alterar `decode()` em só um dos dois arquivos **reprova** o teste de
      identidade, com a mensagem nomeando o arquivo divergente — testado, sai
      com `unified_diff` entre `dump_strings.py:decode` e `dump_units.py:decode`
- [x] Plantar um comprimento errado no `dump_units.py` reprova a tabela —
      `ERROR: test_cada_caso (modulo='dump_units', caso='push imm8')`, mais o
      teste dos mapas de opcode
- [x] `make -C wte check` verde — **76** testes
- [x] `python3 wte/tools/dump_units.py --check` e
      `python3 wte/tools/dump_strings.py --check` verdes
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

O `test_dump_strings.py` passou a importar os dois módulos e a rodar a tabela de
comprimento contra os dois `decode()`, por `subTest(modulo=...)` — 66 casos ×
2. A conferência contra o `objdump` **não** dobrou: ela é cara e já cobre o
algoritmo; o que dobra é a tabela barata, como a CORR pede.

`TestCopiaVerbatim` compara o texto-fonte de `_fill`, `decode` e `extent` entre
os dois arquivos por `inspect.getsource`, e falha com `unified_diff` e a
mensagem dizendo que uma das cópias mudou e que a outra precisa da mesma
mudança — nomeando o que a do `dump_units.py` sustenta.

**Uma coisa a mais do que a CORR pediu, e ela era necessária:** `_fill`
idêntico **não basta**. O mapa de opcodes é montado por 47 chamadas ao nível do
módulo, fora de qualquer função, e `inspect.getsource` não as alcança — trocar
`_MAP1[0x6A]` num arquivo só passaria pelo teste de identidade. Um segundo caso
compara `_MAP1`, `_MAP2` e `PREFIXES` já montados. Foi ele, junto com a tabela
parametrizada, que pegou a mutação A.

O teste de identidade **não** substitui a duplicação por um módulo comum: a
decisão de cada gerador rodar sozinho está no `wte/README.md` e vale igual para
o leitor de PE, que aparece em cinco arquivos. Esta correção não a reabre — põe
uma guarda sobre o preço dela.

**Problemas encontrados:**

Nenhum. Os dois critérios foram exercitados com divergência plantada numa cópia
em sandbox: comprimento errado só no `dump_units.py` reprova a tabela **e** o
teste dos mapas; `decode()` alterado só ali reprova a identidade com o diff.

**Arquivos criados/modificados:**

- `wte/tools/test_dump_strings.py` — os dois módulos na tabela, e
  `TestCopiaVerbatim`
- `wte/tools/README.md` — a linha da tabela de testes e a seção "Código
  duplicado entre geradores tem de ter guarda"
- `docs/tasks/07-unidades-duvidosas.md` — o Log aponta para esta correção
- `docs/tasks/correcoes-progresso.md`
