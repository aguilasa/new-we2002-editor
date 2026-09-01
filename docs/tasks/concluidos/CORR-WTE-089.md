---
id: CORR-WTE-089
title: "Correção: três vereditos `aberto` por 'nada exercita o corpo' quando a bateria golden já os exercita"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-089: a cobertura que a bateria golden já dava

## Problema identificado

A razão mais comum de um veredito ficar `aberto` na fase 4 é a frase *"nada
exercita o corpo"*. Ela foi escrita mais de uma vez a partir do
[`compara_tela.sh`](../../../wte/tools/compara_tela.sh), que é a régua de **pixel**
do grupo de carga — e não a partir da bateria golden, que é a régua de **byte**
e dirige a janela muito mais fundo.

Três handlers estavam `aberto` por esse motivo, e os três disparam dentro de
gates que estão verdes:

| Handler | O que a spec dizia |
|---|---|
| `MainForm.lista_jugadores_1Change` | *"nada dispara o corpo"* |
| `MainForm.lista_equipos_2Change` | *"até a conferência de tela alcançar o lado reserva"* |
| `MainForm.parribaClick` | *"o `--edicao` não foi estendido à lista de descarte"* |

**A pior das três é minha, e é de ontem.** A terceira passagem da
[WTE-TASK-31](/docs/tasks/concluidos/31-fechamento-fase-4.md) (2026-08-23, commit
`505fd4a`) reescreveu a razão do `lista_jugadores_1Change` com número: *"quatro
corridas de `compara_tela.sh` deixaram 150 linhas de `trace.log` com 69
disparos do `lista_equiposChange` e **zero** deste"*. O número está certo. A
conclusão — *"nada dispara o corpo"* — não: generalizei de **um** instrumento
para todos.

## Evidência

Medida com o `port-trace.log` que o
[`golden_run_laz.sh`](../../../wte/tools/golden_run_laz.sh) já escreve, rodando o
lado port dos 16 roteiros com par. ROM japonesa, cópia em `work/`.

| Handler | Roteiro | Disparos |
|---|---|---:|
| `lista_jugadores_1Change` | `golden-09-mover` | 2 |
| | `golden-10-mover-ml` | 2 |
| | `golden-11-descarte-ml` | 2 |
| | `golden-15-ficha` | 1 |
| `lista_equipos_2Change` | `golden-09-mover` | 2 |
| | `golden-10-mover-ml` | **64** |
| | `golden-11-descarte-ml` | **64** |
| `parribaClick` | `golden-11-descarte-ml` | 1 |
| `mostrar_jugadorClick` | `golden-15-ficha` | 1 |

Os quatro roteiros estão `PASSOU` em **controle e golden** no
[`fase-4-golden.tsv`](../../../wte/re/fase-4-golden.tsv).

E o outro lado da medida, que é o que dá limite ao argumento: dos demais
`aberto`, **nenhum** aparece em roteiro nenhum — `BitBtn1Click`,
`flechasapaClick`, `casilla_dorsalKeyPress`, `bolaMouseDown`, `FormCreate`,
`ComboBoxDrawItem`, `boton_dialogo_weClick`, `boton_dialogo_texClick` e
`base_teamClick` dão zero linha. A ferramenta não credita quem não disparou.

## Causa raiz

Uma frase escrita a partir de um instrumento foi lida como afirmação sobre
todos os instrumentos, e nada mecanizava a diferença.

## Correção

### O argumento de verificação, escrito para poder ser contestado

Handler que dispara dentro de um roteiro cujo gate está **verde**, e cujo efeito
entra nos bytes comparados, está verificado por aquele gate. Não é prova de que
todo ramo dele rodou — o `mostrar_jugadorClick` entra só pelo botão do titular —,
e por isso o registro guarda **contagem**, não booleano: 64 disparos num roteiro
que desce 64 itens dizem outra coisa que 1 disparo diz.

### Arquivo: `wte/tools/cobertura_gate.py` *(novo)*

Colhe os `== <formulario>.<handler>` dos `port-trace.log` e escreve
`wte/re/fase-4-cobertura.tsv` (`roteiro`/`handler`/`disparos`). O `--check` é
**offline**: valida o TSV versionado, como o `check_fase4.py` faz com o
`fase-4-golden.tsv` — trace é saída de execução e não se versiona; a medida sim.

Quatro guardas, cada uma contra uma afirmação falsa:

1. handler fora dos 96 do `published_methods.tsv` **aborta**;
2. `disparos` zero **aborta** — ausência se escreve não pondo a linha;
3. roteiro sem par `.port` ou que não esteja `PASSOU` nos **dois** modos
   **aborta**: cobertura dentro de gate vermelho não verifica nada;
