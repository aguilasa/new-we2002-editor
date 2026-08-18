---
id: CORR-WTE-062
title: "Correção: o `lista_formacionesClick` ficou entre duas tasks concluídas e continua `REStub`"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-062: o handler que as duas tasks apontaram uma para a outra

## Problema identificado

`estrategia.lista_formacionesClick` (`0x00409aa0`) pertence ao grupo **carga**,
da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md). A spec dele fecha assim:

> **Veredito `aberto`, com dono nomeado:** o efeito está nas duas rotinas não
> lidas, e o que elas fazem é editar tática — que é a WTE-TASK-26.

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) fechou **sem portá-lo**, e
com razão: ele não está entre os 28 handlers dela — o grupo dele é `carga`. As
duas tasks estão `✅ Concluído`, e o corpo continua `REStub`.

**Não é só um handler parado.** Dois handlers da 26 ficaram `aberto` por
dependerem dele: é o `lista_formacionesClick` que preenche o vetor bola→zona
(`0x00434230`) e as seis tabelas da animação. Enquanto ele não existir:

- o `bolaMouseDown` desenha o retângulo **sempre da zona 0**, porque o vetor
  nasce zerado;
- o `relojTimer` **nunca roda**, porque ninguém habilita o `reloj`;
- os handlers de arrastar precisam de uma guarda de `nil` que o original não
  tem, porque é o `relojTimer` que semeia os dois globais.

É o padrão que este projeto já pagou e escreveu no enunciado da 25: **exclusão
sem dono nomeado é buraco.** Aqui o dono foi nomeado — e nomeado errado.

## Evidência

```
$ awk -F'\t' '$2=="lista_formacionesClick"{print $1"\t"$3"\t"$6}' \
    wte/re/published_methods.tsv
0x00409aa0	estrategia	carga

$ sed -n '212,215p' wte/src/ep2002_estrategia.pas
procedure Testrategia.lista_formacionesClick(Sender: TObject);
begin
  REStub('estrategia.lista_formacionesClick');
end;

$ grep -E 'WTE-TASK-2[56]\]' docs/tasks/progresso.md | cut -d'|' -f2,6,7
 [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | ✅ Concluído | 2026-08-11
 [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | ✅ Concluído | 2026-08-18
```

E as duas auxiliares que a spec chama de "não lidas" já estão inventariadas:

```
$ grep -E "^0x0040(97d4|99bc)" wte/re/auxiliares.tsv | cut -f1,3,4
0x004097d4	474	estrategia.lista_formacionesClick,0x0040a0b4
0x004099bc	227	estrategia.lista_formacionesClick,0x0040a0b4
```

## Causa raiz

A spec da 25 encaminhou pelo **efeito** ("o que elas fazem é editar tática") e
não pelo **grupo**. A 26 seleciona os handlers dela pela coluna `grupo` do
`published_methods.tsv`, que diz `carga` — então o encaminhamento nunca teve
como ser recebido. Nenhuma das duas tasks tinha como notar: a 25 fechou antes de
a 26 existir em detalhe, e a 26 conferiu a própria lista, que estava certa.

## Correção

Portar o `lista_formacionesClick`, com as duas auxiliares (`0x004097d4`, 474 B e
`0x004099bc`, 227 B — as duas já com tamanho medido).

**Onde ela mora não é óbvio, e a escolha tem de ser escrita:** o handler é da
25, o efeito é da 26, e as duas estão fechadas. Executar esta correção é a
terceira opção, e é a que não reabre task nenhuma — mas o Log dela precisa dizer
qual spec foi atualizada e por quê.

Ao fechar, três vereditos mudam de estado e **têm de ser revistos na mesma
passagem**: o `estrategia.lista_formacionesClick`, o `estrategia.bolaMouseDown` e
o `estrategia.relojTimer`. Se os três não forem tocados, a correção deixou
metade do efeito para trás.

### Arquivos

- [`wte/src/impl/`](../../wte/src/impl/) — o `.inc` novo e o estado no `.aux.inc`
- [`wte/re/spec/estrategia.lista_formacionesClick.md`](../../wte/re/spec/estrategia.lista_formacionesClick.md)
- as specs do `bolaMouseDown` e do `relojTimer`
