---
handler: pabajoClick
formulario: MainForm
endereco: 0x0040ecc0
veredito: aberto
---

# MainForm.pabajoClick

A seta para baixo: devolve o jogador guardado na linha selecionada da lista de
descarte para o slot selecionado no lado **direito**. **447 bytes.** É a outra
metade do [`parribaClick`](MainForm.parribaClick.md).

## Entrada

- `lista_descarte.ItemIndex` (campo `+0x3a8`) — a linha, e o índice do buffer
  (`+ 3`).
- `BYTE[0x00434640 + linha]` — a linha tem jogador?
- `lista_equipos_2.ItemIndex`, `lista_jugadores_2.ItemIndex` — o destino.
- `lista_equipos_1.ItemIndex`, `lista_jugadores_1.ItemIndex` — só para decidir
  se o lado esquerdo também precisa ser repovoado.
- O arquivo aberto (`0x00432e58`) e `WORD[0x004335c0]`.

**Evidência:** disassembly lido

## Saída

```text
linha := lista_descarte.ItemIndex
se BYTE[0x00434640 + linha] = 0:
    ficha_error2.etiq1.Caption := 'Selecione um jogador para mover!!!'
    ficha_error2.ShowModal
    sai

guarda1 := lista_jugadores_1.ItemIndex
guarda2 := lista_jugadores_2.ItemIndex

codigo := 0x00404820(buffer := linha + 3,
                     lista_equipos_2.ItemIndex,
                     lista_jugadores_2.ItemIndex, arquivo)
se codigo >= 0:
    0x0040b2d8(lista_equipos_2, lista_jugadores_2)
    lista_jugadores_2.Update
    lista_jugadores_2.ItemIndex := guarda2
    se lista_equipos_1.ItemIndex = lista_equipos_2.ItemIndex:
        0x0040b2d8(lista_equipos_1, lista_jugadores_1)
        lista_jugadores_1.Update
        lista_jugadores_1.ItemIndex := guarda1

casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
0x00403e20(codigo)
```

**Não recarrega buffer nenhum no fim**, ao contrário do `paderechaClick`. A
linha da lista de descarte continua marcada como ocupada e o buffer dela
intocado: dar a seta para baixo duas vezes copia o mesmo jogador duas vezes.

**Evidência:** disassembly lido

## Bytes tocados

**Grava**, dentro da `0x00404820`. Offset por ramo é da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Uma, e é a única do lote que tem mensagem própria:** a linha selecionada
precisa ter jogador (`BYTE[0x00434640 + linha] <> 0`). Nada mais é conferido.

O port acrescenta a faixa da linha e o `ItemIndex >= 0` do lado direito.

**Evidência:** disassembly lido

## Comportamento de erro

Duas portas, e elas usam **formulários diferentes**:

| quando | onde aparece |
|---|---|
| linha vazia | `ficha_error2`, campo `etiq1` (`+0x2f0`), com `Selecione um jogador para mover!!!` (`0x00424e8c`) |
| código `-2` ou `-1` da gravação | `ficha_error`, pela `0x00403e20` |

`ficha_error` e `ficha_error2` são dois formulários distintos no original — os
globais `0x00432dd8` (que aponta para `_ficha_error`) e `0x00432e54`
(`_ficha_error2`). Usar um pelo outro seria mudar a janela que o usuário vê.

**Evidência:** disassembly lido

## Notas

**Ele repovoa o lado esquerdo também, e a condição é medida:** só quando os dois
combos de time mostram o **mesmo** time. Sem isso a lista da esquerda
continuaria exibindo o nome antigo do jogador que acabou de ser substituído.
Nenhum outro handler do lote faz esse cuidado — os de um só e os de lote
repovoam apenas o lado de destino.

### Veredito `aberto`, e é o único dos sete de mover que continua

O Pascal
([`../../src/impl/ep2002_mainform.pabajoClick.inc`](../../src/impl/ep2002_mainform.pabajoClick.inc))
está completo, gravação inclusive: o ramo de destino de Master League da
`0x00404820` foi portado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md). O que falta não
é código — **é gate**, e a razão é medida.

**Este handler é o único que alcança o ramo de ALOCAÇÃO.** Alocar exige origem
do tipo 3, e o `0x00404374` só põe tipo 3 nos buffers de descarte, que são os
do índice 3 em diante — os do `parriba`. Os outros seis de mover trabalham com
os buffers 1 e 2 e nunca chegam lá; por isso o
[`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt), que fecha
para eles, não fecha para este.

**E o gate desta não pode ser escrito hoje.** O alocador pega o **primeiro**
bloco livre, e os dois lados não têm o mesmo conjunto de blocos livres: o
oráculo, ao abrir a imagem, reescreve o par de vínculo em `2012984` de
`(102, 23)` para `(0, 27)` — a faixa que esta task declara `conhecida:` e cujo
autor continua sem nome. Esse par vale o bloco 4; com ele tomado, o primeiro
livre passa de **4** para **350**.

Medido, com a sonda
[`27-descarte-ml.txt`](../../tests/roteiros/27-descarte-ml.txt) sobre a ROM
japonesa: o oráculo gravou o vínculo em `2012730` e o bloco **350** — nome em
`2010092`, atributos em `2208920`, custo em `3069862`. O port, partindo da
tabela limpa, escolheria o bloco **4**. Não é divergência da rotina de
alocação: é a mesma rotina sobre estados diferentes.

**Quem destrava:** o autor da escrita de `2012984`, que é do caminho de carga
(ver a spec do
[`boton_dialogo_weClick`](MainForm.boton_dialogo_weClick.md)). Enquanto ela não
for portada, qualquer golden que aloque bloco compara maçã com laranja.
