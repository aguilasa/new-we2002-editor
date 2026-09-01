---
handler: paderechaeizquierdaClick
formulario: MainForm
endereco: 0x0040e304
veredito: implementado
---

# MainForm.paderechaeizquierdaClick

A seta `<>`: **troca** os dois jogadores selecionados, um de cada lado.
**428 bytes.** É a única do lote que grava nas duas direções, e a única com uma
pré-checagem própria antes de qualquer escrita.

## Entrada

- `lista_equipos_1.ItemIndex`, `lista_jugadores_1.ItemIndex` (campos `+0x390`,
  `+0x388`) e o par da direita (`+0x384`, `+0x38c`).
- `WORD[0x004335c0]` — blocos de Master League livres.
- Os campos `+0x19` (tipo) dos buffers 1 e 2, depois de carregados.
- O arquivo aberto (`0x00432e58`).

**Evidência:** disassembly lido

## Saída

```text
0x004046e8(lista_equipos_1.ItemIndex, lista_jugadores_1.ItemIndex, 1, arquivo)
0x004046e8(lista_equipos_2.ItemIndex, lista_jugadores_2.ItemIndex, 2, arquivo)

se WORD[0x004335c0] = 0
   e ((buf1.tipo = 0 e buf2.tipo = 1) ou (buf2.tipo = 0 e buf1.tipo = 1)):
    0x00403e20(-1); sai

BYTE[0x00423169] := 1
se buf1.tipo = 0 e buf2.tipo em {1,2}: buf1.tipo := 3
se buf2.tipo = 0 e buf1.tipo em {1,2}: buf2.tipo := 3

codigo := 0x00404820(buffer 1, lista_equipos_2.ItemIndex,
                     lista_jugadores_2.ItemIndex, arquivo)
se codigo >= 0:
    codigo := 0x00404820(buffer 2, lista_equipos_1.ItemIndex,
                         lista_jugadores_1.ItemIndex, arquivo)
    0x00403e20(codigo)
    0x0040b934()                                  ' repovoa as duas listas
    casilla_xmlibres.Caption := IntToStr(WORD[0x004335c0])
senao:
    0x00403e20(-2)                                ' FORÇADO, nao e o codigo
BYTE[0x00423169] := 0
```

**Evidência:** disassembly lido

## Bytes tocados

**Grava duas vezes**, dentro da `0x00404820` — o jogador da esquerda no slot da
direita e vice-versa. Offset por ramo é da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Uma, e ela é estreita.** Recusa com `-1` só quando **não** há bloco de ML
livre **e** um dos dois lados é jogador de seleção (`tipo = 0`) enquanto o outro
é slot de clube de ML apontando para seleção (`tipo = 1`). Trocar dois de
seleção, ou dois de clube com bloco próprio, não consome bloco e passa.

Nada mais é conferido — nem índice selecionado, nem imagem aberta. O port
acrescenta o teste de `ItemIndex >= 0`.

**Evidência:** disassembly lido

## Comportamento de erro

Duas mensagens, as do lote, pela `0x00403e20` — ver
[`MainForm.paderechaClick.md`](MainForm.paderechaClick.md).

**E há um descuido do original reproduzido:** quando a **primeira** gravação
falha, o corpo não repassa o código que ela devolveu — ele carrega `-2` em `eax`
e chama a `0x00403e20` com isso (`0x0040e48c`). Uma recusa por falta de bloco na
primeira metade da troca é anunciada como "It's the same player in both
teams...".

**Evidência:** disassembly lido

## Notas

### O que o enunciado da WTE-TASK-26 dizia deste handler, e o que ele é

O enunciado o chamava de "a novidade da v0.98 — mover todos os jogadores de cada
time com um clique", com `ficha_movertodos` como tela dele. **Não é.** Ele troca
**um** jogador com **um**; quem move os 23 são o `paderecha2Click` e o
`paizquierda2Click`, e são eles que abrem o `ficha_movertodos` — este corpo não
toca o global `0x00432e48`. Corrigido no enunciado.

### `0x00423169` não é `0x00423168`

São dois bytes vizinhos e duas chaves diferentes, e confundi-las seria fácil:

| endereço | quem escreve | quem lê |
|---|---|---|
| `0x00423168` | `0x0040fd7a`, dentro do `mostrar_jugadorClick` | `0x00404871` — desliga a recusa `-2` |
| `0x00423169` | **este handler**, `1` antes e `0` depois das duas gravações | `0x00404bc4`, uma vez |

O que a `0x00404bc4` faz com ela é da metade de gravação, e portanto da
WTE-TASK-27. Aqui ela é ligada e desligada na hora certa para que aquela metade
a encontre como encontraria no original.

### A mexida nos tipos é o que faz a troca funcionar

Antes de gravar, o handler reescreve o `+0x19` dos buffers: o lado que é seleção
vira `3` quando o outro é de clube de ML. `3` é o mesmo "solto" que os buffers da
lista de descarte carregam, e o efeito é fazer a rotina de gravação tratar
aquele jogador como conteúdo novo em vez de vínculo — é o que obriga a alocar
bloco, e é por isso que a pré-checagem de bloco livre existe.

**A segunda condição lê o tipo já possivelmente alterado pela primeira**, e o
Pascal reproduz isso relendo. Se os dois fossem `0`, nenhuma das duas dispara.

### `0x0040b934`, 181 bytes: repovoa as duas listas, assimetricamente

Este é o único handler de mover que não repovoa inline. A rotina preserva a
seleção dos dois combos, repovoa o esquerdo **sempre** e o direito **só se**
`lista_jugadores_2.Enabled` — o teste é a chamada virtual `[vmt+0x50]`, que o
`vcl60.bpl` diz ser `TControl::GetEnabled`, medido pelo mesmo caminho que deu o
`SetEnabled` em `+0x64`. Ela pega o formulário pelo ponteiro global
`0x00434360` (`_MainForm`), não por `this`: não é método.

### Veredito `implementado`

O Pascal
([`../../src/impl/ep2002_mainform.paderechaeizquierdaClick.inc`](../../src/impl/ep2002_mainform.paderechaeizquierdaClick.inc))
faz tudo, as duas gravações inclusive.

Fechado em 2026-08-20 pela oitava passagem da
[WTE-TASK-27](../../../docs/tasks/concluidos/27-handlers-de-gravacao.md): o ramo de
**destino de Master League** da `0x00404820` foi portado, com golden verde
([`golden-10-mover-ml`](../../tests/roteiros/golden-10-mover-ml.txt)) e o
contador de blocos livres vindo da
[WTE-TASK-33](../../../docs/tasks/concluidos/33-slots-de-master-league.md).

**Este handler é o único que precisa do `TrocaEmCurso`**, e agora se vê por
quê: o ramo de Master League mostra um aviso modal (`ficha_info4`) quando o
bloco que o destino larga ainda tem outros donos, e uma troca faria o aviso
subir **duas** vezes — uma por gravação. O `BYTE[0x00423169]` que este corpo
liga antes e desliga depois existe para calá-lo, e até esta passagem ele era um
sinalizador sem leitor no port.

**Divergências deliberadas do port**
([WTE-TASK-35](../../../docs/tasks/concluidos/35-divergencias-deliberadas.md)): sai sem
fazer nada se qualquer `ItemIndex` for negativo.
