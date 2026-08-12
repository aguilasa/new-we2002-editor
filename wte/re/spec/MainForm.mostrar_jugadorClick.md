---
handler: mostrar_jugadorClick
formulario: MainForm
endereco: 0x0040f8d4
veredito: aberto
---

# MainForm.mostrar_jugadorClick

Abre a ficha do jogador selecionado. **2.378 bytes** — o maior handler do
grupo de carga, e o segundo maior do `MainForm` depois do
[`lista_equiposChange`](MainForm.lista_equiposChange.md).

Ligado a **dois** botões, `mostrar_jugador_1` e `mostrar_jugador_2`: o do time
titular e o do reserva.

## Entrada

- **`Sender.Name`**, e essa é a parte que a leitura apressada erraria. O
  original **não** compara o ponteiro do `Sender` com o do botão: ele lê o
  campo `Name` do componente (deslocamento `0x08` do `TComponent`, o mesmo que
  o [`sonda_dorsal.py`](../../tools/sonda_dorsal.py) confere) e o compara com a
  cadeia `'mostrar_jugador_1'` em `0x00424f57`. Igual → lado titular; diferente
  → reserva.
- do lado titular, `lista_equipos_1.ItemIndex` e `lista_jugadores_1.ItemIndex`;
  do reserva, `lista_equipos_2` e `lista_jugadores_2`.

**Evidência:** disassembly lido

## Saída

```text
titular := Sender.Name = 'mostrar_jugador_1'
guarda o time e o jogador escolhidos em globais (0x004335dc e vizinhas)
0x00403f00(...)   ' 328 B -- le o numero de camisa, base UM
0x004046e8(...)   ' 164 B -- carrega o jogador para o buffer de 44 B
0x00404820(...)   ' 1.459 B -- GRAVA um jogador (nao "enche a ficha")
0x0040756c(...)   ' 1.275 B -- ENCHE a ficha (lida na 12a passagem)
jugador.ShowModal
```

O `ficha_enlaza` também é alcançado — é o diálogo de confirmação de vínculo,
que aparece quando o jogador escolhido é de clube de Master League.

> **Duas linhas desta lista estavam erradas, e a
> [WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md) as corrigiu ao
> ler as rotinas.** Elas diziam "não lida" e "enche a ficha", escritas na
> décima passagem da WTE-TASK-25 a partir do que o handler *parecia* precisar.
> Medido:
>
> - **`0x004046e8`** carrega um jogador da imagem para um buffer de **44
>   bytes** em `0x004335ec` — 10 B de nome, 12 B de atributos, e um byte que só
>   é lido se a terceira coluna de offsets não for zero (senão vai `50`);
> - **`0x00404820` grava.** Ela chama a escritora de bytes `0x00403400` três
>   vezes e a escritora de número de camisa `0x00404048`, e devolve código de
>   erro — `-2` quando a identidade do jogador de origem bate com a do destino.
>
> **Que este handler chame uma rotina de gravação é o que a leitura antiga
> escondia**, e o que isso significa para o `mostrar_jugadorClick` — abrir a
> ficha grava? só grava ao fechar? — **continua sem medir**: exigiria seguir o
> fluxo dos 1.459 bytes a partir daqui, e não só saber o que a rotina faz. Fica
> como pergunta escrita, não como descrição plausível.
>
> **A outra metade fechou na décima segunda passagem:** o `0x0040756c` —
> "preenche a ficha" — está lido e portado. Ele percorre duas tabelas de
> descritores de bit em `.data` e enche os 16 `barrhab`/`valorhab`/`imghab` e
> os 12 `flechasapa`/`valorapa` do formulário `jugador`, achando cada controle
> por nome. A ficha deixou de abrir vazia. O que continua sem resposta é só a
> `0x00404820`, a que grava.
>
> **Mais um dado sobre o mesmo ponto, medido na nona passagem da WTE-TASK-26 e
> igualmente sem conclusão:** dentro deste corpo, em `0x0040fd7a`, está a
> **única** escrita do `.text` inteiro em `BYTE[0x00423168]` — a chave que
> **desliga** a recusa de jogador repetido da `0x00404820`. Logo acima, em
> `0x0040fd72`, ele marca um buffer com `+0x19 := 3`, o "slot vazio". Os dois
> gestos juntos têm cara de preparar uma gravação que não deve ser recusada,
> mas isso é leitura de intenção; o que está medido são as duas escritas.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum gravado.** Lê a imagem através de `0x00403f00` e das duas rotinas de
preenchimento. Que faixas exatamente, não foi medido — e não precisa ser aqui:
ver as Notas.

**Evidência:** nao medido

## Pré-condições

Não confere seleção. Com `ItemIndex = -1` nas listas o índice calculado sai
negativo e segue.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata.

**Evidência:** disassembly lido

## Notas

**O escopo aqui é navegação, e o resto tem dono.** Das 2.378 instruções, o que
a WTE-TASK-25 deve é *abrir a ficha* — escolher o par de listas certo pelo
`Sender.Name`, guardar a seleção e mostrar o formulário. **Encher a ficha**
(`0x00404820` e `0x0040756c`, 2.734 bytes) é editar jogador, e isso é a
[WTE-TASK-26](../../../docs/tasks/26-handlers-de-edicao.md), dona do formulário
`jugador`.

A divisão foi decidida em 2026-08-11 e está no enunciado da
[WTE-TASK-25](../../../docs/tasks/25-handlers-de-carga.md). Sem ela, o critério
"remover o andaime `--show` com a navegação real no lugar" arrastaria 2,7 KB de
disassembly de outra fase.

**Veredito `aberto` porque metade tem dono fora.** O Pascal da navegação está
escrito em
[`../../src/impl/ep2002_mainform.mostrar_jugadorClick.inc`](../../src/impl/ep2002_mainform.mostrar_jugadorClick.inc);
a ficha **deixou de abrir vazia** na décima segunda passagem da 26, que portou
o `0x0040756c`. O que mantém o veredito é a `0x00404820`.
