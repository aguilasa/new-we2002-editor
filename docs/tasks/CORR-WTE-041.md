---
id: CORR-WTE-041
title: "Correção: o `spec_index.py` tem 15 rotas de recusa, e o README chama as onze testadas de \"as\" rotas"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-041: quatro rotas de recusa sem teste de regressão

## Problema identificado

O [`wte/tools/README.md`](../../wte/tools/README.md), linha 49, descreve o
teste:

> `test_spec_index.py` ✅ | **as onze rotas de recusa** do `spec_index.py`
> sobre specs sintéticas […]

São onze testes de recusa, e eles passam. Mas o validador tem **15** sítios de
`raise SpecError`, e o artigo definido ("as onze rotas") diz que essas são
todas — o leitor da fase 4 conclui que a superfície de recusa está coberta.

Sem teste ficam quatro rotas, todas em `le_handlers()`/`le_frontmatter()`:

| Rota | Onde | Testada |
|---|---|---|
| TSV não existe | `spec_index.py:84` | não |
| TSV sem nenhum handler | `spec_index.py:93` | não |
| frontmatter não fechado com `---` | `spec_index.py:102` | não |
| linha de frontmatter sem `:` | `spec_index.py:108` | não |
| chave obrigatória ausente (`veredito`, `endereco`, …) | `spec_index.py:148` | não |

A última é a que importa: uma spec sem `veredito:` é conteúdo, não infra, e é
o erro mais provável de quem escrever a primeira spec de verdade na
WTE-TASK-25. O teste que existe para frontmatter
(`test_recusa_sem_frontmatter`) cobre só o caso do arquivo que **não começa**
com `---`.

**As quatro rotas funcionam** — foram exercitadas à mão nesta revisão, e as
mensagens saem certas. O que falta é regressão: nada impede que a próxima
mexida em `le_frontmatter` as apague em silêncio, e o `--check` continuaria
verde porque hoje não há uma única spec no disco.

## Evidência

Contagem dos sítios:

```
$ grep -c "raise SpecError" wte/tools/spec_index.py
15
```

Rotas exercitadas à mão, com `RAIZ`/`TSV`/`SPEC` remapeados para um diretório
temporário como o próprio teste faz:

```
recusa ok (veredito ausente): MainForm.lista_equiposChange.md: falta 'veredito' no frontmatter
recusa ok (nao fechado):      MainForm.lista_equiposChange.md: frontmatter nao fechado com ---
recusa ok (TSV ausente):      …/published_methods.tsv nao existe -- rode a WTE-TASK-04 antes
```

Os onze testes de recusa que existem, todos verdes (19 testes no arquivo,
`Ran 19 tests … OK`): bloco `c`, nomes do Ghidra (sete formas em `subTest`),
veredito fora do vocabulário, seção faltando, seção sem evidência, evidência
inventada, `nao portado` sem justificativa, `implementado` só com observação de
tela, frontmatter discordando do TSV, spec órfã, arquivo sem frontmatter.

## Causa raiz

O README contou os testes escritos, não os sítios de recusa do gerador; as
rotas de leitura de arquivo (TSV e frontmatter) ficaram fora da conta e fora do
teste.

## Correção

### Arquivo: `wte/tools/test_spec_index.py`

Acrescentar os casos que faltam — no mínimo o do frontmatter sem a chave
`veredito` e o do frontmatter não fechado, que são as rotas de conteúdo. As
duas de TSV (ausente, vazio) são baratas de plantar no mesmo `Base`, já que ele
escreve o TSV no `setUp`.

### Arquivo: `wte/tools/README.md`

Trocar "as onze rotas de recusa" pelo número que ficar depois dos testes novos,
e dizer que é a contagem de `raise SpecError` do gerador — para a próxima
revisão poder remedir com `grep -c` em vez de recontar teste.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_spec_index.py` | modificar |
| `wte/tools/README.md` | modificar |

## Verificação

- [ ] `grep -c "raise SpecError" wte/tools/spec_index.py` bate com o número
      escrito no `README.md`
- [ ] Cada rota nova falha com a mensagem própria, não com `KeyError`
- [ ] `cd wte/tools && python3 -m unittest test_spec_index -v` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
