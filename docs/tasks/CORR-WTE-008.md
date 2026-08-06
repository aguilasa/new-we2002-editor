---
id: CORR-WTE-008
title: "Correção: o decodificador de instrução x86 do dump_strings.py só foi conferido à mão, e a coluna `handler` inteira depende dele"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-008: a conferência que sustenta a coluna `handler` não tem rota de volta

## Problema identificado

A coluna `handler` do [`strings.tsv`](../../wte/re/strings.tsv) não sai de nenhuma
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
[CORR-WTE-002](/docs/tasks/CORR-WTE-002.md).

E agora existe onde escrever o teste: a
[CORR-WTE-005](/docs/tasks/CORR-WTE-005.md) criou a convenção
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
[`test_dfm_extract.py`](../../wte/tools/test_dfm_extract.py). Duas metades:

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

- [ ] `python3 -m unittest wte.tools.test_dump_strings` (ou o alvo `test` do
      Makefile) verde
- [ ] A metade sem `.exe` roda com o binário do Obocaman ausente
- [ ] A conferência contra o `objdump` afirma **10.416** fronteiras coincidentes
      e falha se uma divergir
- [ ] Um comprimento plantado errado na tabela de opcodes **reprova** o teste
- [ ] `python3 wte/tools/dump_strings.py --check` verde depois de regerar o `.md`
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
