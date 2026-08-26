---
id: CORR-WTE-118
title: "Correção: a seção de renomeação da WTE-TASK-39 ainda manda renomear o que a própria task decidiu não renomear"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-118: a instrução de renomear ficou de pé depois de revogada

## Problema identificado

A [WTE-TASK-39](/docs/tasks/39-empacotamento.md) recebeu da
[WTE-TASK-38](/docs/tasks/38-nome-e-linhagem.md) um repasse com inventário
medido, sob o título *"O que a WTE-TASK-38 decidiu, e que esta task aplica"*.
Uma das linhas manda renomear:

> `wte.lpi`, `wte.lpr` e `build/wte` **passam a levar o slug**. Quem os cita,
> medido em 2026-08-25 com `grep -rl`: 3 ferramentas, o `Makefile`, prosa de
> `docs/`…

**A execução decidiu o contrário**, e escreveu isso no Log da mesma task:

> Uma decisão mudou de forma em relação ao repasse da WTE-TASK-38: o projeto
> continua se chamando `wte` na árvore, e o slug `we2002Lazarus` entra no
> `install`.

A seção do repasse **não foi anotada**. Quem ler a task de cima a baixo
encontra a instrução na seção e a revogação no Log, e nada liga uma à outra; a
seção continua dizendo *"que esta task aplica"*.

O estado da árvore concorda com o Log: `wte/wte.lpi`, `wte/wte.lpr` e
`wte/build/wte` seguem com o nome antigo, e só o binário instalado leva o slug.
O [`wte/README.md`](../../wte/README.md) registra a reversão **corretamente**,
com a razão — então o único documento fora de sincronia é a própria task.

É a **prosa vencida** que a terceira passagem da
[WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) batizou: documento que
envelhece sozinho enquanto alguém o lê como estado corrente. Aqui o prazo é
curto — a próxima leitora é a
[WTE-TASK-40](/docs/tasks/40-verificacao-final.md), que confere o produto
instalado.

## Evidência

As duas frases, no mesmo arquivo:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "passam a levar o slug" docs/tasks/39-empacotamento.md
grep -n "continua se chamando .wte. na árvore" docs/tasks/39-empacotamento.md
```

```text
210:`wte.lpi`, `wte.lpr` e `build/wte` passam a levar o slug. Quem os cita, medido
136:  projeto continua se chamando `wte` na árvore, e o slug `we2002Lazarus` entra
```

A instrução está na **linha 210** e a revogação na **136** — a revogação vem
antes no arquivo, e a seção que ela revoga não diz nada.

O que a árvore diz — os nomes antigos de pé, e o slug só no instalado:

```bash
ls wte/wte.lpi wte/wte.lpr wte/build/wte
make -C wte install PREFIX=/tmp/p && find /tmp/p -type f -name 'we2002*' | head -2
```

```text
wte/build/wte wte/wte.lpi wte/wte.lpr

bin/we2002Lazarus
share/applications/io.github.aguilasa.we2002Lazarus.desktop
```

*(A instalação foi medida nesta revisão: 13 arquivos num prefixo temporário, e
o binário instalado é o único que leva o slug.)*

E o `README.md`, que já registra a reversão como decisão fechada:

```text
### O binário se chama `wte` na árvore e `we2002Lazarus` instalado

O repasse da WTE-TASK-38 previa renomear `wte.lpi`, `wte.lpr` e `build/wte`
para o slug. **Não foi feito, e a razão é de custo:** [...]
```

| Sítio | O que diz |
|---|---|
| `39-empacotamento.md:210` | renomear — **instrução viva** |
| Log da mesma task | não renomear, com razão |
| `wte/README.md` | não renomear, com razão |
| a árvore | não renomeado |

## Causa raiz

A seção do repasse foi escrita pela task anterior como instrução, e a execução
revogou a instrução no Log sem voltar à seção que a carrega.

## Correção

### Arquivo: `docs/tasks/39-empacotamento.md`

Anotar a seção no lugar, no formato que as outras revogações deste projeto já
usam — o fato primeiro, a razão depois:

> ### A renomeação, com o inventário já medido — **não executada**
>
> **O repasse previa isto e a execução decidiu o contrário** (ver o Log, e a
> seção *"O binário se chama `wte` na árvore e `we2002Lazarus` instalado"* do
> [`wte/README.md`](../../wte/README.md)): `wte.lpi`, `wte.lpr` e `build/wte`
> **continuam** com o nome da árvore; o slug entra no `install`. O inventário
> abaixo fica porque continua correto — é quem citaria os três arquivos **se**
> a renomeação vier a acontecer.

O inventário em si vale guardar: os três caminhos e o `Makefile` estão medidos,
e refazê-los custaria o mesmo `grep -rl`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/39-empacotamento.md` | modificar |

## Verificação

- [x] `grep -n "passam a levar o slug" docs/tasks/39-empacotamento.md` sai
      vazio — a frase foi reescrita como condicional
- [x] A seção diz, **no título**, que não foi executada
- [x] `make -C wte check` verde (865 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-26

**Resumo do que foi feito:**

O título da seção passou a dizer **— não executada**, e a primeira coisa depois
dele é a ressalva: o repasse previa, a execução decidiu o contrário, e a razão
está no Log e no `wte/README.md`. A frase que mandava renomear virou
condicional (*"se a renomeação for feita algum dia, quem cita os três…"*), de
modo que o inventário medido continua servindo sem se passar por instrução.

**Problemas encontrados:**

**O `wte/README.md` se contradizia, e a CORR o citava como o documento que
estava certo.** Ele registra a reversão com a razão na linha 201 — isso é
verdade —, mas vinte e sete linhas acima ainda dizia:

> **O que falta, e é da WTE-TASK-39:** renomear `wte.lpi`/`wte.lpr`/`build/wte`
> para o slug […], e criar `packaging/` com o `.desktop`, o AppStream e o ícone.

Falso duas vezes: o `packaging/` existe (`.desktop`, AppStream e os sete PNG) e
a renomeação foi decidida contra. O mesmo arquivo dizia as duas coisas, a 27
linhas de distância — que é exatamente o defeito desta correção, no documento
que ela apontava como referência.

Reescrito para dizer o que a task fez e o que ela decidiu **não** fazer,
apontando para a seção que traz a razão. O `wte/Makefile:138` foi conferido e
já registrava a decisão corretamente.

Sobram duas ocorrências vivas da frase `renomear wte.lpi…`, no `Makefile` e no
`README.md`: as duas dizem *"não foi feito"*. São registro da não-execução, que
é o oposto de instrução viva.

**Arquivos criados/modificados:**

- `docs/tasks/39-empacotamento.md` — o título e a ressalva
- `wte/README.md` — a contradição, achada na varredura
