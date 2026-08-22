---
handler: mostrar_estrategiaClick
formulario: MainForm
endereco: 0x00410220
veredito: implementado
---

# MainForm.mostrar_estrategiaClick

Abre a tela de tática do time selecionado. 1.446 bytes, e o mesmo par de
botões do irmão: `mostrar_estrategia_1` e `mostrar_estrategia_2`.

## Entrada

- **`Sender.Name`**, comparado com a cadeia `'mostrar_estrategia_1'` em
  `0x00425001` — o mesmo mecanismo do
  [`mostrar_jugadorClick`](MainForm.mostrar_jugadorClick.md), e pela mesma
  razão: um corpo servindo dois botões;
- a lista de times do lado escolhido.

**Evidência:** disassembly lido

## Saída

```text
titular := Sender.Name = 'mostrar_estrategia_1'
guarda o time escolhido em global (0x004335cc)
le da imagem CINCO regioes para globais (sete chamadas a 0x004033bc)
0x0040a0b4(...)   ' 1.443 B -- enche a tela de tatica a partir delas
estrategia.ShowModal
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum gravado. As LEITURAS são deste handler, e não da `0x0040a0b4`** — o
contrário do que esta seção dizia até a
[CORR-WTE-082](../../../docs/tasks/CORR-WTE-082.md). Medido: a `0x0040a0b4` não
tem `0x004033BC`, `0x00403388` nem `fseek` no corpo; ela só posiciona a tela a
partir de globais. Quem lê são as sete chamadas a `0x004033BC` daqui, para
cinco regiões:

| destino | índice lógico (setor 850) | bytes |
|---|---|---:|
| formação, linha 0 | `30*t + 2*(t div 95) + 0x40C2C` | 10 |
| formação, linha 1 | idem `+ 10` | 10 |
| formação, linha 2 | idem `+ 20` | 10 |
| cobrador | `6*t + 2*(t div 95) + 0x46228` | 6 |
| tática | `5*t + 0x408A8` | 4 |
| cor de radar 1 | `2*t + 0x3F534` | 2 |
| cor de radar 2 | `2*t + 0x3F634` | 2 |

**As três linhas da formação têm passo 11 em memória, não 10**: elas caem em
`0x00432E89`, `0x00432E94` e `0x00432E9F`, e o byte zero de cada linha fica de
fora. É por isso que a gravação do [` Accept`](estrategia.BitBtn3Click.md)
escreve `[0x00434224][1..10]`.

**A tática lê QUATRO bytes e o ` Accept` grava CINCO.** A assimetria é do
original e está reproduzida: o quinto byte não é lido por ninguém.

**As duas cores de radar só existem para seleção.** Com índice 95 o original
desabilita os dois combos e nem tenta ler.

**Evidência:** disassembly lido

## Pré-condições

Não confere seleção.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**A divisão que deixou a metade sem dono.** Navegação era da WTE-TASK-25 e
encher a tela ficou anotado como da
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md), dona do formulário
`estrategia` — que fechou sem ela. A rotina caiu na fronteira entre as duas e
só ganhou dono na CORR-WTE-082, que a portou como `PreencheTelaDeTatica` na
[`wte_tatica`](../../src/wte_tatica.pas).

**`ShowModal` é chamada virtual, e é por isso que ela não aparece numa busca
por chamada direta.** O símbolo `TCustomForm::ShowModal` é importado do
`vcl60.bpl` e tem thunk em `0x004226de`, e a `.text` inteira tem **zero**
`call rel32` para ele — o `.exe` chama pelo VMT, `mov edx,[eax]` seguido de
`call [edx+<slot>]`, como faz com quase todo método virtual. Vale registrar
porque é a mesma forma da dúvida aberta sobre `SetEnabled` na spec do
[`lista_equiposChange`](MainForm.lista_equiposChange.md) — **com a diferença
de que `ShowModal` é virtual e `SetEnabled` não é**, então a explicação que
serve aqui não serve lá.

**Como o veredito fechou.** A carga e o preenchimento chegaram na
CORR-WTE-082, e a conferência é a do grupo de leitura: `compara_tela.sh
--malha` nos três times `0`, `2` e `63`, com as quatro posições de marcador
batendo com o oráculo antes e depois do clique. O Pascal está em
[`../../src/impl/ep2002_mainform.mostrar_estrategiaClick.inc`](../../src/impl/ep2002_mainform.mostrar_estrategiaClick.inc)
e na [`wte_tatica`](../../src/wte_tatica.pas).

**Duas coisas da tela continuam vazias, e não são deste handler:** os itens dos
dois combos de cor de radar e a bandeira do canto. Os dois saem do
[`estrategia.FormCreate`](estrategia.FormCreate.md), que segue `aberto`.
