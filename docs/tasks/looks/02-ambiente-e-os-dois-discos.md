---
id: LOOKS-TASK-02
title: "Ambiente — o venv, os dois discos e seus papéis, e a armadilha do MSYS"
type: infraestrutura
category: ambiente
phase: 0
depends_on: ["LOOKS-TASK-01"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4"
status: pendente
---

# LOOKS-TASK-02: O ambiente, e a divisão entre os dois discos

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4, e a
  §1.3, que é quem mede a divisão entre os discos.
- **Esta é a task que evita o erro silencioso do ciclo.** O disco inglês tem os
  menus legíveis e geometria byte a byte idêntica; o `DAT2D.BIN` dele
  **difere**. Ler paleta no disco errado entrega gráfico diferente sem erro
  nenhum.

---

## Objetivo

Deixar a máquina pronta e a regra dos dois discos gravada onde a ferramenta a
lê, não só onde a prosa a conta.

---

## Critério de conclusão

- [ ] `work/venv-looks/` criado com PySide6, **nunca** por gerenciador de
      pacote do sistema — a armadilha do Python duplo está na §4.1.
- [ ] `WE2002_LOOKS_IMAGE` nomeada e documentada, apontando para a **japonesa**
      (`roms/japanese-shift-jis.bin`).
- [ ] `WE2002_LOOKS_DRIVE_IMAGE` (ou nome equivalente) nomeada para o `.cue`
      **inglês**, o de dirigir o emulador.
- [ ] O `iso_source.py` (ou `layout.py`) **recusa** ler textura/paleta de uma
      imagem cujo `DAT2D.BIN` não bata com o digest da japonesa. A regra não
      pode existir só em prosa — é caso de controle negativo.
- [ ] Fica registrado que `roms/japanese-shift-jis.bin` e
      `we-2002-original-japao.bin` são **o mesmo dump**
      (`sha256 e853eb14f5bddd50…`), e o comando que reconfere isso.
- [ ] `MSYS_NO_PATHCONV=1` documentado em toda receita que passe caminho de
      dentro do ISO (§4.2).

---

## Log de Execução

*(preencher ao executar)*
