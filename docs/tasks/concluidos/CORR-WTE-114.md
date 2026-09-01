---
id: CORR-WTE-114
title: "Correção: três divergências novas ficaram numa task concluída, e o registro que existe para elas não as tem"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-114: as três candidatas da UI não chegaram ao `divergencias.md`

## Problema identificado

A [WTE-TASK-37](/docs/tasks/concluidos/37-reconferencia-de-ui.md) mediu três coisas que
pedem decisão de registro, e as escreveu numa seção nova no fim do markdown da
[WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md) — *"Candidatas
posteriores — WTE-TASK-37"*. O critério dela pede *"achado que volta para outra
fase registrado com a task de destino"*, e por essa letra está cumprido.

**Só que a WTE-TASK-35 está `concluído`.** Ninguém vai executá-la de novo, e o
artefato que ela produziu — o [`wte/re/divergencias.md`](../../../wte/re/divergencias.md),
que é o registro guardado pelo `check_divergencias.py` — **não tem nenhuma das
três**. A primeira delas diz isso com todas as letras:

> 1. **`ficha_warning` não é levantado pelo port** (achado 8). […] Divergência
>    deliberada de comportamento em produção, **ainda sem entrada aqui**.

Uma divergência **deliberada**, **em produção**, com causa medida e sem entrada
no documento cuja frase de abertura é *"não significa que nenhuma divergência é
aceita — significa que nenhuma é desconhecida"*. É a definição de divergência
documentada virando silenciosa, que é o buraco que o último campo do formato
(*onde o teste sabe*) existe para tapar.

As outras duas precisam de decisão, e as três não são a mesma coisa:

| # | Achado | O que é |
|---|---|---|
| 1 | `ficha_warning` não é levantado; o port aplica os remendos sem perguntar | **divergência deliberada** — entra no registro com os seis campos |
| 2 | `ficha_enlaza` sem chamador no port | **rota não portada**, não divergência escolhida — o vocabulário importa, e o dono é o `mostrar_jugadorClick`, que a WTE-TASK-30 deixou por medir |
| 3 | `help_team` (`TStaticText` desabilitado) pinta fundo próprio no GTK2 | mesma família da divergência 2 (os cinco glifos) — **entra**, e provavelmente ao lado dela |

## Evidência

