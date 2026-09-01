---
id: CORR-PES2-004
title: "Correção: os prompts ficaram agnósticos de plano e de prefixo, e continuam cheios de corpo WTE-específico"
type: correção
category: processo
status: pendente
depends_on: [CORR-PES2-003]
---

# CORR-PES2-004: agnóstico no cabeçalho, WTE-específico no corpo

## Problema identificado

Três correções seguidas tiraram dos prompts o que a regra proíbe **por nome**:
o plano ([`fonte_de_verdade` na task](../../.claude/rules/tasks.md)), o prefixo
de correção ([CORR-PES2-002](/docs/tasks/CORR-PES2-002.md)) e o prefixo de task
([CORR-PES2-003](/docs/tasks/CORR-PES2-003.md)). O que sobrou é maior que os
três, e a varredura da 003 é que o mostrou: **os prompts continuam carregando
um corpo inteiro de conteúdo operacional do ciclo `wte/` Lazarus**, e para uma
task de PES2 ele não é só inaplicável — é instrução ativa apontando para
ferramenta que o projeto não tem.

Não é prefixo mal escrito, e por isso a 003 não podia consertá-lo: trocar
`WTE-TASK-01 a 09` por `<PREFIXO>-TASK-01 a 09` seria **pior** que deixar como
está, porque passaria a afirmar que um checklist sobre extração de `.dfm` e
geração de `.lfm` vale para as fases de PES2. O texto está certo sobre o ciclo
que descreve; o defeito é ele estar num arquivo que se apresenta como agnóstico.

## Evidência

O caso mais claro é a **Etapa 3 do `02-revisar.md`**, 73 linhas indexadas por
faixa de task de um ciclo fechado:

```
$ grep -n 'Etapa 3\|^\*\*Fase' docs/prompts/02-revisar.md
110:### Etapa 3 — Verificações específicas por fase
112:**Fase 0-1 (WTE-TASK-01 a 09) — infra e extração estática:**
126:**Fase 2 (WTE-TASK-10 a 14) — casca:**
140:**Fase 3 (WTE-TASK-15 a 21) — dados:**
155:**Fase 4-5 (WTE-TASK-22 a 33) — comportamento e features:**
175:**Fase 6-7 (WTE-TASK-34 a 40):**
```

O conteúdo é do `wte/` na letra — "Os 18 DFM decodificaram inteiros?", "Os 96
stubs estão na unidade certa?", "Algum asset do Obocaman foi versionado?". PES2
não tem DFM, nem stub, nem Obocaman. As seis fases do
[PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md) não têm entrada nenhuma aqui.

Não é só esse prompt. Caminhos `wte/` cravados, por arquivo:

```
$ grep -o 'wte/[a-z_/.]*' docs/prompts/*.md | cut -d: -f1 | sort | uniq -c
     10 docs/prompts/01-executar.md
     10 docs/prompts/02-revisar.md
     21 docs/prompts/03-corrigir.md
      8 docs/prompts/04-corrigir-tudo.md
     15 docs/prompts/05-executar-lote.md
```

E as 28 citações de task `WTE-` que a 003 preservou **com razão** — são
evidência do que aconteceu — carregam junto instrução que não é história:

- `01-executar.md:249,251` — "`lazbuild wte/wte.lpi` **a partir da**
  WTE-TASK-02", "`golden_check.sh` **a partir da** WTE-TASK-22". São os gates
  do prompt, com disponibilidade datada por task que não existe no ciclo vivo
- `01-executar.md:94,99` — o bloco "Antecipação" nomeia WTE-TASK-32 e -33 como
  as duas exceções autorizadas. O padrão abstrato ao final do bloco é o que
  vale; as duas exceções são precedente de outro ciclo
- `05-executar-lote.md:156` — a matriz de conflito tem linha para `wte/Makefile`
  com "as 03, 04, 05 e 06 querem a mesma mão no mesmo arquivo"
- `03-corrigir.md` — a tabela "O que é gerado" lista cinco geradores de
  `wte/tools/`, e a de "leitura pura", o `we-team-editor.exe`. As duas
  exclusões obrigatórias citam `docs/PLAN-WTE-LAZARUS.md` §2, §4.4, §4.5, §8.10

O `04-corrigir-tudo.md` chega a abrir dizendo *"Você vai trabalhar no projeto
**WE2002 Team Editor → Lazarus**"* — a primeira linha do arquivo que executa as
correções de PES2.

## Causa raiz

Os prompts nasceram para um projeto só e foram generalizados **por sintoma**:
cada correção tirou o acoplamento que a invocação daquele dia esbarrou. Nenhuma
das três olhou o arquivo inteiro perguntando *"o que aqui só vale para o
`wte/`?"*, porque nenhuma precisou.

## Correção

Não é substituição, é separação — e por isso ela não cabia dentro da 003.

### O gesto

Cada prompt fica com o **rito**, que é o que vale para qualquer ciclo: ler o
progresso, achar a próxima pendente, conferir `depends_on`, medir contra o
`fonte_de_verdade` da task, varrer discrepância, `[x]` só depois do commit.

O que é **do ciclo** sai para um arquivo por ciclo — um `perfil` que o prompt
carrega e que o `progresso.md` nomeia, do mesmo jeito que a task nomeia o plano
dela. Ali moram: as verificações por fase, os gates com sua disponibilidade, a
tabela de geradores, a de leitura pura, a matriz de conflito de arquivo e os
precedentes de antecipação.

**A forma exata é decisão do usuário**, e há pelo menos três — arquivo de
perfil carregado pelo prompt, seção do próprio `progresso.md`, ou nada e o
prompt passa a não ter verificação por fase. A escolha muda o trabalho inteiro,
então esta CORR **não a toma sozinha**.

### O que não fazer

- **Não trocar `WTE-TASK-NN` por `<PREFIXO>-TASK-NN` nas verificações por
  fase.** É o erro que esta CORR existe para nomear: passaria a afirmar que um
  checklist de `.dfm` vale para PES2
- **Não apagar as 28 citações** de task real do ciclo fechado. A
  [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md) já mediu o custo disso no pool
  de correções: a varredura ingênua apaga a armadilha junto com o prefixo
- **Não tocar `docs/tasks/concluidos/`**

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/prompts/01-executar.md` | modificar |
| `docs/prompts/02-revisar.md` | modificar (a Etapa 3 é o grosso) |
| `docs/prompts/03-corrigir.md` | modificar |
| `docs/prompts/04-corrigir-tudo.md` | modificar |
| `docs/prompts/05-executar-lote.md` | modificar |
| `.claude/commands/*.md` | modificar, se o rito mudar |
| o perfil por ciclo | criar — **nome e forma a decidir com o usuário** |

## Verificação

- [ ] A decisão de forma foi tomada **com o usuário**, e está escrita
- [ ] Nenhum prompt cita `wte/`, `PLAN-WTE-LAZARUS.md`, `.dfm`, `.lfm`,
      `lazbuild` ou Obocaman como instrução; o que sobrar é citação datada de
      ciclo fechado, e o Log diz quantas
- [ ] O `04-corrigir-tudo.md` não abre mais dizendo que o projeto é o
      Lazarus
- [ ] Existe verificação por fase para as seis fases do
      [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md), ou está escrito que não haverá
- [ ] `grep -rn 'WTE-TASK' docs/tasks/concluidos/ | wc -l` inalterado em 1411
- [ ] `python3 tools/check_tasks.py` verde
- [ ] Conferência de link de `.claude/rules/links.md` sem quebrado novo

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
