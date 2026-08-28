---
id: WTE-TASK-38
title: "Decidir o nome do produto e registrar a linhagem"
type: decisão
category: empacotamento
phase: 7
depends_on: ["WTE-TASK-35"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §2 e Fase 7"
status: concluído
---

# WTE-TASK-38: Nome e linhagem

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §2 e Fase 7.
- Decisão adiada de propósito até aqui, porque **não bloqueava nada antes**.
  Agora bloqueia: o empacotamento escreve o nome em sete lugares.

O `we-team-editor.exe` é obra do **Obocaman (2002)**, sem licença concedida —
mesma situação do código herdado do Moriero e do thyddralisk que o
[`NOTICE.md`](../../NOTICE.md) já registra. O repositório **não tem `LICENSE`** e
não deve ganhar um.

---

## Objetivo

Fechar duas coisas, com a razão escrita.

### 1. O nome

O plano diz: **não reusar "WE2002 Team Editor" tal e qual**. Razões, e vale
escrever qual pesa:

- é o nome do produto de outro autor
- confunde com o binário original, que continua no disco e é oráculo dos testes
- os scripts de teste acham janela por título, e nome igual quebra a WTE-TASK-22

Herdar do `newWe2002` a distinção que já funciona: **nome de produto** e **nome
de formato** são coisas diferentes. Lá, `newWe2002` é o produto e `we2002` é o
formato — o executável e o `share/` usam um, o namespace e as unidades usam o
outro. Aqui vale a mesma separação.

O nome escolhido entra em: binário, `share/`, `.desktop`, appid, ícone, título
da janela, e o `README.md` de `wte/`.

### 2. A linhagem no `NOTICE.md`

Se o app for publicado, o `NOTICE.md` ganha uma seção sobre a linhagem do
Obocaman, no mesmo tom das existentes: quem escreveu o original, quando, que
relação este trabalho tem com ele, e o que **não** foi copiado.

O que a seção deve poder afirmar, e que as fases anteriores construíram:

- o código é escrito a partir de `re/spec/`, não transcrito de decompilado
- a camada de dados vem do `we2002_core` deste repositório
- os formulários vêm de conversão de formato, não de cópia de código
- os assets (`image/`, `data/`) **não** são redistribuídos

O último item precisa de decisão: sem os 198 BMP o app não desenha camisa. O
usuário mantém a pasta, como faz com `roms/` — mas isso tem de estar escrito, e
o app tem de falhar com mensagem clara quando a pasta faltar.

### Decisão que não é minha

**Publicar é decisão do usuário.** Esta task prepara o texto e a decisão; não
publica, não empurra para remote público sem confirmação explícita.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `NOTICE.md` | modificar |
| `wte/README.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§2 e Fase 7) |
| `wte/wte.lpr`, `wte/wte.lpi` | modificar — o `Application.Title` que reusava o nome do Obocaman |
| `wte/re/divergencias.md` | modificar — a entrada 12, a pasta de assets ausente |
| `docs/tasks/39-empacotamento.md` | modificar — os nomes decididos e o inventário da renomeação |
| `docs/tasks/40-verificacao-final.md` | modificar — o defeito que já espera a condição 3 |

*(A tabela original listava os três primeiros. O `Application.Title` entrou
porque a cadeia que ele carregava era o nome do Obocaman letra por letra — a
decisão sem essa linha seria só prosa; os outros quatro são o registro e os
dois repasses.)*

---

## Critério de conclusão

- [x] Nome do produto escolhido, com razão, e a separação produto/formato
      definida — **`WE2002 - Lazarus Editor`**, escolhido pelo usuário, com a
      alusão a Lázaro; slug `we2002Lazarus`, appid
      `io.github.aguilasa.we2002Lazarus`, formato `we2002` (inalterado). A
      tabela dos quatro papéis está no [`wte/README.md`](../../wte/README.md) e
      repetida na Fase 7 do plano
- [x] Seção de linhagem escrita no `NOTICE.md` — *Lineage of WE2002 - Lazarus
      Editor*, mais a linha do Obocaman na tabela de linhagem e a ressalva de
      licença passando a nomear os três autores
- [x] Decidido o que acontece quando a pasta de assets falta — **o app não
      encerra**; registrado como divergência **12** em
      [`wte/re/divergencias.md`](../../wte/re/divergencias.md), com a mensagem
      ("o que falta **e onde pôr**") encaminhada à
      [WTE-TASK-39](/docs/tasks/39-empacotamento.md)
- [x] Registrado que publicar depende de confirmação do usuário — na §2 do
      plano, junto do registro de que a seção foi escrita
- [x] Nenhum `LICENSE` adicionado — conferido: `git ls-files | grep -i license`
      não devolve nada
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-25

- **Resumo do que foi feito:**

  O nome veio do usuário — **`WE2002 - Lazarus Editor`**, com a alusão a Lázaro
  ressuscitando — e o que esta task fez foi tirar dele as consequências. A
  separação produto/formato do `newWe2002` resolve sozinha onde cada nome entra,
  e o caso mais fácil de errar é o `Caption` dos 18 formulários: ele **não**
  recebe o nome do produto, porque ali o critério é fidelidade de tela e é o
  sufixo ` [Lazarus]` que separa os dois lados no mesmo `:98`. Quem mostra o
  nome do programa é o `Application.Title` — e foi ali que a decisão já custou
  uma linha de código: ele dizia `WE2002 Team Editor (Lazarus)`, que tirando o
  parêntese é o nome do produto do Obocaman letra por letra, exatamente o que a
  §2 do plano proíbe.

  O `NOTICE.md` ganhou a seção de linhagem, escrita para poder afirmar o que as
  fases anteriores construíram: especificação escrita à mão, camada de dados
  vinda do `we2002_core`, formulários convertidos de formato, assets **não**
  redistribuídos. Escrever a seção não é publicar — a decisão de publicar
  continua sendo do usuário, e isso ficou escrito na §2.

- **Arquivos criados/modificados:** conferido contra `git show --stat`.

  `NOTICE.md`, [`wte/README.md`](../../wte/README.md) (a decisão 3 e o
  parágrafo de estado, que ainda dizia "Fase 0"),
  `docs/PLAN-WTE-LAZARUS.md` (§2, Fase 7 **e a fração da §4.4**),
  `wte/wte.lpr` + `wte/wte.lpi` (o `Application.Title`),
  `wte/re/divergencias.md` (entrada 12), `wte/re/fase-2.md` (regerado),
  `docs/tasks/progresso.md`, este arquivo, e **os dois repasses**:
  `docs/tasks/39-empacotamento.md` e `docs/tasks/40-verificacao-final.md`.

- **Problemas encontrados:**

  **1. O binário não abre fora de `wte/build/`, e isso não é sobre assets.**
  Descoberto ao tentar medir o que acontece quando a pasta de assets falta: a
  cópia do binário num diretório vazio morre num diálogo da LCL — `File not
  found. / Press OK to ignore and risk data corruption. / Press Abort to kill
  the program.` — **antes de qualquer janela**. A causa é o log de trace:
  `ResolveArquivo` do [`retrace.pas`](../../wte/src/retrace.pas) resolve
  `<dir do executável>/../re/trace.log` e o `Rewrite` levanta `EInOutError`
  quando o diretório não existe.

  **Controle:** com o binário em `<algum>/sub/wte`, criar `<algum>/re/` — o
  `retrace.pas` resolve `<dir do executável>/../re/trace.log`, então o `re/` é
  irmão **do diretório** do binário, como `wte/re/` é irmão de `wte/build/`.
  Feito isso, o mesmo binário abre a janela principal (522×475) e escreve o
  `trace.log` lá. E a versão de uma linha, que não depende de layout nenhum e
  isola o trace de qualquer coisa de assets:

  ```sh
  WTE_TRACE_FILE=/tmp/trace.log ./wte
  ```

  *(Até 2026-08-25 esta receita punha o `re/` irmão do **arquivo**, e o código
  o resolve irmão do **diretório** — medido nos quatro layouts pela
  [CORR-WTE-116](/docs/tasks/CORR-WTE-116.md). Quem a seguisse ao pé da letra
  veria o mesmo diálogo e concluiria que a causa não era o trace, que é a
  hipótese errada de volta pela porta que este controle existe para fechar.)*

  A primeira leitura foi "é a pasta de assets", e o controle a derrubou: com
  `WTE_ASSETS_DIR` apontando para a pasta do Obocaman o diálogo continuava.
  **Sem o controle, esta task teria registrado a causa errada** numa entrada de
  divergência — e a WTE-TASK-39 iria consertar a coisa errada. Encaminhado para
  a 39 (dona da resolução em runtime) e para a 40, cuja condição 3 reprova hoje.

  **2. Mexer no `wte.lpr` derrubou o `check_fase2.py`.** As dez linhas de
  comentário que explicam a troca do título mudaram a contagem de Pascal escrito
  à mão, e a §4.4 do plano carrega a fração medida (`52,0%` → `51,9%`). O guard
  exige o literal, e está certo: número em documento que envelhece sozinho é o
  defeito que este projeto batizou de prosa vencida. Plano e `fase-2.md`
  atualizados; o `fase-2.md` é gerado e foi **regerado**, não editado.
