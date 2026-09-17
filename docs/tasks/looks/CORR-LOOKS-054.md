---
id: CORR-LOOKS-054
title: "Correção: o `screen.json` guarda o título `LOOKS SET`, a tela desenha `S SET`, e nenhum gate compara os dois"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-LOOKS-054: o único texto da tela que ninguém confere contra o que o jogo desenhou

## Problema identificado

A LOOKS-TASK-21 mediu a tela `LOOKS SET` lendo os **objetos de texto** que o
jogo imprime, e conferiu o que o `screen.decode` faz deles contra os **glifos
desenhados** — 34 strings, nos dois states e na ponta de cada linha. É a
verificação que sustenta a tabela inteira.

**O título fica fora dessa conferência**, e é justamente onde as duas leituras
divergem. O objeto diz `LOOKS SET`; o quadro mostra `S SET`.

```text
$ grep -n '"title"' tools/looks/screen.json
64:   "title": "LOOKS SET"
115:   "title": "LOOKS SET"
```

O caminho do título no `oracle.py` é o do objeto, e só:

```text
tools/looks/oracle.py:2863
        return {"title": text(titles[0]), "shirt": text(left[0]),
```

Nenhum dos glifos do título entra na comparação, então o gate vivo
(`oracle.py --screen`) devolve `0 difference(s)` com a divergência presente —
ele compara o `screen.json` com a mesma leitura de objeto que o escreveu.

