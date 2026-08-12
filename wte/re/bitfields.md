# Os campos de bit da ficha do jogador — duas descricoes, uma so resposta

GERADO por `wte/tools/check_bitfields.py`. **Nao editar a mao.**

Produto da WTE-TASK-26, decima primeira passagem. O `0x0040756c` — a rotina que preenche a ficha do jogador — nao traz deslocamento de bit nenhum no codigo: ele percorre as duas tabelas abaixo e chama o extrator `0x00403278` com cada registro.

| tabela | endereco | registros | passo |
|---|---|---|---|
| `habilidades` | `0x00423648` | 16 | 12 B |
| `aparencia` | `0x00423708` | 12 | 12 B |

O terceiro endereco que a rotina carrega — `0x00423798`, no segundo laco — **nao** entra aqui: o passo dele e `0x20` e ele e um vetor de `AnsiString`. O finalizador da RTL em `0x004029b5` recebe contagem `0x60` = 96 = 12 x 8, o que da 12 registros de oito cadeias — as legendas dos campos enumerados da ficha. Ele nasce zerado no arquivo e e preenchido em tempo de execucao (`0x00401db6`), e esse preenchimento continua por ler.

## A conferencia

Cada registro descreve `{byte, bit inicial, largura}` dentro dos 12 bytes de atributo. O `we2002_player.pas` — gerado do `we2002_core`, que ja e byte-identico ao `ed.exe` — desempacota os mesmos 12 bytes com `shr`/`and`. **As duas descricoes sao independentes**: uma e tabela de dados do `wte.exe`, a outra e expressao de codigo herdada do outro editor.

**Os 28 registros batem, um a um.** O port nao precisa de logica de bit nova para a ficha: a camada de dados ja a tem.

| tabela | # | endereco | byte | bit | bits | extracao no `TPlayer.Decode` |
|---|---|---|---|---|---|---|
| habilidades | 0 | `0x00423648` | 7 | 5 | 3 | `(raw_attributes[7] shr 5) and $07` |
| habilidades | 1 | `0x00423654` | 8 | 0 | 3 | `raw_attributes[8] and $07` |
| habilidades | 2 | `0x00423660` | 5 | 6 | 3 | `(raw_attributes[5] shr 6) and $03` + `(raw_attributes[6] shl 2) and $04` |
| habilidades | 3 | `0x0042366c` | 6 | 1 | 3 | `(raw_attributes[6] shr 1) and $07` |
| habilidades | 4 | `0x00423678` | 6 | 7 | 3 | `(raw_attributes[6] shr 7) and $01` + `(raw_attributes[7] shl 1) and $06` |
| habilidades | 5 | `0x00423684` | 7 | 2 | 3 | `(raw_attributes[7] shr 2) and $07` |
| habilidades | 6 | `0x00423690` | 9 | 1 | 3 | `(raw_attributes[9] shr 1) and $07` |
| habilidades | 7 | `0x0042369c` | 8 | 3 | 3 | `(raw_attributes[8] shr 3) and $07` |
| habilidades | 8 | `0x004236a8` | 8 | 6 | 3 | `(raw_attributes[8] shr 6) and $03` + `(raw_attributes[9] shl 2) and $04` |
| habilidades | 9 | `0x004236b4` | 10 | 2 | 3 | `(raw_attributes[10] shr 2) and $07` |
| habilidades | 10 | `0x004236c0` | 9 | 7 | 3 | `(raw_attributes[9] shr 7) and $01` + `(raw_attributes[10] shl 1) and $06` |
| habilidades | 11 | `0x004236cc` | 9 | 4 | 3 | `(raw_attributes[9] shr 4) and $07` |
| habilidades | 12 | `0x004236d8` | 6 | 4 | 3 | `(raw_attributes[6] shr 4) and $07` |
| habilidades | 13 | `0x004236e4` | 10 | 5 | 3 | `(raw_attributes[10] shr 5) and $07` |
| habilidades | 14 | `0x004236f0` | 11 | 0 | 3 | `raw_attributes[11] and $07` |
| habilidades | 15 | `0x004236fc` | 5 | 2 | 3 | `(raw_attributes[5] shr 2) and $07` |
| aparencia | 0 | `0x00423708` | 0 | 0 | 3 | `raw_attributes[0] and $07` |
| aparencia | 1 | `0x00423714` | 4 | 0 | 2 | `raw_attributes[4] and $03` |
| aparencia | 2 | `0x00423720` | 0 | 4 | 5 | `(raw_attributes[0] shr 4) and $0f` + `(raw_attributes[1] shl 4) and $10` |
| aparencia | 3 | `0x0042372c` | 1 | 1 | 3 | `(raw_attributes[1] shr 1) and $07` |
| aparencia | 4 | `0x00423738` | 1 | 5 | 3 | `(raw_attributes[1] shr 5) and $07` |
| aparencia | 5 | `0x00423744` | 2 | 1 | 3 | `(raw_attributes[2] shr 1) and $07` |
| aparencia | 6 | `0x00423750` | 2 | 4 | 6 | `(raw_attributes[2] shr 4) and $0f` + `(raw_attributes[3] shl 4) and $30` |
| aparencia | 7 | `0x0042375c` | 4 | 2 | 3 | `(raw_attributes[4] shr 2) and $07` |
| aparencia | 8 | `0x00423768` | 4 | 5 | 5 | `(raw_attributes[4] shr 5) and $07` + `(raw_attributes[5] shl 3) and $18` |
| aparencia | 9 | `0x00423774` | 11 | 3 | 3 | `(raw_attributes[11] shr 3) and $07` |
| aparencia | 10 | `0x00423780` | 11 | 6 | 2 | `(raw_attributes[11] shr 6) and $03` |
| aparencia | 11 | `0x0042378c` | 3 | 7 | 1 | `(raw_attributes[3] shr 7) and $01` |

## O que isto NAO diz

Qual controle da tela recebe qual campo. A ordem dos registros e a ordem em que a rotina os consome, e casa-la com os controles e leitura do corpo do `0x0040756c` — que continua por fazer.

O campo `number` do `TPlayer` (byte 3, bit 2, 5 bits) **nao tem registro** em nenhuma das duas tabelas: o numero de camisa tem tela propria (`ficha_dorsal`), e a ficha do jogador nao o mostra.
