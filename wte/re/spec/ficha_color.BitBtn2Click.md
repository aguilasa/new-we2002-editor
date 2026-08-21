---
handler: BitBtn2Click
formulario: ficha_color
endereco: 0x004069c8
veredito: implementado
---

# ficha_color.BitBtn2Click

O `Cancela` do editor de cor: desfaz e deixa a janela fechar. Trinta bytes.

**Evidência:** disassembly lido

## Entrada

O **slot 0** do bloco de cor do time, e a global do time em edição
(`0x004335CC`, o `TimeEmCor` do port).

**Evidência:** disassembly lido

## Saída

```text
copia_slot(origem := 0, destino := 1)   ' 0x00404F90
redesenha_bandeira()                    ' 0x00405270
redesenha_uniforme(TimeEmCor, 0)        ' 0x004056C8
```

Quem fecha a janela **não é o handler**: o `BitBtn2` traz `Cancel = True` e
`ModalResult = 7` no `.dfm`, e a VCL grava o 7 antes de chamar o `OnClick`.
Aqui não há `Hide` nem escrita em `+0x24C` — ao contrário do
[`jugador.BitBtn2Click`](jugador.BitBtn2Click.md), que sobrescreve o resultado.

**São duas diferenças contra o [`BitBtn1`](ficha_color.BitBtn1Click.md), e as
duas são "a janela vai sumir":**

1. **não repinta as 16 amostras** — ninguém vai vê-las;
2. **redesenha o uniforme com o jogo 0**, não com o do `lista_col1`. O
   `xor edx,edx` antes da chamada é literal. Faz sentido: o `MainForm` mostra o
   primeiro uniforme, e é para ele que a tela volta.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.**

**Evidência:** disassembly lido

## Pré-condições

Nenhuma.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata — e aqui não há a varredura sem fim que o `BitBtn1` tem, porque o
combo de forma não é reposto.

**Evidência:** disassembly lido

## Notas

**O `Cancela` deste formulário cancela de verdade**, e é a diferença que vale
anotar contra os outros dois `Cancela` do binário: aqui o handler restaura o
estado antes de sair, enquanto o do [`jugador`](jugador.BitBtn2Click.md) só põe
resultado modal e esconde — quem desfaz lá é o `Original `.

O port chama `RestauraOriginal` da [`wte_cor`](../../src/wte_cor.pas), o mesmo
par que o `BitBtn1` estreou.
