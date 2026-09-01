---
id: PES2-TASK-23
title: "O editor — leitura e exibição"
type: implementação
category: ui
phase: 6
depends_on: ["PES2-TASK-22"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 6)"
status: pendente
---

# PES2-TASK-23: O editor, lado da leitura

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 6, e §0 (objetivo).
- **Metade fácil primeiro.** Ler não corrompe imagem; gravar sim. O editor
  abre lendo, e a PES2-TASK-24 acrescenta a gravação depois de esta estar
  verificada.

---

## Objetivo

Um editor que abre o `.bin` do Track 1 e mostra o banco: times, elencos,
jogadores, atributos, formações, uniformes, bandeiras — tudo pelo
`pes2_map.json`, nada por constante embutida.

### O que ele mostra que o disco não guarda

A §1.8 é clara: **o disco não sabe que `PIEMONTE` é a Juventus.** O mapa
fictício → real é conhecimento externo, e está em
[/docs/PES2-NOMES.md](/docs/PES2-NOMES.md), com a procedência separada — índice,
nome e offset saem do disco; o clube real vem dos FAQs.

Mostrar "PIEMONTE (Juventus)" ao lado do slot é, nas palavras do plano, *"a
diferença entre uma tabela e uma ferramenta"*. Mas a procedência tem de
aparecer na interface também: o que veio do disco e o que veio de FAQ não
podem ser lidos como a mesma coisa.

### Multi-track: o argumento é o Track 1

A §6.4 é armadilha ativa: *"uma ferramenta que abra o `.cue` e concatene as
trilhas produz offsets que não existem em lugar nenhum."* O editor recebe o
caminho do **`(Track 1).bin`**. Se um dia aceitar a pasta ou o `.cue`, é para
resolver o Track 1 dentro deles, nunca para concatenar.

### Identificar a imagem antes de exibir

Duas guardas antes de mostrar qualquer coisa:

1. **a release**, pelo `SYSTEM.CNF` (`SLES_039.57` contra `SLES_039.46`);
2. **os marcadores**, que falham alto se ausentes (§1.13) — o que também
   serve de verificação de que a imagem aberta é mesmo PES2.

Abrir uma imagem de WE2002 por engano e exibir lixo plausível é o modo de
falha que estas duas guardas existem para impedir.

---

## Critério de conclusão

- [ ] Abre as **duas** releases e exibe o banco igual nas duas — a §1.12
      prevê que o conteúdo seja idêntico, e divergência ali é bug do leitor.
- [ ] Recusa, com mensagem legível, imagem que não seja PES2.
- [ ] Nenhuma constante de offset no código do editor: tudo pelo mapa.
- [ ] O clube real exibido, com a procedência distinguível do que é medido.
- [ ] Nenhum caminho de escrita ainda — abrir é **somente leitura** nesta
      task, e o arquivo é aberto como tal.

---

## Log de Execução

*(a preencher)*
