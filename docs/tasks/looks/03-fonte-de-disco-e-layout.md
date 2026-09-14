---
id: LOOKS-TASK-03
title: "`iso_source.py` e `layout.py` — a fachada de disco e o monopólio de endereço"
type: implementação
category: núcleo
phase: 1
depends_on: ["LOOKS-TASK-02"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.1"
status: pendente
---

# LOOKS-TASK-03: A fachada de disco e o monopólio de endereço

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.1, §3.2
  e §3.3 (regra 1).
- **Nada de leitor de ISO é escrito aqui.** `tools/pes2/iso.py` já lê a imagem
  japonesa nesta máquina, inclusive no Windows; esta task o **embrulha**, não o
  duplica.
- A regra 1 do ciclo — só `layout.py` carrega endereço — é o que permite mover
  um offset depois sem caçá-lo pela árvore.
- **`tools/looks/layout.py` já existe, e esta task o estende — não o cria.** A
  [`LOOKS-TASK-02`](/docs/tasks/looks/02-ambiente-e-os-dois-discos.md) o abriu
  em 2026-09-14 para plantar a guarda dos dois discos, porque a regra da §4.5
  do plano precisava existir como código antes de qualquer leitura de textura.
  O que está lá hoje: os nomes das duas variáveis de ambiente, os quatro
  caminhos de dentro do ISO como constante, o sha256 de cada um como lido do
  disco japonês, a exceção `WrongDisc`, `require()` e um `self_check()` com
  três casos vermelhos. **Nenhum LBA, nenhum `BASE`, nenhum 157.164** — esses
  são desta task.
- **O `_check_discs()` do `layout.py` é dívida desta task.** Ele importa
  `tools/pes2/iso.py` direto, com um comentário dizendo que é temporário,
  porque a fachada de disco é justamente o `iso_source.py` que esta task
  escreve. Ao criar o `iso_source.py`, **mova a leitura para trás dele** e
  deixe o `layout.py` sem I/O nenhum, que é o contrato dele (ele não sabe
  formato, e o `self_check()` roda sem imagem).

---

## Objetivo

`tools/looks/iso_source.py` entrega bytes de arquivo do disco;
`tools/looks/layout.py` é o **único** módulo que sabe LBA, `BASE` e offset.

---

## Critério de conclusão

- [ ] `iso_source.py` abre a imagem por `tools/pes2/iso.py` e entrega
      `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` e `/BIN/DAT2D.BIN`.
- [ ] `layout.py` carrega, e é o único a carregar: os LBAs (5000, 8100, 5300),
      os dois `BASE` (`0x8011C000`, `0x8016E800`), o início de geometria do
      `MODEL.BIN` (1816) e o offset dos registros de jogador (157.164).
      **Acrescentados ao que a LOOKS-TASK-02 já pôs lá**, sem apagar a guarda
      dos discos nem os três casos vermelhos dela.
- [ ] O `layout.py` fica **sem I/O**: o `_check_discs()` que hoje importa
      `tools/pes2/iso.py` direto passa a ler pelo `iso_source.py`.
- [ ] Os dois `BASE` são **derivados do cabeçalho e conferidos** contra a
      constante, não apenas cravados — é o método que a §1.2 usa.
- [ ] Varredura mecânica: nenhum endereço fora de `layout.py`.
- [ ] `self_check()` em cada um, com caso vermelho.

---

## Log de Execução

*(preencher ao executar)*
