---
handler: boton_nombres2isoClick
formulario: MainForm
endereco: 0x0040d534
veredito: implementado
---

# MainForm.boton_nombres2isoClick

Grava os três nomes do time selecionado nos blocos de nome da imagem. 2.268
bytes, do `0x0040d534` ao `0x0040de15` — o maior handler do grupo, e o único
que depende de duas tabelas e de duas rotinas internas.

Portado na [WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md), com
golden verde.

## Entrada

- os três `edit_nombreN` (`[this+0x35c]`, `+0x360`, `+0x364`) — o texto da
  tela, não o modelo;
- `lista_equipos.ItemIndex` (`[this+0x2f0]`), que decide o time e entra em
  duas das três regras de exclusão;
- a **tabela de blocos** em `0x004231a0`: 3 linhas × 6 `DWORD`. A linha é o
  campo, a coluna é o bloco de nome, e o valor zero quer dizer "este campo não
  tem esse bloco". Extraída pela
  [WTE-TASK-06](../../../docs/tasks/06-mapa-de-offsets.md);
- a **tabela de registros** em `0x00433a0c`: 3 × 6 registros de 52 bytes,
  preenchidos por time na carga. Cada um é
  `{offset absoluto: DWORD, comprimento: DWORD, modo: DWORD, buffer: 40 bytes}`.
  O `+4` dela é o `0x00433a10` que a
  [CORR-WTE-061](../../../docs/tasks/CORR-WTE-061.md) mediu como largura por
  time.

**Evidência:** disassembly lido

## Saída

Três coisas, nesta ordem:

1. **o rótulo do combo**, remontado: `IntToStr(idx)` alinhado à direita em três
   colunas (dois espaços para `idx < 10`, um para o resto — as cadeias
   `0x00424dfb` e `0x00424e00`) seguido do texto de `edit_nombre1`. Ele é
   escrito em `Items[idx]` de **`lista_equipos_1` e `lista_equipos_2`**, achados
   por `FindComponent('lista_equipos_' + IntToStr(n))`, `n` em 1..2. Como
   atribuir a `Items[]` zera a seleção, o handler guarda o `ItemIndex` antes e
   o repõe depois — mas só quando ele ainda for igual ao do combo principal;
2. **os bytes na imagem** — a seção abaixo;
3. `ficha_info3` (`0x00432e40`) recebe em `etiq1` a cadeia
   `Nomes inseridos no jogo!!!     ` (`0x00424e1f`) e é exibido modal. É o
   mesmo formulário que o [`boton_barras2isoClick`](MainForm.boton_barras2isoClick.md)
   usa, com outra cadeia.

**Evidência:** disassembly lido

## Bytes tocados

Dez blocos, medidos com o time 2 (`WALES`) e o texto `A B-C.DEFG` do
`compara_tela.sh --nomes`:

| campo | offset | tamanho | região | ficou |
|---|---:|---:|---|---|
| `edit_nombre1` | 2003954 | 10 | `OFS_TEAM_NAME_KANJI_A+26` | `Ａ Ｂ Ｃ ．` (dois bytes por letra) |
| `edit_nombre1` | 4599398 | 6 | `OFS_TEAM_MIXED_CASE_NAME+802` | `A BC.` |
| `edit_nombre2` | 1013918 | 7 | `OFS_TEAM_NAME_1_A+182` | `A BC.DE` |
| `edit_nombre2` | 1882878 | 7 | `OFS_TEAM_NAME_2+910` | `A BC.DE` |
| `edit_nombre2` | 2004970 | 7 | `OFS_TEAM_NAME_3+974` | `A BC.DE` |
| `edit_nombre2` | 2830926 | 7 | `OFS_TEAM_NAME_4+766` | `A BC.DE` |
| `edit_nombre2` | 5652630 | 7 | `OFS_TEAM_NAME_6_B+266` | `A BC.DE` |
| `edit_nombre3` | 2005366 | 3 | `OFS_TEAM_ABBREV_1+370` | `ABC` |
| `edit_nombre3` | 4234854 | 3 | `OFS_TEAM_ABBREV_3+370` | `ABC` |
| `edit_nombre3` | 5651438 | 3 | `OFS_TEAM_ABBREV_2+370` | `ABC` |

