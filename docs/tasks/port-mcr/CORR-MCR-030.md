---
id: CORR-MCR-030
title: "Correção: a Fase 5 pede captura de tela no Log, e as dez sondas da MCR-TASK-17 só têm testemunho"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-030: a tabela de sondas não tem uma imagem sequer

## Problema identificado

A seção "Fase 5" de [`/docs/prompts/perfil-mcr.md`](/docs/prompts/perfil-mcr.md)
manda **captura no `:98` no Log, como na Fase 3**. O Log da
[MCR-TASK-17](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md) não tem
nenhuma, e o mapa também não.

Toda a coluna "O que apareceu" da tabela de sondas de
[`/docs/MCR-DESBLOQUEIOS.md`](/docs/MCR-DESBLOQUEIOS.md) — dez linhas, que são
o mapa inteiro — existe só como testemunho. Os artefatos versionados provam a
regra da soma e o conteúdo de cada sonda; **nenhum** prova o que a tela
mostrou.

Não é caso de refazer as nove corridas: uma imagem basta. A sonda
`mapa-completo` (`ff 05`) é a confirmação ponta a ponta, e um quadro dela com
as dez opções na lista ancora a tabela toda.

## Evidência

```
$ grep -n "png\|captura\|screenshot" docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md \
        docs/MCR-DESBLOQUEIOS.md
(vazio)
```

A regra do repositório manda `:98`, e a exceção com nome próprio é
`we2002-play`, que a task usou por ser sessão em que o usuário olha. A exceção
dispensa o display, não a evidência — e o quadro é alcançável dos dois jeitos:
`python3 tools/pes2/pad.py shot` sobre a instância viva, ou
`import -window root` no `:98`.

## Causa raiz

A tarefa correu como sessão de jogo na tela do usuário, e nesse caminho não há
gate que capture nada; ninguém pediu o quadro no meio das nove corridas.

## Correção

### Arquivo: `docs/MCR-DESBLOQUEIOS.md`

Uma captura da sonda `mapa-completo` — a lista com as dez opções — referenciada
na tabela de sondas, com o comando que a produziu. O arquivo de imagem entra
junto (é pequeno, e é a evidência do mapa; não é cartão de jogo, então a regra
de não versionar cartão não o alcança).

Se refazer a sonda for caro, vale a alternativa honesta: dizer na tabela que a
coluna é observação direta não capturada, e qual corrida a produziu.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/MCR-DESBLOQUEIOS.md` | modificar |
| a captura referenciada | **não criada** — ver o Log |

## Verificação

- [x] o mapa referencia uma captura, ou declara explicitamente que a coluna é
      testemunho
- [x] a sonda que a captura mostra é reconstruível pelo bloco "Reproduzir"
- [x] `roms/` e `mcr/` intocadas

## Log de Execução

**Executado em:** 2026-09-10

**Resumo do que foi feito:**

A captura foi tentada e **não** foi obtida; ficou a alternativa que esta CORR
autoriza por escrito. A tabela de sondas do mapa agora diz o que a coluna é —
**observação direta, não capturada** —, de qual corrida ela saiu (as nove de
`make we2002-play` de 2026-09-10, sessão na tela do usuário) e por que esse
caminho não deixa artefato: ele não tem gate que capture quadro. A distinção
que faltava está junto: o versionado prova a **regra da soma** e o conteúdo de
cada sonda, não o que a tela mostrou.

O Log da [MCR-TASK-17](/docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md) ganhou
a mesma declaração, porque era ali que a Fase 5 do perfil pedia a imagem — dizer
no mapa e calar no Log deixaria o Log em desacordo com o perfil sem que nada
apontasse isso.

E a porta ficou aberta, com o gesto escrito: montar a sonda pelo bloco
"Reproduzir", guardar o cartão vivo com `make we2002-card-snap`, pôr a sonda no
lugar, e capturar com `pad.py shot` sobre a instância viva ou com
`DISPLAY=:98 import -window root` se o boot for por `make we2002-98`.

**Problemas encontrados:**

**A via barata não existia.** Há dois save states de WE2002 de hoje, e o
DuckStation embute um quadro de 256×192 em cada um — `savestate.py shot` o
extrai sem subir emulador. Nenhum dos dois é a sonda: o `.bak` é a tela de
título e o `.sav` é o diálogo `MEM CARD SLOT`. Vale registrar o caminho, que
serve para a próxima: **quadro de save state é evidência de graça**, e um state
tirado na tela da sonda teria fechado esta CORR em dois comandos.

**A via cara ouve um limite de permissão, não de esforço.** Refazer a sonda
precisa instalá-la no cartão que o jogo lê, e ele é
`~/.local/share/duckstation/memcards/World Soccer Winning Eleven 2002
(Japan)_1.mcd` — **diretório do usuário**, e a escrita foi negada. Não há
desvio legítimo: o `fork.py launch` não aceita `--memcard`, e apontar o caminho
por `settings.ini` seria **configurar o DuckStation**, o que a decisão de
2026-09-02 proíbe aos lançadores deste repositório. O `make we2002-card-snap`
do cartão vivo tinha sido feito antes da tentativa e foi desfeito depois: o
cartão do usuário está no md5 em que estava, e `work/cards/` voltou às cinco
amostras da série mais as duas cópias.

Fica como pendência de uma linha para quem tiver a permissão: **uma imagem, a
sonda `ff 05`.**

**Medições:**

| medida | resultado |
|---|---|
| capturas no mapa e no Log antes | **0** |
| quadros de save state disponíveis | **2** (título, `MEM CARD SLOT`) — nenhum é a sonda |
| a captura da sonda | **não obtida** (escrita no cartão vivo negada) |
| cartão vivo `…(Japan)_1.mcd` | `3a8066c5…8ae8c33f` antes e depois — intocado |
| `work/cards/` | 7 arquivos, os mesmos de antes |
| `roms/`, `mcr/` | intocados |

**Arquivos criados/modificados:**

- `docs/MCR-DESBLOQUEIOS.md` — a coluna declarada como testemunho, a corrida
  que a produziu, e o gesto que produz a imagem
- `docs/tasks/port-mcr/17-mapa-dos-desbloqueios.md` — a mesma declaração no
  Log, onde a Fase 5 do perfil pedia a captura
