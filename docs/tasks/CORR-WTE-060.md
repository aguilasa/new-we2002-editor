---
id: CORR-WTE-060
title: "Correção: o `iguala_nombres` não acinzenta no port, e o defeito atravessou duas tasks sem correção própria"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-060: o botão que não acinzenta, e a correção que ninguém abriu

## Problema identificado

No time-modelo (índice 95) o `nacional` vira falso e o original acinzenta o
`iguala_nombres`. **O port não acinzenta nada** — e não é falta de código: a
linha existe.

A [CORR-WTE-057](/docs/tasks/CORR-WTE-057.md) mediu isso enquanto estendia a
conferência de tela, escreveu no próprio Log que o defeito **"pede correção
própria"** porque o escopo dela era o instrumento, e **nenhuma correção foi
aberta**. A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) fechou com o
`iguala_nombresClick` em `aberto` por causa disso, apontando de novo para uma
CORR que não existia.

Duas tasks concluídas e uma correção concluída falam do mesmo defeito, e
nenhuma o conserta. Este arquivo existe para o defeito parar de ser encaminhado.

## Evidência

A medição, da CORR-WTE-057:

```
2. **O `iguala_nombres` não é desabilitado no time-modelo.** Zero pixel de
   mudança contra 518 do oráculo.
```

O Pascal **põe** o estado, e o vizinho na linha seguinte acinzenta certo:

```
$ grep -n "iguala_nombres\|boton_nombres2iso" \
    wte/src/impl/ep2002_mainform.lista_equiposChange.inc
49:  iguala_nombres.Enabled := nacional;
55:  boton_nombres2iso.Enabled := nacional;
```

Os dois são `TSpeedButton`, os dois nascem `Enabled = False` no `.lfm`, os dois
são `Flat = True` e os dois têm `Glyph`. A única diferença declarada:

```
$ awk '/object iguala_nombres:/,/^ *end$/' wte/forms/ep2002_mainform.lfm \
    | grep -E "Font|ParentFont"
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clCream
      Font.Height = -11
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
```

## Causa raiz

**Não medida.** Duas hipóteses foram levantadas em 2026-08-18 e **nenhuma foi
testada**, então nenhuma entrou na spec:

1. a **cor transparente do glifo** — o `iguala_nombres` começa em `FFB676`, que
   é o fundo do formulário, e o `boton_nombres2iso` em `C0C0C0`. Se a LCL usa o
   primeiro pixel como transparente para montar a versão desabilitada, o
   resultado difere entre os dois;
2. o **`ParentFont = False`** com `Font.Color` explícita.

Registrar hipótese não medida como causa é o modo de a spec virar ficção; por
isso elas estão aqui, na correção, e não lá.

## Correção

**Medir antes de mexer.** O caminho barato, nesta ordem:

1. no `:99`, com a `--habilitacao` do `compara_tela.sh`, capturar o
   `iguala_nombres` do port nos dois times e confirmar que o pixel não muda —
   é reproduzir o sintoma isolado, sem depender do relatório inteiro;
2. trocar **uma** variável por vez: `ParentFont := True` em tempo de execução, e
   depois um glifo cuja cor de canto seja `C0C0C0`. A que mudar o pixel é a
   causa;
3. só então corrigir — no `.lfm` se for propriedade, e no
   [`dfm2lfm.py`](../../wte/tools/dfm2lfm.py) se for conversão, **nunca** no
   `.lfm` gerado à mão.

Se a causa for da LCL e não do port, o resultado é
[divergência deliberada](/docs/tasks/35-divergencias-deliberadas.md) com a
medição escrita — e isso fecha esta correção do mesmo jeito. **Resultado
negativo é resultado.**

### Arquivo: `wte/re/spec/MainForm.iguala_nombresClick.md`

Depois de medida a causa, trocar o bloco "Continua sem causa medida" pelo que se
mediu, e promover o veredito se o defeito sair.
