---
id: WTE-TASK-31
title: "Fechamento da fase 4 — os 96 têm veredito?"
type: fechamento
category: comportamento
phase: 4
depends_on: ["WTE-TASK-25", "WTE-TASK-26", "WTE-TASK-27", "WTE-TASK-28", "WTE-TASK-29", "WTE-TASK-30"]
status: em andamento
---

# WTE-TASK-31: Fechamento da fase 4

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4, critério de pronto.

> **Esta task não implementa, e por isso ela tem pré-requisitos nomeados.** O
> primeiro critério é *"nenhuma `aberto`"*, e a
> [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) mediu em 2026-08-21 que
> três handlers do grupo `auxiliar` **gravam na imagem** e ficaram sem dono. Eles
> estavam na [CORR-WTE-081](/docs/tasks/CORR-WTE-081.md), que fechou em
> 2026-08-22 — mas **sobraram outros 18**, e a primeira passagem desta task
> (2026-08-22) mediu quais são, um a um. Ver o Log de Execução e
> [`wte/re/fase-4.md`](../../wte/re/fase-4.md).

> **Pronto quando:** os 96 têm veredito e nenhum é "não portado" sem
> justificativa escrita.

---

## Objetivo

Provar o critério, ou listar o que falta.

### Conferências

1. **Cobertura.** `spec_index.py` sobre `re/spec/` tem de listar 96 entradas.
   Nenhuma `aberto`.
2. **Justificativa.** Todo `não portado` com razão escrita, e a razão tem de
   ser de escopo, não de dificuldade. "Não deu tempo" não é veredito.
3. **Evidência.** Quantas specs se apoiam só em "observação de tela"? Essas são
   hipóteses vestidas de spec. Listar, e decidir quais precisam de disassembly
   antes da Fase 6.
4. **Golden.** Toda operação de gravação verde nas duas ROMs.
5. **Nenhum decompilado colado.** Varredura por trecho de C nas specs — a §2
   depende disso e ninguém confere sozinho.

### Métrica a registrar

Distribuição dos vereditos: quantos `implementado`, `trivial`, `divergência
deliberada`, `não portado`. E a comparação com o que a Fase 4 previa.

Se `trivial` for a maioria esmagadora, provavelmente foi atribuído sem olhar —
a WTE-TASK-30 avisa disso. Amostrar cinco `trivial` ao acaso e reconferir.

### O que ainda não foi provado

As quatro features da Fase 5. O app já edita e grava como o original nas
operações comuns, mas o **motivo do projeto** — preço, `.mcr`, camisa 2D, slots
de ML — ainda não está feito.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/fase-4.md` | criar |
| `wte/re/spec/INDICE.md` | regenerar |
| `docs/tasks/progresso.md` | modificar |

---

## Critério de conclusão

- [ ] 96 entradas no índice, nenhuma `aberto` — **as 96 estão lá; 16 `aberto` e
      2 sem arquivo de spec continuam.** É o único critério em aberto, e a
      primeira passagem mediu exatamente quais
- [x] Todo `não portado` com justificativa de escopo — é **um**,
      `MainForm.Button2Click`, handler órfão que nenhum componente referencia
- [x] Specs de evidência fraca listadas, com decisão sobre cada — são **3
      pontos soltos**, nenhuma spec inteira; a decisão de cada está no
      `fase-4.md` e o gerador **aborta** se aparecer ponto novo sem decisão
- [x] Golden verde para toda gravação — **32 de 32 corridas**, controle e
      golden de cada roteiro, byte-idênticas. *Adaptado:* o critério dizia "nas
      duas ROMs", e a europeia não hospeda o oráculo — o `wte.exe` morre ao
      trocar de time (49.749 violações de acesso) e a gravação nunca acontece.
      Medido em 2026-08-18 e registrado em
      [`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md); a
      europeia é da [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md)
- [x] Varredura por decompilado colado, limpa — **229 arquivos**, nada
- [x] Cinco `trivial` reamostrados e reconferidos — os cinco confirmados por
      disassembly
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-22 *(primeira passagem — a task não fechou)*

