---
handler: edit_nombre3KeyPress
formulario: MainForm
endereco: 0x0040d41c
veredito: implementado
---

# MainForm.edit_nombre3KeyPress

Filtro de tecla do terceiro campo de nome. **32 bytes** — um terço dos irmãos,
e a diferença de tamanho é a diferença de comportamento.

## Entrada

`Key`, por referência.

**Evidência:** disassembly lido

## Saída

```text
se Key <> #8 e nao isalnum(Key):  Key := #0
```

Nada mais. **Não encadeia foco**: `Return` não faz nada aqui.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Tecla recusada vira `#0`, sem aviso.

**Evidência:** disassembly lido

## Notas

**Duas diferenças para os dois irmãos, e as duas são do original:**

1. **Só alfanumérico.** Espaço e ponto, que
   [`edit_nombre1`](MainForm.edit_nombre1KeyPress.md) e
   [`edit_nombre2`](MainForm.edit_nombre2KeyPress.md) aceitam, aqui **não
   passam**.
2. **Não move o foco.** A corrente `nombre1 → nombre2 → nombre3` termina aqui.

As duas fazem sentido no dado: este campo é a **abreviatura** de três letras —
`abbreviations[0]` da camada de dados, e o próprio DFM lhe põe `MaxLength = 3`.
Foi a WTE-TASK-25 que descobriu, comparando telas, que o terceiro campo é a
abreviatura e não `names[2]`; o filtro mais estreito é a confirmação
independente disso, vinda do código.

O teste é `isalnum` da RTL da Borland (`0x00419018`, máscara `0x104` do
`_ctype` — alfa mais dígito), enquanto os irmãos comparam faixa a faixa,
escrito à mão. Sem consequência em ASCII; registrado porque a assimetria é do
original.

Pascal em
[`../../src/impl/ep2002_mainform.edit_nombre3KeyPress.inc`](../../src/impl/ep2002_mainform.edit_nombre3KeyPress.inc).
