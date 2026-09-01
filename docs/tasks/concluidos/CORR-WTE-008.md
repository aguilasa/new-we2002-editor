---
id: CORR-WTE-008
title: "Correção: o decodificador de instrução x86 do dump_strings.py só foi conferido à mão, e a coluna `handler` inteira depende dele"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-008: a conferência que sustenta a coluna `handler` não tem rota de volta

## Problema identificado

A coluna `handler` do [`strings.tsv`](../../../wte/re/strings.tsv) não sai de nenhuma
tabela do binário: ela sai de **medir onde cada um dos 96 handlers termina**, e
isso exige um decodificador de comprimento de instrução x86-32 escrito à mão em
`wte/tools/dump_strings.py` (`decode()`, `extent()`, ~200 linhas de tabela de
opcode).

O próprio `strings.md` explica por que isso é delicado, e diz que a conferência
não é reproduzível:

> O decodificador não é um detalhe de implementação — se ele errar o comprimento
> de uma instrução, todas as extensões depois dela ficam erradas em silêncio. Foi
> conferido contra o `objdump` [...]
> **Essa conferência é manual e não roda no `--check`**; o que roda no `--check` é
> a consequência dela, que são os números desta página.

A ressalva é honesta e o resultado está certo — esta revisão o reproduziu. O
problema é que reproduzi-lo exigiu **reescrever o arranjo de comparação**, e a
primeira tentativa deu falso positivo (48 "divergências" que eram linhas de
continuação do `objdump`, sem mnemônico). Um número que só volta assim é um
número sem rota de volta, como o da
[CORR-WTE-002](/docs/tasks/concluidos/CORR-WTE-002.md).

E agora existe onde escrever o teste: a
[CORR-WTE-005](/docs/tasks/concluidos/CORR-WTE-005.md) criou a convenção
`wte/tools/test_<gerador>.py`, com o alvo `test` do qual o `check` depende. Na
WTE-TASK-05 essa convenção ainda não existia.

O que cai junto se o decodificador errar um comprimento: a coluna `handler` das
474 referências, os 122 pares string↔handler, a cobertura de 26,8% da `.text`, a
tabela inteira da pergunta 2 e a concentração em `MainForm` da pergunta 3 — tudo
em silêncio, porque uma extensão errada não parece errada.

## Evidência

A conferência **reproduz**, refeita nesta revisão com harness próprio
(`m.extent()` + `m.decode()` contra `objdump -D -b binary -m i386`, corpo a
corpo, `.text` recortada para arquivo):

```
handlers lidos do TSV: 96
corpos: 96 | bytes: 36983 | menor: 1 | maior: 2378
instrucoes pelo script: 10416
instrucoes pelo objdump: 10464
iguais: False | so no script: 0 | so no objdump: 48
```

As 48 são artefato do harness, não do decodificador — linhas de continuação que
o `objdump` emite para instrução longa, com endereço e **mnemônico vazio**:

```
0x402b47 objdump[00 00 00      ]        (sem mnemonico)  | script: 0x402b40 len=10
0x408587 objdump[00            ]        (sem mnemonico)  | script: 0x408580 len=8
Counter({'': 48})
```

Filtrando-as: **10.416 contra 10.416, zero divergência** — exatamente o que o
`strings.md` afirma. O ponto é que essa armadilha custou uma iteração para quem
já sabia a resposta.

Os dois abortos do decodificador respondem, testados com bytes plantados:

```
0f 0f (3dnow):  ABORT -> opcode 0f0f em 0x0 nao esta no mapa deste decodificador
truncado (b8 01): ABORT -> a instrucao em 0x0 atravessa o limite 0x2
```

E um caso que **não** aborta, medido: `ff ff` (que o `objdump` chama `(bad)`)
volta com `len=2` e mnemônico vazio. Não ocorre dentro dos 96 corpos, então não
contamina medida nenhuma hoje — mas é o tipo de silêncio que o teste deve fixar.

## Causa raiz

A conferência do decodificador foi feita antes de o repositório ter lugar para
teste de ferramenta Python, e ficou como parágrafo em vez de arquivo.

## Correção

### Arquivo: `wte/tools/test_dump_strings.py`

`unittest` de stdlib pura, no molde do
[`test_dfm_extract.py`](../../../wte/tools/test_dfm_extract.py). Duas metades:

1. **Comprimento por caso, sem o `.exe`.** Uma tabela de (bytes, comprimento
   esperado) cobrindo o que a `.text` do Obocaman exercita e o que ela não
   exercita: prefixos (`66`, `67`, `f2`, `f3`, `lock`), `modrm` com SIB e
   deslocamento de 0/1/4 bytes, imediato dependente de prefixo de tamanho de
   operando, saltos curtos e longos, `0f`-escape, e os dois abortos acima. Esta
   metade roda em qualquer máquina e é a que pega regressão de verdade.