O que a task 35 recebeu, e o que o registro tem:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -n "Candidatas posteriores" docs/tasks/35-divergencias-deliberadas.md
grep -n "^status:" docs/tasks/35-divergencias-deliberadas.md
grep -c "ficha_warning\|ficha_enlaza\|help_team" wte/re/divergencias.md
python3 wte/tools/check_divergencias.py --check
```

```text
427:## Candidatas posteriores — WTE-TASK-37 (2026-08-25)
8:status: concluído
0
check_divergencias: wte/re/divergencias.md: ok -- 3 excecao(oes) nomeada(s) com entrada, 1 retirada(s) que nao voltou(aram), 0 faixa(s) `conhecida:` na bateria de bytes, 9 secao(oes) no documento
```

**Zero ocorrências** das três no registro, e o gate passa verde — porque ele
confere *exceção de ferramenta contra entrada*, e estas três não são exceção de
ferramenta: são comportamento. O guarda não erra; ele não cobre esta direção.

E a medição do `help_team`, que já está feita e só precisa de destino:

```text
wte/re/visual.md:536: `help_team` (`Time Res.`, `Enabled = False` no DFM), que
sai `#76B6FF` (a cor do formulário) no oráculo e `#DCDAD5` (o cinza do tema) no
port
```

## Causa raiz

O repasse foi escrito na task que originou o formato, e não no documento que o
formato produz — e aquela task já estava fechada.

## Correção

### Arquivo: `wte/re/divergencias.md`

Abrir a entrada da **1** e da **3**, com os seis campos, como as seis que já
estão lá. A **3** tem a evidência pronta (a medição do `check_carregado.py`, com
as duas cores e o contraste do `base_team`, que bate porque o app o reabilita);
a **1** precisa do campo *onde o teste sabe* dizer que a bateria de bytes fecha
**por causa** da divergência — o port não pergunta, aplica, e é por isso que os
remendos de arranque saem iguais.

A **2** não é entrada de divergência: é rota não portada, e o lugar dela é o
veredito do `MainForm.mostrar_jugadorClick` mais a linha que a
[CORR-WTE-086](/docs/tasks/concluidos/CORR-WTE-086.md) já abriu sobre o chamador do
`ficha_enlaza`. Escrever isso na seção "O que NÃO entra aqui" do registro fecha
a pergunta em vez de deixá-la voltando.

### Arquivo: `docs/tasks/concluidos/35-divergencias-deliberadas.md`

Depois de as entradas existirem, a seção *"Candidatas posteriores"* passa a
apontar para elas — vira índice, não pendência.

### Guarda

O `check_divergencias.py` cobre "exceção de ferramenta sem entrada". A direção
que faltou é "achado de divergência escrito em task e sem entrada", e ela é
mecanizável barato: recusar a frase **`sem entrada aqui`** (e variantes) em
`docs/tasks/*.md` quando o alvo citado não tiver seção no registro. Uma linha de
prosa que se declara pendente é exatamente o que uma guarda consegue ler.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/divergencias.md` | modificar — as duas entradas novas e a nota da terceira |
| `docs/tasks/concluidos/35-divergencias-deliberadas.md` | modificar |
| `wte/tools/check_divergencias.py` | modificar (opcional — a guarda da frase) |
| `wte/tools/test_check_divergencias.py` | modificar, se a guarda entrar |

## Verificação

- [x] `grep -c "ficha_warning\|help_team" wte/re/divergencias.md` maior que
      zero — **4**
- [x] As entradas novas têm os seis campos, como as seis existentes
- [x] `python3 wte/tools/check_divergencias.py --check` verde, com a contagem de
      seções atualizada — **11**, era 9
- [x] `make -C wte check` verde (850 testes, era 846)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

As três candidatas ganharam destino, e **não o mesmo destino** — que era o
ponto da CORR:

- **§10** do registro, `ficha_warning` não levantado: divergência deliberada de
  comportamento, decisão *não reproduzir*;
- **§11**, o `TStaticText` desabilitado: limitação de widgetset, ao lado da §2
  por família;
- o `ficha_enlaza` **não virou entrada** — é rota não portada, e foi para a
  seção *"O que NÃO entra aqui"*, com o dono nomeado (a spec do
  `mostrar_jugadorClick`) e o que fazer quando a condição for medida.

As duas entradas seguem o formato das seis existentes: tabela de três campos
mais **Razão**, **Evidência** e **Onde o teste sabe**. O registro foi de 9 para
**11 seções**.

O campo *onde o teste sabe* da §10 é o que valeu escrever: o
`golden-01-arranque` sabe **pelo silêncio** — o roteiro do lado oráculo dispensa
o aviso com um clique e o do lado port não tem esse passo, porque não há o que
dispensar. Os dois chegam à mesma imagem, e é essa igualdade que prova que o
modal não muda byte nenhum.

A seção *"Candidatas posteriores"* da WTE-TASK-35 virou **índice**, apontando
para os três destinos.

**Problemas encontrados:**

**A guarda entrou, e ela cobre a direção que faltava.** As tabelas do
`check_divergencias.py` conferem *exceção de ferramenta contra entrada*; achado
de divergência escrito numa task e sem entrada passava batido, com o gate verde
— foi exatamente o que aconteceu aqui.

**O alcance é estreito, e a palavra que o define é `ainda`.** O enunciado da
regra — *"uma exceção no golden sem entrada aqui é buraco"* — vive em cinco
arquivos e não é pendência nenhuma; ele nunca diz "ainda". Alargar para `sem
entrada aqui` cru marcaria os cinco, e guarda que erra é guarda que se desliga.
É a mesma escolha do `BLOQUEIO_VENCIDO` do `check_fase4.py`.

**E na primeira corrida ela marcou o `correcoes-progresso.md`**, que **cita** a
frase para descrever este defeito. Excluído por nome, junto dos `CORR-WTE-*.md`,
e não por heurística de contexto: a diferença entre citar e declarar não se lê
de uma regex — lê-se de onde a frase está. Plantando uma declaração na task 37,
o gate sai com **código 2**.

**Arquivos criados/modificados:**

- `wte/re/divergencias.md` — as §§10 e 11, e o `ficha_enlaza` na exclusão
- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — a seção virou índice
- `wte/tools/check_divergencias.py` — `PENDENCIA_DECLARADA` e a varredura
- `wte/tools/test_check_divergencias.py` — `TestPendenciaDeclarada`, 4 casos
