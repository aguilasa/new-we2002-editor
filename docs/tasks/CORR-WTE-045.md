---
id: CORR-WTE-045
title: "Correção: a seção das seis áreas cita `roms/09-areas-com-time`, que é o nome da sessão e não o da imagem"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-WTE-045: o `offsets-novos.md` nomeia uma ROM que não existe

## Problema identificado

A seção **"As seis áreas, com um time carregado"** do
[`wte/re/offsets-novos.md`](../../wte/re/offsets-novos.md) — gerada por
`wte/tools/analisar_io.py` — diz que a medição foi feita sobre

> cópia de `roms/09-areas-com-time`

`09-areas-com-time` é o nome da **sessão** (o diretório de saída do
`diff_dirigido.sh`), não o da imagem. Não existe `roms/09-areas-com-time`:
`roms/` tem `golden-european-deluxe.bin`, `golden-european-deluxe.cue` e
`japanese-shift-jis.bin`. A imagem real dessa sessão é
`japanese-shift-jis.bin`, e o `io-medido.tsv` a registra em cada uma das 64
linhas.

O erro é do interpolador: a constante `AREAS` foi posta onde o nome da imagem
devia ir. A frase seguinte (*"com a europeia o `wte.exe` morre na troca de
time"*) só faz sentido se a imagem for a japonesa — então o parágrafo se
contradiz sozinho.

Isso importa porque a escolha da imagem é justamente o que a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md) desbloqueou, e é o insumo do gate da
[WTE-TASK-22](/docs/tasks/22-harness-golden.md), que precisa **fixar a imagem
japonesa e dizer por quê**. Quem for buscar essa referência no `offsets-novos.md`
encontra um caminho inexistente.

## Evidência

O texto gerado:

```
$ sed -n '/## As seis áreas/,+6p' wte/re/offsets-novos.md
## As seis áreas, com um time carregado

Medido com o roteiro
[`09-areas-com-time.txt`](../tests/roteiros/09-areas-com-time.txt) sobre
cópia de `roms/09-areas-com-time`. **A imagem não é escolha de gosto:** com a
europeia o `wte.exe` morre na troca de time, e o roteiro mediria o
travamento em vez das áreas ([`crash-causa.md`](crash-causa.md)).
```

A imagem verdadeira, na evidência:

```
$ awk -F'\t' 'NR>1{c[$2"\t"$1]++} END{for(k in c) print c[k], k}' wte/re/io-medido.tsv | sort
102 10-telas-que-faltavam	japanese-shift-jis.bin
125 11-varredura-de-times	japanese-shift-jis.bin
38 06-diff-dirigido	golden-european-deluxe.bin
38 06-truncada	truncada-474431328.bin
64 09-areas-com-time	japanese-shift-jis.bin
```

E o caminho não existe:

```
$ ls roms/
golden-european-deluxe.bin  golden-european-deluxe.cue  japanese-shift-jis.bin
```

A fonte do defeito, em `wte/tools/analisar_io.py:478`:

```python
w(f"cópia de `roms/{AREAS}`. **A imagem não é escolha de gosto:** com a")
```

com `AREAS = "09-areas-com-time"` (linha 446).

## Causa raiz

A f-string interpola a constante da **sessão** onde devia interpolar o campo
`imagem` das linhas dessa sessão.

## Correção

### Arquivo: `wte/tools/analisar_io.py`

O alvo é gerado — a correção entra no gerador. Tirar o nome da imagem da própria
evidência, não de constante:

```python
imagens = sorted({r["imagem"] for r in linhas})
w(f"cópia de `roms/{'`, `roms/'.join(imagens)}`. "
  "**A imagem não é escolha de gosto:** com a")
```

Uma sessão tem uma imagem só; derivar do dado em vez de escrever à mão faz a
frase seguir a evidência se outra sessão vier a ocupar essa seção.

### Arquivo: `wte/re/offsets-novos.md`

Regerar (`python3 wte/tools/analisar_io.py`, sem `--check`).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/analisar_io.py` | modificar |
| `wte/tools/test_analisar_io.py` | modificar — teste que a seção nomeie um arquivo existente em `roms/` |
| `wte/re/offsets-novos.md` | modificar (regerado) |

## Verificação

- [ ] `grep -n 'roms/' wte/re/offsets-novos.md` só devolve nome de arquivo que
      existe em `roms/`
- [ ] teste novo reprova quando o nome da sessão volta ao lugar do nome da imagem
- [ ] `python3 wte/tools/analisar_io.py --check` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