- **Resumo do que foi feito:**

  Seis dos sete critérios fecharam, medidos por ferramenta nova
  ([`check_fase4.py`](../../wte/tools/check_fase4.py), irmã das `check_fase1/2/3`)
  que gera o [`wte/re/fase-4.md`](../../wte/re/fase-4.md). O sétimo — *"nenhuma
  `aberto`"* — não fecha, e agora se sabe exatamente o quanto falta: **78 dos 96
  têm veredito fechado**, 16 continuam `aberto` e 2 não têm arquivo de spec.

  **O achado que muda uma conta do projeto inteiro: as gravações não são nove,
  são dezessete.** Nove era o número de quem alguém *chamou* de gravação — seis
  na WTE-TASK-27, uma na 28, uma na 29 e as três órfãs da 30. Lendo a seção
  `## Bytes tocados` das 94 specs, a diferença aparece nos dois sentidos:
  **entram** os sete de mover jogador e número de camisa (grupo `edicao`, que
  gravam dentro da `0x00404820`) e mais dois que gravam no arranque
  (`MainForm.FormShow` e `MainForm.boton_dialogo_weClick`); **saem** o
  `grabar_memoryClick` e o `grabar_camisetaClick`, que apesar do nome não tocam
  a ROM — leem dela e emitem um arquivo. A tabela de gates do gerador é
  **guardada**: handler que a spec diz que grava e não tem roteiro declarado
  aborta o fechamento. Era exatamente por não existir essa conta que três
  gravações ficaram sem dono até a WTE-TASK-30 as achar por leitura.

  **Os 16 `aberto`, e o que segura cada grupo.** Doze deles **já têm corpo
  Pascal escrito** — o que falta não é código, é régua ou dono:

  | Quantos | Quem | O que falta |
  |---:|---|---|
  | 2 | `jugador.etiqprecioClick`, `jugador.casilla_precioKeyPress` | tudo — nem spec têm. São da [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) |
  | 1 | `MainForm.base_teamClick` | a fórmula e a gravação; a moldura ficou pronta na WTE-TASK-30. Também da 32 |
  | 4 | `estrategia.FormCreate`, `estrategia.ComboBoxDrawItem`, `jugador.BitBtn1Click`, `MainForm.boton_dialogo_texClick` | **corpo Pascal**, cada um por uma razão própria escrita na spec |
  | 11 | os demais, todos com corpo escrito | régua — a de tela que o `compara_tela.sh` ainda não alcança, ou uma metade com dono nomeado noutra task |

  Somam 18: os 16 `aberto` mais as 2 sem spec.

  **A bateria custou 3.161 segundos de relógio** — 53 minutos para 32 corridas
  sobre a ROM japonesa, cada roteiro com controle e golden. Todas
  byte-idênticas.

- **Problemas encontrados:**

  **O `golden-06-textura` reprovou nos dois lados na primeira corrida, e a
  culpa era do fixture, não do port.** A mensagem foi
  `ERRO: janela 'W11 TE PT' nao apareceu em 30s` — a mesma assinatura da
  [CORR-WTE-080](/docs/tasks/CORR-WTE-080.md), que é falha de tempo. Não era: o
  roteiro exige que `work/t.bin` seja o arquivo sintético de **5.000 bytes** que
  o cabeçalho dele manda criar, e o `work/` tinha um `t.bin` de **307 MB** —
  uma cópia de ROM deixada ali por outra corrida. O editor engasgava importando
  a textura, e o diálogo do fim nunca vinha.

  Reproduzido com o fixture certo, o par ficou verde de primeira nos dois modos.
  A coluna `tentativas` do registro guarda o 2, porque *"precisou de duas
  corridas"* é fato sobre o gate, mesmo quando a causa é do operador.

  **A lição é para a
  [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md), que vai versionar a
  bateria:** `work/` é rascunho compartilhado e nome de fixture colide com nome
  de cópia de trabalho. A bateria tem de **criar** as fixtures que usa em vez
  de as encontrar — e conferir tamanho antes de rodar, porque a falha por
  fixture errado se disfarça de falha por tempo.

  **Um segundo achado, menor, sobre a guarda de decompilado.** A marca
  `undefined[0-9]?` do `spec_index.py` tem o dígito opcional, e por isso casa
  com a palavra inglesa `undefined` em prosa — o `we2002_types.pas` tem
  `undefined behaviour, not a behaviour` num comentário. Não é defeito lá: o
  `spec_index.py` varre só as specs, escritas em português. A varredura desta
  task alcança `.pas` e `.inc`, então ela exige o dígito, e o custo está escrito
  no cabeçalho do gerador — um `undefined` de Ghidra sem dígito passaria por
  ela.

