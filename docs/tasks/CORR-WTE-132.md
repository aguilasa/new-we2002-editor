---
id: CORR-WTE-132
title: "Correção: nenhuma — os 52 bytes do port é que estão certos; quem diverge é o ed.exe x64"
type: correção
category: paridade
status: concluído
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

**O port está certo, e a CORR nasceu com o diagnóstico invertido.** O que
diverge é o `ed.exe` que serve de oráculo.

`legacy/mfc/tattica.h` declara a classe assim:

```cpp
class tattica {
public:
    char nome[7];
    char ruoli[11], x[10], y[10];   // 38 bytes de dados
    tattica();
    virtual ~tattica();             // ... e um vptr, por causa disto
};
```

O destrutor virtual põe um vptr no início do objeto, e **o tamanho dele muda
com a arquitetura**:

| build | vptr | `sizeof(tattica)` | arquivo (`8 + sizeof`) |
|---|---:|---:|---:|
| 32-bit — o que o fonte original pressupõe | 4 | 44 | **52** |
| x86-64 — o `Debug/ed.exe` deste repositório | 8 | 48 | **56** |

E o import do original, em `legacy/mfc/tattDlg.cpp:701`, valida com um número
**literal**:

```cpp
if(strcmp(aux,"f.m.tatt") != 0 || fil_ctrl.GetLength() != 52)
{
    AfxMessageBox("Not right file !");
```

Ou seja: **o formato do `.t2002` é de 52 bytes**, o `52` está escrito no fonte,
e o port grava exatamente isso. O `ed.exe` x64 exporta 56 porque o
`sizeof(tattica)` cresceu na recompilação, enquanto o `52` do import ficou —
por isso ele **recusa o arquivo que ele mesmo produz**. É um defeito de
recompilação do oráculo, não do formato nem do port.

**Medido, e é o que fecha o caso:** o `ed.exe` **aceita** o arquivo de 52 bytes
exportado pelo port, e grava a tática importada (`before first offset+374188` e
`+374780`, mais `OFS_TEAM_MIXED_CASE_NAME+223676`). A troca funciona no sentido
port → `ed.exe`; o inverso falha porque o arquivo do oráculo é que está torto.

**Por contraste, `.b2002` e `.m2002` funcionam nos dois sentidos** (§8.8): as
classes de bandeira e uniforme **não têm destrutor virtual**, então não têm
vptr e o tamanho não muda entre 32 e 64 bits — `graf.cpp` valida 41 e 40, e os
dois lados exportam byte-idêntico. O contraste que a §8.8 registrou tem esta
causa.

## Correção

**Nenhuma. Esta CORR se fecha sem mudar código, e mudar seria regressão.**

Aplicar o que a redação original pedia — `VPTR_BYTES = 8` e `FILE_BYTES`
somando-o — faria o port gravar 56 bytes: o mesmo arquivo que **o import do
original recusa**. Trocaria um port correto por um que reproduz um defeito de
recompilação do oráculo.

`VPTR_BYTES = 4` e `FILE_BYTES = 52` em
[`src/app/DefaultTacticsDialog.cpp`](../../src/app/DefaultTacticsDialog.cpp)
**ficam como estão**, e o comentário de lá passa a dizer por quê.

O que sobra é de documentação, e está feito nesta invocação:

1. o item 5 da §8.7 do inventário dizia "reprovou" — não reprovou, e a
   assimetria é do oráculo;
2. a §4.3 do inventário e o `PLAN-LINUX.md` foram editados em 2026-08-31 para
   dizer que "o medido é 8" — conclusão errada, propagada por esta mesma CORR
   antes de o fonte ser lido. Revertidos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/DefaultTacticsDialog.cpp` | **não mudar as constantes** — só o comentário, dizendo por que 4 e 52 estão certos |
| `docs/PARIDADE-FUNCIONAL.md` | corrigir a §4.3 (revertida) e o item 5 da §8.7 |
| `docs/PLAN-LINUX.md` | reverter a edição de 2026-08-31 |
| `docs/tasks/PAR-TASK-06.md` | corrigir o item 5 e o Log |

## Verificação

- [x] O fonte do original diz qual é o formato — `tattDlg.cpp:701` valida 52
- [x] A conta de `sizeof(tattica)` explica os dois números (44 em 32 bits, 48
      em x64), e `tattica.h` mostra o destrutor virtual que a causa
- [x] O `ed.exe` **aceita** o `.t2002` de 52 bytes do port, e grava a tática
- [x] As constantes do port ficaram intactas
- [x] Os docs que afirmavam "8 bytes" foram revertidos
- [x] `ctest` do `newWe2002` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31 (primeira passagem, parcial) e 2026-09-01
(diagnóstico refeito, CORR fechada sem mudar código).

### Segunda passagem — o diagnóstico estava invertido

A pendência da primeira passagem era ler o `OnImporta` do `tattDlg` para saber
o que o import valida. Lido, e a resposta desfaz a CORR:
`legacy/mfc/tattDlg.cpp:701` compara `GetLength()` com **52**, um literal. O
formato é de 52 bytes, o port grava 52, e **o port está certo**.

Quem diverge é o `Debug/ed.exe`: ele é x86-64, onde o vptr da `class tattica`
(que tem destrutor virtual) passa de 4 para 8 bytes, e `sizeof(tattica)` de 44
para 48 — por isso ele exporta 56 e **recusa o próprio arquivo**. Defeito de
recompilação do oráculo.

Medido para fechar: **o `ed.exe` aceita o arquivo de 52 bytes do port** e grava
a tática. A troca funciona no sentido port → oráculo.

**Nada implementado, e implementar seria regressão.** `VPTR_BYTES = 8` faria o
port gravar 56 — o arquivo que o import do original recusa.

**O que se aprendeu, e custou dois documentos:** eu tratei o `ed.exe` como
definição do formato, quando ele é **um binário recompilado** do fonte que está
neste repositório. Onde os dois discordam, **o fonte manda** — ele é a fonte de
verdade, o binário é uma build. E propaguei a conclusão errada para a §4.3 do
inventário e para o `PLAN-LINUX.md` **antes** de abrir o fonte; as duas edições
foram revertidas nesta invocação. Ler o `.h` custou dois minutos e teria evitado
os dois.

### Primeira passagem, 2026-08-31 — parcial

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
