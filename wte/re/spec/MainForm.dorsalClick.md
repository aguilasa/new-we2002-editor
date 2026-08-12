---
handler: dorsalClick
formulario: MainForm
endereco: 0x00410a74
veredito: aberto
---

# MainForm.dorsalClick

Clicar num dos 23 números de camisa. **872 bytes**, um corpo para os 23
rótulos.

## Entrada

- `lista_equipos.ItemIndex` — se `< 0`, sai sem fazer nada. É a única
  pré-condição do handler.
- **`Sender.Name`.** O índice da camisa sai de `Copy(Name, 7, 2)` sobre
  `'dorsalNN'` — não do `Tag`, não do ponteiro, não da posição na tela.
- `0x004335e4` — a camisa marcada agora, para decidir se o bloco de seleção
  roda.
- `lista_equipos_1.ItemIndex` — decide o teto do número (ver Saída).
- `lista_jugadores_1.ItemIndex` e `.Items[]` — para o título da janelinha.
- Ao voltar do modal: `ficha_dorsal.etiq_dorsal.Caption`.

**Evidência:** disassembly lido

## Saída

```text
se lista_equipos.ItemIndex < 0: sai

se Sender <> camisa_marcada:
    numero := StrToInt(Copy(Sender.Name, 7, 2))
    lista_jugadores_1.ItemIndex := numero - 1
    0x0040b188(numero)                      ' MarcaCamisa

ficha_dorsal.Left := MainForm.Left + Sender.Left + 0x26
ficha_dorsal.Top  := MainForm.Top  + GroupBox1.Top + 0x3c
ficha_dorsal.etiq_dorsal.Caption := camisa_marcada.Caption
ficha_dorsal.scroll_dorsal.Max :=
    99 se lista_equipos_1.ItemIndex > 62 senao 32
ficha_dorsal.scroll_dorsal.Position := Max - numero_atual + 1

origem := 4; se lista_jugadores_1.ItemIndex < 9: origem := 5
ficha_dorsal.Caption := ' ' + Copy(lista_jugadores_1.Items[i], origem, 10)

ficha_dorsal.ShowModal                      ' VMT slot 0xe8

escolhido := StrToInt(ficha_dorsal.etiq_dorsal.Caption)
0x00404048(escolhido, lista_equipos_1.ItemIndex,
           lista_jugadores_1.ItemIndex, arquivo)      ' GRAVA -- ver abaixo
camisa_marcada.Caption := IntToStr(escolhido)
```

**Evidência:** disassembly lido

## Bytes tocados

**Grava**, e é a descoberta que muda a classificação deste handler.

`0x00404048` é a irmã escritora da rotina de leitura `0x00403f00` — mesmos três
ramos (o time 48, o clube de ML, a seleção), mesma aritmética de endereço. Ela
recebe o número escolhido, o índice do time, o slot do jogador e o arquivo já
aberto; faz `add al,0xff` — o `- 1` que devolve o número à base zero —, escreve
o valor no lugar certo e **grava aquele trecho no arquivo** (`0x00403400`),
sem passar por nada parecido com um `Save` do banco inteiro.

Que offset exatamente, por ramo, **não foi medido aqui** — é o que a
WTE-TASK-27 vai precisar, e é lá que o gate por byte existe.

**Evidência:** disassembly lido

## Pré-condições

Só `lista_equipos.ItemIndex >= 0`. Não confere se há jogador selecionado, não
confere se o índice extraído do nome caiu em 1..23.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. `StrToInt` sobre um nome que não termine em dígito levantaria
exceção; `FindComponent` que devolvesse `nil` dentro do `0x0040b188`
derrubaria o programa, e isso já está registrado como divergência deliberada na
spec daquela rotina.

**Evidência:** disassembly lido

## Notas

**A regra de validação que a WTE-TASK-26 pedia não é um `if` — é o `Max` da
barra.** Clube de Master League (índice `> 62`) aceita até **99**; seleção, até
**32**. Bate com a mensagem de erro que a
[WTE-TASK-05](../../../docs/tasks/05-inventario-de-strings.md) mapeou
(`Numero do uniforme invalido ([33 ... 99] somente na Mastere`) e com o teto de
32 do `newWe2002`, que grava os cinco bits do `TSquadNumbers`. O usuário não
consegue digitar um número inválido porque **não há onde digitar**: a escolha é
uma barra de rolagem com faixa fixada na abertura.

**Veredito `aberto`, e o que falta tem dono nomeado.** O Pascal está escrito
([`../../src/impl/ep2002_mainform.dorsalClick.inc`](../../src/impl/ep2002_mainform.dorsalClick.inc))
e faz tudo **menos a gravação**. Escrever a gravação aqui seria antecipar a
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md), que é a dona de
gravação e a única com gate por byte; e seria a primeira escrita pontual do
port — o `we2002_database.pas` gerado sabe `Save` do banco inteiro, não
"escreve estes dois bytes aqui".

**Isso torna o `dorsalClick` o primeiro caso de handler que o
`published_methods.tsv` classifica como `edicao` e que grava na imagem.** A
classificação não está errada — o que ele faz é edição, e a gravação é uma
chamada no fim —, mas o par edição × gravação atravessa task como o das barras,
e por isso está escrito no critério de conclusão da 27.

**A janelinha nasce colada no rótulo clicado**, e a vertical não vem do
`Sender`: vem do `GroupBox1`. Os 23 rótulos estão na mesma linha, então um
`Top` só serve para todos — economia do autor, reproduzida.

**O título é `' ' + nome`**, com o espaço vindo da cadeia de um caractere em
`0x00425077`. O `Caption = 'Number'` do DFM é de projeto e some no primeiro
clique. O nome sai do item do combo por `Copy(item, 4 ou 5, 10)` — a origem
muda conforme o índice tenha um ou dois dígitos, que é aritmética de largura de
número e não de conteúdo.