---

### Segunda passagem — 2026-08-22

**Objetivo:** as prosas de *"veredito `aberto` porque…"* de vários dos 16 citam
bloqueios que **caíram** desde que foram escritas — `0x0040756c` portada,
`0x00404820` portada, a tela do `MainForm` populada. Reconferir veredito contra
a régua é trabalho de fechamento, não implementação, então a passagem rodou o
[`compara_tela.sh`](../../wte/tools/compara_tela.sh), que é a régua do grupo de
carga.

**Nenhum veredito virou, e a razão é melhor do que se esperava: a conferência
achou um defeito.**

Quatro times medidos — 2, 0, 56 e o combo 68:

| Time | Barras | Uniforme | Bandeira |
|---|---|---|---|
| 2 | 5/5 em pixel | em pixel | em pixel |
| 0 | 5/5 em pixel | em pixel | em pixel |
| 56 `CLASSIC ENGLAND` | 5/5 em pixel | em pixel | **3.840/3.840 px diferentes** |
| 68 `HIGHLANDS` (`ml_teams[5]`) | 5/5 em pixel | em pixel | **3.840/3.840 px diferentes** |

**Dez times desenham a bandeira preta no port**, e o dump da camada de dados
diz por quê: `flag_colours` carrega como dezesseis zeros em `teams[56..63]` —
os oito CLASSIC — e em `ml_teams[5]` e `ml_teams[22]`. Zero na paleta é preto.

A causa **não é do port**, é de alcance entre os dois oráculos. O laço de carga
é transpilado do `we2002_core`, que é byte-idêntico ao `ed.exe`, e o `ed.exe`
para no time 55 (`for(i = 0;i < 56;i ++)`) e pula os índices 5 e 22 no bloco de
Master League. Ele nunca precisou dessas cores: **não desenha bandeira
nenhuma.** O editor do Obocaman desenha, e as lê pela tabela de offsets em
`.data`. O port herdou a camada de dados de um e a tela do outro.

É a classe de achado da
[WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) — *"os offsets que o
Obocaman tem e nós não"* —, e escapou dela porque a conferência de tela daquela
época não olhou a bandeira desses dez. Aberta como
[CORR-WTE-083](/docs/tasks/CORR-WTE-083.md), com as duas rotas possíveis e a
recomendação de **não** mexer no `we2002_core`.

**O que isso ensina sobre o fechamento:** reconferir veredito velho não é
burocracia. Três handlers de carga carregavam prosa que dizia *"falta a carga
da tela"* enquanto a tela já carregava; medir para confirmar o óbvio custou uma
corrida e devolveu um defeito de dez times que ninguém procurava.

- **O que falta para esta task fechar:**

  Os 16 `aberto` e as 2 specs ausentes. Três deles são da WTE-TASK-32, que é a
  próxima na ordem; os outros 13 precisam de dono, e um deles — o
  `lista_equiposChange` — ganhou nesta passagem uma razão nova e concreta, a
  CORR-WTE-083. **Esta task volta a rodar depois disso** — é fechamento, e
  fechamento não implementa.

- **Arquivos criados/modificados:**

  - criados: `wte/tools/check_fase4.py`, `wte/tools/test_check_fase4.py`,
    `wte/re/fase-4.md`, `wte/re/fase-4-golden.tsv`,
    `wte/re/fase-4-trivial.tsv`; na segunda passagem,
    `docs/tasks/CORR-WTE-083.md`
  - modificados: `docs/tasks/progresso.md`, `docs/PLAN-WTE-LAZARUS.md`, e na
    segunda passagem `docs/tasks/correcoes-progresso.md` e
    `wte/re/spec/MainForm.lista_equiposChange.md`; este arquivo
