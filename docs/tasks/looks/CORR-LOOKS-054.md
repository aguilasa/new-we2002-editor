---
id: CORR-LOOKS-054
title: "Correção: o `screen.json` guarda o título `LOOKS SET`, a tela desenha `S SET`, e nenhum gate compara os dois"
type: correção
category: verificação
status: pendente
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

- [ ] `python tools/looks/oracle.py --screen` fica **vermelho** com o título
      guardado como `LOOKS SET`, e verde com o que a tela desenha
- [ ] o controle negativo do novo caso fica vermelho (`controls.py`)
- [ ] `python tools/looks/screen.py --check` e
      `python tools/looks/selftest.py --quiet` verdes
- [ ] §10.3 (q) do plano diz o que o título mostra e o que o objeto guarda
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
