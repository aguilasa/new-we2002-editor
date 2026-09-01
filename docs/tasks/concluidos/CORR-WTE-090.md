---
id: CORR-WTE-090
title: "Correção: três vereditos `aberto` esperando decisão que já foi tomada, ou que pertence a outra fase"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-090: `aberto` não é onde se guarda decisão de escopo

## Problema identificado

O vocabulário de veredito tem cinco valores, e `aberto` significa **pergunta em
aberto**. Três handlers estavam ali sem pergunta nenhuma:

| Handler | O que realmente falta |
|---|---|
| `jugador.flechasapaClick` | nada — a exclusão foi decidida em 2026-08-18 |
| `estrategia.ComboBoxDrawItem` | uma decisão que a WTE-TASK-37 tem por escrito |
| `MainForm.boton_dialogo_weClick` | nada — sobra uma diferença de estrutura, por decisão |

E o segundo caso é pior que classificação errada: **é ciclo.** A WTE-TASK-37 é
fase 6 e depende da [WTE-TASK-34](/docs/tasks/concluidos/34-bateria-golden-completa.md),
que depende da [WTE-TASK-31](/docs/tasks/concluidos/31-fechamento-fase-4.md), que exige
nenhum `aberto`. Esperar a 37 travava as três para sempre.

## Evidência

**`flechasapaClick`** — a [CORR-WTE-063](/docs/tasks/concluidos/CORR-WTE-063.md) fechou em
2026-08-18 levando as três carregadoras de bitmap (`0x00406fe0`, `0x00407110`,
`0x00407338`) para a [WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md)
como exclusão deliberada: elas abrem o `.bmp` em `"r+b"` e regravam a paleta
dentro do arquivo de asset compartilhado. A spec já descrevia o efeito no port
— as setas mudam o rótulo e não mudam o desenho. O veredito ficou `aberto`
mesmo assim, por 6 dias.

**`ComboBoxDrawItem`** — a própria spec nomeia a dona da decisão: *"o corpo
depende de decidir se o port desenha ou deixa a LCL desenhar, e essa decisão
pertence à conferência de UI da WTE-TASK-37"*. O ciclo acima é o que torna
isso insustentável.

**`boton_dialogo_weClick`** — as duas razões antigas caíram (as faixas de
arranque em 2026-08-20, a carga da tela em 2026-08-23). O que sobra é que o
port tem **uma** rota de injeção onde o original tem duas, e que sem window
manager nenhuma régua entra por um `TOpenDialog`. A cobertura medida pela
[CORR-WTE-089](/docs/tasks/concluidos/CORR-WTE-089.md) confirma: **zero** linha nos 16
roteiros.

## Causa raiz

`aberto` estava sendo usado como "ainda não resolvido por alguém", e ele
significa "ainda não respondido".

## Correção

| Handler | Novo veredito | Por quê |
|---|---|---|
| `jugador.flechasapaClick` | `divergencia deliberada` | portado, com desvio consciente e registrado |
| `estrategia.ComboBoxDrawItem` | `nao portado` | com `## Justificativa` de **escopo**, como o critério da fase 4 exige |
| `MainForm.boton_dialogo_weClick` | `divergencia deliberada` | uma rota de injeção onde o original tem duas |

**A justificativa do `nao portado` distingue escopo de dificuldade**, que é o que
o critério pede. O corpo tem 422 bytes e a spec já o descreve — dois
`Rectangle` e o texto por cima. Não falta medida, e o Pascal seria curto. Falta
a **política de desenho**, que vale para os dois combos e para todo *owner-draw*
que apareça; tomá-la dentro de um fechamento que não implementa seria tomá-la
no lugar errado, com um caso só à vista.

### A guarda ficou melhor por causa de um falso positivo dela mesma

O `boton_dialogo_weClick` passou a citar o `fase-4-cobertura.tsv` justamente
para registrar que dá **zero** linha — afirmação verdadeira e útil — e a guarda
da CORR-WTE-089 a recusou, porque só sabia checar o sentido positivo.

Afrouxar seria a saída errada. A guarda virou **bidirecional**: spec que afirma
cobertura zero e tem linha no TSV **também** aborta. A afirmação negativa é tão
conferível quanto a positiva, e agora as duas são conferidas. Recusa vista nos
dois sentidos.

Detalhe medido: a ênfase markdown entra no meio da frase (`**zero** linha`), e
a busca é sobre o texto sem ela — mesma precaução que o `check_fase4.py` toma ao
ler a primeira linha de `## Bytes tocados`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/jugador.flechasapaClick.md` | modificar |
| `wte/re/spec/estrategia.ComboBoxDrawItem.md` | modificar |
| `wte/re/spec/MainForm.boton_dialogo_weClick.md` | modificar |
| `wte/tools/cobertura_gate.py` | modificar (guarda bidirecional) |
| `wte/tools/test_cobertura_gate.py` | modificar |
| `wte/re/spec/INDICE.md`, `wte/re/fase-4.md` | regerar |
| `docs/tasks/concluidos/progresso.md`, `docs/tasks/concluidos/correcoes-progresso.md` | modificar |

## Verificação

- [x] `make -C wte check` verde
- [x] `python3 -m unittest test_cobertura_gate` — 14 testes, com a recusa vista
      nos dois sentidos da guarda
- [x] `spec_index.py` aceita o `nao portado`, que exige `## Justificativa` não
      vazia
- [x] `check_fase4.py` desce de 10 para 7 `aberto`
- [x] `roms/` intocada — nenhuma execução nesta correção

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** três vereditos saíram de `aberto` sem uma linha de Pascal, porque
  nenhum dos três tinha pergunta em aberto. O placar foi de **84 para 87 de
  96**. O ciclo 31→37→34→31 está desfeito: a decisão de *owner-draw* continua
  sendo da WTE-TASK-37, e o que muda é que ela deixou de bloquear o fechamento
  da fase 4 — quando a 37 decidir, o veredito vira um corpo ou uma linha na
  WTE-TASK-35.

- **Problemas encontrados:** a guarda que eu tinha escrito uma hora antes
  recusou minha própria prosa, e estava certa em recusar — ela não sabia
  distinguir "cito o TSV para provar cobertura" de "cito o TSV para registrar
  que não há". Consertar alargando o vocabulário teria sido pior que o defeito;
  a guarda passou a conferir os dois sentidos.

- **Arquivos:** as três specs, `wte/tools/cobertura_gate.py`,
  `wte/tools/test_cobertura_gate.py`, este arquivo, `docs/tasks/concluidos/progresso.md`,
  `docs/tasks/concluidos/correcoes-progresso.md`, e regerados `wte/re/fase-4.md` e
  `wte/re/spec/INDICE.md`
