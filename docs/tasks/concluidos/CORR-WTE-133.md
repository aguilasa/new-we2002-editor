---
id: CORR-WTE-133
title: "Correção: os dois lados liam defaultlook.txt diferentes — fixture do oráculo fora de sincronia"
type: correção
category: paridade
status: concluído
depends_on: []
---

# CORR-WTE-133: o "reset def. look" diverge em 92 bytes

## Problema identificado

`CMB_EDITALLLOOK` (rotulado *"reset def. look"*) grava **quase** o mesmo que o
`ed.exe`, e diverge em quatro faixas de atributo de jogador.

Medido em 2026-09-01 na `ptbr-remaster.bin`, pela
[PAR-TASK-08](/docs/tasks/concluidos/PAR-TASK-08.md) item 4, com
[`tools/par/8.9-reset-look.sh`](../../../tools/par/8.9-reset-look.sh):

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

**Não era código: os dois lados liam arquivos diferentes.**

O legado abre o arquivo com **caminho relativo**, em
`CEdDlg::OnEditAllPlayersLook`:

```cpp
myfile.open("defaultlook.txt");
```

O `golden_run.sh` executa o `ed.exe` de dentro de `Debug/`, então quem o
oráculo lê é `Debug/defaultlook.txt` — enquanto o port lê
`data/defaultlook.txt` via `app::DataFile()`. **O `Debug/` é gitignored**, e as
duas cópias tinham saído de sincronia em **4 das 95 linhas**:

| linha | `Debug/` (oráculo) | `data/` (port) |
|---|---|---|
| 20 Hungary | `...;I1;**B**;A;A` | `...;I1;**C**;A;A` |
| 40 Colombia | `...;I1;**A**;A;A` | `...;I1;**B**;A;A` |
| 48 Japan | `...;**L2**;A;A;A` | `...;**I1**;A;A;A` |
| 49 South Korea | `...;**L2**;A;A;A` | `...;**I1**;A;A;A` |

E os 92 bytes medidos batem linha a linha com essa diferença — **cada lado
gravou corretamente o que leu**:

| time | oráculo gravou | do rótulo | port gravou | do rótulo |
|---|---:|---|---:|---|
| 20 `hair_colour` | 1 | `B` | 2 | `C` |
| 40 `hair_colour` | 0 | `A` | 1 | `B` |
| 48/49 `hair_style` | 26 | `L2` | 20 | `I1` |

**O versionado é o fiel.** O `defaultlook.txt` do commit raiz (`fd705ec`) traz
`C`, `B`, `I1` e `I1` nessas quatro linhas — os valores de `data/`. Quem
divergiu foi a cópia de `Debug/`, que não está sob versionamento e por isso
envelheceu em silêncio.

## Correção

**Nenhuma no código — o port estava certo.** O que se corrigiu foi a
**fixture do oráculo**: `Debug/defaultlook.txt` passou a ser cópia do
versionado.

```sh
cp data/defaultlook.txt Debug/defaultlook.txt
```

Depois disso o golden do `CMB_EDITALLLOOK` sai `OK`, e os dois lados gravam:
port 16 faixas / 3468 bytes, oráculo 17 / 3483 — a faixa a mais e os 15 bytes
são a divergência conhecida.

A armadilha entrou no `CLAUDE.md`, na seção de encoding, com o `cmp` que a
detecta: **duas cópias do mesmo arquivo, uma versionada e uma não, lidas por
lados opostos do golden.**

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/Commands.cpp` | **não mudou** — o port estava certo |
| `Debug/defaultlook.txt` | alinhado ao versionado (gitignored, não entra no commit) |
| `CLAUDE.md` | a armadilha das duas cópias, com o `cmp` que a detecta |
| `docs/PARIDADE-FUNCIONAL.md` | o item 4 da §8.9 |
| `docs/tasks/concluidos/PAR-TASK-08.md` | o item 4 e o Log |

## Verificação

- [x] A divergência tem causa nomeada — duas cópias do `defaultlook.txt`, e o
      caminho relativo do legado escolhendo a de `Debug/`
- [x] `golden_check.sh` em modo `gui` com `tools/par/8.9-reset-look.sh` sai `OK`
- [x] Os outros dois roteiros da §8.9 continuam verdes
- [x] `ctest` do `newWe2002` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito:**

A evidência foi reproduzida (as mesmas 4 faixas, 92 bytes) e o diagnóstico saiu
pelo caminho barato que a própria CORR sugeria: dumpar o que cada lado decidiu
gravar. O padrão apontou para **times inteiros** — 20, 40, 48 e 49 —, e não
para jogadores espalhados, o que descartou erro de parsing e mandou olhar as
linhas desses times no arquivo.

Aí o legado entregou a causa numa linha: `myfile.open("defaultlook.txt")`, com
**caminho relativo**. O `ed.exe` roda de dentro de `Debug/`, e aquela cópia é
gitignored — tinha 4 linhas diferentes da versionada. Cada lado gravou
corretamente o que leu.

**Nada de código mudou.** A fixture do oráculo foi alinhada ao versionado, que
é o fiel (bate com o commit raiz), e o golden ficou verde.

**Problemas encontrados:**

**Duas hipóteses plausíveis e erradas foram descartadas por medição**, e vale
registrar porque as duas custariam uma correção indevida no port:

1. *o `0x92` cp1252 desalinha o parser* — a própria CORR sugeria isso primeiro.
   Falso: a linha do `0x92` ("Costa d'Avorio") não está entre as afetadas;
2. *deslocamento de uma linha* — o valor do oráculo no time 20 batia com a
   linha do time 19, o que parecia confirmar. Falso: nos times 40 e 48 não
   batia. **Uma coincidência que confirma a hipótese em um caso de quatro não
   é confirmação.**

**Arquivos criados/modificados:**

- `docs/tasks/concluidos/CORR-WTE-133.md` — este Log e o diagnóstico
- `docs/tasks/concluidos/correcoes-progresso.md` — o `[x]` e a data
- `CLAUDE.md` — a armadilha das duas cópias, com o `cmp` que a detecta
- `docs/PARIDADE-FUNCIONAL.md` e `docs/tasks/concluidos/PAR-TASK-08.md` — o item 4 da §8.9
- `Debug/defaultlook.txt` — alinhado ao versionado (gitignored, fora do commit)
