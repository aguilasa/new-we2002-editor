# Progresso — <título do projeto>

Rastreamento das tasks de [`../<PLANO>.md`](/docs/<PLANO>.md), que é a fonte de
verdade do projeto. Este arquivo registra **andamento**; o plano registra
**objetivo e critério**. Divergência entre os dois se resolve a favor do plano.

<!-- Se o projeto for separado de outro do mesmo repositório, diga aqui o que
     compartilha e o que não compartilha (build, código, conhecimento de
     formato) -- é o que impede alguém de assumir dependência que não existe. -->

<!-- Se este arquivo hospedar tasks de outro projeto por conveniência de
     leitura, abra a citação de aviso aqui e repita no anexo do fim:
> **As `<OUTRO>-TASK-*` no fim deste arquivo são do outro projeto.** A fonte de
> verdade delas é o `<OUTRO-PLANO>.md`, não o `<PLANO>.md`. **Nenhuma
> `<ESTE>-TASK` depende delas, e vice-versa.**
-->

## Resumo

| ID | Tarefa | Fase | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | ---- | ------------ | ------ | ------------ | ----------- |
| [<PREFIXO>-TASK-01](/docs/tasks/01-<nome-do-arquivo>.md) | <o que a task entrega> | 0 | — | ⬜ Pendente | — | — |
| [<PREFIXO>-TASK-02](/docs/tasks/02-<nome-do-arquivo>.md) | <o que a task entrega> | 0 | 01 | ⬜ Pendente | — | — |

**Legenda:** ⬜ Pendente · 🔄 Em andamento · ✅ Concluído · ❌ Bloqueado · ⏭️ Pulado

**As duas colunas de data são datas de commit**, não datas de intenção.

- **"Concluída em"** — o commit que fechou a tarefa. Tarefa pendente leva `—`.
- **"Revisado em"** — o commit da revisão. Tarefa concluída e ainda não revisada
  leva `⬜ pendente`; tarefa que nem começou leva `—`, porque não há o que
  revisar.

**Revisão sem discrepância também preenche a coluna.** É resultado legítimo, e
sem a data não há como distinguir "revisada, nada achado" de "nunca revisada".

<!-- Abaixo do quadro entram as notas de exceção: task que mudou de status por
     mudança de natureza, task executada fora da ordem do `depends_on`, achado
     que sai de uma fase e vale para outra. Cada uma com a razão medida. -->

---

## Escopo e fases

<uma frase dizendo o que o projeto entrega, e contra o que ele se verifica. Ver
[`../<PLANO>.md`](/docs/<PLANO>.md) para o objetivo completo e o modelo de
verificação.>

| Fase | Tasks | O que entrega |
| --- | --- | --- |
| 0 — <nome> | 01 a 0N | <entrega> |
| 1 — <nome> | 0N a 0M | <entrega> |

**O que não pode ser pulado:** <as ordens obrigatórias, com a razão de cada
uma — quem depende de quem para não virar opinião.>

---

## Grafo de dependências

```text
Fase 0
  01 ──► 02
          │
Fase 1    ├──► 03 ──┐
          └──► 04 ──┴──► 05 (fechamento)
```

**Sequência mínima de execução:**

```text
1.  01, 02 (infra)
2.  03, 04 em paralelo — nenhuma depende da outra
3.  05 (fechamento da fase 1)
```

<!-- Se alguma task for antecipável por dependência, diga qual, por que, e o que
     ela valida ao ser antecipada. -->

---

## Checklist geral

### Fase 0 — <nome>

- [ ] <critério verificável, não intenção>
- [ ] <critério verificável, não intenção>

### Fase 1 — <nome>

- [ ] <critério verificável, não intenção>

---

## Decisões de design

Vindas de [`../<PLANO>.md`](/docs/<PLANO>.md) e de erro já pago.

| Decisão | Escolha | Razão |
| --- | --- | --- |
| <eixo> | <o que foi escolhido> | <por que, em uma frase> |

---

## Armadilhas medidas que valem para todas as fases

Cada uma custou tempo real.

1. **<a armadilha em uma frase de negrito>.** <o sintoma, a causa e o gesto que
   evita — o que a próxima pessoa precisa saber antes de tropeçar de novo.>

---

## Pendências externas

- **<pendência>.** <de quem depende, e o que fica bloqueado até ela sair.>

---

## Estrutura de pastas (estado final esperado)

```text
<raiz>/
├── docs/
│   ├── <PLANO>.md                    ← fonte de verdade
│   └── tasks/
│       ├── 01-...md ... NN-...md
│       └── progresso.md              ← este arquivo
└── <arvore do projeto>/
```

---

## Estado medido, reconciliado pela <PREFIXO>-TASK-NN

<quando a primeira medição foi feita, com que ferramenta, e qual task a remediu
com ferramenta versionada.>

| Eixo | Estado |
| --- | --- |
| <o que foi medido> | <o número, e se foi *corrigido* depois> |

---

## Notas de execução

*(preenchido conforme as tasks forem executadas — mesmo formato do "Log de
Execução" de cada arquivo de task, resumido aqui quando houver algo relevante
para o conjunto)*

**<PREFIXO>-TASK-NN — <o achado em uma frase>.** <o que foi medido, com o
número; o que mudou por causa disso; e o que ficou aberto.>

<!-- ---------------------------------------------------------------------- --
     Anexo opcional: tasks de outro projeto hospedadas neste arquivo.
     Apague o bloco inteiro se não houver.
     ---------------------------------------------------------------------- -->

---

# Anexo — `<outro projeto>`: <o que estas tasks rastreiam>

> **Outro projeto.** Estas tasks não entram nas fases acima. Fonte de verdade:
> [/docs/<OUTRO-PLANO>.md](/docs/<OUTRO-PLANO>.md) §N.

## Por que existem

<o que os testes automáticos do outro projeto já cobrem, o que eles não
alcançam, e por que estas tasks dão dono a isso.>

## Resumo

| ID | Tarefa | §  | Itens | Dependências | Status | Concluída em | Revisado em |
| -- | ------ | -- | ----: | ------------ | ------ | ------------ | ----------- |
| [<OUTRO>-TASK-01](/docs/tasks/<OUTRO>-TASK-01.md) | <o que a task confere> | N.1 | 0 | — | ⬜ Pendente | — | — |

**<N> itens, <M> tasks.** <se houver bloqueada, o bloqueio de cada uma, nomeado.>

## Ordem sugerida

```
01 ─┬─ 02
    └─ 03
```

<por que a primeira é a primeira, e qual é a mais barata se ela travar.>

## Método comum

<o gesto que toda task da série repete, e o critério de aprovação — em uma
frase, com a régua nomeada.>

<qual imagem/fixture é a preferida, e quando usar outra.>

Divergência fora do esperado vira **CORR**, com a faixa e o offset simbólico.
