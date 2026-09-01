---
handler: dorsalClick
formulario: MainForm
endereco: 0x00410a74
veredito: implementado
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

Os três ramos, agora com endereço — recuperados na sexta passagem da
WTE-TASK-27 e **conferidos contra o `we2002_core`**, que é a conferência que a
§4.2 do plano manda fazer antes de acreditar em fórmula:

| ramo | condição | endereço | forma |
|---|---|---|---|
| all-star | `índice = 48` | setor 850, lógico `$299AF + 12·slot` | 2 B lidos, 5 bits a partir do bit 2, 2 B gravados |
| Master League | `índice > 62` | **absoluto** `$1EB797 + 23·i − 760·(i div 95) + slot` | 1 B cru |
| seleção | `índice ≤ 62` | setor 24, lógico `$4A094 + 16·índice` | 16 B lidos, 5 bits em `32·(slot div 6) + 5·(slot mod 6)`, 16 B gravados |

As duas fontes concordam onde poderiam divergir. `EnderecoDeDados(24, $4A094)`
dá **404716**, o `OFS_SQUAD_NUMBERS_NATIONAL`; a fórmula de ML no time 95 dá
**2014504**, o `OFS_SQUAD_NUMBERS_ML`. E o `+1` entre o time-modelo e o
primeiro clube também bate: o `Load` do `we2002_core` lê 23 bytes, **pula um**,
e só então os 32 clubes — e a fórmula põe o time 63 em 2014528, que é
`2014504 + 23 + 1`.

**O ramo de Master League é o único que não passa pelo fluxo.** Ele usa
`fseek`/`fputc` crus, sem o salto de fronteira de setor que os outros dois
fazem por `0x004033bc`/`0x00403400`. É um byte só, e o original não pula.

Medido: com o time 2 da ROM japonesa, mudar `dorsal1` de 1 para 5 troca **um**
byte, em 404748 — setor 172, byte 204, dentro do payload de 2048 B.

**Evidência:** diff medido

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
[WTE-TASK-05](../../../docs/tasks/concluidos/05-inventario-de-strings.md) mapeou
(`Numero do uniforme invalido ([33 ... 99] somente na Mastere`) e com o teto de
32 do `newWe2002`, que grava os cinco bits do `TSquadNumbers`. O usuário não
consegue digitar um número inválido porque **não há onde digitar**: a escolha é
uma barra de rolagem com faixa fixada na abertura.

**Veredito `implementado` desde 2026-08-19.** O Pascal
([`../../src/impl/ep2002_mainform.dorsalClick.inc`](../../src/impl/ep2002_mainform.dorsalClick.inc))
faz a edição e a gravação, e a gravação é a `GravaNumeroDaCamisa` do
`.aux.inc`. Ele fechou `aberto` na WTE-TASK-26 pela **opção A** — não misturar
duas causas possíveis num golden vermelho —, e é **o primeiro dos nove** que a
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md) promove.

É também a primeira escrita **pontual** do port: o `we2002_database.pas` gerado
sabe `Save` do banco inteiro, não "escreve estes dois bytes aqui". O que
tornou isso barato foi o `LeDoFluxoEm`/`GravaNoFluxo` que o
`boton_nombres2isoClick` já tinha posto no `we2002_estado`.

**Divergência deliberada, a mesma das barras:** o port também atualiza
`Jogo` ao gravar (`GuardaNumeroNoModelo`). O `wte.exe` relê a imagem a cada
troca de time; o port carrega uma vez, e sem isso a tela dele discordaria do
próprio arquivo na volta ao time. Mesmo byte, mesma posição.

**Gate:** [`golden-08-dorsal-mcr`](../../tests/roteiros/golden-08-dorsal-mcr.txt),
com controle byte-idêntico antes. Ele julga esta gravação **e** o `.mcr` na
mesma corrida, porque o número é o único campo do cartão que vem da tela.

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
