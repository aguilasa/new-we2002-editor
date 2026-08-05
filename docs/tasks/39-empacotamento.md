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

Os 197 BMP e o `dat.bin` **não são redistribuídos** (WTE-TASK-38). Então a busca
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