São **dez** e não onze porque o sexto bloco de `edit_nombre2` é o que a regra
do índice 3 exclui — ver Pré-condições.

**O trace não separa bloco de bloco, e por isso a régua aqui é o `cmp`.** As
oito faixas de escrita que o `27-gravacao-controle` registrou são fronteiras de
**descarga** do buffer do runtime C, não gravações lógicas; duas gravações
vizinhas caem na mesma faixa e uma faixa pode cobrir duas. A sessão
`27-nomes-editados` digita texto distinto nos três campos exatamente para que o
`cmp` possa atribuir cada bloco ao seu campo.

**Evidência:** diff medido

## Pré-condições

Três validações, todas com aborto e caixa de aviso, na ordem:

| condição | mensagem (`0x00424db1`, `+0x16`, `+0x2b`) |
|---|---|
| `edit_nombre1` vazio | `Insira o nome (1)   ` |
| `edit_nombre2` vazio | `Insira o nome (2)   ` |
| `Length(edit_nombre3) < 3` | `Insira o nome (3) de 3 letras ` |

Cada uma exibe o aviso pelo formulário `0x00432e54` e devolve o foco ao campo
que falhou (`SetFocus`, VMT+0xc0) antes de sair.

Dentro do laço de gravação há mais **três** exclusões, e nenhuma delas é
validação de entrada:

1. **bloco ausente** — `0x004231a0[campo][bloco] = 0` pula o bloco. É como a
   tabela diz que `edit_nombre1` tem 2 blocos, `edit_nombre2` tem 6 e
   `edit_nombre3` tem 3;
2. **`edit_nombre1` começando com `?`** (`0x00424e1d`) pula **todos** os blocos
   daquele campo. O `?` é o que a carga mostra quando não soube decodificar o
   nome; regravá-lo destruiria o original;
3. **`edit_nombre2`, bloco 3, com `ItemIndex < 63`** — o bloco é o
   `OFS_ML_TEAM_NAME_7`, e só clube de Master League o tem. O salto é
   `cmp eax,0x3f` / `jl`: pula quando o índice é **menor** que 63. A primeira
   leitura desta spec inverteu o sentido, e a medição desmentiu — a tabela
   promete onze blocos e o `cmp` vê dez, com o time 2.

**Evidência:** disassembly lido

## Comportamento de erro

Fora das três validações, não trata. Sem imagem aberta o `FILE*` global
(`0x00432e58`) é nulo; o botão nasce `Enabled = False` no DFM e só é habilitado
pelo `lista_equiposChange` com `ItemIndex < 95`, que é o que impede o caso.

**Evidência:** disassembly lido

## Notas

### As duas rotinas internas, e a divisão de trabalho entre elas

| endereço | tamanho | papel |
|---|---:|---|
| `0x00403a68` | — | **codifica** o texto da tela no buffer do registro |
| `0x00403dcc` | 82 B | resolve o registro `(campo, bloco)` e chama o gravador |
| `0x00403400` | 70 B | `fseek(f, offset, SEEK_SET)` e `fputc` byte a byte |

O gravador é trivial e não conhece nome nenhum: recebe offset, contagem e
buffer. Toda a semântica está no codificador.

### Duas codificações, escolhidas pelo `modo` do registro

O campo `+8` do registro seleciona:

- **modo 1** — dois bytes por caractere. Cada letra passa por `0x00403448`, que
  devolve o par em `0x00432eb4` e `0x00432eb8`; caractere que a tabela não
  reconhece vira um espaço simples. É o bloco `OFS_TEAM_NAME_KANJI_A`, e é por
  isso que `A BC.` ocupa 10 bytes lá;
- **modo 2** — um byte por caractere.

