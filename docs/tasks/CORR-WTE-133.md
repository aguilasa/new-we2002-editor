---
id: CORR-WTE-133
title: "Correção: CMB_EDITALLLOOK grava 92 bytes diferentes do ed.exe em quatro faixas de atributo"
type: correção
category: paridade
status: pendente
depends_on: []
---

# CORR-WTE-133: o "reset def. look" diverge em 92 bytes

## Problema identificado

`CMB_EDITALLLOOK` (rotulado *"reset def. look"*) grava **quase** o mesmo que o
`ed.exe`, e diverge em quatro faixas de atributo de jogador.

Medido em 2026-09-01 na `ptbr-remaster.bin`, pela
[PAR-TASK-08](/docs/tasks/PAR-TASK-08.md) item 4, com
[`tools/par/8.9-reset-look.sh`](../../tools/par/8.9-reset-look.sh):

```text
FALHOU: 4 divergencia(s) nao esperada(s):
  2185925..2186189   23 byte(s)  data  OFS_PLAYER_ATTR_3+893
  2192357..2192621   23 byte(s)  data  OFS_PLAYER_ATTR_6+269
  2194868..2195408   46 byte(s)  data  OFS_PLAYER_ATTR_7+428
  2197236..2197236    1 byte(s)  data  OFS_PLAYER_ATTR_8+444
```

**Os dois lados gravam, e gravam quase igual** — o que torna o achado estreito
e provavelmente localizado:

| lado | contra a imagem original |
|---|---|
| `Debug/ed.exe` | 17 faixas, **3468 bytes** |
| `newWe2002` | 16 faixas, **3468 bytes** |

O mesmo total de bytes, e a faixa a mais do oráculo é a conhecida
(`405724..405739`). São **92 bytes** em desacordo dentro de 3468 que concordam.

## Causa raiz

**Não diagnosticada.** Os dois handlers fazem a mesma coisa em estrutura: leem
`data/defaultlook.txt`, que lista por time a pele / cabelo / barba que o elenco
inteiro deve receber, e traduzem rótulos (`"A"`, `"B1"`, …) para índices por
meio de tabelas — `map<string,int>` no legado
(`CEdDlg::OnEditAllPlayersLook`), arrays de `const char*` no port
(`MainWindow::OnEditAllPlayersLook`, `src/app/Commands.cpp:290`).

Duas pistas para começar, nesta ordem:

1. **O `defaultlook.txt` é cp1252, não UTF-8** — ele carrega um `0x92`
   (apóstrofo curvo) em `"Costa d'Avorio"`. O `CLAUDE.md` registra isso como
   dado lido em runtime que **não deve ser convertido**. Se o port e o original
   discordarem no tratamento dessa linha, a divergência cairia num punhado de
   times, que é a forma do que se mediu.
2. **Campo vazio significa "não mexer"**, e as quatro faixas podem ser o
   desacordo sobre o que é vazio — uma coluna ausente, um `-1` contra um zero.

O caminho barato é dumpar, para cada time, o que cada lado decidiu escrever, e
achar em qual linha do `defaultlook.txt` os dois se separam. Não precisa
decompilador: os dois lados são código deste repositório.

## Correção

Diagnosticar primeiro, corrigir depois — e a correção entra no port, salvo se
o achado mostrar que o original faz algo indefinido, caso em que vira
divergência declarada com a justificativa medida.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/Commands.cpp` | modificar — `OnEditAllPlayersLook`, depois do diagnóstico |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 4 da §8.9 quando fechar |
| `docs/tasks/PAR-TASK-08.md` | modificar — o item 4 e o Log |

## Verificação

- [ ] A divergência tem causa nomeada, com a linha do `defaultlook.txt` onde os
      dois se separam
- [ ] `golden_check.sh` em modo `gui` com `tools/par/8.9-reset-look.sh` sai `OK`
- [ ] Os outros dois itens medíveis da §8.9 continuam verdes —
      `8.9-update-costs.sh` e `8.9-update-bars.sh`
- [ ] `ctest` do `newWe2002` continua verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*
