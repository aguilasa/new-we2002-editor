---
id: CORR-WTE-024
title: "Correção: as duas coisas que a WTE-TASK-11 delegou — o sufixo [Lazarus] e o --show — não chegaram a quem recebe"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-024: a WTE-TASK-11 delegou duas coisas e nenhum destinatário foi avisado

## Problema identificado

O Log da WTE-TASK-11 registra dois itens que ela cria e entrega a outra tarefa.
Nos dois casos a entrega ficou só no lado de quem manda.

**1. A divergência deliberada do título.** O Log, problema 2, e o comentário de
`MarcaOsTitulos` em `wte/src/wtemain.pas` dizem a mesma frase:

> **Divergência deliberada — registrar na WTE-TASK-35.**

A WTE-TASK-35 tem uma seção chamada "Candidatas já conhecidas antes de a task
rodar", com quatro entradas — tolerância de cor do render 2D, `TStaticText` no
GTK2, rótulos cortados, truncamento de campo. O sufixo ` [Lazarus]` não está
lá, e a string `Lazarus]` não ocorre em nenhum markdown de `docs/` fora do
próprio arquivo da WTE-TASK-11. A seção existe justamente para que a fase 6 não
tenha de redescobrir cada divergência lendo Log de fase 2.

Agrava que esta é a única divergência do projeto que **já está no código
rodando** — as outras quatro são hipóteses sobre o que pode divergir. E o
critério da própria WTE-TASK-35 diz o que acontece quando um item não chega:
"uma exceção no golden sem entrada aqui é buraco".

**2. O andaime `--show`.** O Log, problema 3, diz que não há navegação — quem
abre formulário são os handlers, e na fase 2 eles são stub — e que no lugar
ficou `--show <nome>` / `--show all`, "andaime explícito para a captura da
WTE-TASK-12".

A WTE-TASK-12 não sabe. O método dela diz "O app Lazarus no `:99`, mesmo
formulário, mesma captura", sem dizer como se abre um formulário num app que
não navega. `grep -rn -- "--show" docs/` só acha o arquivo da WTE-TASK-11. Quem
executar a 12 vai clicar num botão que só loga, concluir que a casca está
quebrada, e ter de achar o `--show` lendo o Log da task anterior ou o
`--help` do binário.

E ninguém é dono de tirar o andaime: o Log diz que ele "some quando a navegação
de verdade chegar", que é a WTE-TASK-25, e a 25 também não sabe.

Este é o mesmo defeito que a [CORR-WTE-021](/docs/tasks/concluidos/CORR-WTE-021.md) abriu
sobre o critério dos blobs: decisão registrada onde nasceu, e não onde é
consumida.

## Evidência

O sufixo, mandado para a 35:

```
$ grep -n "WTE-TASK-35" docs/tasks/11-app-com-a-casca-completa.md
144:     deliberada -- registrar na WTE-TASK-35.**

$ grep -rn "Lazarus\]" docs/ --include='*.md' | grep -v 11-app
(nenhuma saída)

$ grep -n "Candidatas já conhecidas" -A6 docs/tasks/35-divergencias-deliberadas.md
- **Tolerância de cor do render 2D** (WTE-TASK-29) [...]
- **`TStaticText` no GTK2** (§8.9) [...]
- **Rótulos cortados por fonte substituta** [...]
- **Comportamento de truncamento de campo** (WTE-TASK-36) [...]
```

O andaime, feito para a 12:

```
$ grep -rn -- "--show" docs/ | grep -v 11-app
(nenhuma saída)
```

E ele funciona — esta revisão o exercitou no `:99`: `--show all` mapeia 18
janelas visíveis, todas com o sufixo, e depois do `kill` sobra zero. É
ferramenta boa que só o autor sabe que existe.

## Causa raiz

O Log de execução registrou as duas entregas no lado de quem manda, e nenhuma
delas foi escrita no arquivo de quem recebe.

