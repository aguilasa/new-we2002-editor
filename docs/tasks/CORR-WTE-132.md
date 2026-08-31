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
   o valor é do espaço de endereços dele. A pergunta a medir antes de escolher:
   **o `ed.exe` confere esses 8 bytes ao importar?** Se ignorar, zeros servem e
   a troca nos dois sentidos passa a funcionar; se conferir, é preciso saber
   contra o quê.

**Medir antes de escolher.** Escrever um valor inventado sem saber se o
original o valida troca uma divergência conhecida por uma não medida — o erro
que a [CORR-WTE-127](/docs/tasks/CORR-WTE-127.md) já cobrou uma vez.

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

## Log de Execução *(preenchido após execução)*
