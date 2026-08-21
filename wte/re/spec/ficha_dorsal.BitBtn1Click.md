---
handler: BitBtn1Click
formulario: ficha_dorsal
endereco: 0x00402b40
veredito: trivial
---

# ficha_dorsal.BitBtn1Click

O ` Ok` da janelinha de número de camisa. Vinte e um bytes: põe o resultado
modal e esconde o formulário.

**Evidência:** disassembly lido

## Entrada

Nada. O corpo não lê campo do formulário nem estado global — o número
escolhido já está no `etiq_dorsal`, escrito pelo
[`scroll_dorsalChange`](ficha_dorsal.scroll_dorsalChange.md) a cada movimento
da barra, e quem o lê é o [`dorsalClick`](MainForm.dorsalClick.md) depois que o
modal fecha.

**Evidência:** disassembly lido

## Saída

```text
this.ModalResult := 1        ' mrOk
ficha_dorsal.Hide()
```

O campo de resultado modal é o `+0x24C` da instância. Não foi adivinhado: o
`TCustomForm::ShowModal` do `vcl60.bpl` gira o laço enquanto
`[this+0x24C] = 0` e o `TCustomForm::CloseModal` o zera, o que fixa o
deslocamento pelos dois lados.

**O `Hide` é redundante e está lá.** O `BitBtn1` já traz `ModalResult = 1` no
`.dfm`, e a VCL grava esse valor no formulário **antes** de chamar o
`OnClick`; o handler regrava o mesmo 1 e ainda esconde a janela à mão. O port
reproduz os dois movimentos porque reproduzir é mais barato que provar que a
ordem não importa.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Não há chamada de escrita no corpo — a única chamada é o
`TCustomForm::Hide`, resolvida pelo `jmp DWORD PTR ds:<IAT>` em `0x004226ea`.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. O handler não confere nada.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Não há entrada para ser inválida.

**Evidência:** disassembly lido

## Notas

O `ficha_dorsal` não tem botão de cancelar: fechar pela cruz do gerenciador de
janelas deixa o `etiq_dorsal` com o número que a barra tiver, e o
`dorsalClick` grava esse número. Não é bug do port — é o que o original faz, e
é a razão de o `dorsalClick` reler a legenda em vez do resultado modal.
