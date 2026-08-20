---
handler: boton_mcr2isoClick
formulario: MainForm
endereco: 0x0040c46c
veredito: aberto
---

# MainForm.boton_mcr2isoClick

Leva o time inteiro de um memory card para a imagem de CD: 23 jogadores,
23 números de camisa, formação e tática. **1.361 bytes**, e quase nada deles é
gravação nova — o handler é sobretudo um laço em volta das duas rotinas de
escrita que a [WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md)
já portou.

É o sentido inverso do `grabar_memoryClick`, e os dois lados do formato estão
mapeados em [`../mcr.md`](../mcr.md).

## Entrada

- `lista_equipos.ItemIndex` (campo `+0x2f0`, VMT `+0xc8`), que decide o time de
  destino;
- o `.mcr` aberto, na global `0x00432e5c` — quem o abre é o
  [`boton_mcrClick`](MainForm.boton_mcrClick.md), e é ele quem habilita este
  botão;
- os buffers que o `0x0040b9ec` encheu ao abrir o cartão: nomes, atributos,
  números de camisa, formação e cobradores;
- a imagem aberta, na global `0x00432e58`;
- o vetor de ocupação de blocos de Master League (`0x00433224`) e o contador
  de blocos livres (`0x004335c0`), os dois da
  [WTE-TASK-33](../../../docs/tasks/33-slots-de-master-league.md).

**Evidência:** disassembly lido

## Saída

```text
time := lista_equipos.ItemIndex

' --- a recusa, e ela e aritmetica ANTES de gravar ---
se time > 62:                       ' so clube de Master League
    precisa := 0
    fseek(imagem, vinculo(time, 0))
    para slot := 0 ate 22:
        b0 := fgetc();  b1 := fgetc()
        se b1 < 23:                       precisa := precisa + 1
        senao se ocupacao[bloco(b0,b1)] > 1: precisa := precisa + 1
        salta_fronteira_de_setor()
    se blocos_livres < precisa:
        ficha_?.etiq := 'Voce precisa de   ' + precisa + ' mais blocos livres!!!.'
        ShowModal;  sai sem gravar byte nenhum

' --- a gravacao, slot a slot ---
para slot := 0 ate 22:
    0x0040478c(slot, buffer := 23, arquivo_mcr)    ' enche o buffer 23 do .mcr
    0x00404820(origem := 23, time, slot, imagem)   ' a MESMA da WTE-TASK-27
    numero := 5 bits do buffer de numeros, no slot, mais 1
    0x00404048(numero, time, slot, imagem)         ' a MESMA do dorsalClick

' --- formacao e tatica, direto na imagem ---
grava 30 bytes de formacao em EnderecoDeDados(850, 0x40C2C + 30*time
                                              + 2*(time div 95))
le a tatica do .mcr (0x64E2, 0x6488, ...) para o rascunho 0x00432eaf
```

O buffer 23 é o mesmo que o `grabar_memoryClick` usa, e tem o mesmo efeito
colateral: cai dentro da lista de descarte, embaralhando a linha 20.

**Evidência:** disassembly lido

## Bytes tocados

**Grava na imagem**, e por três caminhos, dois deles já medidos noutra task:

| o quê | por onde | onde está medido |
|---|---|---|
| 23 jogadores | `0x00404820` | [`golden-09`](../../tests/roteiros/golden-09-mover.txt), [`golden-10`](../../tests/roteiros/golden-10-mover-ml.txt), [`golden-11`](../../tests/roteiros/golden-11-descarte-ml.txt) |
| 23 números de camisa | `0x00404048` | [`golden-08`](../../tests/roteiros/golden-08-dorsal-mcr.txt) |
| 30 B de formação | `0x00403400` direto | **não medido** |

O terceiro é o único endereço novo deste handler, e sai da mesma base lógica
das barras: `EnderecoDeDados(850, 0x40C2C + 30·time + 2·(time div 95))`, que
para o time 0 dá 2303700 = `OFS_FORMATIONS`. O par de bytes extra é o mesmo
`Read(buf,2)` que o `Load` do `we2002_core` faz entre os clubes de ML e o
time-modelo.

**Evidência:** disassembly lido

## Pré-condições

Duas, e nenhuma é conferida aqui:

- **um `.mcr` aberto.** O botão nasce `Enabled = False` no DFM e quem o liga é
  o `boton_mcrClick` depois de carregar o cartão;
- **imagem aberta e time escolhido**, pelo mesmo caminho de todo handler que
  grava.

**Evidência:** disassembly lido

## Comportamento de erro

Uma recusa, e ela é da família da `-1` da `0x00404820` sem ser ela: a rotina de
gravação recusa **um** slot por falta de bloco, e este handler recusa **os 23 de
uma vez**, contando antes quantos blocos precisaria e comparando com o contador
de livres. Sem isso, importar um cartão numa Master League quase cheia gravaria
metade do time e pararia no meio.

A mensagem é `Voce precisa de   ` + o número + ` mais blocos livres!!!.       `,
das cadeias `0x00424D0D` e `0x00424D20`, e o número passa por um `Currency`
como no `parribaClick` — a multiplicação por 10.000 é a escala do tipo, não um
preço.

Para destino de seleção não há conferência nenhuma: não há bloco a alocar.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto`, e o que falta não é o mapa.** O formato está medido
([`../mcr.md`](../mcr.md)) e as duas rotinas de gravação que ele reusa estão
portadas e com golden verde desde a WTE-TASK-27. Falta o Pascal deste corpo, a
unidade `we2002_mcr` que o alimenta, e o golden próprio — todos da
[WTE-TASK-28](../../../docs/tasks/28-import-de-mcr.md).

**Ele reusa, não reimplementa.** Vale escrever porque a tentação é a oposta:
`0x00404820` e `0x00404048` já sabem tratar destino de seleção, vínculo de
Master League, bloco próprio, alocação e o número dentro do registro de
atributos do time 48. Reimplementar aqui duplicaria cinco ramos que já têm gate.

**Evidência:** disassembly lido
