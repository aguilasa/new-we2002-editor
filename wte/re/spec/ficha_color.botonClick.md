---
handler: botonClick
formulario: ficha_color
endereco: 0x00406078
veredito: implementado
---

# ficha_color.botonClick

Um corpo para os quatro rádios `boton0`…`boton3`, que escolhem **qual paleta**
o editor edita.

**Evidência:** disassembly lido

## Entrada

`Sender->Name` — e só. O handler não olha o `Sender` como objeto.

**Evidência:** disassembly lido

## Saída

```text
0x00405b48()                     ' rotina de apoio, antes de tudo
0x00433dc4 := StrToInt(SubString(Sender->Name, 6, 1))
<enche as 16 amostras>
```

O `6` não é mágico: `"boton"` tem cinco letras, e a posição 6 (base um) é o
dígito. Ligar um quinto rádio a este handler mudaria a família para 4 — que não
existe.

```text
4060ae:  lea eax,[ebx+0x8]        ; TComponent.FName
4060b1:  call 0x421678            ; SubString(6, 1)
4060b9:  call 0x42175c            ; StrToInt
4060be:  mov ds:0x433dc4,eax      ; a familia
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata: nome curto ou sem dígito levaria a `StrToInt` a levantar. O port sai
sem fazer nada nos dois casos, que é o mais próximo de não acontecer.

**Evidência:** disassembly lido

## Notas

### As quatro famílias, e as duas que o port não desenha

| dígito | família | fonte das 16 palavras | portada? |
|---|---|---|---|
| 0 | bandeira | `0x00432ef4` | **sim** |
| 1 | uniforme | `0x00432f56 + conjunto * 32` | **sim** |
| 2 | chuteira | `0x00433096 + conjunto * 32` | não |
| 3 | (quarta) | `0x004331b6` | não |

As duas de fora são o combo `lista_col2` (`BOOTS TYPE`, nove itens) e uma quarta
paleta sem combo visível. Nenhuma das duas é camisa nem bandeira, que é o
escopo da [WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md); portar
chuteira exigiria descobrir onde o dado dela mora na imagem.

**O port não pinta nada quando a família não é portada.** O original pinta: com
a família fora de 0..3 a rotina de preenchimento (`0x00405d6c`) cai no laço com
o ponteiro de fonte **não inicializado** e desenha o que houver na pilha.
Reproduzir isso seria reproduzir comportamento indefinido, que não é
comportamento.
