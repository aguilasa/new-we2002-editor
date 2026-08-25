---
id: WTE-TASK-39
title: "Ícone, .desktop, AppStream e regras de instalação"
type: implementação
category: empacotamento
phase: 7
depends_on: ["WTE-TASK-38"]
status: pendente
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
| `wte/packaging/*.desktop` | criar |
| `wte/packaging/*.metainfo.xml` | criar |
| `wte/tools/make_icon.py` | criar |
| `wte/src/datafiles.pas` | criar — a ordem de busca |
| `wte/Makefile` ou equivalente | modificar — alvo de install |

---

## Critério de conclusão

- [ ] `install` num prefixo temporário põe tudo no lugar
- [ ] Árvore instalada funciona depois de movida
- [ ] Assets ausentes produzem mensagem que diz o que falta e onde pôr
- [ ] `.desktop` e AppStream validados pelas ferramentas do freedesktop
- [ ] Ícone conferido a olho, nos sete tamanhos
- [ ] Nenhum formato de pacote (AppImage/Flatpak) adicionado
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**

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

### A renomeação, com o inventário já medido

`wte.lpi`, `wte.lpr` e `build/wte` passam a levar o slug. Quem os cita, medido
em 2026-08-25 com `grep -rl`:

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