4. **spec que cita o TSV como evidência e não tem linha nele aborta.** É a lição
   literal do `check_edicao.py:106-111`, onde o `dorsalMouseDown` dizia
   `compara_tela.sh --edicao` até o trace mostrar que aquele modo não clica
   camisa nenhuma. Citar régua é barato; ter disparo medido não.

Uma armadilha medida na coleta e travada por teste: o `flechasapaClick` emite um
**segundo** `REMark` por sufixo (`: bitmap N sem dono`), então `grep -c` cru
conta dobrado. O padrão ancora no fim da linha.

### Arquivo: as quatro specs

`lista_jugadores_1Change`, `lista_equipos_2Change` e `parribaClick` passam a
`implementado`, cada um com a tabela de disparos e o roteiro citado. O
`mostrar_jugadorClick` ganha a evidência do ramo titular e **continua `aberto`**
pelo ramo do reserva, que nenhum roteiro alcança: entrar pelo
`mostrar_jugador_2` é estímulo novo, e estímulo novo é correção própria.

A spec do `lista_jugadores_1Change` registra o erro de ontem em vez de o
apagar: a frase antiga fica citada, com o motivo pelo qual o número estava certo
e a conclusão não.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/cobertura_gate.py` | criar |
| `wte/tools/test_cobertura_gate.py` | criar |
| `wte/re/fase-4-cobertura.tsv` | criar (medido) |
| `wte/re/spec/MainForm.lista_jugadores_1Change.md` | modificar |
| `wte/re/spec/MainForm.lista_equipos_2Change.md` | modificar |
| `wte/re/spec/MainForm.parribaClick.md` | modificar |
| `wte/re/spec/MainForm.mostrar_jugadorClick.md` | modificar |
| `wte/re/spec/INDICE.md`, `wte/re/fase-4.md` | regerar |
| `docs/tasks/concluidos/progresso.md`, `docs/tasks/concluidos/correcoes-progresso.md` | modificar |

## Verificação

- [x] `make -C wte check` verde, com o `cobertura_gate.py --check` incluído
- [x] `python3 -m unittest test_cobertura_gate` — as quatro guardas com recusa
      vista, mais a armadilha do `REMark` com sufixo
- [x] `python3 wte/tools/check_fase4.py` desce de 13 para 10 `aberto`
- [x] `roms/` intocada — cópias em `work/cobertura/`

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** os 16 roteiros com par tiveram o lado port rodado, e o
  `port-trace.log` de cada um virou `wte/re/fase-4-cobertura.tsv` — **325
  linhas, 47 handlers, 16 roteiros**. Três vereditos subiram para
  `implementado` e o placar da fase 4 foi de **81 para 84 de 96**.

  **A medida tem os dois lados, e é isso que a torna argumento.** Dos nove
  `aberto` restantes fora de preço, **nenhum** aparece em roteiro nenhum: a
  ferramenta credita quem disparou e cala sobre quem não disparou. Se ela
  creditasse todo mundo, não diria nada.

- **Problemas encontrados:**

  **O `flechasapaClick` conta dobrado em `grep -c`.** Ele emite um segundo
  `REMark` por sufixo (`: bitmap N sem dono`), e a leitura ingênua contaria os
  dois como disparo. O padrão ancora no fim da linha e um teste guarda isso —
  não é hipótese, o handler está na árvore emitindo as duas linhas.

  **Três roteiros não rodam sem fixture, e o modo de falhar é enganoso.** O
  `golden-06-textura` quer `WTE_TEXTURA`, o `-12` e o `-13` querem
  `WTE_MCR_ENTRADA`, o `-07`/`-08` querem `WTE_MCR` e o `-14` quer `WTE_UNI`.
  Sem elas o driver sai com erro genérico. Seguindo a lição da primeira passagem
  da WTE-TASK-31, as fixtures foram **criadas** nesta corrida
  (`work/cobertura/t.bin` com os 5.000 bytes que o cabeçalho do roteiro manda,
  e o `entrada.mcr` saído do próprio `golden-07-mcr`), não encontradas.

- **Arquivos:** criados `wte/tools/cobertura_gate.py`,
  `wte/tools/test_cobertura_gate.py`, `wte/re/fase-4-cobertura.tsv`,
  este arquivo; modificadas as quatro specs, `docs/tasks/concluidos/progresso.md`,
  `docs/tasks/concluidos/correcoes-progresso.md`, e regerados `wte/re/fase-4.md` e
  `wte/re/spec/INDICE.md`
