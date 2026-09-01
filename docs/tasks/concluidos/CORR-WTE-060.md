---
id: CORR-WTE-060
title: "Correção: o `iguala_nombres` não acinzenta no port, e o defeito atravessou duas tasks sem correção própria"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-060: o botão que não acinzenta, e a correção que ninguém abriu

## Problema identificado

No time-modelo (índice 95) o `nacional` vira falso e o original acinzenta o
`iguala_nombres`. **O port não acinzenta nada** — e não é falta de código: a
linha existe.

A [CORR-WTE-057](/docs/tasks/concluidos/CORR-WTE-057.md) mediu isso enquanto estendia a
conferência de tela, escreveu no próprio Log que o defeito **"pede correção
própria"** porque o escopo dela era o instrumento, e **nenhuma correção foi
aberta**. A [WTE-TASK-26](/docs/tasks/concluidos/26-handlers-de-edicao.md) fechou com o
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
   [`dfm2lfm.py`](../../../wte/tools/dfm2lfm.py) se for conversão, **nunca** no
   `.lfm` gerado à mão.

Se a causa for da LCL e não do port, o resultado é
[divergência deliberada](/docs/tasks/concluidos/35-divergencias-deliberadas.md) com a
medição escrita — e isso fecha esta correção do mesmo jeito. **Resultado
negativo é resultado.**

### Arquivo: `wte/re/spec/MainForm.iguala_nombresClick.md`

Depois de medida a causa, trocar o bloco "Continua sem causa medida" pelo que se
mediu, e promover o veredito se o defeito sair.

---

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-18

**Resumo do que foi feito:**

O sintoma foi reproduzido isolado no `:99` antes de qualquer edição
(`compara_tela.sh --habilitacao`): `iguala_nombres: oraculo muda (518 px), port
nao muda (0 px)`, com os outros 15 controles medidos batendo.

**As duas hipóteses da correção estão refutadas, e nenhuma delas era a causa.**
Um harness LCL de 90×40 px em `/tmp` — um `TSpeedButton` com o glifo real,
renderizado com `Enabled` verdadeiro e falso — reproduziu o app com fidelidade
de número: o vizinho `boton_nombres2iso` deu **280 px**, exatamente o que ele
muda na tela de verdade. Com o instrumento calibrado, uma variável por vez:

| variável trocada | mudança ao desabilitar |
|---|---|
| nada | 0 px |
| `ParentFont := True` | **0 px** — hipótese 2 morta; o botão nem tem `Caption` |
| glifo do `iguala_nombres` recolorido para fundo `C0C0C0` | 257 px |
| glifo do vizinho recolorido para fundo `FFB676` | **513 px** — hipótese 1 morta: se a cor transparente fosse a causa, isto teria dado 0 |

**A causa é a LCL, e é geral.** `gdeDisabled` é uma conversão para tons de
cinza, e pixel com `R = G = B` é ponto fixo dela. O glifo do `iguala_nombres`
tem **três cores** — `#000000` (275 px), `#FFFFFF` (306 px) e `#76B6FF`, a
transparente. Todo pixel desenhado já é cinza, logo o grayscale não muda nada.
O terceiro passo da correção não se aplica: não há o que consertar no `.lfm`
nem no `dfm2lfm.py`.

O que o Win32 faz de diferente foi medido no próprio recorte do oráculo, não
suposto: preto vira `#A6A6A6` (275 px) e 123 px brancos viram fundo — 275 + 243
= os **518**. É máscara monocromática, não grayscale.

**Resultado negativo virou conferência.** Em vez de deixar a medição como
parágrafo, ela virou `check_glifos_disabled.py`: decodifica os `Glyph.Data` dos
18 formulários sem PIL (BMP 24 bpp `BI_RGB` bottom-up, e **aborta** diante de
qualquer outro em vez de adivinhar), conta os pixels desenhados não-cinza, e
declara o conjunto invariante. São **5** de **59** botões com glifo:
`iguala_nombres`, `parriba`, `pabajo` (`MainForm`), `oscurecer` e `aclarar`
(`color`). Entrar ou sair do conjunto derruba o `make -C wte check`. O
`boton_nombres2iso` fica lá como **controle**: se ele deixar de medir 280, quem
quebrou foi o decodificador, não os glifos.

**A régua parou de mentir sem parar de contar.** O `compara_tela.py` chamava
isso de `DIVERGE`, o que virou rótulo falso depois desta medição. O
`iguala_nombres` passou do grupo `segue_nacional` para um grupo novo
`glifo_cinza`, que **relata e não reprova** — o mesmo tratamento que o
`pendente_32` já dava à bandeira. Os 518 e o 0 continuam impressos; o que mudou
foi o veredito, para `divergencia deliberada (WTE-TASK-35)`.

**Problemas encontrados:**

A primeira versão do harness usava `PaintTo` sobre formulário não mostrado e
deu **0 px em todos os cinco casos**, inclusive no vizinho que muda 280 na
tela. Zero em toda a linha não é resultado, é instrumento morto — foi o
controle que denunciou. Com `Show` + `ProcessMessages` + `GetFormImage` os
números passaram a bater com o app. Medir sem controle teria "confirmado" a
hipótese errada com a mesma cara de sucesso.

**Arquivos criados/modificados:**

- `wte/tools/check_glifos_disabled.py` — **novo**; entra sozinho no
  `make -C wte check` pelo wildcard, como o `check_lcl_props.py`
- `wte/tools/test_check_glifos_disabled.py` — **novo**; 17 testes, com BMP
  plantado, os cinco abortos do decodificador e as três guardas do `conferir()`
- `wte/tools/compara_tela.py` — grupo `glifo_cinza`, e `iguala_nombres` nele
- `wte/tools/test_compara_tela.py` — 2 testes do grupo novo, nos dois sentidos
- `wte/re/spec/MainForm.iguala_nombresClick.md` — causa medida no lugar das
  hipóteses; veredito `aberto` → `implementado`
- `wte/re/spec/INDICE.md` — regenerado (`implementado` 16 → 17)
- `wte/re/spec/MainForm.lista_equiposChange.md` — quatro pontos que diziam
  `DIVERGE` / "causa não achada" (discrepância da varredura)
- `wte/re/edicao-cobertura.md` — a linha do `iguala_nombresClick` (idem)
- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — a candidata, com os campos que
  a task exige
- `docs/tasks/concluidos/26-handlers-de-edicao.md` — a pendência encaminhada, fechada com
  data na lista "o que esta task NÃO fechou"
