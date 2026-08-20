---
handler: boton_mcr2isoClick
formulario: MainForm
endereco: 0x0040c46c
veredito: implementado
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

' --- e repovoa a tela ---
0x0040b934()          ' as duas listas de jogador
0x0040b0b4()          ' as 23 legendas `dorsalN`

' --- e avisa ---
ficha_?.etiq := 'MCR inserida no jogo!!!.'      ' cadeia 0x00424D3F
ficha_?.<slot +0xe8>                            ' o mesmo `W11 TE PT` do
                                                ' grabar_memoryClick
```

**O aviso do fim ficou de fora da primeira leitura desta spec**, e so apareceu
quando a [WTE-TASK-28](../../../docs/tasks/28-import-de-mcr.md) escreveu o
primeiro roteiro que precisa clicar DEPOIS do import: sem dismissar a janela, o
clique seguinte nao alcanca a principal.

O buffer 23 é o mesmo que o `grabar_memoryClick` usa, e tem o mesmo efeito
colateral: cai dentro da lista de descarte, embaralhando a linha 20.

**Evidência:** disassembly lido

## Bytes tocados

**Grava na imagem**, e por três caminhos, dois deles já medidos noutra task:

| o quê | por onde | onde está medido |
|---|---|---|
| 23 jogadores | `0x00404820` | [`golden-09`](../../tests/roteiros/golden-09-mover.txt), [`golden-10`](../../tests/roteiros/golden-10-mover-ml.txt), [`golden-11`](../../tests/roteiros/golden-11-descarte-ml.txt) |
| 23 números de camisa | `0x00404048` | [`golden-08`](../../tests/roteiros/golden-08-dorsal-mcr.txt) |
| 30 B de formação, 3 de tática, 6 de cobrador | `0x00403400` direto | [`27-mcr2iso`](../../tests/roteiros/27-mcr2iso.txt) |

Os endereços novos deste handler saem da mesma base lógica das barras. Medido
com o time 3 da ROM japonesa, sete faixas ao todo:

| faixa | bytes | o quê |
|---|---:|---|
| `388786..389008` | 223 | os 23 nomes |
| `404765..404778` | 14 | os 23 números de camisa |
| `2180624..2180899` | 276 | os 23 × 12 atributos |
| `2302816` | 1 | tática |
| `2303791..2303817` | 27 | formação |
| `2329074..2329078` | 5 | cobradores |
| `3067473..3067495` | 23 | o campo condicional — o literal **25** que a `0x0040478c` põe |

A formação é `EnderecoDeDados(850, 0x40C2C + 30·time + 2·(time div 95))`, que
para o time 0 dá 2303700 = `OFS_FORMATIONS`. O par de bytes extra é o mesmo
`Read(buf,2)` que o `Load` do `we2002_core` faz entre os clubes de ML e o
time-modelo, e **só o capitão o leva** entre os campos de cobrador.

Os 23 bytes de condicional não estão na lista de destinos do handler: chegam
lá pela `0x00404820`, porque a `0x0040478c` põe **25** no campo de todo
jogador vindo de cartão — o `.mcr` não guarda o campo.

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

**Veredito `implementado`.** O formato está medido
([`../mcr.md`](../mcr.md)), o Pascal está em
[`../../src/impl/ep2002_mainform.boton_mcr2isoClick.inc`](../../src/impl/ep2002_mainform.boton_mcr2isoClick.inc)
e há dois gates verdes:
[`golden-12-mcr2iso`](../../tests/roteiros/golden-12-mcr2iso.txt), que importa
no time 3, e
[`golden-13-roundtrip`](../../tests/roteiros/golden-13-roundtrip.txt), que
importa no time **0** e exporta de volta.

**O time 0 do `golden-13` não é escolha arbitrária.** É o caso do *"goleiro da
Eire"* do readme da v0.98: a `0x0040478c` carimba `+0x16 := 0xFF` na identidade
do buffer, e sem esse carimbo o buffer chegaria com `(0, 0)` — a identidade
real do slot 0 do time 0 —, que esta rotina recusaria como jogador repetido.
Um só slot, num só time. O `--check` do `dump_mcr.py` lê o carimbo do `.text` e
o compara com o Pascal; o gate mede o efeito.

**As duas chamadas de repovoamento não são enfeite, e uma delas é
load-bearing.** A `0x0040b0b4` reescreve as 23 legendas `dorsalN`, e o
[`grabar_memoryClick`](MainForm.grabar_memoryClick.md) monta o `.mcr` lendo o
`Caption` de cada uma — não o modelo. Exportar logo depois de importar, sem
repovoar, emite os números de camisa do time que estava na tela antes. **Medido:**
a primeira corrida do [`golden-13-roundtrip`](../../tests/roteiros/golden-13-roundtrip.txt)
reprovou com 16 bytes de diferença em `0x5404` do cartão — o campo de números,
exatamente. O `golden-12` não via porque trocava de time ao terminar, e a troca
repovoa.

**A terceira divergência deliberada é de tela: o port não avisa.** O original
abre `W11 TE PT` com `MCR inserida no jogo!!!.` ao terminar; o `MostraCodigo`
do port só fala nas duas recusas. Nenhum byte muda por causa disso — o
[`golden-13-roundtrip`](../../tests/roteiros/golden-13-roundtrip.txt) sai
byte-idêntico com o lado oráculo tendo um clique a mais para dismissar. Fica
para a [WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md)
decidir se o aviso entra.

**Ele reusa, não reimplementa.** Vale escrever porque a tentação é a oposta:
`0x00404820` e `0x00404048` já sabem tratar destino de seleção, vínculo de
Master League, bloco próprio, alocação e o número dentro do registro de
atributos do time 48. Reimplementar aqui duplicaria cinco ramos que já têm gate.

**Evidência:** disassembly lido
