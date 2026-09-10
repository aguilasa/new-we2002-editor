---
id: CORR-MCR-030
title: "Correção: a Fase 5 pede captura de tela no Log, e as dez sondas da MCR-TASK-17 só têm testemunho"
type: correção
category: processo
status: pendente
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
| a captura referenciada | criar |

## Verificação

- [ ] o mapa referencia uma captura, ou declara explicitamente que a coluna é
      testemunho
- [ ] a sonda que a captura mostra é reconstruível pelo bloco "Reproduzir"
- [ ] `roms/` e `mcr/` intocadas

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
