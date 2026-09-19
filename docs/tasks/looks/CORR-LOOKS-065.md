---
id: CORR-LOOKS-065
title: "Correção: três medições da LOOKS-TASK-29 sobre o ritmo e a mistura ficaram \"para o leitor de pose\", sem linha na task que as mede"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-065: o que a 29 achou sobre a caminhada não chegou à 32

## Problema identificado

O Log da [`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md) registra,
nos problemas 3 e 4, três medições que não são de estatura e sim do **ritmo e
da mistura da caminhada**, e as encaminha sem nomear para onde vão:

```text
  3. ... uma passada desenha dois quadros do `ANIME.BIN` cortados numa peça que
     muda com a fase ...
  4. **Passada com pares pode ser interpolação** (11 pares, 0 de 11 exatas),
     e **o quadro 0 do goleiro é mistura** mesmo na estatura do estado. O
     controle exige uma passada que o leitor de pose reproduz inteira e
     imprime as que recusa (armadilha 74) — o que fica para o leitor de pose,
     não para esta task.
```

A task que mede isso existe e está pendente: a
[`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md) — *"quadros por
passada, interpolação e balanço"*, com o critério *"Quadros-chave contra
quadros desenhados: iguais, ou a interpolação medida"*. O arquivo dela não foi
tocado desde `85ca349`, anterior à 29, e não traz nenhuma das três:

1. **uma passada de desenho atravessa dois quadros do `ANIME.BIN`**, cortados
   numa peça que muda com a fase — `(1, 2)` no slot 2 e `(3, 4)` no slot 1,
   medido hoje;
2. **uma passada inteira pode vir interpolada**: 11 pares lidos, 0 de 11
   matrizes exatas, pela média `(a+b)>>1` de `0x80011F90..0x800120D0`. A 32 cita
   o `0x80011F90` para as 6 misturas de peça avulsa da 26, e não a passada
   inteira;
3. **no goleiro, o quadro 0 é mistura** na estatura do próprio estado: a
   `foot b` sai até **92 de 4096** fora da matriz do arquivo, com os ângulos
   do scratchpad **iguais** aos do par.

As três estão no perfil (armadilhas 73 e 74), que todo executor lê. Mas a
regra do `/executar` é explícita — *"pendência encaminhada para outra task
precisa da linha escrita na task de destino, não só no seu Log: quem executar
a NN lê o arquivo dela"* —, e já falhou duas vezes neste repositório
(CORR-WTE-086 e CORR-WTE-105). "Fica para o leitor de pose" não é destino: a
32 é, e o critério dela sobre "iguais, ou a interpolação medida" é exatamente
onde a passada de 0 de 11 e o quadro 0 do goleiro entram.

## Evidência

Recorrido hoje, na árvore de `d85ada8`:

```text
$ python tools/looks/oracle.py --stature
  -- slot 2 (outfield player) --
    state           175 cm A  ... pieces 12/12 exact, frames [1, 2], 12 with the control's own pair  ok
  -- slot 1 (goalkeeper) --
      control refuses pass 2, frames [0, 1]: 11 of 12 exact, ['foot b'] off by up to 92 of 4096 with the scratchpad angles the file's own
    state           175 cm A  ... pieces 12/12 exact, frames [3, 4], 12 with the control's own pair  ok
oracle --stature: 0 problem(s) over 2 slot(s)

$ git log --format=%h -1 -- docs/tasks/looks/32-o-ciclo-da-caminhada.md
85ca349

$ grep -n "92 de 4096\|0 de 11\|dois quadros\|goleiro" docs/tasks/looks/32-o-ciclo-da-caminhada.md
(vazio)
```

## Causa raiz

A 29 achou coisas da caminhada enquanto controlava a estatura, recusou-as do
controle com razão, e as escreveu no perfil e no próprio Log, mas não na task
que as mede.

## Correção

### Arquivo: `docs/tasks/looks/32-o-ciclo-da-caminhada.md`

No Contexto, um item datado com as três medições e o comando que as reproduz:

- a passada desenha dois quadros (`oracle._stature_frames`, armadilha 73);
- a passada de 11 pares e 0 de 11 exatas, e o caminho `(a+b)>>1` que a 29
  nomeou;
- o quadro 0 do goleiro, `foot b` 92 de 4096 fora com os ângulos do arquivo,
  que o `oracle.py --stature` imprime como passada recusada em toda corrida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/32-o-ciclo-da-caminhada.md` | modificar |

## Verificação

- [ ] a LOOKS-TASK-32 traz as três medições no Contexto, com o comando que as
      reproduz e o link para a 29
- [ ] `python tools/check_tasks.py` ok
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
