---
id: CORR-WTE-032
title: "Correção: a \"regra zero\" do `tipos.md` proíbe `LongInt` e `SizeInt` em campo de registro, e a tabela usa os dois"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-WTE-032: o documento que governa os dois geradores se contradiz na primeira seção

## Problema identificado

A seção "Regra zero" de [`wte/re/tipos.md`](../../wte/re/tipos.md) fecha assim:

> `Integer`, `Cardinal`, `PtrInt`, `PtrUInt`, `NativeInt`, `SizeInt` e
> `LongInt` **não são equivalentes** em FPC. […] **Nenhum deles entra em campo
> de registro nem em variável que toque a imagem.**

"Nenhum deles" alcança os sete nomes da lista, e dois deles são usados na
tabela logo abaixo:

- `std::int32_t`, `int` → **`LongInt`**, com o motivo "os 30 atributos de
  `Player`". Esses 30 atributos são campos de registro, e o `Load()`/`Save()`
  os lê e grava da imagem: é exatamente o que a frase proíbe.
- `std::size_t` → **`SizeInt`**, com a ressalva "**só** na fronteira do
  `CdImage`; nunca em campo de registro". A fronteira do `CdImage` é a contagem
  de bytes lidos e escritos — variável que toca a imagem, também proibida pela
  frase.

Não é preciosismo de redação. Este arquivo é a **fonte para os geradores** (o
próprio plano diz isso, §Fase 3 item 2), e a WTE-TASK-17/18 tem de escolher
entre duas instruções que se anulam. Pior: quem escolher pela regra zero vai
procurar substituto para `LongInt` nos 30 atributos e mexer no que já estava
certo — `LongInt` em FPC é 32 bits com sinal em todas as plataformas suportadas
nos modos que o projeto usa, que é o motivo de ele estar na tabela e é o que a
linha seguinte da própria regra zero afirma.

## Evidência

A contradição, nas duas pontas do mesmo arquivo:

```
$ sed -n '21,30p' wte/re/tipos.md
## Regra zero: nada de tipo cujo tamanho dependa da plataforma

`Integer`, `Cardinal`, `PtrInt`, `PtrUInt`, `NativeInt`, `SizeInt` e `LongInt`
**não são equivalentes** em FPC. `Integer` é 16 bits em `{$mode tp}`;
`PtrInt`/`NativeInt` seguem o ponteiro; `SizeInt` idem. Nenhum deles entra em
campo de registro nem em variável que toque a imagem.

Os tipos usados abaixo são todos de largura fixa por definição do FPC:
`Byte` (8), `ShortInt` (8, com sinal), `Word` (16), `LongWord` (32),
`LongInt` (32, com sinal), `Int64` (64), `AnsiChar` (8), `Double` (64).
```

A linha 30 declara `LongInt` de largura fixa; a linha 25 o lista entre os que
"não entram em campo de registro". As duas afirmações não podem valer juntas
com a tabela:

```
$ grep -n 'LongInt\|SizeInt' wte/re/tipos.md
23:`Integer`, `Cardinal`, `PtrInt`, `PtrUInt`, `NativeInt`, `SizeInt` e `LongInt`
25:`PtrInt`/`NativeInt` seguem o ponteiro; `SizeInt` idem. Nenhum deles entra em
30:`LongInt` (32, com sinal), `Int64` (64), `AnsiChar` (8), `Double` (64).
41:| `std::int32_t`, `int` | `LongInt` | os 30 atributos de `Player` |
46:| `std::size_t` | `SizeInt` | **só** na fronteira do `CdImage`; nunca em campo de registro |
216:  1. Largura fixa em tudo que toca a imagem; `Integer`/`Cardinal`/`PtrInt`
217:     proibidos por regra, não por gosto.
```

O resumo da linha 216 já lista **três** proibidos, não sete — é a redação certa,
e a divergência com a linha 23 mostra que a lista de cima cresceu por descuido.

Os 30 atributos são campos de registro que atravessam a imagem:

```
$ grep -c '^    int ' src/core/include/we2002/Player.hpp
30
```

## Causa raiz

A lista da regra zero juntou "tipos que não são equivalentes entre si" com
"tipos proibidos", e `LongInt` e `SizeInt` pertencem só à primeira.

## Correção

### Arquivo: `wte/re/tipos.md`

Separar as duas ideias, alinhando a regra zero ao resumo da linha 216:

> `Integer`, `Cardinal`, `PtrInt`, `PtrUInt` e `NativeInt` **não entram em campo
> de registro nem em variável que toque a imagem**: `Integer` é 16 bits em
> `{$mode tp}` e `PtrInt`/`NativeInt` seguem o ponteiro.
>
> `SizeInt` também segue o ponteiro e vale a mesma proibição, **com uma exceção
> escrita**: contagem de bytes na fronteira do `CdImage`, onde ele é o tipo de
> retorno de `TStream.Read`/`Write` e nunca é gravado.
>
> `LongInt` **não** está nessa lista: em FPC ele é 32 bits com sinal em todas as
> plataformas suportadas, e é o mapeamento de `int`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/tipos.md` | modificar |

## Verificação

- [ ] A regra zero e o resumo do fim do arquivo listam o **mesmo** conjunto de
      proibidos
- [ ] `LongInt` não aparece mais como proibido em nenhum ponto do arquivo
- [ ] A exceção de `SizeInt` está escrita onde ela é enunciada, não só na
      célula da tabela
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
