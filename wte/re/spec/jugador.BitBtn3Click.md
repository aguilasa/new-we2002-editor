---
handler: BitBtn3Click
formulario: jugador
endereco: 0x00408548
veredito: aberto
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
mesma nos dois lugares.

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

## Justificativa do veredito `aberto`

**É gravação, e gravação fecha com golden, não com leitura.** A régua do
[`GABARITO.md`](GABARITO.md) para o grupo de gravação é byte: o
[`golden_check.sh`](../../tools/golden_check.sh) verde nas duas ROMs, com o
**controle** — original contra original, zero divergência — fechando antes.
Isso é um roteiro novo de cada lado e duas corridas de Wine; não cabe numa task
cujo escopo declarado é *"abrir, fechar, OK/Cancelar"*.

**Dono: [CORR-WTE-081](../../../docs/tasks/CORR-WTE-081.md)**, que a põe em **primeiro** lugar das três — é a mais
barata, e o ciclo de `uses` que ela obriga a resolver destrava junto o
[`BitBtn1`](jugador.BitBtn1Click.md).

**A metade escritora já existe no port.** `GravaJogador` e
`GravaNumeroDaCamisa`, no
[`impl/ep2002_mainform.aux.inc`](../../src/impl/ep2002_mainform.aux.inc), são a
`0x00404820` e a `0x00404048` — foram portadas pela
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md) para os oito
handlers de mover jogador e para o `dorsalClick`. Quem herdar este não escreve
o escritor: escreve a validação, a cópia dos campos e o roteiro golden. E
esbarra no mesmo ciclo de `uses` do
[`BitBtn1`](jugador.BitBtn1Click.md) — as duas rotinas moram no `.aux.inc` do
`MainForm`.

## Notas

**O campo de créditos aparece aqui, e a fórmula dele não.** Este handler só
**valida** a faixa 1..250; quem *calcula* o preço a partir dos atributos é o
`jugador.etiqprecioClick`, da
[WTE-TASK-32](../../../docs/tasks/32-preco-do-jogador.md). São coisas
diferentes no mesmo campo, e confundi-las faria a task de preço parecer
dependente de gravação — ela não é.
