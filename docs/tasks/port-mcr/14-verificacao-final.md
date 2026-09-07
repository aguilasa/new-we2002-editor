---
id: MCR-TASK-14
title: "Verificação final contra a definição de pronto"
type: verificação
category: processo
phase: 4
depends_on: ["MCR-TASK-12", "MCR-TASK-13"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §9"
status: pendente
---

# MCR-TASK-14: Fechamento

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §0 (definição
  de pronto) e §9 (entregáveis).

---

## Critério de conclusão

- [ ] Os seis itens da definição de pronto conferidos **um a um**, com o comando
      que reproduz cada um colado no Log.
- [ ] O plano atualizado com o que a execução mediu — inclusive o que saiu
      diferente do previsto, que é o que vale registrar.
- [ ] **A §1.1 do plano remedida**, que a MCR-TASK-04 tocou e nenhuma outra
      task remede: ela cita a entrada 1 do diretório em bytes crus e **não diz
      que a cadeia tem dois blocos**. O comando é
      `python3 tools/mcr/card.py <cartão> --json`, e o que ele tem de dizer é
      `"blocos": [1, 2]`, `"tamanho_declarado": 16384` e um único bloco fora da
      cadeia (o 3, `0xA0`, 41 bytes não-zero). Se o plano continuar mudo sobre
      a cadeia, acrescente a frase.
- [ ] [`/docs/prompts/perfil-mcr.md`](/docs/prompts/perfil-mcr.md) com as
      decisões confirmadas, as armadilhas medidas, os gates e os arquivos
      quentes do ciclo.
- [ ] `CLAUDE.md` com a seção do projeto, no formato da de PES2: o que é, onde
      mora, como se roda, e as três armadilhas que custam tempo.
- [ ] `NOTICE.md` conferido: linhagem, SHA e a diferença de método.
- [ ] `python3 tools/check_tasks.py` e `ctest -R 'tasks|mcr'` verdes.
- [ ] Nada do upstream no repositório; `roms/` e o cartão do usuário intocados.

---

## Log de Execução

*(a preencher)*
