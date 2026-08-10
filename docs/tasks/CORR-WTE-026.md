---
id: CORR-WTE-026
title: "Correção: a coluna VCL da tabela do achado 2 não foi medida, e a tabela se anuncia inteira como medida"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-026: metade da tabela de semântica de sinal é memória, não medida

## Problema identificado

O achado 2 do [`wte/re/eventos.md`](../../wte/re/eventos.md) abre com
**"Medido no fonte da LCL 3.0 instalada:"** e logo abaixo vem uma tabela de
três colunas — `VCL/Win32 (2002)`, `LCL/GTK2 3.0` e `Diverge?`.

Só a coluna do meio foi medida. Cada linha dela tem arquivo e rotina logo
abaixo da tabela (`gtk2wsstdctrls.pp`, `gtk2wscomctrls.pp`,
`include/customedit.inc`), e a revisão as reconferiu uma a uma no disco. A
coluna `VCL/Win32 (2002)` **não tem fonte nenhuma** — nem arquivo, nem
observação de tela, nem disassembly —, e a coluna `Diverge?` é a comparação das
duas: ela vale exatamente o que a coluna sem fonte valer.

A consequência não fica na tabela. A única divergência que o achado declara —
`ComboBox.Text := s` dispara na VCL e não dispara na LCL — vira o item 2 da
seção final "O que a fase 4 leva daqui":

> Ao escrever `Text` num combo, lembrar que o `OnChange` **não** reentra na LCL
> e reentrava na VCL. Perguntar isso na spec dos 12 handlers de `OnChange`.

Isto é uma instrução escrita para quem for implementar 12 handlers, apoiada num
lado não medido. É o padrão que a §2 do plano chama de hipótese vestida de
spec — e o próprio achado 2 é a prova de que a memória erra neste terreno: a
premissa que a WTE-TASK-13 carregava (`ItemIndex :=` dispara `OnChange`,
herdada do `QSignalBlocker` do `newWe2002`) estava invertida, e caiu justamente
quando alguém foi ler o fonte.

**Não é o veredito que está em disputa** — `Text := s` num `csDropDown` da VCL
provavelmente dispara mesmo, por `WM_SETTEXT` → `EN_CHANGE` → `CBN_EDITCHANGE`.
O que está errado é a tabela dizer "medido" sobre uma coluna que ninguém mediu,
e a fase 4 herdar isso como fato fechado.

## Evidência

O que a revisão conseguiu remedir, linha a linha, na LCL 3.0 instalada:

```
$ grep -n -A12 "TGtk2WSCustomComboBox.SetItemIndex" \
    /usr/lib/lazarus/3.0/lcl/interfaces/gtk2/gtk2wsstdctrls.pp
1998:  // to be delphi compatible OnChange only fires in response to user actions not program actions
2000:  Inc(WidgetInfo^.ChangeLock);
2135:  // we use user ChangeLock to not signal onchange      <- SetText
 433:  // lock Range, so that no OnChange event is not fired <- TGtk2WSTrackBar.SetPosition
 585:  Inc(WidgetInfo^.ChangeLock);                          <- TGtk2WSCustomListBox.SetItemIndex
2694:  g_signal_connect(AGtkWidget, 'change-value', ...)     <- TGtk2WSScrollBar.SetCallbacks
```

E `include/customedit.inc:577`, `TCustomEdit.TextChanged`: chama `Change`, com
`FTextChangedByRealSetText` governando só `Modified` — como o `eventos.md` diz.

Do lado VCL, a mesma varredura não tem o que citar: o `vcl60.bpl` está na pasta
do editor e nada no repositório o lê. `grep -n` no `eventos.md` entre a tabela
(linhas 89-96) e o fim do achado não devolve uma única referência para o lado
Win32 — só para o lado LCL.

## Causa raiz

A frase "Medido no fonte da LCL 3.0 instalada" cobre a tabela inteira, e a
tabela tem uma coluna que não vem da LCL.

## Correção

### Arquivo: `wte/re/eventos.md`

1. Na tabela do achado 2, marcar a coluna `VCL/Win32 (2002)` como **não
   medida**, dizendo de onde ela vem (semântica documentada de `WM_SETTEXT` →
   `EN_CHANGE`/`CBN_EDITCHANGE`, não leitura do `vcl60.bpl`). Uma nota de
   rodapé por baixo da tabela basta; o texto acima dela passa a dizer
   "medido no fonte da LCL" **da coluna LCL**.
2. Na seção "A divergência que sobra", acrescentar a rota de confirmação:
   ela se fecha na fase 4, quando o disassembly de qualquer dos 12 handlers de
   `OnChange` mostrar (ou não) escrita em `Text` de combo — ou por observação do
   `wte.exe`, que é VCL de verdade rodando.

### Arquivo: `docs/tasks/13-trace-de-eventos.md`

No Log de Execução, item 1, a frase "Sobra uma divergência real:
`ComboBox.Text := s` dispara na VCL e **não** dispara na LCL" ganha o mesmo
qualificador — **um lado medido, o outro não**.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/eventos.md` | modificar |
| `docs/tasks/13-trace-de-eventos.md` | modificar |

## Verificação

- [x] A tabela do achado 2 diz, por coluna, o que foi medido e o que não foi
- [x] A divergência de `ComboBox.Text` tem rota de confirmação escrita, com dono
      (fase 4)
- [x] O item 2 de "O que a fase 4 leva daqui" não afirma o lado VCL como fato
      fechado
- [x] `make -C wte check` continua verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

A abertura do achado 2 deixou de cobrir a tabela inteira: agora ela nomeia a
coluna medida (`LCL/GTK2 3.0`) e diz que a `VCL/Win32 (2002)` não foi. A coluna
VCL ganhou marca de nota de rodapé, e a nota diz de onde a afirmação vem
(semântica documentada de `WM_SETTEXT` → `EN_CHANGE`/`CBN_EDITCHANGE`, mais o
comentário *"to be delphi compatible"* da própria LCL, que descreve a VCL) e o
que ninguém fez: **nada no repositório abre o `vcl60.bpl`**. Como a coluna
`Diverge?` é a comparação das duas, ela vale o que a coluna VCL valer — está
escrito.

A seção "A divergência que sobra" passou a separar as duas metades e ganhou rota
de confirmação com dono na fase 4, em duas vias: (1) disassembly dos 12
handlers de `OnChange` — se nenhum escreve `Text` em combo, a divergência é
vazia e morre sem medir a VCL; (2) observação do `wte.exe` sob Wine no `:99`,
que é VCL de 2002 rodando. O item 2 de "O que a fase 4 leva daqui" e o item 1
do Log da WTE-TASK-13 receberam o mesmo qualificador.

**Problemas encontrados:**

Nenhum. A varredura por `Medido no fonte da LCL`, `dispara na VCL` e `vcl60` em
`docs`, `wte/re`, `.claude` e `CLAUDE.md` não achou terceiro sítio afirmando o
lado Win32 como medido — as demais ocorrências de `vcl60.bpl` são sobre imports
e VMT, alheias a esta correção.

**Arquivos criados/modificados:**

- `wte/re/eventos.md`
- `docs/tasks/13-trace-de-eventos.md`
