---
handler: BitBtn3Click
formulario: jugador
endereco: 0x00408548
veredito: implementado
---

# jugador.BitBtn3Click

O `Comple.` da ficha do jogador: valida os campos e **grava o jogador na
imagem**. 1.453 bytes — o maior handler do grupo auxiliar, e não é auxiliar
coisa nenhuma.

**Evidência:** disassembly lido

## Entrada

- os campos da ficha, lidos por `TControl::GetText` — nome, número de camisa,
  créditos e os demais;
- os `TUpDown` de habilidade, por
  `@Comctrls@TCustomUpDown@GetPosition$qqrv`, achados por `FindComponent` com
  os prefixos `barrhab` e `flechasapa`;
- o buffer de jogador em `0x004335C4` e as globais de time e slot
  (`0x004335CC`, `0x004335D0`).

**Evidência:** disassembly lido

## Saída

Em ordem:

```text
se creditos fora de 1..250:
    ficha_error2.etiq1 := 'Insert a valid number of credits (1 ... 250)'
    ficha_error2.ShowModal(); campo.SetFocus(); sai

se numero de camisa invalido:
    ficha_error2.etiq1 := 'Numero do uniforme invalido ([33 ... 99] somente na Master...'
    ficha_error2.ShowModal(); campo.SetFocus(); sai

... copia os campos e as habilidades para o buffer ...

grava_jogador(buffer, time, slot)          ' 0x00404820
grava_numero_da_camisa(numero, time, slot) ' 0x00404048
```

As duas cadeias saem do `.exe` em `0x00424A93` e `0x00424AC0`, e a segunda é a
mesma que o [`dorsalClick`](MainForm.dorsalClick.md) já conhecia — a regra do
número de camisa (até 99 em clube de Master League, até 32 na seleção) é a
mesma nos dois lugares. A segunda está **truncada no binário**, com um `e` e
quatro espaços que sobraram da tradução; o port a reproduz como está lá.

**Evidência:** disassembly lido

## Bytes tocados

Os do jogador: 10 bytes de nome, 12 de atributos e o byte condicional, no
destino que a `0x00404374` monta — a descrição está na
[`auxiliares.md`](../auxiliares.md), linha `0x00404820` —, mais o byte de
número de camisa da `0x00404048`.

**Evidência:** disassembly lido

## Pré-condições

As duas validações acima, e cada uma devolve o foco ao campo culpado antes de
sair. Não confere imagem aberta.

**Evidência:** disassembly lido

## Comportamento de erro

Erro de entrada vira `ficha_error2` modal e retorno; a gravação em si não é
conferida.

**Evidência:** disassembly lido

## Como o veredito fechou

**Fechou pela régua do grupo de gravação, que é byte.** O
[CORR-WTE-081](../../../docs/tasks/concluidos/CORR-WTE-081.md) o implementou em
[`impl/ep2002_jugador.BitBtn3Click.inc`](../../src/impl/ep2002_jugador.BitBtn3Click.inc)
e o fechou com o par
[`golden-15-ficha`](../../tests/roteiros/golden-15-ficha.txt), nos três modos
do [`golden_check.sh`](../../tools/golden_check.sh): `controle` byte-idêntico,
`positivo` detectando o byte plantado em 405228, e `golden` byte-idêntico
contra o oráculo.

**O roteiro não edita nada na ficha, e mesmo assim julga a gravação.** Isso é
possível porque o `Comple.` é destrutivo por si só: o campo de nome mostra o
nome **filtrado** pelo `0x0040b2d8` — na ROM japonesa, uma corrida de `?` — e é
esse texto que volta para o disco. Medido: os quatro bytes de
`OFS_PLAYER_NAME+774` saem de `ba b0 d7 dd` para `3f 3f 3f 3f` nos **dois**
lados. Um port que não gravasse nada reprovaria.

**O ciclo de `uses` foi resolvido movendo, não contornando.** `GravaJogador` e
`GravaNumeroDaCamisa` moravam no `.aux.inc` do `MainForm`, que é incluído na
implementação daquela unidade e por isso invisível de fora; desceram com o
resto do buffer de jogador para a unidade nova
[`wte_ficha.pas`](../../src/wte_ficha.pas), que nenhum dos dois formulários
possui. É a saída que o [`BitBtn1`](jugador.BitBtn1Click.md) já descrevia, e
ela destrava aquele handler também.

**A recusa `-2` não dispara aqui, e isso é do original.** O destino é o mesmo
par (time, slot) da origem, então a identidade bate e a `0x00404820` sairia sem
gravar. O `mostrar_jugadorClick` liga `0x00423168` antes do `ShowModal`
(`0x0040ffb3`) e desliga depois (`0x0040ffcc`) justamente para abrir passagem.

## Notas

**O campo de créditos aparece aqui, e a fórmula dele não.** Este handler só
**valida** a faixa 1..250; quem *calcula* o preço a partir dos atributos é o
`jugador.etiqprecioClick`, da
[WTE-TASK-32](../../../docs/tasks/concluidos/32-preco-do-jogador.md). São coisas
diferentes no mesmo campo, e confundi-las faria a task de preço parecer
dependente de gravação — ela não é.
