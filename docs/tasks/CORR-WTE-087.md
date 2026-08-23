---
id: CORR-WTE-087
title: "Correção: o Log da WTE-TASK-30 conta 12 .inc novos e 6 .uses tocados; são 11 e 5"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-087: o Log da WTE-TASK-30 conta 12 `.inc` novos, e são 11

## Problema identificado

Na lista de arquivos criados/modificados da
[WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md):

> `wte/src/impl/` — 12 `.inc` novos e 6 `.uses` tocados; o
> `ep2002_mainform.colorearClick.inc` ganhou a foto do slot 0

Medido no commit que fechou a task (`fb640cd`): **11** `.inc` novos e **5**
`.uses` tocados (um novo, quatro modificados). O `colorearClick.inc` — citado
na mesma frase — é **modificado**, não novo, e é ele que faz o total de corpos
tocados dar doze; contado como `.inc` novo, vira doze duas vezes.

O próprio Log corrobora o 11 por outro caminho: a linha de "Escrito à mão" do
[`wte/re/fase-2.md`](../../wte/re/fase-2.md), regerada no mesmo commit, foi de
**83 para 94 arquivos** — onze.

Nada quebra por causa disso; o que se perde é a única conta que permite
reconstituir o que a task entregou sem abrir o commit.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git show --diff-filter=A --name-only --format= fb640cd -- 'wte/src/impl/*'
git show --diff-filter=M --name-only --format= fb640cd -- 'wte/src/impl/*'
```

```text
== adicionados (12 arquivos, dos quais 11 .inc) ==
wte/src/impl/ep2002_about.imagen_urlClick.inc
wte/src/impl/ep2002_color.BitBtn1Click.inc
wte/src/impl/ep2002_color.BitBtn2Click.inc
wte/src/impl/ep2002_color.SpeedButton1Click.inc
wte/src/impl/ep2002_dorsal.BitBtn1Click.inc
wte/src/impl/ep2002_error.SpeedButton1Click.inc
wte/src/impl/ep2002_error.uses          <- .uses, nao .inc
wte/src/impl/ep2002_jugador.BitBtn2Click.inc
wte/src/impl/ep2002_mainform.Image3Click.inc
wte/src/impl/ep2002_mainform.SpeedButton1Click.inc
wte/src/impl/ep2002_mainform.SpeedButton2Click.inc
wte/src/impl/ep2002_mainform.base_teamClick.inc

== modificados ==
wte/src/impl/ep2002_about.uses
wte/src/impl/ep2002_color.uses
wte/src/impl/ep2002_dorsal.uses
wte/src/impl/ep2002_mainform.colorearClick.inc
wte/src/impl/ep2002_mainform.uses
```

E a confirmação independente, no mesmo commit:

```bash
git show fb640cd -- wte/re/fase-2.md | grep -E '^[-+]\| Escrito à mão'
```

```text
-| Escrito à mão | 83 | 6476 |
+| Escrito à mão | 94 | 6816 |
```

| Afirmado no Log | Medido | Fonte da medição |
|---|---|---|
| 12 `.inc` novos | 11 | `git show --diff-filter=A` |
| 6 `.uses` tocados | 5 (1 novo + 4 modificados) | `git show --diff-filter=A/M` |

## Causa raiz

O `.uses` novo do `ep2002_error` e o `.inc` ampliado do `colorearClick` foram
somados na coluna errada ao escrever o Log — cada um deslocou uma das duas
contagens em um.

## Correção

### Arquivo: `docs/tasks/30-handlers-auxiliares.md`

Na lista de arquivos: `12 .inc novos e 6 .uses tocados` → `11 .inc novos, 1
.uses novo e 4 .uses modificados`. A frase seguinte, sobre o
`colorearClick.inc`, já diz que ele é ampliação e fecha os doze corpos.

### Arquivo: `docs/PLAN-WTE-LAZARUS.md` *(linha 523)*

A §4.4 diz "ao escrever doze corpos de uma vez". O número está certo se
"corpo" contar o `colorearClick` ampliado, e a medida de 9.416 → 9.374 /
6.476 → 6.816 sai daquele mesmo commit — mas a frase fica ambígua ao lado da
correção acima. Escrever `onze corpos novos e um ampliado`, mantendo os quatro
números como estão.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/30-handlers-auxiliares.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar |

## Verificação

- [ ] A lista da task bate com `git show --diff-filter=A --name-only --format= fb640cd -- 'wte/src/impl/*'`
- [ ] Os quatro números da §4.4 (9.416, 9.374, 6.476, 6.816) continuam intactos
- [ ] `make -C wte check` continua verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
