---
id: PES2-TASK-07
title: "Dump de RAM e casamento com o bloco do disco"
type: engenharia-reversa
category: formato
phase: 3
depends_on: ["PES2-TASK-06"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §5 (Fase 3)"
status: pendente
---

# PES2-TASK-07: Dump de RAM e casamento com o disco

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §5, Fase 3, segundo item.
- **É a ponte entre o cartão e o disco.** A PES2-TASK-06 fecha o registro no
  save; esta descobre onde o mesmo dado mora no `.bin`.

O DuckStation tem *save state* e dump de RAM (§3.4, item 2 — disponível,
nenhum feito ainda). A PSX tem 2 MiB de RAM principal em `0x80000000`, o que
é pequeno o bastante para varrer inteiro.

---

## Objetivo

Localizar, na imagem de CD, o bloco que o jogo carrega quando entra no menu
de edição — e portanto o registro de jogador **no disco**.

### Método: assinatura de conteúdo

O caminho curto não é entender o carregador; é usar o dado como sua própria
assinatura.

1. Dump de RAM com o jogo parado no menu de edição.
2. Achar na RAM a sequência de nomes de um elenco conhecido — as fronteiras
   dos 54 já estão medidas (§3.3), então há 54 assinaturas prontas.
3. A partir da âncora, ler a vizinhança: o array de atributos que o menu
   mostra está por perto, e os valores da tela dizem quais bytes são quais.
4. Procurar **a mesma vizinhança no disco**, por conteúdo. Se o overlay é
   carregado sem descompressão — o que a §1.10 sugere, já que as tabelas de
   texto estão em claro —, o bloco cai idêntico.

### O que fazer se não cair idêntico

Duas explicações, nesta ordem de probabilidade:

- **o jogo desempacota ao carregar** — atributos guardados comprimidos em
  bits no disco e expandidos em RAM. Sintoma: o bloco da RAM é um múltiplo
  inteiro maior que o candidato no disco;
- **o bloco é montado de duas fontes** — nome de um lugar, atributo de
  outro. Sintoma: o nome casa no disco e a vizinhança não.

Nos dois casos a saída é a §4.2.4 — desmontar a rotina de carga — e aí a
PES2-TASK-01 deixa de ser conforto.

### Disciplina

Save state e dump de RAM são derivados de jogo comercial: **ficam fora do
git**, como os quadros do `boot_check.sh` e os FAQs. O que entra é o script
que os produz e o offset que eles revelaram.

---

## Critério de conclusão

- [ ] Um dump de RAM tirado no menu de edição, com o comando versionado.
- [ ] O elenco conhecido localizado na RAM, com offset.
- [ ] O bloco correspondente localizado no disco — arquivo, offset relativo,
      marcador de âncora — **ou** o diagnóstico de por que não caiu, com a
      medida que o sustenta.
- [ ] O par RAM ↔ disco verificado por `poke`: alterar o byte no disco muda o
      que o menu de edição mostra.

---

## Log de Execução

*(a preencher)*
