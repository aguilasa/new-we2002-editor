---
id: CORR-WTE-035
title: "Correção: a decisão 5 do `tipos.md` não tem o \"teste que prova\", e o critério que o exige está marcado"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-035: quatro das cinco decisões têm teste nomeado; a do `_url.txt` não

## Problema identificado

O critério de conclusão da
[WTE-TASK-15](/docs/tasks/15-mapeamento-de-tipo.md) traz:

> - [x] Cada decisão com o teste que a prova nomeado

[`wte/re/tipos.md`](../../wte/re/tipos.md) tem cinco decisões e **quatro**
blocos "Teste que prova". A que ficou sem é a decisão 5 — o sidecar `_url.txt`
por `TFileStream` com `#10` à mão, em vez de `TStringList`.

É a decisão com o menor custo de teste e o maior custo de erro silencioso das
cinco: `TStringList.SaveToFile` usa o `LineEnding` da plataforma e tem
`WriteBOM`, então um deslize ali reescreve **arquivo do usuário** com CRLF ou
com BOM UTF-8 na primeira linha, e nada na tela do editor denuncia. O
`newWe2002` já registra em `CLAUDE.md` que esse sidecar não pode ser desligado
junto com o SoFIFA, exatamente porque a gravação o trunca se for tratada por
alto.

Não há como afirmar o critério enquanto a quinta decisão não nomear o seu teste.

## Evidência

```console
$ grep -n '^## Decisão' wte/re/tipos.md
66:## Decisão 1 — `char[N]` não pode virar `string`, e o `strcpy` vem junto
95:## Decisão 2 — bitfield: acessor por máscara e deslocamento, não `bitpacked`
130:## Decisão 3 — `CdImage`: `TFileStream`, e `Read` nunca `ReadBuffer`
166:## Decisão 4 — `char` numérico é `ShortInt`, e `Byte` estaria errado
191:## Decisão 5 — o sidecar `_url.txt` é byte a byte, e por isso não é `TStringList`

$ grep -n 'Teste que prova' wte/re/tipos.md
88:> **Teste que prova:** `raw_formation` com 30 bytes sem `#0` na entrada — a
120:> **Teste que prova, e são dois.** (a) O mesmo vetor do
160:> **Teste que prova:** ler 64 bytes a 32 do fim de um arquivo temporário —
186:> **Teste que prova:** gravar `$C8` (200) num byte de posição e conferir que o
```

Cinco decisões, quatro testes; a decisão 5 vai da linha 191 ao fim da seção sem
um.

O que o lado C++ faz, e que o teste tem de fixar:

```console
$ sed -n '1453,1459p' src/core/Database.cpp
		std::ofstream url_file;
	url_file.open(UrlSidecarPath(image), std::ios::trunc);
	for(i=0;i<PLAYERS_TOTAL;i++)
	{
		url_file << players[i].url << std::endl;
	}
	url_file.close();
```

`PLAYERS_TOTAL` é 1.911 (`Types.hpp:12`), e `std::endl` no Linux é um `#10` só.

## Causa raiz

A decisão 5 apareceu por último, fora das três previstas pelo enunciado, e o
bloco de teste que as outras quatro receberam não foi escrito para ela.

## Correção

### Arquivo: `wte/re/tipos.md`

Acrescentar ao fim da decisão 5 o bloco no mesmo formato das outras quatro:

> **Teste que prova:** gerar o sidecar de uma base com URL conhecida e conferir
> **em bytes**, não em linhas — o arquivo tem 1.911 ocorrências de `#10`, nenhum
> `#13`, nenhum BOM nos três primeiros bytes, e termina em `#10`. Comparar
> `cmp` contra o arquivo que o `we2002_core` grava para a mesma base.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/tipos.md` | modificar |
| `docs/tasks/15-mapeamento-de-tipo.md` | modificar (o critério que estava marcado) |

## Verificação

- [x] `grep -c 'Teste que prova' wte/re/tipos.md` dá 5, contra 5 decisões
- [x] O teste da decisão 5 diz o que contar: `#10`, ausência de `#13`, ausência
      de BOM, e o `cmp` contra o lado C++
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A decisão 5 ganhou o bloco "Teste que prova" no mesmo formato das outras quatro,
em bytes: 1.911 ocorrências de `#10` (`PLAYERS_TOTAL`, `Types.hpp:12`), nenhum
`#13`, nenhum BOM nos três primeiros bytes, término em `#10`, e `cmp` contra o
sidecar que o `we2002_core` grava para a mesma base. Foi escrito por que o teste
é em byte e não em linha: `TStringList` com `LineEnding` de Windows ou com
`WriteBOM` ligado produz as mesmas 1.911 linhas e passa num teste de contagem —
reescrevendo arquivo do usuário sem nada denunciar na tela.

`grep -c 'Teste que prova'` agora dá 5, contra 5 `## Decisão`.

**Problemas encontrados:**

Nenhum. O critério "Cada decisão com o teste que a prova nomeado" da WTE-TASK-15
continuava `[x]` afirmando algo que só agora é verdade; ficou com a ressalva
datada e o ponteiro para esta correção, em vez de ser desmarcado — o estado que
o `[x]` descreve existe a partir deste commit.

**Arquivos criados/modificados:**

- `wte/re/tipos.md`
- `docs/tasks/15-mapeamento-de-tipo.md`
