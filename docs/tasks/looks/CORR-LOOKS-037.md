---
id: CORR-LOOKS-037
title: "Correção: as alturas da cabeça e da chuteira estão escritas com o sinal trocado"
type: correção
category: dados
status: done
depends_on: []
origin: LOOKS-TASK-15
severity: low
done_on: 2026-09-16
done_commit: efd4440
---

# CORR-LOOKS-037: "a cabeça de y -15 a 48" é a do render, não a do arquivo

## Problema identificado

O achado da LOOKS-TASK-15 — que nenhum dos dois arquivos de modelo diz onde uma
peça fica — está certo, e os dois números que o ilustram estão **com o sinal
trocado**. A frase aparece em dois lugares, com o mesmo texto:

```text
docs/PLAN-LOOKS-PY.md, §5.6
   Cada seção é modelada em torno da própria origem — a cabeça vai de
   y -15 a 48 e a chuteira de -15 a 18 —, então desenhar as doze peças
   NAS COORDENADAS DO ARQUIVO empilha o boneco inteiro num ponto só.

docs/tasks/looks/15-visualizador-opengl.md, o Log
   … a cabeça de y -15 a 48, a chuteira de -15 a 18 …
```

Nas coordenadas do arquivo, que é o que a frase diz estar citando, os dois
intervalos são **-48..15** e **-18..15**. Os escritos são os do render, depois
de o `scene.UP = -1` virar o eixo.

Não muda o achado — a peça continua em torno da própria origem, e a soma das
doze continua empilhando —, mas é exatamente o eixo que o `UP = -1` deste
módulo torna fácil de errar, e a frase convida a conferir no arquivo e achar o
contrário.

## Evidência

Script próprio sobre `roms/japanese-shift-jis.bin`, lendo os vértices como o
`section.scan` os entrega:

```text
head section 24: y -48..15
boot section 9:  y -18..15
boot section 10: y -18..15
```

E o render, que é de onde os números escritos vieram:

```text
python tools/looks/scene.py --check-image
      the head sits at y 17 and the boots at y -3, with UP = -1
```

`-(-48..15)` é `-15..48`, e `-(-18..15)` é `-15..18`: os dois valores do texto,
já virados.

## Causa raiz

Os intervalos foram lidos depois do `UP` e escritos numa frase que diz estar
falando das coordenadas do arquivo.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§5.6) e `docs/tasks/looks/15-visualizador-opengl.md`

Escrever os dois intervalos como o arquivo os guarda — a cabeça de **-48 a 15**
e a chuteira de **-18 a 15** — e dizer, na mesma frase, que no render eles
aparecem virados porque `scene.UP` é `-1`. As duas metades juntas custam meia
linha e fazem a frase sobreviver a quem for conferir no disco.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/15-visualizador-opengl.md` | modificar |

## Verificação

- [x] os intervalos escritos são os que um `section.scan` devolve, e o texto
      diz de qual eixo fala — e diz também onde os do render aparecem
- [x] `python tools/looks/scene.py --check-image` verde (o `UP` continua medido
      pela cabeça ficar acima da chuteira, não declarado)
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

Lido do disco pelo `section.scan`, que é o que a frase dizia estar citando:

```text
head section 24: y -48..15
boot section 9:  y -18..15
boot section 10: y -18..15
```

Os dois lugares — a §5.6 do plano e o Log da task — passaram a trazer os
intervalos do **arquivo**, com a segunda metade na mesma frase: no render eles
aparecem virados porque o `scene.UP` é `-1`. As duas metades juntas custam meia
linha e fazem a frase sobreviver a quem for conferir no disco — que era o
problema, já que a versão antiga convidava a conferir e a achar o contrário.

O achado não muda: a peça continua modelada em torno da própria origem, e somar
as doze continua empilhando o boneco num ponto só.

### Problemas encontrados

Nenhum. O `UP` continua **medido** pelo `--check-image` — a cabeça fica em
y 17 e a chuteira em y -3 —, não declarado, que é o que torna esta correção só
de texto.

### Arquivos criados/modificados

- `docs/PLAN-LOOKS-PY.md` — §5.6
- `docs/tasks/looks/15-visualizador-opengl.md` — o Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-037.md` — este arquivo
_Migrated on 2026-09-21: done_commit approximated from the last commit touching this file._
