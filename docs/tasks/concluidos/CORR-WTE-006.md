---
id: CORR-WTE-006
title: "Correção: os fatos medidos pela WTE-TASK-04 não chegaram aos documentos que serão executados"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-006: seis documentos ainda dizem o que a medição já desmentiu

## Problema identificado

A WTE-TASK-04 mediu os 96 handlers com dono e **listou** as divergências contra
texto já escrito — o critério "discordância listada, não escondida" está
cumprido. Mas a lista mora só em
[`../../wte/re/published_methods.md`](../../../wte/re/published_methods.md), e os
documentos errados continuam errados.

Quem executar a WTE-TASK-25, a 28 ou a 30 abre `docs/tasks/25-*.md`,
`28-*.md`, `30-*.md` — não o relatório de engenharia reversa. O documento que
comanda a execução é o que está errado; o que está certo é um anexo que ninguém
é obrigado a abrir.

Seis lugares, todos conferidos contra `wte/re/published_methods.tsv`:

| Arquivo | Linha | Diz | Medido |
|---|---:|---|---|
| `docs/tasks/concluidos/25-handlers-de-carga.md` | 42, 44 | `FormCreate`/`FormShow` — **19 endereços**, "um por formulário" | **18** = 16 + 2, e **não** é um por formulário: `ficha_error` e `ficha_error2` não têm |
| `docs/tasks/concluidos/30-handlers-auxiliares.md` | 45 | `malla1MouseDown`/`malla2MouseDown` pertencem a `ficha_color` e `ficha_creditos_equipo` | os dois são de **`estrategia`** |
| `docs/tasks/concluidos/30-handlers-auxiliares.md` | 35-38 | `BitBtn1Click` (3×); `SpeedButton2Click`, `Button2Click`, `Image3Click`, `botonClick`, `base_teamClick`, `imagen_urlClick` entre os "repetidos por vários formulários" | `BitBtn1Click` **4×**; os outros seis aparecem **uma vez cada** |
| `docs/PLAN-WTE-LAZARUS.md` | 769-770 | §5.1: `etiqprecioClick` e o formulário `ficha_creditos_equipo` | o dono é **`jugador`**; `ficha_creditos_equipo` publica só `FormCreate` |
| `docs/tasks/concluidos/32-preco-do-jogador.md` | 37 | `formulário ficha_creditos_equipo` na tabela de entrada | idem — **`jugador`** |
| `docs/tasks/concluidos/04-mapa-de-handlers.md` | 32 | `FormCreate` 17 vezes, `BitBtn1Click` duas | **16** e **4** |
| `docs/prompts/02-revisar.md` | 113 | "`FormCreate` aparece 17 vezes", como conferência da fase 2 | **16** — o próprio gate de revisão carrega o número velho |

O caso da 30 é o mais caro: a tabela "O que fica de fora, e por quê" existe para
o executor **não** implementar duas vezes o mesmo handler. Com o dono errado,
ela manda procurar `malla1MouseDown` num formulário que não o publica, e o
executor da 29 vai procurá-lo em `estrategia` sem saber que a 30 já o cedeu.

## Evidência

Dono e contagem, do `published_methods.tsv` (96 registros, coluna `formulario`
vinda do `vmtClassName`):

```
$ grep -P '\t(malla1MouseDown|malla2MouseDown|etiqprecioClick|botonClick)\t' \
    wte/re/published_methods.tsv | cut -f1-3
0x00406078  botonClick        ficha_color
0x00408bb8  etiqprecioClick   jugador
0x00409f4c  malla1MouseDown   estrategia
0x0040a000  malla2MouseDown   estrategia
```

Contagem por nome, do mesmo arquivo:

```
BitBtn1Click         4  ficha_dorsal ficha_color jugador estrategia
BitBtn2Click         2  ficha_color jugador
BitBtn3Click         3  ficha_color jugador estrategia
SpeedButton1Click    3  ficha_color MainForm ficha_error
SpeedButton2Click    1  MainForm
Button2Click         1  MainForm
Image3Click          1  MainForm
botonClick           1  ficha_color
base_teamClick       1  MainForm
imagen_urlClick      1  ficha_about
FormCreate          16    FormShow  2
```

O cruzamento independente pelo lado do DFM concorda com o VMT — 219 ligações
`On<Evento> = <handler>` nos 18 `.dfm`, reduzidas a 95 pares
(formulário, handler), **todos** presentes no TSV, e um único par do TSV sem
ligação de DFM (`MainForm.Button2Click`):

```
$ grep -hoE '^ *On[A-Za-z]+ = [A-Za-z_][A-Za-z0-9_]*$' wte/re/dfm/*.dfm | wc -l
219
$ comm -23 dfm_pairs tsv_pairs      # pares do DFM ausentes do TSV
(vazio)
$ comm -13 dfm_pairs tsv_pairs      # pares do TSV ausentes do DFM
MainForm	Button2Click
```

## Causa raiz

A WTE-TASK-04 tinha escopo de **medir e listar**, não de corrigir documento
alheio; a lista foi escrita no relatório gerado e nenhuma tarefa ficou dona de
propagá-la.

## Correção

Substituir o texto errado pelo medido, em cada arquivo. Nenhuma medição nova é
necessária — os valores estão no TSV e na tabela acima.

### Arquivo: `docs/tasks/concluidos/25-handlers-de-carga.md`

