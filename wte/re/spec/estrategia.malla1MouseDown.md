---
handler: malla1MouseDown
formulario: estrategia
endereco: 0x00409f4c
veredito: implementado
---

# estrategia.malla1MouseDown

A malha de quatro colunas do campinho tático. **O X escolhe a coluna e o Y
escolhe a linha** — o `Left` de cada `simboloN` é fixo desde o `.dfm`, e quem
anda é o `Top`.

**Evidência:** disassembly lido, e medido contra o oráculo por
`compara_tela.sh --malha` — ver as Notas

## Entrada

- `Button`, em `cl` — só `mbLeft` faz alguma coisa;
- `X`, em `[ebp+0xc]`, e `Y`, em `[ebp+0x8]`, os dois em coordenada de cliente
  da própria `malla1`;
- `malla1.Top` (`[this+0x384]`, campo `FTop` em `+0x44`).

`Sender` chega em `EDX` e **não é lido**: o handler está ligado a um controle
só, e o original vai buscar `malla1` pelo campo em vez de pelo parâmetro.

**A ordem de `X` e `Y` na pilha foi conferida contra o `bolaMouseDown`**, que
guarda os dois num `TPoint` global (`0x0043434c`): `[ebp+0xc]` vai para o campo
`x` e `[ebp+0x8]` para o `y`. Trocá-los aqui daria um handler que compila,
roda e move o marcador errado para a altura errada.

**Evidência:** disassembly lido

## Saída

```text
se Button <> mbLeft: sai

indice := X div 24 + 1
simbolo<indice>.Top := malla1.Top + (Y div 16) * 16 + 3
```

```asm
409f62:  test bl,bl              ; Button
409f64:  jne  0x409fef           ; qualquer outro sai sem tocar em nada
409f70:  mov  eax,[ebp+0xc]      ; X
409f73:  mov  ecx,0x18           ; a largura da coluna
409f79:  idiv ecx
409f80:  inc  edx                ; a base UM do sufixo
409f81:  call 0x421370           ; IntToStr
409f93:  mov  eax,0x424bbf       ; "simbolo"
409f9b:  call 0x421870           ; concatena
409fa7:  call 0x4224ce           ; FindComponent
409fac:  mov  ecx,[esi+0x384]    ; malla1
409fb2:  mov  edx,[ecx+0x44]     ; .Top
409fb5:  mov  ecx,[ebp+0x8]      ; Y
409fbf:  sar  ecx,0x4            ; snap para multiplo de 16,
409fc2:  shl  ecx,0x4            ;   truncando para zero
409fc5:  add  edx,ecx
409fc7:  add  edx,0x3            ; a folga
409fca:  call 0x4228ae           ; TControl.SetTop
```

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não há I/O no corpo: 180 bytes de aritmética, uma busca por nome e
um `SetTop`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. `X` e `Y` chegam em coordenada de cliente da imagem, então o índice já
cai em `1..4` para qualquer clique dentro dela.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Um índice fora de `1..4` faria o `FindComponent` devolver nulo e o
`SetTop` seguinte cair com `this` nulo. **O port sai sem fazer nada** — a
diferença é entre comportamento indefinido e comportamento, e a mesma decisão
que o `CamisaMarcada` do `MainForm` já registra.

**Evidência:** disassembly lido

## Notas

### As três constantes são medidas, não digitadas

`24`, `16` e `3` saem do `.text` pelo
[`dump_zonas.py`](../../tools/dump_zonas.py) e vão para
[`wte_zonas.pas`](../../src/wte_zonas.pas) como `MALHA_PASSO_X`,
`MALHA_PASSO_Y` e `MALHA_FOLGA`. O gerador as confere contra o `.lfm` em quatro
pontos — `malla1.Width div 24 = 4 = quantos simboloN existem`,
`simbolo1.Left = malla1.Left + 3`, `simbolo1.Top = malla1.Top + 3`, e o passo
de `Left` entre marcadores vizinhos —, e **aborta** se alguma deixar de fechar.
As duas fontes são independentes: o código de 2002 e o formulário de 2002.

### O `MALHA_PASSO_Y` não é um imediato

Ele sai do deslocamento do par `sar ecx,N` / `shl ecx,N`, e o gerador exige que
os dois `N` sejam iguais: um arredondamento que descesse e subisse por valores
diferentes não seria arredondamento.

### Medido contra o oráculo, e o que se compara é o **delta**

`compara_tela.sh --malha` leva os dois lados ao mesmo time, abre o campinho e
clica na coluna 2, linha 5 da `malla1` — `X = 30`, `Y = 88`, escolhidos para que
as duas divisões **mordam**: uma coluna que não a primeira, e um `Y` que não é
múltiplo de 16.

```text
marcador    oráculo antes/depois   port antes/depois   delta
simbolo1     None/None            316/316         None / 0
simbolo2      316/396             316/396         80 / 80
simbolo3      380/380             316/316         0 / 0
simbolo4      460/460             316/316         0 / 0
```

**Só a coluna clicada anda, e anda 80 px nos dois lados** — `(88 div 16) * 16`.
As duas recusas foram vistas: trocar `X` por `Y` move o `simbolo4` em 16 px e
deixa o `simbolo2` parado; tirar o arredondamento do `Y` move 88 em vez de 80.

**As posições de partida divergem de propósito**, e é por isso que a régua
compara delta e não posição: o oráculo carrega a posição de cada marcador da
imagem (a rotina interna `0x0040a0b4`) e o port não — os quatro ficam no default
do `.dfm`. O handler não lê a posição corrente, ele a calcula a partir do `Top`
da malha, então o efeito do clique é comparável mesmo com pontos de partida
diferentes. O `simbolo1` do oráculo nem aparece dentro da malha, e a régua só
exige presença da coluna clicada.

### A janela do campinho **não se acha pelo nome**

O `.dfm` diz `Caption = 'Estrategia'` e o oráculo o reescreve no arranque com o
nome do time em Shift-JIS: sob Wine o título sai `'   ?????'`. O port mantém o
do formulário. A régua acha os dois lados **pelo tamanho**, como o `roteiro.sh`
já faz com a janela principal — achar por nome funcionaria de um lado só, que é
pior do que não funcionar de nenhum.

### Este par é só a metade de entrada

Quem lê a posição do marcador de volta é o `estrategia.BitBtn3Click`
(`0x0040a660`, que também cita `"simbolo"` e `"tirador"`), da
[WTE-TASK-30](../../../docs/tasks/30-handlers-auxiliares.md); quem a escreve a
partir do dado carregado é a rotina interna `0x0040a0b4`. Nenhuma das duas é
desta task, e nenhuma das duas muda o que este handler faz.