A diferença **está registrada**, mas só na
[`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md), como decisão dela
("o que a janela desenha ali é decisão desta task"). Não está no veredito da
§10.3 (q) do plano, que é a fonte de verdade da incógnita, nem no Log da
própria 21, nem no `screen.json`. Quem ler a tabela — e a janela da 22 é o
primeiro consumidor — escreve na tela um título que o jogo não escreve.

## Evidência

O dump de VRAM da própria execução (`work/looks-shots/vram-0.png`, 2026-09-17
15:20, o recorte nativo de 512×240 a partir de 0,0), na faixa do título, que o
`screen.json` ancora em `x=-224, y=-100` — ou seja, `x=32, y=20` no display:

```text
faixa y=0..70 do display, ampliada 3x:  'S SET'
o primeiro glifo cai em x≈33, que é o x da âncora do objeto
```

O que o `screen.json` guarda para os dois slots, no mesmo quadro:

```text
"title": "LOOKS SET"      slot 1
"title": "LOOKS SET"      slot 2
```

Cinco glifos desenhados contra nove guardados, e o começo do texto é que falta
— não é corte de overscan à direita, e à esquerda do `S` a faixa do título está
desenhada e vazia.

A conferência que existe para este caso não alcança o título:

```text
$ python tools/looks/screen.py --check
  ok    the glyph pass keeps the drawing pass and splits strings
  ok    pieces land on their rows; labels, plate, shirt and title kept out
screen.py: 0 failure(s)
```

`title` aparece no `self_check()` só como objeto que **não** pertence às
linhas; nada compara o texto dele com o desenho.

## Causa raiz

A conferência decode-contra-glifo foi construída para as linhas, e o título,
que é objeto de outra espécie (`ASCII_KINDS[1]`), entrou na tabela pela leitura
de objeto sem passar por ela.

## Correção

### Arquivo: `tools/looks/oracle.py` e `tools/looks/screen.py`

Levar título, placa e nome da camisa para a mesma conferência das linhas: o
texto do objeto contra os glifos que o quadro tem naquela âncora. Onde os dois
diferirem — e no título eles diferem —, o `screen.json` guarda **o que a tela
desenha**, com o texto do objeto ao lado e o nome do resíduo, como o
`confront.EXPECTED` faz com o goleiro. O gate fica vermelho se a diferença
mudar de forma, que é o que "medido" quer dizer aqui.

Se a razão for medida (animação de entrada do título, recorte do próprio jogo,
código de controle que o desenho consome), ela entra no lugar do resíduo.

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§10.3 (q))

O veredito ganha a linha do título: o objeto diz `LOOKS SET`, o quadro mostra
`S SET`, e por quê não foi medido. Hoje a única cópia dessa frase está na
task 22, e o plano é a fonte de verdade da incógnita.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | modificar |
| `tools/looks/screen.py` | modificar |
| `tools/looks/screen.json` | modificar (pela ferramenta, `--screen --write`) |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/22-a-tela-na-janela.md` | modificar (o que a janela desenha no título passa a sair da tabela) |

## Verificação

- [x] `python tools/looks/oracle.py --screen` fica **vermelho** com o título
      guardado como `LOOKS SET`, e verde com o que a tela desenha
- [x] o controle negativo do novo caso fica vermelho (`controls.py`)
- [x] `python tools/looks/screen.py --check` e
      `python tools/looks/selftest.py --quiet` verdes
- [x] §10.3 (q) do plano diz o que o título mostra e o que o objeto guarda
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `6c35155`: o `screen.json` guarda `LOOKS SET` nos dois
slots e a faixa do título do dump da 21 (`work/looks-shots/vram-0.png`, recorte
nativo) desenha quatro letras — `S SET`.

**A razão foi medida, então entrou no lugar do resíduo.** O título é impresso
pela **segunda** fonte ASCII (`kind` 33), e essa não passa pela rotina de
glifos: nenhuma string é desenhada na linha dele (`y=-100`) nas duas leituras
de `screen_glyphs`. O que ela desenha foi medido escrevendo um marcador de onze
bytes sobre a string, na RAM do jogo em execução (`write_memory`), e lendo a
faixa de volta da VRAM:

```text
AAAAAAAAAAA   desenha onze As
ABCDEFGHIJK   desenha  A E J
0123456789A   desenha  1 2 A
01234     A   desenha  1 2     A   (os cinco espaços empurram o A 42 px)
```

Varrendo um caractere de cada vez, **nove dos 71 imprimíveis desenham** —
`AEJSTW12-` —; os outros 62 **não desenham e não andam com a caneta**. Por isso
`LOOK` some e a tela mostra `S SET`. Não é captura cortada: a faixa tem as
mesmas quatro letras do quadro 0 ao 600. O state foi recarregado no fim de cada
sonda e a string voltou a ler `LOOKS SET  `; `roms/` não foi tocada.

- `screen.py` — `TITLE_FONT` com a medição, `title_drawn`, `title_skipped`,
  `title_band`, `ink_runs` (uma corrida de branco por letra) e a regra nova do
  `validate()`: os três campos do título têm de concordar, o que **recusa** a
  tabela que guardava `LOOKS SET`.
- `oracle.py` — `outside_control()`: placa e nome da camisa passam a ser
  comparados **string por string** contra os glifos desenhados à esquerda da
  caixa das linhas, e o título contra a **contagem de letras** da faixa. O
  `outside()` devolve os objetos, não mais texto solto.
- `screen.json` — regravado pela ferramenta: `title` é o que a tela desenha,
  com `title_object` e `title_skipped` ao lado.
- Plano §10.3 (q), `perfil-looks.md` (armadilha 37) e a LOOKS-TASK-22.

**Uma armadilha do ciclo custou uma varredura inteira:** a primeira passagem do
alfabeto tirou **um** dump por caractere e concluiu que `2` não tem glifo. Um
quadro terminado sem o título é o mesmo piscar que o cursor tem — a §33/36 do
perfil já dizia isso do cursor. Com quatro dumps por caractere o conjunto fecha,
e o `outside_control` aceita faixa vazia num buffer e recusa faixa com **outra**
contagem.

### Gates

```text
$ python tools/looks/oracle.py --screen          # antes de regravar
  slot 1 on load: ... the title object holds 'LOOKS SET' and the band draws 'S SET'
  slot 2 on load: ... the title object holds 'LOOKS SET' and the band draws 'S SET'
  screen measured in 660s
oracle FAILED: tools\looks\screen.json does not hold together: slot 1 does not
say what string the title object holds; slot 2 does not say what string the
title object holds                                        # exit 1

$ python tools/looks/oracle.py --screen --write  # 721 s
oracle --screen --write: wrote tools\looks\screen.json
$ git diff --stat tools/looks/screen.json
 tools/looks/screen.json | 6 +++++-   # só os três campos do título, por slot

$ python tools/looks/oracle.py --screen          # depois
oracle --screen: 0 difference(s) from screen.json   # 716 s, exit 0

$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ python tools/looks/controls.py --only screen-title-as-the-object-holds-it
  RED    screen-title-as-the-object-holds-it screen.py :: title_drawn
$ python tools/looks/selftest.py --quiet
  ..... 68 of 68 controls red
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

E a recusa que a CORR pede, sobre a tabela medida:

```text
>>> table["initial"]["1"]["title"] = table["initial"]["1"]["title_object"]
  FAIL  slot 1 stores the title 'LOOKS SET', and the object holds 'LOOKS SET',
        which draws 'S SET'
```

`roms/` intocada (leitura pura); nenhuma cópia de imagem em `work/`; nenhum
DuckStation de pé no fim.

### Problemas encontrados

- A placa divide a linha com `NAT` (`y=-67`): a primeira versão da conferência
  comparou a linha inteira e recusou `GK` contra `['Unknown', 'GK', 'NAT']`. A
  comparação é do que se desenha **à esquerda da caixa das linhas**, que é o
  mesmo critério que o `screen.in_rows` já usava.
- **Achado fora do escopo desta correção:** `screen.py --report` morre com
  `UnicodeEncodeError` no `■` da ajuda quando a saída é cp1252, que é o default
  desta máquina; só imprime com `PYTHONIOENCODING=utf-8`. Virou a
  [`CORR-LOOKS-055`](/docs/tasks/looks/CORR-LOOKS-055.md).

### Arquivos criados/modificados

- `tools/looks/screen.py`, `tools/looks/oracle.py`, `tools/looks/controls.py`
- `tools/looks/screen.json` — pela ferramenta
- `docs/PLAN-LOOKS-PY.md` §10.3 (q), `docs/prompts/perfil-looks.md`,
  `docs/tasks/looks/22-a-tela-na-janela.md`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
