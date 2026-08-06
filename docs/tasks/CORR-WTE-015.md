---
id: CORR-WTE-015
title: "Correção: duas transcrições de evidência do assets.md não batem com a medida — o ano dos 195 .bmp e o endereço do fread"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-015: o `assets.md` acerta as conclusões e erra duas evidências

## Problema identificado

O `wte/re/assets.md` é escrito à mão — a WTE-TASK-08 decidiu rota inline, com o
comando que reproduz cada número ao lado dele, e essa decisão se sustentou: esta
revisão rodou os comandos e **todos os números principais reproduzem**. Duas
transcrições, porém, não.

**1. O ano dos arquivos não tocados (§6.1).**

> Os outros 195 mantêm o `mtime` de **2006** do pacote do Obocaman.

Medido: dos 195, **176 são de 2002** e 19 são de 2006. Nenhuma conclusão muda —
os três reescritos continuam sendo três, no mesmo segundo, com tamanho intacto —,
mas a frase é usada como evidência de proveniência, e a proveniência real é
melhor do que a descrita: a maioria dos arquivos carrega a data do próprio
lançamento do editor.

**2. O endereço do `fread` (§8.1).**

O bloco que prova que `grabar_memoryClick` copia os 128 KiB do molde lista:

```
40f80c:  call 0x417770              ; fread (buf, 0x20000, 1, dat.bin)
```

Em `0x0040f80c` está `push 0x1` — o segundo argumento. A chamada está em
`0x0040f81a`. As outras quatro linhas do mesmo bloco conferem no endereço exato.

O erro é de rótulo, não de leitura: a sequência é mesmo o `fread` de `0x20000`
do `dat.bin`, e o comando `objdump` que o `.md` traz ao lado mostra isso. Mas o
bloco é uma tabela de endereços, e quem for ao `0x40f80c` no Ghidra da
WTE-TASK-24 encontra um `push`.

## Evidência

O `mtime` dos 198, por ano:

```
$ find we-team-editor -iname '*.bmp' -printf '%TY\n' | sort | uniq -c
    176 2002
     19 2006
      3 2026
```

Os três de 2026 são os que o `.md` já nomeia, e a conclusão dele sobre eles
confere:

```
$ find we-team-editor -iname '*.bmp' -newermt '2026-01-01' -printf '%TY-%Tm-%Td %p\n'
2026-08-05 we-team-editor/image/uniformes2d/pantalon0.bmp
2026-08-05 we-team-editor/image/uniformes2d/camiseta2.bmp
2026-08-05 we-team-editor/image/banderas/bandera37.bmp
```

O trecho em torno de `0x0040f80c`, pelo próprio comando do `.md`:

```
40f806:  a1 68 2e 43 00    mov    eax,ds:0x432e68
40f80b:  50                push   eax
40f80c:  6a 01             push   0x1
40f80e:  68 00 00 02 00    push   0x20000
40f813:  8d 95 c8 ff fd ff lea    edx,[ebp-0x20038]
40f819:  52                push   edx
40f81a:  e8 51 7f 00 00    call   0x417770
```

Para contraste, o que reproduz exato — as duas tabelas medidas e o outro bloco
de disassembly, rodados verbatim do `.md` nesta revisão:

```
bandeiras -> entradas: 95 | distintas: 53 | faltando: [44,45,46,47,48,49,50,51]
camiseta: 0 .. 98  distintas 99  faltando []      pantalon: [0,1,2,3,4,5]
times 0..62: 0..49    times 63..94: 50..98
camiseta 0..49: 40x42 (50 arquivos) | camiseta 50..98: 51x42 (49 arquivos)
lista_col0: 95 itens, '  0 Irlanda' … '94 Boca Juniors'
40c0f0: push 0x2e14 | 40c111: cmp eax,0xfc | 40c11e: push 0x20000
40c139: push 0x2e08 | 40c18a: push 0x130   | 40c199: cmp edi,0x7
Player.cpp:22-26 — skin_colour, hair_style, hair_colour, beard_style, beard_colour
flechasapa2 Max=3 | 3 Max=31 | 4 Max=7 | 5 Max=6 | 6 Max=6
dat.bin: 145408 bytes, "MC", 145408-0x20000 = 14336 = 7 x 2048
198 bitmaps = 53 + 105 + 32 + 7 + 1;  41 dos 45 TImage com Picture.Data
```

## Causa raiz

Documento escrito à mão: os dois trechos foram transcritos de uma sessão de
medição em vez de colados da saída, e nenhum `--check` cobre prosa.

## Correção

### Arquivo: `wte/re/assets.md`

- **§6.1:** trocar "Os outros 195 mantêm o `mtime` de 2006" por o que a
  varredura mostra — 176 de 2002, 19 de 2006 —, e acrescentar o comando que
  produz a quebra por ano, no padrão do resto do arquivo:

  ```sh
  find we-team-editor -iname '*.bmp' -printf '%TY\n' | sort | uniq -c
  ```

- **§8.1:** corrigir `40f80c` para `40f81a` na linha do `fread`. Vale conferir
  os outros quatro endereços do mesmo bloco no mesmo passe — esta revisão
  conferiu e eles batem, mas o custo é um `objdump`.

**Não** é caso de criar gerador. A decisão de rota inline da WTE-TASK-08 está
registrada e continua certa para um documento de ~15 medidas com prosa entre
elas; o que estas duas linhas mostram é que **evidência transcrita à mão precisa
ser colada da saída**, e é isso que a correção faz.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/assets.md` | modificar |

## Verificação

- [ ] `grep -n "2006" wte/re/assets.md` mostra a frase já com 176/19
- [ ] O comando da quebra por ano está no `.md` e reproduz o que ele afirma
- [ ] `objdump -d -M intel --start-address=0x40f7a0 --stop-address=0x40f850
      we-team-editor/we-team-editor.exe` confirma cada endereço do bloco da §8.1
- [ ] Nenhum outro número do `.md` mudou — os demais foram reconferidos nesta
      revisão e batem
- [ ] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
