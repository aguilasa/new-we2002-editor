---
id: WTE-TASK-39
title: "Ícone, .desktop, AppStream e regras de instalação"
type: implementação
category: empacotamento
phase: 7
depends_on: ["WTE-TASK-38"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 7"
status: concluído
---

# WTE-TASK-39: Empacotamento

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 7.
- Copiar o padrão que o `newWe2002` já tem em
  [`packaging/`](../../packaging/) — não inventar.

**Formato de pacote fica de fora.** AppImage e Flatpak foram deliberadamente
excluídos no plano Linux do `newWe2002` e a decisão vale aqui: só as regras de
instalação.

---

## Objetivo

Instalação limpa num prefixo, com os arquivos nos lugares certos.

### O que instalar

| Item | Destino |
|---|---|
| binário | `bin/` |
| dados lidos em runtime | `share/<produto>/` |
| `.desktop` | `share/applications/` |
| ícone, sete tamanhos | `share/icons/hicolor/*/apps/` |
| AppStream | `share/metainfo/` |
| documentação | `share/doc/<produto>/` |

### A regra que o `newWe2002` já aprendeu

**O binário acha os dados relativo a si mesmo**, não por caminho absoluto
compilado. A ordem de busca de
[`DataFiles.cpp`](../../src/app/DataFiles.cpp) é: variável de ambiente, ao lado
do executável, o prefixo instalado, o diretório de fonte. Isso permite mover a
árvore instalada.

Reproduzir a mesma ordem em Pascal. A variável de ambiente muda de nome
conforme a WTE-TASK-38.

### Os assets são o caso especial

Os 198 BMP e o `dat.bin` **não são redistribuídos** (WTE-TASK-38). Então a busca
tem um caso a mais: se a pasta não estiver lá, o app precisa falhar com mensagem
que diga **o que falta e onde colocar** — não um erro genérico de arquivo não
encontrado.

### O ícone

O `newWe2002` gera os sete PNG com `tools/make_icon.py`, e esse é o único
gerador do repositório **sem `--check`**: a saída do PIL não é
byte-determinística entre versões, e um guard que quebra quando o Pillow sobe é
pior que nenhum.

Herdar a decisão, e herdar a consequência: **ao mexer no ícone, olhe o
resultado** — é a única coisa gerada que teste nenhum julga.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/packaging/io.github.aguilasa.we2002Lazarus.desktop` | criar |
| `wte/packaging/io.github.aguilasa.we2002Lazarus.metainfo.xml` | criar |
| `wte/packaging/README-assets.txt` | criar — o que vai em `share/we2002Lazarus/` |
| `wte/packaging/icons/we2002Lazarus-*.png` | criar — os 7, gerados |
| `wte/tools/make_icon.py` | criar |
| `wte/src/wte_datafiles.pas` | criar — a ordem de busca *(o enunciado dizia `datafiles.pas`; o prefixo `wte_` é o que as outras unidades de aplicação usam)* |
| `wte/src/retrace.pas` | modificar — o trace passa pela mesma resolução, e nunca derruba o app |
| `wte/src/we2002_estado.pas` | modificar — `RaizDosAssets` vira encaminhamento |
| `wte/src/impl/ep2002_mainform.FormShow.inc` + `.uses` | modificar — a mensagem de assets ausentes |
| `wte/Makefile` | modificar — alvos `install` e `icon` |

---

## Critério de conclusão

- [x] `install` num prefixo temporário põe tudo no lugar — **13 arquivos**,
      conferidos por `find`: `bin/we2002Lazarus`, o `.desktop`, o AppStream, os
      7 PNG em `hicolor/*/apps/`, `share/we2002Lazarus/README.txt` e os dois
      documentos em `share/doc/we2002Lazarus/`
- [x] Árvore instalada funciona depois de movida — instalada num prefixo,
      **movida de diretório**, e o binário abriu, achou os assets no caminho
      novo (`share/we2002Lazarus/`) e carregou o time 2 da ROM japonesa, com
      bandeira e uniforme desenhados. As mensagens que ele imprime trazem o
      caminho novo, o que é a prova de que nada é compilado
- [x] Assets ausentes produzem mensagem que diz o que falta e onde pôr — em
      **três lugares**, porque tem três leitores: o rótulo da janela, a saída de
      erro e um diálogo. Ela nomeia os arquivos (`image/` e `data/dat.bin`) e os
      três diretórios onde o app procura, com os caminhos resolvidos
- [x] `.desktop` e AppStream validados pelas ferramentas do freedesktop —
      `desktop-file-validate` sem saída; `appstreamcli validate --pedantic`
      **verde**, com uma nota pedante (`cid-contains-uppercase-letter`) que o
      metainfo do `newWe2002` também tem, pela mesma razão: o appid segue o
      slug camelCase do produto
- [x] Ícone conferido a olho, nos sete tamanhos — bandeirinha de escanteio,
      legível em 16 px, distinta da camisa do irmão. As três cores saem do
      próprio app (`$00FFB676`, `$00E68F41`, `$003C3CDC`)
- [x] Nenhum formato de pacote (AppImage/Flatpak) adicionado
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-26

- **Resumo do que foi feito:**

  A instalação existe e foi **provada movendo a árvore**: `make -C wte install
  PREFIX=<p>`, `mv <p> <outro>`, e o binário abriu, achou os assets em
  `share/we2002Lazarus/` do lugar novo e carregou o time 2 da ROM japonesa com
  bandeira e uniforme desenhados. As mensagens que ele imprime trazem o caminho
  novo — é isso que prova que nada é compilado.

  **O que estava quebrado não era o que a task previa.** O enunciado esperava
  que o caso especial fosse a pasta de assets; o defeito real era o **log de
  trace**, que resolvia `<exe>/../re/trace.log` e derrubava o app com um
  diálogo genérico da LCL antes de qualquer janela. As duas resoluções de
  caminho viraram uma, no
  [`wte_datafiles.pas`](../../wte/src/wte_datafiles.pas), com a mesma ordem de
  busca — e o `retrace` passou a **desligar o log** quando o arquivo não abre,
  em vez de matar o programa. Um log é diagnóstico; diagnóstico que mata o
  paciente é pior que nenhum, e este matou.

  **Uma decisão mudou de forma em relação ao repasse da WTE-TASK-38:** o
  projeto continua se chamando `wte` na árvore, e o slug `we2002Lazarus` entra
  no `install`. Renomear `wte.lpi`/`wte.lpr`/`build/wte` custaria 3 ferramentas,
  o `Makefile` e prosa de `docs/`, e nenhum desses leitores é o usuário.

  **O escopo veio do usuário**, em 2026-08-26: *a princípio* esta aplicação não
  será distribuída na internet — é de uso próprio, e vai servir de base para um
  app novo que juntará o que ela e o `newWe2002` fazem. Nada de formato de
  pacote (já estava fora); o `.desktop` e os ícones ficam porque são o que faz a
  entrada de menu existir na máquina de quem instala, e o AppStream ficou por
  ser o único do lote que só teria consumidor numa loja — escrevê-lo custou um
  arquivo e mantém a porta aberta.

- **Arquivos criados/modificados:** conferido contra `git show --stat`.

  Criados: `wte/src/wte_datafiles.pas`, `wte/tools/make_icon.py`,
  `wte/packaging/` inteiro (o `.desktop`, o `.metainfo.xml`, o
  `README-assets.txt` e os **7 PNG** de `icons/`).

  Modificados: `wte/Makefile` (alvos `install` e `icon`), `wte/src/retrace.pas`,
  `wte/src/we2002_estado.pas`, `wte/src/impl/ep2002_mainform.FormShow.inc` e o
  `.uses` dele (mais o `wte/src/ep2002_mainform.pas`, **regerado** pelo
  `dfm2lfm.py` por causa do `.uses`), `wte/README.md`, `wte/re/fase-2.md` e
  `wte/re/fase-4.md` (**regerados**), `docs/PLAN-WTE-LAZARUS.md`,
  `docs/tasks/progresso.md`, este arquivo, e o repasse em
  [`docs/tasks/40-verificacao-final.md`](/docs/tasks/40-verificacao-final.md).

- **Problemas encontrados:**

  **1. `pkill -x -f <caminho>` não mata processo que recebeu argumento.** O
  `-x` exige casamento exato da linha de comando inteira, e o app tinha sido
  lançado com o caminho da imagem. O processo sobreviveu, a janela ficou no
  `:98`, e o `golden_check.sh` **recusou começar** — a guarda de janela grande
  fez exatamente o que existe para fazer. Custou uma corrida de gate.

  **2. Mexer no `.uses` do `MainForm` derruba o `check_fase2.py`, e mexer no
  Pascal também.** Cada linha nova de código escrito à mão move a fração da
  §4.4 do plano (`51,9%` → `51,3%`). Pior: a passagem anterior escreveu os
  números por arquivo **à mão** (`wte.lpr` 41, `retrace.pas` 125) e eles nunca
  bateram com a tabela do `fase-2.md`, que é quem os mede — 52 e 148. Corrigido
  aqui, com o ponteiro para a tabela ao lado, para a próxima passagem copiar em
  vez de estimar.

  **3. O `cd` do shell é persistente entre comandos.** Os três arquivos de
  `packaging/` nasceram em `wte/packaging/icons/wte/packaging/`, porque o
  comando anterior tinha entrado em `icons/`. Movidos, e o diretório espúrio
  removido — mas o tipo de erro merece registro: caminho relativo depois de
  `cd` num shell que não voltou.

---

## O que a WTE-TASK-38 decidiu, e que esta task aplica (2026-08-25)

### Os quatro nomes

| Papel | Nome | Onde entra |
|---|---|---|
| **Produto** | `WE2002 - Lazarus Editor` | `Name=` do `.desktop`, `<name>` do AppStream, `Application.Title` *(já feito)* |
| **Slug** | `we2002Lazarus` | binário, `share/<slug>/`, ícone, `StartupWMClass`, `share/doc/<slug>/` |
| **AppID** | `io.github.aguilasa.we2002Lazarus` | `<id>` do AppStream e o nome dos dois arquivos de `wte/packaging/` |
| **Formato** | `we2002` | as unidades `we2002_*.pas` e as variáveis `WTE_*` — **não muda** |

O slug é camelCase por simetria com o irmão (`newWe2002` já ocupa `bin/` e
`share/` assim), e sem hífen porque a forma reversa de DNS do appid não os
aceita. A razão completa está na
[WTE-TASK-38](/docs/tasks/38-nome-e-linhagem.md) e no
[`wte/README.md`](../../wte/README.md).

**O `Caption` dos 18 formulários não entra nessa lista.** Ele continua sendo o
do DFM mais o sufixo ` [Lazarus]` — critério de fidelidade de tela, e é o que
separa os dois lados no mesmo `:98`. Trocá-lo derrubaria os **27** roteiros do
lado port.

### A renomeação, com o inventário já medido — **não executada**

> **O repasse previa isto e a execução decidiu o contrário.** Ver o Log desta
> mesma task e a seção *"O binário se chama `wte` na árvore e `we2002Lazarus`
> instalado"* do [`wte/README.md`](../../wte/README.md), que traz a razão:
> `wte.lpi`, `wte.lpr` e `build/wte` **continuam** com o nome da árvore, e o
> slug entra no `install`. A árvore concorda — os três seguem com o nome
> antigo, e só o binário instalado leva o slug.
>
> **O inventário abaixo fica porque continua correto**: é quem citaria os três
> arquivos **se** a renomeação vier a acontecer, e refazê-lo custaria o mesmo
> `grep -rl`. Anotado pela
> [CORR-WTE-118](/docs/tasks/CORR-WTE-118.md) em 2026-08-26 — a instrução
> estava viva nesta seção enquanto a revogação morava setenta linhas acima, no
> Log, sem nada ligando uma à outra.

Se a renomeação for feita algum dia, quem cita os três — medido em 2026-08-25
com `grep -rl`:

- **3 ferramentas:** `wte/tools/golden_run_laz.sh`, `wte/tools/compara_tela.sh`,
  `wte/tools/captura_ui.sh` (as três apontam para `build/wte`; as duas últimas
  também usam o caminho como padrão de `pgrep` nas guardas de sobra);
- **`wte/Makefile`** (`LPI` e `BIN`);
- prosa de `docs/` — os `docs/tasks/*.md` e os `docs/prompts/*.md` que ensinam
  `lazbuild wte/wte.lpi`. **Registro histórico (`CORR-*` e Logs de Execução)
  não se reescreve**: ele descreve o que aconteceu.

### O arranque quebra fora de `wte/build/` — achado desta preparação

**Medido, e é o defeito de empacotamento que a fase 7 existe para pegar.** O
binário copiado para um diretório qualquer **não abre**: morre num diálogo da
LCL antes de qualquer janela, dizendo

```
File not found.

Press OK to ignore and risk data corruption.
Press Abort to kill the program.
```

A causa é o log de trace, não os assets: `ResolveArquivo` em
[`wte/src/retrace.pas`](../../wte/src/retrace.pas) resolve
`<dir do executável>/../re/trace.log` quando `WTE_TRACE_FILE` não está
definida, e o `Rewrite` levanta `EInOutError` porque o diretório não existe.
**Controle:** com o binário em `<algum>/sub/wte`, criar `<algum>/re/` — o `re/`
é irmão **do diretório** do binário, como `wte/re/` é irmão de `wte/build/`.
Feito isso, o mesmo binário abre a janela principal (522×475) e escreve o
`trace.log` lá. Sem criar diretório nenhum:
`WTE_TRACE_FILE=/tmp/trace.log ./wte` faz o mesmo, e é a segunda evidência
porque isola o trace dos assets. *(Ver a
[CORR-WTE-116](/docs/tasks/CORR-WTE-116.md): esta receita punha o `re/` irmão
do **arquivo**, e assim o diálogo continua.)*

Duas consequências para esta task:

1. **A condição 3 da [WTE-TASK-40](/docs/tasks/40-verificacao-final.md) —
   "árvore instalada funciona depois de movida" — reprova hoje**, e não por
   causa dos assets. A resolução do trace precisa entrar na mesma ordem de
   busca dos dados, com um caminho gravável de verdade (ou o trace desligado
   por padrão em build instalado);
2. o diálogo que aparece é o genérico da LCL, e ele oferece *"Press OK to
   ignore and risk data corruption"* num editor que grava em imagem de CD. Seja
   qual for a saída escolhida, ela não pode ser essa.

### A mensagem de assets ausentes

Decidido na WTE-TASK-38 e registrado como divergência 12 em
[`wte/re/divergencias.md`](../../wte/re/divergencias.md): o app **não encerra**
quando falta a pasta — encerrar mataria todo roteiro do lado port, que abre o
app antes de tudo. O que falta é a **mensagem**: hoje o rótulo diz
`data/dat.bin nao encontrado`, que diz o que falta e não onde pôr. O critério
"assets ausentes produzem mensagem que diz o que falta e onde pôr" já está na
lista acima; o texto do `make -C wte assets`, que já falha dizendo o que
colocar onde, é o modelo a levar para dentro do app.
