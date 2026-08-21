---
handler: colorMouseDown
formulario: ficha_color
endereco: 0x00406a0c
veredito: implementado
---

# ficha_color.colorMouseDown

Um corpo para as 16 amostras `color1`…`color16`, 1.320 bytes — o maior do
formulário. **É o cola-cores que dá título à
[WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md)**, e o readme do
original o vende como *"an improvement over WE2002 Painter features"*.

**Evidência:** disassembly lido

## Entrada

- `Shift`, em `[ebp+0x10]` — bit `0x4` é `ssCtrl`, bit `0x1` é `ssShift`;
- `Button`, em `cl` — `0` é `mbLeft`, `1` é `mbRight`;
- `Sender->Name`, de onde sai o índice da amostra clicada;
- `0x00433dc0` (`entrada`), a amostra selecionada até agora;
- o vetor `0x00433dd4`.

**Evidência:** disassembly lido

## Saída

Cinco caminhos:

```text
Ctrl+Shift, direito:                       ' copiar a paleta inteira
    para b := 0 ate 15:
        word[0x00433e16 + b*2] := vetor[b]
        colcop<b+1>.Color := color<b+1>.Color

Ctrl+Shift, esquerdo:                      ' colar a paleta inteira
    para b := 0 ate 15:  0x00405bc8(b+1, @word[0x00433e16 + b*2])
    0x00405b48()
    se boton0.Checked: 0x00405270()
    se boton1.Checked: 0x004056c8([0x4335cc], lista_col1.ItemIndex)

Ctrl, direito:                             ' copiar UMA cor
    n := StrToInt(SubString(Sender->Name, 6, 2))
    word[0x00433e14] := vetor[n-1]
    colcop0.Color := Sender.Color

Ctrl, esquerdo:                            ' colar UMA cor
    0x00405bc8(n, @word[0x00433e14])
    0x00405b48()
    se boton0.Checked: 0x00405270()
    se boton1.Checked: 0x004056c8([0x4335cc], lista_col1.ItemIndex)

sem Ctrl, esquerdo:                        ' selecionar a amostra
    color<entrada+1>.Left   := entrada*32 + 0x10
    color<entrada+1>.Top    := 0x56
    color<entrada+1>.Width  := 0x21
    color<entrada+1>.Height := 0x19
    color<entrada+1>.SendToBack
    entrada := StrToInt(SubString(Sender->Name, 6, 2)) - 1
    Sender.BringToFront
    Sender.Left      := entrada*32 + 9
    recuadro2.Left   := entrada*32 + 8
    Sender.Top       := 0x4f
    Sender.Width     := 0x2f
    Sender.Height    := 0x27
    <poe as tres barras na cor da amostra selecionada>
```

E, depois dos quatro caminhos com `Ctrl`, uma cauda comum:

```text
se boton0.Checked: 0x00405b48(); 0x00405270()
se boton0.Checked: 0x00405b48(); 0x004056c8([0x4335cc], lista_col1.ItemIndex)
```

**Evidência:** disassembly lido

## Bytes tocados

Nenhum na imagem.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. O botão do meio não cai em caminho nenhum: os testes são `= mbRight` e
`= mbLeft`, sem `else`.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

### O `boton0` testado duas vezes na cauda é defeito do original

O segundo `if` redesenha o **uniforme** e testa o rádio da **bandeira**
(`[0x433dbc]+0x388` nas duas vezes; o rádio do uniforme é `+0x384`). Com a
bandeira marcada ele redesenha os dois; com o uniforme marcado não redesenha
nenhum — e o caminho de colar já redesenhou o certo antes, então o efeito
visível é só um redesenho a mais.

**Está reproduzido como está.** O gate desta task compara pixel, e "corrigir"
aqui produziria divergência contra o oráculo em vez de fidelidade.

### Copiar lê o `Name`, e não a `entrada`

A cor copiada ou colada é a da amostra **clicada**, que não precisa ser a
selecionada. Usar `entrada` daria a cor errada sempre que o usuário copiasse sem
selecionar antes. O recorte é `SubString(Name, 6, 2)` — dois caracteres, porque
os índices vão até 16.

### Os dois blocos de área de transferência não se sobrepõem

`0x00433e14` são dois bytes (uma cor) e `0x00433e16` são 32 (as dezesseis).
`0x00433e14 + 2 = 0x00433e16`: copiar uma cor não estraga a paleta guardada, e
vice-versa. Os dois sobrevivem a troca de família, de time e de conjunto, que é
o que torna o recurso útil.

### `colcop0` é o mostruário da cor única

A fileira `colcop1`…`colcop16` mostra a paleta guardada e `colcop0` mostra a cor
guardada. Nenhum dos dezessete é editável: só recebem tinta.
