---
id: PES2-TASK-01
title: "Ferramental das fases 3 e 4 — numpy e desmontador MIPS"
type: decisão
category: infra
phase: 0
depends_on: []
fonte_de_verdade: "/docs/PES2-AJUSTES.md §7.1"
status: pendente
---

# PES2-TASK-01: Ferramental das fases 3 e 4

## Contexto

- **Referência:** `docs/PES2-AJUSTES.md` §7.1, e `docs/PLAN-PES2-PSX.md` §3.2.
- **Não bloqueia nada das Fases 0–2.** As três estão fechadas ou a um item, e
  nenhuma delas precisa de varredura numérica nem de desmontador.
- **Instalar pacote na máquina é decisão do dono da máquina.** Esta task
  existe para dar dono à decisão, não para tomá-la.

Duas ausências confirmadas em 2026-08-30:

| Falta | Para quê | Bloqueia |
|---|---|---|
| `numpy` | varredura de padrão em 466 MB em tempo civilizado | conforto, não capacidade |
| Desmontador MIPS — `ghidra`, `radare2` ou `rizin`, os três ausentes | ler o código que consome a tabela, quando a estatística empacar | Fase 4, **se** ela empacar |

---

## Objetivo

Decidir, e registrar a decisão no plano:

1. instalar ou não `numpy` — e, se não, qual é o caminho lento aceito
   (`array`, `memoryview`, `mmap` + fatiamento) para as varreduras da Fase 3;
2. instalar ou não um desmontador MIPS, e **qual**.

### O que pesa em cada escolha

- **`numpy`** é conforto puro. As varreduras que a Fase 3 pede — achar `N`
  registros de largura constante numa faixa de 466 MB — rodam em Python
  puro, só que em minutos em vez de segundos. Um `mmap` com passo fixo já
  resolve a maior parte; o que dói é correlação de coluna.
- **Desmontador** só vale quando a estatística empacar (§4.2.4 do plano, a
  alavanca mais cara). Ghidra traz decompilador e reconhece MIPS de PSX;
  `radare2`/`rizin` são mais leves e bastam para ler uma rotina de acesso a
  tabela. **O overlay não é ELF** — é código realocado carregado em
  `0x800xxxxx`, e o desmontador precisa ser carregado com base explícita.

---

## Critério de conclusão

- [ ] Decisão tomada e escrita na §3.2 do plano, com a razão em uma frase.
- [ ] Se instalado: o comando que instalou, e a versão, registrados no Log.
- [ ] Se recusado: qual é o plano B para a Fase 3, nomeado.

Recusar é resultado legítimo desta task, desde que o plano B esteja escrito.

---

## Log de Execução

*(a preencher)*