2. **A conferência contra o `objdump`, versionada e opcional.** Um teste que se
   declara `skipUnless(shutil.which("objdump") and EXE.is_file())`, refaz o
   recorte da `.text`, roda o `objdump` corpo a corpo e compara os conjuntos de
   fronteira — **descartando as linhas sem mnemônico**, que é a armadilha
   documentada acima. Assertiva: `10416 == 10416` e conjuntos idênticos.

O `skipUnless` é o que mantém a regra do `test_dfm_extract.py` ("não abre o
`.exe`") de pé para a bateria padrão, sem jogar fora a única conferência
externa que o projeto tem do decodificador.

### Arquivo: `wte/re/strings.md`

A frase "essa conferência é manual e não roda no `--check`" deixa de valer.
Como o arquivo é **gerado**, o texto entra no `render_md()` do
`dump_strings.py`, apontando para o teste.

### Arquivo: `wte/tools/README.md`

Uma linha na tabela de testes, ao lado da do `test_dfm_extract.py`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_dump_strings.py` | criar |
| `wte/tools/dump_strings.py` | modificar — o texto da conferência em `render_md()` |
| `wte/re/strings.md` | regerar (nunca editar à mão) |
| `wte/tools/README.md` | modificar |

## Verificação

- [x] `python3 -m unittest wte.tools.test_dump_strings` (ou o alvo `test` do
      Makefile) verde — **17 casos**, e `make -C wte test` passou de 43 para 60
- [x] A metade sem `.exe` roda com o binário do Obocaman ausente — medido numa
      cópia em árvore onde `EXE.is_file()` é falso: `OK (skipped=2)`
- [x] A conferência contra o `objdump` afirma **10.416** fronteiras coincidentes
      e falha se uma divergir
- [x] Um comprimento plantado errado na tabela de opcodes **reprova** o teste —
      oito mutações, oito reprovadas
- [x] `python3 wte/tools/dump_strings.py --check` verde depois de regerar o `.md`
- [x] `make -C wte check` verde
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

`wte/tools/test_dump_strings.py`, 17 casos, no molde do `test_dfm_extract.py`.
Duas metades, como a CORR pede:

1. **Comprimento por caso**, sem `.exe` e sem `objdump`: 66 entradas de
   (bytes, comprimento, classe de fluxo) cobrindo prefixos (`66`, `f2`, `f3`,
   `lock`, segmento, dois encadeados), os quatro modos de ModRM com e sem SIB,
   `disp` de 0/1/4 bytes, SIB com base=5, imediato que segue o prefixo de
   tamanho de operando, o grupo 3 (`f6`/`f7`, imediato só no `/0` e no `/1`),
   saltos curtos e longos, o escape `0f`, x87 e ponteiro far. Mais os **sete
   abortos**, o `ff ff` que **não** aborta, o alvo de cada desvio relativo, e
   quatro casos de `extent()` — inclusive o que a regra do teto de alvos
   existe para acertar: `ret` no meio do corpo com desvio apontando além dele
   **não** encerra a função.
2. **A conferência contra o `objdump`**, atrás de
   `skipUnless(objdump e .exe e published_methods.tsv e re/dfm)`. Recorta a
   `.text`, roda corpo a corpo e compara conjuntos de fronteira. Afirma
   `10416 == 10416`, `36.983` bytes nos 96 corpos (menor 1, maior 2378), e
   **48** linhas de continuação descartadas — a armadilha documentada. Afirmar
   o 48 é deliberado: se virar outro número, o recorte mudou e a comparação
   merece um olhar.

O texto da conferência saiu do `render_md()` e do docstring do módulo: a frase
"essa conferência é manual e não roda no `--check`" deixou de valer.

**Problemas encontrados:**

Um erro meu, pego pelo próprio teste: escrevi que `eb fe` tem alvo 1. É 0 — o
deslocamento −2 aponta para a própria instrução, o autoloop clássico.

A varredura de mutação enganou-me primeiro. Duas das oito passaram como "OK"
até eu conferir à mão: as duas trocavam bytes de **mesmo tamanho**
(`(False, 1)` → `(False, 2)`), e com mtime colidindo no mesmo segundo o
CPython reusou o `__pycache__` obsoleto. Com `python3 -B` as oito reprovam.
Vale a lição para a próxima varredura de mutação neste repositório.

A regra que a CORR-WTE-005 escreveu no `wte/tools/README.md` — "o teste **não
abre o `.exe`**" — ficou falsa com este arquivo. Reescrita para o que
realmente vale: *a bateria padrão* não depende do `.exe`, e caso que precise
dele ou de ferramenta externa vai atrás de `skipUnless`, nunca solto. Pular é
o desfecho certo onde falta o insumo; falhar ensinaria a ignorar vermelho, e
jogar a conferência fora devolveria o número à memória de quem o mediu.

**Arquivos criados/modificados:**

- `wte/tools/test_dump_strings.py` — criado
- `wte/tools/dump_strings.py` — o texto da conferência em `render_md()` e no
  docstring do módulo
- `wte/re/strings.md` — regerado
- `wte/tools/README.md` — a linha na tabela de testes e a regra do `.exe`
- `docs/tasks/concluidos/correcoes-progresso.md`
