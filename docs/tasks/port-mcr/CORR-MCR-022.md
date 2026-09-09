---
id: CORR-MCR-022
title: "Correção: a Fase 5 nasceu sem entrada em \"Verificações específicas por fase\", que é o único lugar onde o `/revisar` procura o que perguntar de uma fase"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-MCR-022: fase nova, e o perfil não diz o que se pergunta dela

## Problema identificado

A MCR-TASK-15 abriu a **Fase 5** — o plano ganhou a linha na §7, com o motivo
de ela não ser reabertura, e o `progresso.md` ganhou a fase no quadro e no
grafo. O `perfil-mcr.md`, porém, tem entrada só até a Fase 4:

```
$ grep -n "^- \*\*Fase" docs/prompts/perfil-mcr.md
200:- **Fase 0** — …
206:- **Fase 1** — …
224:- **Fase 2** — …
231:- **Fase 3** — …
244:- **Fase 4** — …
```

E o `02-revisar.md` manda, em letras, olhar exatamente ali:

> Abra a seção "verificações específicas por fase" do perfil, ache a fase da
> task em mãos (a coluna `Fase` do `progresso.md`), e responda item a item. Se
> o perfil não tiver entrada para essa fase, **diga isso na saída** em vez de
> improvisar — **fase sem verificação escrita é achado, e vira CORR**.

Quem revisar a próxima task de Fase 5 abre a seção, não acha a fase, e
improvisa — que é o que esta revisão teve de fazer.

**O que salva a corrida de hoje, e é a razão de isto ser Baixa:** a substância
existe, só não está onde o rito manda procurar. A linha do `mcr_ui` na tabela
de gates **foi** atualizada por esta task e descreve o que a Fase 5 exige:

> Desde a MCR-TASK-15 ele também sobe a janela **sem cartão** — esse passo roda
> com ou sem fixture — e exige que ela seja a porta de entrada: página vazia com
> botão, botão e item de menu disparando a **mesma** ação, diálogo cancelado sem
> efeito, e edição não gravada que só se perde depois de uma pergunta

Faltou a segunda escrita — a entrada da fase —, e é ela que o revisor lê.

## Evidência

```
$ grep -n "phase:" docs/tasks/port-mcr/15-abrir-cartao-pela-tela.md
7:phase: 5

$ grep -n "^| 5 " docs/PLAN-MCR-PY.md
668:| 5 | pedidos posteriores ao fechamento — hoje só abrir cartão pela tela |

$ sed -n '/## Verificações específicas por fase/,$p' docs/prompts/perfil-mcr.md | grep -c "Fase 5"
0
```

A task lista `docs/prompts/perfil-mcr.md` entre os arquivos que modificou — e
modificou mesmo, a linha do `mcr_ui`. A seção das fases ficou.

## Causa raiz

A fase nova foi registrada nos dois lugares que descrevem **o que ela é** (o
plano e o progresso) e num que descreve **o que o gate faz** (a tabela de
gates), e não no que descreve **o que se pergunta dela numa revisão**.

## Correção

### Arquivo: `docs/prompts/perfil-mcr.md`

Acrescentar a entrada, depois da Fase 4. O conteúdo já foi medido — é o que a
MCR-TASK-15 exercitou e o que a linha do `mcr_ui` promete:

```markdown
- **Fase 5** — escopo pedido **depois** do fechamento, e por isso a task é a
  própria fonte de verdade: o critério dela é o que se confere, não uma seção
  do plano. Captura no `:98` no Log, como na Fase 3. Três perguntas que a
  MCR-TASK-15 fixou e valem para qualquer tela que entre aqui:
  **um caminho, dois gatilhos** — botão e item de menu disparam a **mesma**
  `QAction`, e o controle plantado prova que trocar a ligação fica vermelho;
  **modal nenhum sobe num gate** — a caixa mora atrás de um método que o probe
  substitui, e alcançá-la numa corrida `headless` **levanta**, para que o dia
  em que o seam sumir seja vermelho e não travamento (lição 2 da MCR-TASK-12);
  e **o que a fase fecha não pode desfazer o que a definição de pronto já
  media** — os passos das fases 3 e 4 continuam no gate, e a corrida os mostra.
```

E, na mesma passagem, dizer que a Fase 5 **não** reabre a definição de pronto —
o plano já diz, e o perfil é quem o revisor lê primeiro.

### O que impede a próxima