## Correção

### Arquivo: `docs/tasks/concluidos/35-divergencias-deliberadas.md`

Acrescentar o sufixo à lista de candidatas, marcado como o único item já
implementado, com os campos que a própria task exige:

```markdown
- **Sufixo ` [Lazarus]` no `Caption` dos 18** (WTE-TASK-11) — **já está no
  código**, diferente das outras quatro, que são hipóteses. Natureza: escolha.
  Razão: o `Caption` vem do DFM e o do `MainForm` é literalmente
  `' W11 Team Editor PT by chagas_michel!'`; a partir da WTE-TASK-22 os dois
  rodam no mesmo `:99` e o harness acha janela por título e por tamanho —
  título igual faria ele dirigir o lado errado (armadilha 6 do `progresso.md`).
  Posto em tempo de execução por `MarcaOsTitulos`, em `wte/src/wtemain.pas`,
  não no `.lfm`, que é gerado. Onde o teste sabe: no `:99` não há window
  manager, nenhuma barra de título é desenhada, e a captura da WTE-TASK-12 não
  enxerga o sufixo — num desktop de verdade enxerga, e deve.
```

### Arquivo: `docs/tasks/concluidos/12-comparacao-visual.md`

No "Método", trocar o passo 2 por um que diga como se abre formulário num app
que ainda não navega:

```markdown
2. O app Lazarus no `:99`. **Ele não navega** — na fase 2 os handlers são stub
   (WTE-TASK-11, problema 3). O andaime é `--show`:
   `./wte/build/wte --show all` abre os 18 de uma vez, `--show <nome>` abre um
   só, `--list` dá os nomes. Mesma captura.
```

E acrescentar ao critério de conclusão da 12 a nota de que o sufixo
` [Lazarus]` no `Caption` é divergência deliberada e **não** conta como achado.

### Arquivo: `docs/tasks/concluidos/25-handlers-de-carga.md`

Uma linha dizendo que, quando a navegação de verdade entrar, o `--show` de
`wtemain.pas` sai junto — senão ele fica para sempre.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/35-divergencias-deliberadas.md` | modificar |
| `docs/tasks/concluidos/12-comparacao-visual.md` | modificar |
| `docs/tasks/concluidos/25-handlers-de-carga.md` | modificar |

## Verificação

- [ ] `grep -rn "Lazarus\]" docs/ --include='*.md'` acha a 35 e a 12, não só a 11
- [ ] `grep -rn -- "--show" docs/` acha a 12 e a 25
- [ ] a entrada da 35 tem os seis campos que a tabela "Cada entrada precisa de"
      exige
- [ ] a conferência de forma e de destino de link de `.claude/rules/links.md`
      sai vazia nos três arquivos
- [ ] `make -C wte check` verde
- [ ] nada de código tocado: `git diff --name-only` só lista markdown de
      `docs/tasks/`
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-09

**Resumo do que foi feito:** As duas entregas da WTE-TASK-11 chegaram a quem
recebe. O sufixo ` [Lazarus]` entrou na lista de candidatas da WTE-TASK-35 com
os seis campos que a tabela dela exige, marcado como o único item que já está
no código. O `--show` entrou no passo 2 do método da WTE-TASK-12, com `--show
all` / `--show <nome>` / `--list`, e a 12 ganhou o critério de que o sufixo não
conta como achado. A WTE-TASK-25 ganhou dono da remoção do andaime, na tabela
de arquivos e no critério de conclusão.

**Problemas encontrados:** Nenhum. O `--list` ficou de fora da remoção
proposta para a 25 — ele não simula navegação e não custa nada; só o `--show`
sai.

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/35-divergencias-deliberadas.md` (candidatas)
- `docs/tasks/concluidos/12-comparacao-visual.md` (método passo 2 + critério)
- `docs/tasks/concluidos/25-handlers-de-carga.md` (arquivos + critério)
