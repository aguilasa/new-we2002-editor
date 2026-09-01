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
0x00405b48()                     ' grava o vetor na fonte ANTERIOR
0x00433dc4 := StrToInt(SubString(Sender->Name, 6, 1))       ' a familia

se familia = 1 ou familia = 2:
    0x00433dc8 := lista_col<familia>.ItemIndex              ' o conjunto

lista_col<familia>.Visible := True
para b := 0 ate 3, b <> familia:
    lista_col<b>.Visible := False

0x00405d6c()                     ' recarrega e pinta as 16 da fonte NOVA
```

**São cinco movimentos, e até a quinta passagem da WTE-TASK-29 o port tinha
dois.** O que faltava era o começo e o fim: a gravação de volta, o `conjunto` e
a visibilidade dos combos. A gravação é a que doía — editar a bandeira e clicar
em "Unifo. 2D" perdia a edição, e o sintoma só aparecia quando o usuário
voltava.

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

As duas de fora são o combo `lista_col2` (`BOOTS TYPE`, oito itens) e uma quarta
paleta sem combo visível. Nenhuma das duas é camisa nem bandeira, que é o
escopo da [WTE-TASK-29](../../../docs/tasks/concluidos/29-camisa-e-bandeira-2d.md); portar
chuteira exigiria descobrir onde o dado dela mora na imagem.

**O port não pinta nada quando a família não é portada.** O original pinta: com
a família fora de 0..3 a rotina de preenchimento (`0x00405d6c`) cai no laço com
o ponteiro de fonte **não inicializado** e desenha o que houver na pilha.
Reproduzir isso seria reproduzir comportamento indefinido, que não é
comportamento.

### O `conjunto` só é lido para as famílias 1 e 2

São as duas que têm combo próprio — `lista_col1` (`Primeiro`/`Segundo`) e
`lista_col2` (chuteira). As famílias 0 e 3 não têm, e o handler não mexe no
`0x00433dc8` nesses dois casos: o valor anterior fica, e não é lido por
ninguém enquanto a família for 0 ou 3.

É a explicação de por que o [`lista_col1change`](ficha_color.lista_col1change.md)
e o [`lista_col2Change`](ficha_color.lista_col2Change.md) escrevem o **mesmo**
global.