Linha 42: `19 endereços` → `18 endereços`. Linha 44: trocar "são um por
formulário" por "são 16 `FormCreate` mais 2 `FormShow`; `ficha_error` e
`ficha_error2` não publicam nenhum dos dois".

### Arquivo: `docs/tasks/concluidos/30-handlers-auxiliares.md`

- Linha 45: o parágrafo "Estes pertencem a `ficha_color` e
  `ficha_creditos_equipo`" passa a nomear os donos reais — `ficha_color`,
  `jugador` e `estrategia` —, e a linha da tabela que cede
  `malla1MouseDown`/`malla2MouseDown` diz `estrategia`.
- Linhas 35-38: `BitBtn1Click` vira 4×, e os seis que aparecem uma vez saem da
  lista de repetidos (ou ganham a contagem `1×` explícita, se a intenção era
  enumerar o escopo e não a repetição).

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

§5.1, linha 770: `ficha_creditos_equipo` → `jugador`.

**Fora de escopo aqui:** os números do censo da §1 (componentes, bitmaps) —
esses são da WTE-TASK-09, que já tem a reconciliação da §1 no critério. Esta
correção toca só a §5.1, que a 09 não cobre.

### Arquivo: `docs/tasks/concluidos/32-preco-do-jogador.md`

Linha 37: `formulário ficha_creditos_equipo` → `formulário jugador`.

### Arquivo: `docs/tasks/concluidos/04-mapa-de-handlers.md`

Linha 32: `17 vezes` → `16 vezes`, `BitBtn1Click duas` → `BitBtn1Click quatro`.
O Log da tarefa registra a divergência e fica como está — ele é histórico.

### Arquivo: `docs/prompts/02-revisar.md`

Linha 113: `FormCreate` aparece **16** vezes. É item de conferência da fase 2;
com 17 ele reprova um `dfm2lfm.py` correto.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/25-handlers-de-carga.md` | modificar |
| `docs/tasks/concluidos/30-handlers-auxiliares.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar |
| `docs/tasks/concluidos/32-preco-do-jogador.md` | modificar |
| `docs/tasks/concluidos/04-mapa-de-handlers.md` | modificar |
| `docs/prompts/02-revisar.md` | modificar |

## Verificação

- [x] `grep -rn "19 endereços\|ficha_creditos_equipo" docs/tasks/25-*.md
      docs/tasks/30-*.md` não devolve mais a afirmação errada
- [x] `grep -n "malla" docs/tasks/concluidos/30-handlers-auxiliares.md` diz `estrategia`
- [x] `grep -n "17 vezes" docs/` não devolve nada — **fora** dos registros de
      correção (`CORR-WTE-006.md`, `CORR-WTE-007.md`,
      `correcoes-progresso.md`), que citam o sintoma e têm de continuar citando
- [x] Cada número escrito bate com
      `cut -f2,3 wte/re/published_methods.tsv | sort | uniq -c`
- [x] `python3 wte/tools/dump_published.py --check` continua verde (nenhum
      arquivo gerado foi tocado por esta correção)
- [x] Links de markdown conforme `.claude/rules/links.md`
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

Os seis lugares passaram a dizer o medido. Nenhuma medição nova: os valores
saem de `wte/re/published_methods.tsv`, reconferidos antes de escrever —
`FormCreate` 16, `FormShow` 2, `BitBtn1Click` 4, `SpeedButton1Click` 3,
`BitBtn3Click` 3, `BitBtn2Click` 2, e 1 para cada um dos seis restantes.

Na 28, a tabela "O que fica de fora" ganhou uma coluna **Formulário**: o
parágrafo que a introduzia nomeava dois donos para dezesseis handlers de quatro
formulários diferentes, e trocar só os nomes do parágrafo deixaria o executor
sem saber qual linha pertence a qual. Agora cada linha carrega o dono, e a de
`malla1MouseDown`/`malla2MouseDown` diz `estrategia`.

**Problemas encontrados:**

A varredura achou um sétimo lugar, que a lista da CORR não previa e que a
própria correção tornou incoerente: `30-handlers-auxiliares.md:44` dizia que
sem a coluna `formulario` o `BitBtn1Click` é "ambíguo entre **três**
formulários". São quatro — o mesmo número que a linha acima acabara de ganhar.
Corrigido na mesma invocação.

O critério `grep -n "17 vezes" docs/` não devolve nada só **fora** dos
registros de correção: `CORR-WTE-006.md`, `CORR-WTE-007.md` e
`correcoes-progresso.md` citam a frase como sintoma, e apagá-la ali destruiria
o registro do que foi consertado. Nenhuma afirmação viva sobrou.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/25-handlers-de-carga.md` — 19 → 18, e o "um por formulário"
- `docs/tasks/concluidos/30-handlers-auxiliares.md` — contagens, donos por linha, e o
  "três formulários" que a correção revelou
- `docs/PLAN-WTE-LAZARUS.md` — §5.1: `ficha_creditos_equipo` → `jugador`
- `docs/tasks/concluidos/32-preco-do-jogador.md` — idem, na tabela de entrada
- `docs/tasks/concluidos/04-mapa-de-handlers.md` — 17 → 16, duas → quatro
- `docs/prompts/02-revisar.md` — o gate da fase 2 pedia 17
- `docs/tasks/concluidos/correcoes-progresso.md`
