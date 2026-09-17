---
id: LOOKS-TASK-21
title: "Incógnita (q) — a tela `LOOKS SET` medida no jogo: texto de cada valor, ajuda, cursor e valores iniciais"
type: investigação
category: oráculo
phase: 8
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (q)"
status: pendente
---

# LOOKS-TASK-21: A tela `LOOKS SET`, medida

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1, §10.2 e §10.3 (q).
- **O pedido do usuário:** a janela do visualizador tem de **ser** a tela
  `LOOKS SET` que os dois save states mostram — doze linhas, cursor, valores
  trocáveis, caixa de ajuda, placa de posição. Esta task mede a tela; a
  [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) a constrói. **Texto de tela inventado a partir do rótulo é a armadilha
  17 do perfil**, e um gate que confere a janela contra uma tabela inventada
  confere a invenção.
- **O que já existe:** as doze linhas, domínios e rótulos no `looks.py`
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)); o `oracle.row_value` e o `confront.glyph_mask`, que leem a célula de
  valor sem o cursor que pisca (armadilha 28); e a tabela de texto da tela em
  Shift-JIS full-width na RAM (§1.10).
- **Os campos travam nas pontas** (armadilha 14) — medido nas linhas de cor e
  de cabelo. As outras seis (`DEFAUL`, `NAT`, `HEIG`, `BODY`, `AGE`, `FOOT`)
  não foram andadas.
- **Toda medição começa em `load_state`**, nos dois slots. Slot 1 é goleiro
  (placa `GK`), slot 2 jogador de linha (placa `CB`).

---

## Objetivo

Uma tabela medida, num módulo do núcleo sem Qt (`tools/looks/screen.py`), com
tudo o que a tela `LOOKS SET` escreve e como ela anda — de modo que a janela da
[`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) só desenhe o que o jogo desenha.

---

## Critério de conclusão

- [ ] **O texto de cada valor de cada uma das doze linhas**, lido por
      ferramenta — da tabela de texto em RAM, ou das células capturadas —,
      nunca transcrito à mão: `A TYPE`, `A1 TYPE`, `175 cm`, `RIGHT`, e o que
      mais houver, incluindo os valores sem rótulo de terceiro
      (`FACE` e `H.F.COL.` com um valor sem nome, `FOOT` com um).
- [ ] **O texto da caixa de ajuda** para cada linha sob o cursor.
- [ ] **O cursor:** vertical dá a volta ou trava; horizontal trava nas pontas
      — medido nas **doze** linhas, andando até as duas pontas.
- [ ] **Os valores iniciais dos dois save states**, lidos do registro do
      jogador em RAM e conferidos contra o que a tela mostra; a placa de
      posição e o nome da camisa de cada um.
- [ ] O domínio da linha `NAT` — quantos valores e em que ordem — medido;
      o que ele **aplica** é da [`LOOKS-TASK-23`](/docs/tasks/looks/23-default-por-nacionalidade.md).
- [ ] As regiões da tela (título, placa, painel, linhas, cursor, ajuda) em
      frações do quadro capturado, medidas pela ferramenta, para a janela
      reproduzir o arranjo.
- [ ] `screen.py` com `self_check()` e caso vermelho, na lista do
      `selftest.py`; o comando de medição no `oracle.py` pula com 77 sem as
      variáveis e os states, e entra na tabela de gates do perfil.
- [ ] §10.3 (q) do plano com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
