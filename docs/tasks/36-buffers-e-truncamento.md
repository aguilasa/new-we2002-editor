---
id: WTE-TASK-36
title: "Buffers de tamanho fixo e comportamento de truncamento"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-26", "WTE-TASK-34"]
status: pendente
---

# WTE-TASK-36: Buffers e truncamento

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 3.
- **A classe de bug invertida.** O Pascal com strings gerenciadas não tem
  estouro de buffer — mas o original **pode depender** de truncamento
  silencioso, e o Pascal não vai reproduzi-lo por acidente.

Precedente medido no `newWe2002`, e ele mostra o quanto isso é sutil: com `-O2`
a glibc liga `_FORTIFY_SOURCE`, e um `strcpy` estourava **um byte** em toda
imagem aberta (`raw_formation[30]` recebendo 30 bytes mais terminador). O editor
morria com `*** buffer overflow detected ***` antes de qualquer coisa aparecer.
Invisível em Debug. Só apareceu em Release.

O original do Obocaman é C++Builder, com `char` fixo, e o mesmo padrão.

> **Entrada aberta pela [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md)
> em 2026-08-25 — esta task é a dona do último item em aberto do registro de
> divergências.**
>
> A 35 fechou com **seis** divergências deliberadas registradas e as quatro
> candidatas do enunciado dela decididas. Sobrou **uma** linha aberta, e é esta:
> *"comportamento de truncamento de campo, se o Pascal não reproduzir o do
> buffer fixo"*. Está na §7 do
> [`wte/re/divergencias.md`](../../wte/re/divergencias.md) como **em aberto, com
> dono** — que é o que separa pendência de buraco.
>
> **O que a 36 deve devolver para a 35, e em que forma.** Se algum campo
> divergir e a decisão for não reproduzir o truncamento do original, a entrada
> **nasce aqui e volta para o `divergencias.md`** com os seis campos que ele
> usa: o que diverge, natureza, decisão, razão, evidência, e *onde o teste
> sabe*. Se nenhum divergir, a linha da §7 vira "conferido, não é divergência",
> como as outras três candidatas.
>
> **E se a régua ganhar exceção nomeada, ela tem de passar pelo
> [`check_divergencias.py`](../../wte/tools/check_divergencias.py):** isenção que
> faz um teste deixar de reprovar precisa da entrada correspondente, e o gate
> aborta nos dois sentidos. A 35 achou uma isenção (`pendente_32`) que tinha
> sobrevivido à própria causa por duas tasks; a guarda existe para isso não se
> repetir.

---

## Objetivo

Inventariar todo campo de tamanho fixo e provar que o app se comporta como o
original nas bordas.

### O inventário

Sai de duas fontes que precisam concordar:

1. **A camada de dados** (WTE-TASK-18) — todo `array[0..N-1] of AnsiChar`, com
   o `N`.
2. **As specs de edição** (WTE-TASK-26) — todo campo com `MaxLength` no DFM ou
   validação no handler.

Discordância é achado: campo com `MaxLength` 20 gravando em array de 16 é bug
esperando a entrada certa.

### Os testes de borda, por campo

| Entrada | O que verificar |
|---|---|
| exatamente `N` caracteres | grava íntegro, sem terminador comendo o vizinho |
| `N+1` caracteres | trunca? recusa? o que os dois lados fazem |
| string vazia | grava o quê — zeros, espaços, valor anterior |
| caractere fora do conjunto | o codec de texto aceita? |

O caso `N` exato é o que pegou o `newWe2002`, e é o mais fácil de não testar.

### A ROM japonesa

`KanjiToAscii`/`AsciiToKanji` mudam o tamanho em bytes de um nome. Um campo que
cabe em latim pode estourar em Shift-JIS. Testar as bordas **nas duas ROMs**,
não só na europeia.

### Verificação

Golden test por campo, com entrada de borda, nos dois lados. Divergência que
sobreviver vai para a WTE-TASK-35.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/buffers.md` | criar — inventário e comportamento por campo |
| `wte/tests/test_bordas.pas` | criar |
| `wte/tools/roteiros/borda-*.sh` | criar |

---

## Critério de conclusão

- [ ] Inventário completo, com as duas fontes conciliadas
- [ ] Os quatro casos de borda testados por campo
- [ ] Bordas testadas também na ROM japonesa
- [ ] Comportamento do original reproduzido, ou divergência registrada
      **no `wte/re/divergencias.md`, com os seis campos** — e a linha da §7
      de lá fechada num dos dois sentidos (ver o Contexto)
- [ ] Nenhum campo sem entrada no inventário
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
