---
id: CORR-MCR-022
title: "Correção: a Fase 5 nasceu sem entrada em \"Verificações específicas por fase\", que é o único lugar onde o `/revisar` procura o que perguntar de uma fase"
type: correção
category: processo
status: pendente
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

- [ ] `sed -n '/## Verificações específicas por fase/,$p' docs/prompts/perfil-mcr.md | grep -c "Fase 5"` devolve **1**
- [ ] a entrada nomeia os três itens medidos pela MCR-TASK-15, cada um com o
      que o exercita
- [ ] se a conferência for escrita: uma task com `phase: 9` e sem entrada no
      perfil faz `python3 tools/check_tasks.py` sair **1**, nomeando a fase
- [ ] `python3 tools/check_tasks.py` verde na árvore como está (101 tasks)
- [ ] `ctest -R tasks` verde
- [ ] `WE2002_MCR_CARD=… ctest -R mcr` = 3 de 3, e `controls.py` todos vermelhos
- [ ] `roms/` intocada; a fixture com o mesmo `sha256sum`

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
