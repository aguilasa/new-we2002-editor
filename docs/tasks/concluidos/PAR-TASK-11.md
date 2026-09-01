---
id: PAR-TASK-11
title: "SoFIFA: o que dá para conferir sem rede"
type: verificação
category: features
projeto: newWe2002
depends_on: ["PAR-TASK-01", "PAR-TASK-02", "PAR-TASK-03", "PAR-TASK-04", "PAR-TASK-05", "PAR-TASK-06", "PAR-TASK-07", "PAR-TASK-08", "PAR-TASK-09"]
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.6"
status: bloqueado
---

# PAR-TASK-11: SoFIFA, o possível sem rede

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.6.
- **Projeto:** `newWe2002` (port Qt do `ed.exe`), **não** o `wte/` Lazarus.

## Por que está bloqueada

**O import do SoFIFA está desligado desde 2026-08-05, por decisão**, e fica em
último plano até a paridade com o `ed.exe` estar conferida tela a tela — que é
exatamente o que as PAR-TASK-01 a 09 entregam. O interruptor é
`app::SOFIFA_ENABLED` em [../../src/app/Features.hpp](../../../src/app/Features.hpp).

Ele apaga (em cinza, não escondido) os três botões de SoFIFA, o botão de edit
options, as 23 caixas de URL, o `CMD_READ_URL` do diálogo de atributos e a
leitura dos dois arquivos de regras no startup. **Nada disso toca a imagem.**

Reativar é o primeiro passo desta task, e **não deve ser feito antes** das
dependências fecharem.

---

## O que NÃO pode ser desligado junto

**O sidecar `<imagem>_url.txt`.** O `OnWriteCD` original o grava
(`legacy/mfc/edDlg.cpp:6207`) e o `Database::Save()` gerado herda isso, montando
o arquivo a partir de `players[].url`. Por isso o `LoadUrls()` roda **mesmo com o
SoFIFA desligado**: sem ele a gravação truncaria o arquivo do usuário para 1.911
linhas em branco. Detalhe na §1.1 do
[/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md).

Ao reativar, conferir que esse caminho continua igual — é regressão silenciosa e
destrutiva se quebrar.

---

## Itens a conferir

- [ ] Sem `SOFIFA attributes.txt` → aviso "Impossible to read SOFIFA attributes !"
- [ ] Sem o arquivo de regras → silêncio, editor continua utilizável
- [ ] Cache `<imagem>_SOFIFAdb.txt` escrito à mão + `CMB_IMPFIFATXT` +
      `CMB_EDITALLTXT`, com as 4 combinações relevantes de checkbox
- [ ] URL `dummy` num jogador + `CMD_READ_URL`
- [ ] **Com rede, se ainda funcionar:** um jogador real, ida e volta

## Ressalva sobre o último item

**O site mudou desde 2015 e o raspador pode não achar mais nada.** Isso **não é
regressão do port** — conferir contra o `ed.exe` antes de acusar. Se os dois
falharem igual, o item passa: paridade é o critério, não funcionamento.

Há também uma **divergência deliberada** da Fase 5 nesta área — o preço do
jogador importado. Está na lista de aceitas do
[/docs/PLAN-LINUX.md](/docs/PLAN-LINUX.md) e não aparece nos golden tests.

---

## Definição de pronto

- [ ] `app::SOFIFA_ENABLED` reativado, e a decisão de mantê-lo ligado registrada
- [ ] O sidecar `_url.txt` continua com 1.911 linhas preenchidas depois de gravar
- [ ] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.6
- [ ] Divergência fora de `405724..405739` registrada como CORR
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