Fase nova sem entrada no perfil é achado que só aparece na revisão seguinte. O
barato é o `tools/check_tasks.py` — que já lê o `phase:` de cada task e o
`perfil:` de cada `progresso.md` — recusar uma fase que não tenha entrada na
seção do perfil. É a mesma forma dos outros guards deste ciclo: uma varredura
que recusa, em vez de uma convenção que alguém lembra.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/perfil-mcr.md` | modificar |
| `tools/check_tasks.py` | modificar (a conferência, opcional mas é o que fecha) |

## Verificação

- [x] `sed -n '/## Verificações específicas por fase/,$p' docs/prompts/perfil-mcr.md | grep -c "Fase 5"` devolve **1**
- [x] a entrada nomeia os três itens medidos pela MCR-TASK-15, cada um com o
      que o exercita
- [x] se a conferência for escrita: uma task com `phase: 9` e sem entrada no
      perfil faz `python3 tools/check_tasks.py` sair **1**, nomeando a fase
- [x] `python3 tools/check_tasks.py` verde na árvore como está (101 tasks)
- [x] `ctest -R tasks` verde
- [x] `WE2002_MCR_CARD=… ctest -R mcr` = 3 de 3, e `controls.py` todos vermelhos
- [x] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução

**Executado em:** 2026-09-09

**Resumo do que foi feito:**

O sintoma reproduziu: a seção "Verificações específicas por fase" ia da Fase 0 à
4, a MCR-TASK-15 declara `phase: 5`, e a §7 do plano já tem a linha da fase.
`grep -c "Fase 5"` na seção dava **0**.

A entrada foi escrita com o que a MCR-TASK-15 exercitou — os três itens (um
caminho com dois gatilhos, modal nenhum num gate, e os passos das fases 3 e 4
continuando no gate) — mais as duas coisas que a CORR pede em prosa: que a Fase
5 **não reabre a definição de pronto**, e que, como o pedido nasce fora do
plano, **a própria task é a fonte de verdade**.

E foi escrita a conferência, que é o que fecha. O `check_tasks.py` já lia o
`phase:` de cada task; agora resolve o `perfil:` do `progresso.md` da pasta e
**recusa** fase sem entrada na seção. Mesma forma dos outros guards do ciclo:
uma varredura que recusa, no lugar de uma convenção que alguém lembra.

**Problemas encontrados:**

**1. A primeira forma da conferência daria falso vermelho nas oito fases do
ciclo de PES2.** Os dois perfis escrevem a entrada de jeitos diferentes: o
`perfil-mcr.md` usa `- **Fase 3** — …` e o `perfil-pes2.md` usa
`**Fase 0 (tasks 01, 32, 33, 34) — …:**`, sem o traço. Medi antes de escrever:
com o regex ancorado no traço, PES2 dava `entradas=[]` contra sete fases de
task. O regex aceita as duas formas, e aí PES2 fecha 0–7 e só a Fase 5 do
`port-mcr` falta — o raio de alcance da conferência é exatamente o defeito.

**2. Três casos ficam de fora, e cada um por um motivo.** `progresso.md` sem
campo `perfil:` (o do arquivo em `concluidos/` é assim, e é história), perfil
que não existe no disco, e perfil sem a seção. Recusar esses alargaria a regra
além do que esta CORR mediu — a conferência é sobre **fase que falta numa seção
que existe**.

**3. A varredura puxou dois documentos que a CORR não listava.** O
`.claude/rules/tasks.md` diz "Ele confere as quatro coisas da lista acima" e o
`CLAUDE.md` diz "confere as quatro convenções" — as duas frases passaram a ser
falsas no instante em que a quinta entrou. Ganharam a convenção nova, com o
motivo e com os três casos que ficam de fora.

**4. A transcrição da Evidência tem duas linhas fora do lugar.** Ela dá
`phase: 5` na linha 7 (é a **6**) e a linha da Fase 5 do plano na 668 (é a
**671**). O sintoma não depende disso — a seção realmente não tinha a fase — e
a Evidência do revisor fica como está.

**Medições:**

| gate | número |
|---|---|
| `grep -c "Fase 5"` na seção, antes | **0** |
| depois | **1**, com os três itens medidos pela MCR-TASK-15 |
| caso vermelho A — `phase: 9` numa task | `check_tasks.py` sai **1**, nomeando a task, a fase e o perfil |
| caso vermelho B — tirar a entrada da Fase 5 do perfil | `check_tasks.py` sai **1**, nomeando `phase: 5` |
| raio de alcance, medido antes de escrever | `port-mcr` 0–4 contra fases 0–5; PES2 0–7 contra 0–7; `concluidos/` sem `perfil:`, fora |
| `check_tasks.py` na árvore como está | **101 task(s), ok** |
| `ctest -R tasks` | **1/1 Passed** |
| `ctest -R 'tasks\|mcr'` | **4 de 4** |
| `make test` | **10/10** |
| `controls.py` | **20 of 20 red (19 substitutions, 1 new file)** |
| `selftest.py` | `0 failure(s)` sobre 12 módulos |
| conferência de existência de link | **vazia** |
| fixture / `roms/` | `sha256 e53f4895…c47546`, intocada; `roms/` sem alteração |

**Arquivos criados/modificados:**

- `docs/prompts/perfil-mcr.md` — a entrada da Fase 5
- `tools/check_tasks.py` — a quinta conferência, `entradas_de_fase()`, e o
  docstring renumerado
- `.claude/rules/tasks.md`, `CLAUDE.md` — a contagem do que o `check_tasks.py`
  confere (varredura de discrepância)
