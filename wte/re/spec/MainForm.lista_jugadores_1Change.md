---
handler: lista_jugadores_1Change
formulario: MainForm
endereco: 0x0040f8b8
veredito: aberto
---

# MainForm.lista_jugadores_1Change

O menor handler do `MainForm`: **28 bytes**, e o corpo inteiro é uma chamada.

## Entrada

`lista_jugadores_1.ItemIndex` — o jogador escolhido na lista do time titular.
O campo é o de deslocamento `0x388`, pelo [`../campos.tsv`](../campos.tsv).

**Evidência:** disassembly lido

## Saída

Chama a rotina em `0x0040b188` passando `ItemIndex + 1` — um argumento, na
pilha, convenção `cdecl` (o chamador limpa com `pop ecx`). Nada mais: o handler
não toca controle nenhum diretamente.

O `+1` é a única aritmética do corpo, e diz que a rotina numera jogador a
partir de 1 enquanto o combo numera a partir de 0.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum**, nem neste corpo nem na rotina chamada: `0x0040b188` só mexe em
propriedade de controle. Medida em
[`../auxiliares.md`](../auxiliares.md) — 335 bytes, sem uma única chamada de
leitura ou escrita de arquivo.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não confere `ItemIndex = -1`: com a lista vazia o argumento vira `0`,
e é a rotina chamada que decide o que fazer com isso.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**`0x0040b188` está medida.** É a mesma rotina que o
[`lista_equiposChange`](MainForm.lista_equiposChange.md) chama com `1` no fim
da carga — isto é, "mostrar o jogador 1" —, e ela **marca uma camisa**: apaga a
que estava marcada, acha a nova por nome e a destaca.

```text
se ha camisa marcada (o ponteiro global nao e nulo):
    Font.Size  := 8
    Left       := Left + 5      ; Width  := Width - 10
    Top        := Top + 5       ; Height := Height - 10
    Color      := $808080       ; Font.Color := $C0C0C0
    manda para tras
marcada := MainForm.FindComponent('dorsal' + numero)
    traz para frente
    Left       := Left - 5      ; Width  := Width + 10
    Top        := Top - 5       ; Height := Height + 10
    Color      := $FFFFFF       ; Font.Color := $0000FF   ' vermelho
    Font.Size  := 14
```

As cores estão no `$00BBGGRR` da VCL: `$0000FF` é vermelho puro, e escrevê-lo
como `#0000FF` pintaria de azul. Os nomes de propriedade não são inferência —
saem dos símbolos importados do `vcl60.bpl` (`TControl::SetLeft`, `SetWidth`,
`SetTop`, `SetHeight`, `SetColor`, `BringToFront`, `SendToBack`,
`TFont::SetSize`, `TFont::SetColor`) e do `TComponent::FindComponent`.

**O ponteiro global é o mesmo que derrubava o oráculo.** É o `0x004335e4` da
[`../crash-causa.md`](../crash-causa.md): o resultado do `FindComponent` é
guardado sem conferência, e com a ROM europeia a carga de time o sobrescreve
com dado de tabela vizinha. Aqui está o outro lado da mesma história — a rotina
que grava esse ponteiro.

**O Pascal está escrito**, em
[`../../src/impl/ep2002_mainform.lista_jugadores_1Change.inc`](../../src/impl/ep2002_mainform.lista_jugadores_1Change.inc),
e a rotina em
[`ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc) — a casa
dos auxiliares que não são handler, decidida na quinta passagem da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md).

**E não há bloqueio de sinal, porque a LCL não precisa.** A pergunta era real:
o Win32 não dispara `CBN_SELCHANGE` em `SetCurSel`, o Qt **dispara**
`currentIndexChanged` em `setCurrentIndex` — e o `newWe2002` precisou de
`QSignalBlocker` nas cargas de time por causa disso. Medido em 2026-08-11 com
[`../../tests/test_lcl_combo.pas`](../../tests/test_lcl_combo.pas), gtk2: a LCL
**não dispara** `OnChange` em `ItemIndex :=`, nem no `Items.Clear` com item
selecionado, nem ao reatribuir o mesmo índice. Como o Win32, ao contrário do
Qt. A medição é remedida a cada `make -C wte check` pelo
[`check_lcl_combo.py`](../../tools/check_lcl_combo.py), porque a resposta é
propriedade do widgetset instalado e pode virar num upgrade sem que uma linha
deste repositório mude.

**Veredito ainda `aberto`, e por um motivo só: nada dispara o corpo.** O golden
test não cobre isto e não deveria — ele compara bytes da imagem, e este handler
não grava nada. Enquanto não houver como dispará-lo, `implementado` afirmaria
uma verificação que não aconteceu.

**A causa, porém, não é a que esta seção deu por três passagens**, e a diferença
importa porque a antiga apontava para trabalho que já foi feito. Ela dizia que o
combo *não é povoado*, e que o `lista_equiposChange` estava *"preso em
`0x00404374`, não lido"*. As duas coisas mudaram: aquele handler está
`implementado` desde 2026-08-23, o combo é povoado a cada troca de time e o
`compara_tela.sh` mede a lista resultante na montagem da janela inteira.

**O que impede é o widgetset, e está medido.** A LCL **não** dispara `OnChange`
em `ItemIndex :=`, nem no `Items.Clear` com item selecionado, nem ao reatribuir
o mesmo índice — como o Win32, e ao contrário do Qt; é o que o
[`check_lcl_combo.py`](../../tools/check_lcl_combo.py) reconfere a cada
`make -C wte check`. Então povoar a lista, que é o que o irmão faz, **não**
chama este handler: só um clique do usuário na `lista_jugadores_1` chama, e
nenhuma régua clica ali. Medido em 2026-08-23, na terceira passagem da
[WTE-TASK-31](../../../docs/tasks/31-fechamento-fase-4.md): quatro corridas de
`compara_tela.sh` (dois times em `barras`, dois em `--malha`) deixaram 150
linhas de `trace.log` com 69 disparos do `lista_equiposChange` e **zero** deste.

Uma tentativa de exercitá-lo por programa de console **falhou por outra
razão**, e ela vale como achado: `Tficha_about.Create(nil)` — qualquer um dos
18, não só o `MainForm` — **bloqueia em `poll` na conexão X** quando o programa
é compilado direto com `fpc`, mesmo com as mesmas unidades da LCL e no mesmo
`:99` onde o `wte` construído por `lazbuild` cria os 18 sem travar. Não é
`cthreads` e não é `RequireDerivedFormResource`; um formulário montado em
código, sem `.lfm`, não trava. Fica registrado: testar corpo de handler fora do
binário do projeto exige resolver isso antes.
