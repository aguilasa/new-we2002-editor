---
id: CORR-WTE-054
title: "Correção: o `vmt.md` diz que todo número saiu do `vmt_probe.java`, e os votos da âncora não saíram"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-054: os "4 votos entre ~150 referências" não têm ferramenta versionada

## Problema identificado

O [`wte/re/vmt.md`](../../wte/re/vmt.md) abre com uma afirmação de proveniência:

> Todo número deste arquivo saiu de `wte/tools/ghidra/vmt_probe.java` e de
> `decompile_one.java`, rodando sobre o projeto que o `run_headless.sh` monta.

Ela vale para quase todos, e esta revisão remediu os principais rodando o probe
— 217 chamadas virtuais, 189 com campo, corrida de 113 slots, os dez slots de
VMT, a assinatura `__fastcall` de `colorearClick`. **Menos** os números da
tentativa de âncora:

> o candidato mais votado teve **4 votos** entre ~150 referências, e os dois
> primeiros colocados ficaram a 4 bytes um do outro.

Nem o `vmt_probe.java` nem o `decompile_one.java` computam voto:

```
$ grep -in "voto\|ancora\|anchor" wte/tools/ghidra/vmt_probe.java
(nada)
```

O que o probe imprime é a **entrada** do cálculo — a seção
`CAMPOS-POR-HANDLER` —, e o próprio `vmt.md` diz isso ("que é a entrada da
tentativa de âncora"). O voto em si foi feito fora, por meio descartável, e
ninguém consegue refazê-lo a partir do que está versionado.

Isso importa mais aqui do que num número decorativo: **é esse número que decide
a rota da §8.2**. "Não convergiu: 4 votos entre ~150" é a evidência de que a
âncora por dono de handler não fecha, e é dela que sai a consequência escrita —
*spec de handler cita `campo +0xNNN` e `slot +0xNN`, nunca nome de componente
inferido*. Uma decisão de método apoiada num número que não se remede é
exatamente a armadilha 11 do `progresso.md` (*"todo número em doc vem de
ferramenta"*), agravada pela frase que promete o contrário.

## Evidência

O que o probe sabe imprimir:

```
$ grep -n 'println("' wte/tools/ghidra/vmt_probe.java
111:        println("vmt_probe: formulario " + forma);
112:        println("vmt_probe: " + vcalls + " chamada(s) virtual(is), "
118:        println("vmt_probe: " + campos.size() + " campo(s) distinto(s):");
143:        println("vmt_probe: slots de VMT usados:");
152:        println("vmt_probe: CAMPOS-POR-HANDLER (handler<TAB>0xNNN,...)");
173:            println("CAMPOS\t" + fn.getName() + "\t" + sb);
```

Rodado nesta revisão, ele reproduz tudo o mais:

```
vmt_probe: 217 chamada(s) virtual(is), 189 com campo de objeto recuperado
vmt_probe: 41 campo(s) distinto(s)
vmt_probe: corrida de +0x2f0 a +0x4b0 = 113 slot(s) de 4 bytes; 26 par(es) consecutivo(s) com passo 4
vmt_probe: slots de VMT usados:  +0xc 6x, +0x20 6x, +0x3c 5x, +0x64 39x, +0x80 1x,
                                 +0x88 10x, +0xc0 3x, +0xc8 97x, +0xcc 22x, +0xe8 28x
```

(os dez slots somam 217 — a afirmação "dez slots cobrem 217 chamadas" fecha).

Mas não há saída nenhuma com voto, candidato ou base — os dois únicos números do
arquivo sem origem executável.

## Causa raiz

O cálculo da âncora foi feito fora dos scripts versionados, e a frase de
proveniência do topo não foi qualificada.

## Correção

Duas rotas, e a primeira é melhor porque devolve o número à ferramenta:

1. **Pôr a votação no `vmt_probe.java`.** Ele já tem os dois insumos — o campo
   por handler e o `published_methods.tsv` com o dono de cada um — e a conta é
   `base = campo − 4·(posição − 1)`. Imprimir a tabela de candidatos com os
   votos, e o `vmt.md` passa a citar saída de ferramenta como o resto do
   arquivo;
2. **Qualificar a frase**, dizendo que os votos foram calculados fora, a partir
   da seção `CAMPOS-POR-HANDLER`, e registrando o comando — mantendo o número,
   mas sem prometer proveniência que ele não tem.

Escolhida a rota 1, o número pode mudar (a contagem "~150" já é aproximada no
texto); o que não pode é continuar afirmado como medido sem medidor.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/ghidra/vmt_probe.java` | modificar (rota 1) |
| `wte/re/vmt.md` | modificar — o número, e a frase de proveniência |

## Verificação

- [ ] todo número do `vmt.md` sai de saída de script versionado, ou o texto diz
      de onde veio
- [ ] rodar o `vmt_probe.java` reproduz os números de âncora citados
- [ ] os números já conferidos não mudam: 217 / 189 / 113 slots / dez slots de
      VMT / `colorearClick` `__fastcall` com 1 parâmetro
- [ ] `make -C wte check` verde
- [ ] nenhum trecho decompilado colado no `vmt.md` (§2, §8.10)

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
