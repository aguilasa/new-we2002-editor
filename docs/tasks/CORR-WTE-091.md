---
id: CORR-WTE-091
title: "Correção: o `Original ` da ficha esperava uma mudança de estrutura, e a régua dele precisa ser um par"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-091: `jugador.BitBtn1Click` e a régua diferencial

## Problema identificado

Dois handlers da ficha do jogador continuavam `aberto`, e por razões diferentes:

- **`jugador.BitBtn1Click`** (`0x00407a80`, o botão `Original `) tem **seis
  bytes** — uma chamada e um `ret` — e nenhum corpo Pascal. O que faltava não
  era código: a rotina que ele chama, `PreencheFicha` (`0x0040756c`), morava no
  `impl/ep2002_mainform.aux.inc`, que é incluído na **implementação** do
  `MainForm` e portanto invisível de fora. O `uses` que o `dfm2lfm.py` emite sai
  na **interface**, então `ep2002_jugador` não podia usar `ep2002_mainform` de
  jeito nenhum.
- **`jugador.casilla_dorsalKeyPress`** estava `aberto` porque *"o
  `compara_tela.sh --edicao` não alcança a ficha"* — régua de pixel para um
  handler cujo efeito é **byte na imagem**.

## Evidência

`PreencheFicha` em `impl/ep2002_mainform.aux.inc:878-1059`, 182 linhas, um único
chamador (`mostrar_jugadorClick`). A spec do `BitBtn1Click` já nomeava a saída:
*"pôr a rotina numa unidade que **nenhum** dos dois formulários possui"*.

## Causa raiz

Rotina com dois chamadores em formulários diferentes não cabe no `.aux.inc` de
nenhum deles.

## Correção

### A mudança de estrutura

`PreencheFicha` e os dois `CAMPOS_*` desceram para
[`wte/src/wte_ficha.pas`](../../wte/src/wte_ficha.pas), a unidade neutra que a
[CORR-WTE-081](/docs/tasks/CORR-WTE-081.md) criou — mesma forma que a
`wte_render2d` estreou e a `wte_tatica` repetiu. A regra de corte do cabeçalho
daquela unidade vale e foi conferida: veio a rotina inteira e nada do que ela
chama ficou para trás — `FindComponent` é da LCL, `Legenda`/`LegendaDoCabelo`
são da `wte_legendas`, e `CONDICIONAL_AUSENTE` **já morava lá**.

A unidade ganhou `ep2002_jugador` e `wte_legendas` no `uses` da **implementação**
(que é o que quebra o ciclo), mais `Controls`, `ComCtrls` e `we2002_player` na
interface. A rotina passou a ser declarada na interface, porque agora tem dois
chamadores.

### A régua tem de ser um PAR, e essa é a parte que quase saiu errada

**Clicar `Original ` sem ter editado nada antes passaria com o corpo vazio.** A
ficha já mostra o dado carregado; reencher com o mesmo valor não muda byte
nenhum. Um roteiro só teria dado verde para um stub.

Por isso o gate são **dois** roteiros que diferem por um único clique:

| Roteiro | O que faz | Byte em `404748` |
|---|---|---|
| [`golden-18-ficha-edicao`](../../wte/tests/roteiros/golden-18-ficha-edicao.txt) | edita o número de camisa para `7` e grava | `0xc0` |
| [`golden-19-ficha-original`](../../wte/tests/roteiros/golden-19-ficha-original.txt) | edita para `7`, clica `Original `, e grava | `0x80` |

**`0x80` é o valor que a ROM japonesa já tinha ali**, conferido no arquivo
intocado. O `Original ` não devolveu *um* valor: devolveu **o** valor. Com o
corpo vazio os dois gravariam `0xc0` e o par não distinguiria nada.

E o par fecha os dois handlers de uma vez: o `golden-18` prova que a tecla
chega, o filtro a aceita e o valor chega ao disco; o `golden-19` prova que o
`Original ` o desfaz.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wte_ficha.pas` | modificar (recebe `PreencheFicha`) |
| `wte/src/impl/ep2002_mainform.aux.inc` | modificar (perde 182 linhas) |
| `wte/src/impl/ep2002_jugador.BitBtn1Click.inc` | criar |
| `wte/tests/roteiros/golden-1{8,9}-*.txt` e `.port.txt` | criar |
| `wte/tools/check_fase4.py` | modificar (`GOLDEN_DE`) |
| `wte/tools/check_bitfields.py` | modificar (o caminho do `PreencheFicha`) |
| `wte/re/spec/jugador.BitBtn1Click.md`, `jugador.casilla_dorsalKeyPress.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` §4.4 | modificar (fração remedida) |

## Verificação

- [x] `lazbuild wte/wte.lpi` do zero — 16.572 linhas, sem erro
- [x] `make -C wte check` verde
- [x] `golden-18` e `golden-19`, **controle e golden** cada um: byte-idêntico
- [x] o par produz bytes **diferentes** entre si — 1 byte, em `404748`
- [x] disparo medido no `fase-4-cobertura.tsv`: `BitBtn1Click` 1× no `golden-19`
      e **0×** no `golden-18`, que é a diferença entre os dois
- [x] `roms/` intocada — cópias em `work/par/`

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** a mudança de estrutura era o trabalho todo; o corpo tem três
  linhas. O placar da fase 4 foi de **87 para 89 de 96**.

  **O achado que vale para as próximas réguas:** um handler de *desfazer* não se
  julga sozinho. A pergunta "ele desfez?" só tem resposta se houve o que
  desfazer, e a forma barata de garantir isso é um par de roteiros que difere
  por um clique. Vale para qualquer botão cujo efeito seja restaurar estado.

- **Problemas encontrados:**

  **Duas ferramentas seguiam o arquivo, não a rotina.** O `check_bitfields.py`
  lia `PreencheFicha` de `impl/ep2002_mainform.aux.inc` por caminho fixo, e
  mover a rotina fez o `--check` reprovar com dez linhas de
  *"o PreencheFicha não tem chamada para esta posição"* — sintoma que aponta
  para o Pascal e cuja causa era o caminho. E o `check_fase2.py` reprovou de
  novo pela fração de código gerado (52,8% agora, contra 53,0%), porque 182
  linhas mudaram de arquivo e o total escrito à mão subiu com o corpo novo.

  **O `golden-18` precisou de duas corridas no modo golden**, a primeira saindo
  com código 144. A coluna `tentativas` do `fase-4-golden.tsv` guarda o 2 — é
  fato sobre o gate, como a WTE-TASK-31 já registrou uma vez.
