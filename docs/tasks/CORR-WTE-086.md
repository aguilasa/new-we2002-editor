---
id: CORR-WTE-086
title: "Correção: o dono do ficha_enlaza não é o pabajoClick — nenhuma spec ou código liga os dois"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-086: o dono do `ficha_enlaza` não é o `pabajoClick`

## Problema identificado

A [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md), na seção viva
*"E a resposta dos dois é a mesma, medida"*, justifica o veredito `trivial` do
`ficha_enlaza` e do `ficha_movertodos` dizendo que **quem toca dados é o
chamador**, e nomeia dois:

> O desvincular está no `pabajoClick` e vizinhos e o mover em lote no
> `MoveTodosOsJogadores` do `ep2002_mainform.aux.inc`, os dois lendo `mrYes` do
> modal.

A **metade do `movertodos` está certa e se verifica**. A do `ficha_enlaza`
**não**: o `pabajoClick` não menciona vínculo em lugar nenhum — nem na spec,
nem no `.inc` —, e nenhum arquivo do `wte/src/` mostra o `ficha_enlaza`. O
único documento que nomeia um chamador para ele é a spec do
`MainForm.mostrar_jugadorClick`, que continua `aberto`.

O veredito `trivial` dos dois handlers do `ficha_enlaza` **não muda** — o
`.dfm` realmente não tem `OnClick` nos botões, só `ModalResult = 6/7`. O que
está errado é a atribuição de dono, e ela importa: escrita como está, faz
parecer que a rota de vínculo já tem dono fechado, quando ela mora num handler
que ninguém fechou.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "enlaza\|vincul" wte/re/spec/MainForm.pabajoClick.md
grep -rn "enlaza" wte/src/impl/*.inc
grep -rn "enlaza" wte/re/spec/*.md | grep -v '^wte/re/spec/ficha_enlaza'
```

```text
(as duas primeiras não imprimem nada)
wte/re/spec/INDICE.md:40:| `0x00402c44` | `ficha_enlaza` | [FormShow](ficha_enlaza.FormShow.md) | OnShow | carga | trivial |
wte/re/spec/INDICE.md:41:| `0x00402c54` | `ficha_enlaza` | [FormCreate](ficha_enlaza.FormCreate.md) | OnCreate | carga | trivial |
wte/re/spec/MainForm.mostrar_jugadorClick.md:42:O `ficha_enlaza` também é alcançado — é o diálogo de confirmação de vínculo,
```

A metade que fecha, para contraste:

```bash
grep -rn "mrYes" wte/src/impl/*.inc | grep -i "movertodos\|paderecha"
```

```text
wte/src/impl/ep2002_mainform.paderecha2Click.inc:8:  1. abre o `ficha_movertodos` como modal e so segue com `mrYes`;
wte/src/impl/ep2002_mainform.aux.inc:864:  if ficha_movertodos.ShowModal <> mrYes then
```

E o `.dfm`, que sustenta o veredito `trivial` e continua correto:

```bash
grep -aE "ModalResult|OnClick" wte/re/dfm/ficha_enlaza.dfm
```

```text
    ModalResult = 6
    ModalResult = 7
```

## Causa raiz

O par `ficha_enlaza`/`ficha_movertodos` foi respondido junto — os dois são
janela sem `OnClick` — e o chamador do segundo, que estava medido, foi escrito
como se valesse para os dois.

## Correção

### Arquivo: `docs/tasks/30-handlers-auxiliares.md`

Na seção *"E a resposta dos dois é a mesma, medida"*, separar as duas metades:
o `ficha_movertodos` sai do `paderecha2Click` / `MoveTodosOsJogadores`, com o
`mrYes` medido; o `ficha_enlaza` é alcançado pelo
[`MainForm.mostrar_jugadorClick`](../../wte/re/spec/MainForm.mostrar_jugadorClick.md),
que continua `aberto` — e é ali, não aqui, que a rota de vínculo será fechada.

Vale escrever o que **não** foi medido: qual condição faz o
`mostrar_jugadorClick` abrir o `ficha_enlaza` (a spec diz "quando o jogador
escolhido é de clube de Master League", sem endereço de teste), e o que o
chamador faz com o `mrYes`.

### Arquivo: `wte/re/spec/ficha_enlaza.FormShow.md`

Acrescentar a linha de quem abre o formulário, como as specs dos outros modais
já fazem — é o que teria evitado a atribuição errada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/30-handlers-auxiliares.md` | modificar |
| `wte/re/spec/ficha_enlaza.FormShow.md` | modificar |

## Verificação

- [ ] `grep -n "pabajoClick" docs/tasks/30-handlers-auxiliares.md` não aparece
      mais ligado ao `ficha_enlaza`
- [ ] A spec do `ficha_enlaza.FormShow` nomeia o chamador, e o nome bate com
      `grep -rn "enlaza" wte/re/spec/*.md`
- [ ] `make -C wte check` continua verde (o `spec_index.py` reindexa)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