Nos dois, o que sobra do comprimento é preenchido com `0x00`, e o laço para no
comprimento do registro — nunca no fim do texto. É truncamento por campo, o
mesmo que o [`truncamento.md`](../truncamento.md) mapeou para a tela.

### A regra que enche os 18 registros — `0x00403c0c`

É a peça que faltava, e ela não usa tabela de offset por time nem de
comprimento: **varre a imagem**.

```text
restantes := 94 - indice
seek(tabela[campo][bloco] + 1)
repetir `restantes` vezes:
    anda ate o fim do nome corrente        (ate o byte 0)
    anda pelo enchimento                   (bytes 0) ate o proximo nao-zero
offset      := posicao - 1
comprimento := quantos bytes o slot tem, nome mais enchimento
le o slot para o buffer do registro e marca o fim com 0xFF
se (campo, bloco) = (0, 0):  comprimento := comprimento - 1;  modo := 1
senao:                       modo := 2
```

Duas coisas que isso revela e que nenhuma tabela diria:

- **os blocos guardam os times em ordem inversa.** O offset da tabela é o slot
  do time **94**, e a varredura anda `94 - índice` registros para frente. O
  `we2002_core` conhece a mesma inversão pelo outro lado — o `Save` dele grava
  `ml_teams[31-i]`;
- **o comprimento é a largura do slot medida na imagem**, não uma constante. É
  por isso que o mesmo campo grava 7 bytes num bloco e 3 noutro.

Há um caso especial morto no original: `(campo 0, bloco 5, 32º registro)` faz
um `seek` fixo para `0x563f8d`. O bloco 5 da linha 0 é buraco na tabela, então
o laço nunca chega lá. Não foi portado, e a razão está aqui.

### O salto de setor é do fluxo, não do endereço — `0x00403388`

Depois de **cada** byte lido ou gravado, o original testa
`posicao mod 2352 = 2072` e, se bate, pula 304. É o que torna o formato
MODE2/2352 invisível para o resto do código: nome que atravessa fronteira de
setor não escreve por cima do EDC/ECC.

No port isso é `SaltaFronteiraDeSetor` / `LeDoFluxo` / `GravaNoFluxo`, no
`we2002_estado`.

### O espaço é codificado diferente do `ed.exe`, e isso é medição

No modo de dois bytes o `wte.exe` escreve **um** `0x20` para o espaço; o
`AsciiToKanji` do `we2002_core`, que veio do `ed.exe`, escreve o par
`0x82 0x80`. Medido no byte gravado: `A BC.` sai
`82 60 20 82 61 82 62 81 44`, nove bytes e não dez.

Como este projeto porta o editor do Obocaman, a regra que vale é a dele — e é
por isso que o port **não** reusa o codec do core aqui.

O original também não trata caractere fora de `[A-Za-z0-9 .]` nesse modo:
deixa o segundo byte com o valor do caractere anterior. Não há como chegar lá
pela tela — os três filtros de `KeyPress` só deixam passar esse conjunto —, e o
port escreve espaço. Divergência inalcançável, registrada aqui.

### O que a régua desta task mediu

`golden_check.sh` sobre `golden-05-nomes` / `.port`: **passou**, só as duas
faixas do arranque divergem, e o **controle** (oráculo contra oráculo) fechou
byte-idêntico antes — o roteiro digita, e roteiro que digita precisa provar que
é determinístico.

E a passagem não é vazia: rodado o lado port sozinho contra a ROM limpa, ele
grava **os dez blocos**, nos mesmos offsets e com os mesmos tamanhos que a
sonda `27-nomes-editados` mediu no oráculo.

### O que faltava para escrever o Pascal

~~Falta a regra geral que a carga usa para preencher os 18 registros.~~
**Recuperada em 2026-08-19** e escrita acima — é a varredura do `0x00403c0c`.
Com ela a spec bastou: o Pascal saiu daqui, e está em
[`../../src/impl/ep2002_mainform.boton_nombres2isoClick.inc`](../../src/impl/ep2002_mainform.boton_nombres2isoClick.inc),
com as auxiliares no `.aux.inc` da mesma unidade.
