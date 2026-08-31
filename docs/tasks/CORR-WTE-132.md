---
id: CORR-WTE-132
title: "Correção: o .t2002 exportado pelo port tem 52 bytes contra 56 do ed.exe"
type: correção
category: paridade
status: pendente
depends_on: []
---

# CORR-WTE-132: o `.t2002` do port não é o do original

## Problema identificado

Exportar uma tática produz arquivos **de tamanhos diferentes** nos dois lados,
com o mesmo preset e o mesmo roteiro:

| lado | tamanho |
|---|---:|
| `Debug/ed.exe` | **56 bytes** |
| `newWe2002` | **52 bytes** |

Medido em 2026-08-30 pela [PAR-TASK-06](/docs/tasks/PAR-TASK-06.md) item 5, com
[`tools/par/8.7-t2002-exportar.sh`](../../tools/par/8.7-t2002-exportar.sh) na
`ptbr-remaster.bin`.

```text
oráculo (56):
00000000: 662e 6d2e 7461 7474 18e3 5c40 0100 0000  f.m.tatt..\@....
00000010: 342d 352d 3141 0001 0206 0708 0a0c 0d0e  4-5-1A..........

port (52):
00000000: 662e 6d2e 7461 7474 0000 0000 342d 352d  f.m.tatt....4-5-
00000010: 3141 0001 0206 0708 0a0c 0d0e 1012 0909  1A..............
```

A assinatura `f.m.tatt` e o corpo do registro batem. **O que diverge é o
espaço entre eles:** o original grava **8 bytes** (`18e3 5c40 0100 0000`), o
port grava **4 zeros**. Daí os 4 bytes de diferença, e o desalinhamento de todo
o resto do arquivo.

**Os 8 bytes do original são determinísticos**, não lixo: duas exportações
seguidas deram exatamente o mesmo valor. `18e3 5c40` é little-endian
`0x405ce318` — com cara de ponteiro estável —, seguido de `0100 0000` = 1.

## Impacto

É o item que a task chama de "o mais valioso da série": **troca de arquivo nos
dois sentidos**. Hoje ela não funciona — um `.t2002` do original não é aceito
pelo port e vice-versa, porque o registro começa em offsets diferentes.

## Causa raiz

Em [`src/app/DefaultTacticsDialog.cpp`](../../src/app/DefaultTacticsDialog.cpp):

```cpp
constexpr int RECORD_BYTES = 44;
constexpr int FILE_BYTES   = sizeof(MAGIC) + RECORD_BYTES;   // 8 + 44 = 52
constexpr int VPTR_BYTES   = 4;
...
char* rec = out + sizeof(MAGIC) + VPTR_BYTES;                // escreve em 8+4
```

Dois defeitos que se somam:

1. **`FILE_BYTES` não soma `VPTR_BYTES`.** O buffer tem 52 bytes, mas o
   registro é escrito a partir do byte 12 — então os últimos `VPTR_BYTES` do
   registro caem fora do que foi dimensionado.
2. **`VPTR_BYTES` é 4, e no original são 8.** O `ed.exe` é PE32+ **x86-64**
   (`CLAUDE.md`), onde o ponteiro de vtable de uma classe C++ ocupa 8 bytes. O
   `4` corresponderia a um binário de 32 bits.

O mesmo `VPTR_BYTES` é usado na leitura (linha 202), então o port **é
consistente consigo mesmo** — exporta e importa o próprio formato sem erro. Foi
o que escondeu o defeito até a comparação com o oráculo.

## Correção

1. `VPTR_BYTES = 8`, com o comentário dizendo por quê (o oráculo é x64);
2. `FILE_BYTES = sizeof(MAGIC) + VPTR_BYTES + RECORD_BYTES`;
3. decidir o que gravar nos 8 bytes. O original grava um valor estável que
   parece ponteiro; **reproduzi-lo byte a byte não é possível nem desejável** —
   o valor é do espaço de endereços dele.

**Medir antes de escolher.** Escrever um valor inventado sem saber se o
original o valida troca uma divergência conhecida por uma não medida — o erro
que a [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md) já cobrou uma vez.

### A medição do passo 3 não pôde ser feita, e o motivo é um achado novo

A pergunta era **"o `ed.exe` confere esses 8 bytes ao importar?"**. Ela não tem
resposta por este caminho, porque **o import do `ed.exe` recusa até o arquivo
que o próprio `ed.exe` exportou**, com o aviso `Not right file !`.

Medido em 2026-08-31, com o `CMD_IMP` do `DefaultTacticsDialog`:

| arquivo | origem | veredito do `ed.exe` |
|---|---|---|
| `o.t2002` | exportado pelo próprio `ed.exe`, intacto | **`Not right file !`** |
| `z.t2002` | o mesmo, com os 8 bytes do cabeçalho zerados | **`Not right file !`** |
| `d.t2002` | o mesmo, com nome e um byte do corpo alterados | **`Not right file !`** |

Não é o caminho: as três recusas se repetiram com `Z:\tmp\<nome>` e com o
arquivo copiado para o CWD do `ed.exe` (`Debug/`), digitando só `o.t2002` —
curto, sem barras, como o `CLAUDE.md` recomenda.

**O port, no mesmo teste, aceita o arquivo que ele próprio exportou** sem
aviso nenhum.

Antes disso houve uma medição que *parecia* responder a pergunta e não
respondia: importar `o.t2002` e `z.t2002` no oráculo deu imagens **idênticas**,
o que se leria como "o `ed.exe` ignora os 8 bytes". O controle desmentiu — a
comparação contra a imagem original mostrou **só as não-idempotências
conhecidas**, nenhuma faixa de formação. Os dois imports tinham falhado igual.
**Dois caminhos que falham produzem o mesmo resultado que dois que concordam.**

### O que fazer antes de escolher, agora

1. descobrir **o que o import do `ed.exe` valida** — o `OnImp` do diálogo de
   táticas no `legacy/mfc/`, que é código deste repositório e não exige
   decompilar nada;
2. com isso, saber se os 56 bytes exportados são sequer o formato que ele lê —
   a hipótese que o achado abre é **export e import assimétricos no próprio
   original**;
3. só então decidir o conteúdo dos 8 bytes, e implementar os passos 1 e 2.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | modificar — as duas constantes |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 5 da §8.7 |
| `docs/tasks/PAR-TASK-06.md` | modificar — o item 5 e o Log |

## Verificação

- [ ] Um `.t2002` exportado pelo port tem **56 bytes** e é byte-idêntico ao do
      `ed.exe` no que não for o campo de ponteiro
- [ ] O `ed.exe` **importa** o arquivo do port, e a tática resultante bate
- [ ] O port **importa** o arquivo do `ed.exe`, e a tática resultante bate
- [ ] `golden_check.sh` em modo `gui` com o roteiro de importação sai `OK`
- [ ] `ctest` do `newWe2002` continua verde
- [ ] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31 — **PARCIAL: nada implementado, medição
bloqueada.**

**Resumo do que foi feito:**

A evidência foi **reproduzida**: exportando a mesma tática dos dois lados,
`ed.exe` dá 56 bytes e o port 52, com os cabeçalhos
`662e6d2e7461747418e35c4001000000` e `662e6d2e7461747400000000342d352d`.
Idêntico ao que a CORR descreve.

**Os passos 1 e 2 da Correção não foram implementados, de propósito.** Eles são
`VPTR_BYTES = 8` e `FILE_BYTES` somando esse campo — mudanças que parecem
óbvias, mas que só têm sentido junto com o passo 3, e o passo 3 depende de uma
medição que **não pôde ser feita**: o import do `ed.exe` recusa até o arquivo
que ele mesmo exportou (`Not right file !`), testado em três variantes de
conteúdo e dois caminhos. Implementar 1 e 2 sozinhos escreveria 56 bytes num
formato que ninguém verificou que o original lê — trocaria uma divergência
medida por uma suposta, que é exatamente o que a seção **Correção** proíbe.

**Problemas encontrados:**

**Uma medição falsa, pega pelo controle.** Importar o arquivo intacto e o de
cabeçalho zerado deu imagens idênticas, o que se leria como "o `ed.exe` ignora
os 8 bytes" — e teria fechado esta CORR com a conclusão errada. O controle
contra a imagem original mostrou **só as não-idempotências conhecidas**: os dois
imports falharam igual. **Dois caminhos que falham produzem o mesmo resultado
que dois que concordam**, e só o controle os separa.

**Pendências:** ler o `OnImp` do diálogo de táticas no `legacy/mfc/` para saber
o que o import valida, testar a hipótese de export e import assimétricos no
próprio original, e só então escolher o conteúdo dos 8 bytes e implementar.

**Arquivos criados/modificados:**

- `docs/tasks/CORR-WTE-132.md` — este Log e a seção da medição bloqueada
- `tools/par/8.7-t2002-importar.sh` — o roteiro de importação, novo
