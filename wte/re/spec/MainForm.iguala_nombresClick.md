---
handler: iguala_nombresClick
formulario: MainForm
endereco: 0x0040d43c
veredito: implementado
---

# MainForm.iguala_nombresClick

"Usar Nome1 nos 3 tipos de nomes" — a dica do próprio botão, no DFM. 248 bytes.

## Entrada

`edit_nombre1.Text` (campo `0x35c`) e a global `0x00433b48`.

**Evidência:** disassembly lido

## Saída

```text
edit_nombre2.Text := Copy(edit_nombre1.Text, 1, DWORD[0x00433b48] - 1)
edit_nombre3.Text := Copy(edit_nombre1.Text, 1, 3)
```

Duas cópias truncadas, cada uma ao que cabe no campo de destino. O `3` é
literal no original e casa com o `MaxLength = 3` que o DFM põe no
`edit_nombre3` — é a abreviatura.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum.** Mexe só nos dois `TEdit`. Quem leva nome para a imagem é o
`boton_nombres2isoClick`, da
[WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md).

**Evidência:** disassembly lido

## Pré-condições

**Nenhuma.** Não confere se há time carregado nem se o campo está vazio. O que
o segura é a tela: o botão nasce `Enabled = False` e a carga de um time
nacional o habilita — e é justamente aí que mora o defeito registrado abaixo.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Com `edit_nombre1` vazio, os outros dois ficam vazios.

**Evidência:** disassembly lido

## Notas

**O limite do segundo campo era o motivo do veredito, e o que a Fase anterior
escreveu aqui estava errado — medido e corrigido em 2026-08-18 pela
[CORR-WTE-061](../../../docs/tasks/CORR-WTE-061.md).** O original usa
`DWORD[0x00433b48] - 1`, e essa global **não é constante**.

`lista_equiposChange` chama `0x0040cbc8`, que percorre uma tabela de **lotes**
em `0x004231a0` — 3 linhas × 6 colunas de offset, 11 das 18 entradas não-zero,
e as 11 são `OFS_*` que o `we2002_core` já conhecia. Para cada lote ela **anda
pelo arquivo** até o registro do time selecionado (`0x00403c0c`, pulando o
rodapé de cada setor MODE2/2352) e grava três campos em `0x00433a0c`: o offset
do registro, a **largura** dele, e os bytes. Passo 312 por linha e 52 por
coluna, logo:

```text
[0x00433a10]  linha 0 coluna 0  = OFS_TEAM_NAME_KANJI  ->  edit_nombre1
[0x00433b48]  linha 1 coluna 0  = OFS_TEAM_NAME_3      ->  edit_nombre2, e este handler
```

**Não é `mixed_case_name`, e não é 19.** O `mixed_case_name` é a linha 0 coluna
1 (`0x00433a44`), outro lote. Emulada a travessia sobre a imagem japonesa, a
largura do lote `OFS_TEAM_NAME_3` bate com `TEAM_NAME_LEN_3` em **95/95**
times, e para o time 2 dá 8 — logo o limite é **7**, não 19.

Confirmado na tela do oráculo no mesmo dia, com `A B-C.DEFG`: os dois lados
mostram `A BC.DE`, sete caracteres. O port mostrava nove antes.

O truncamento daqui usa a mesma fonte que o `MaxLength`, agora de verdade:
`LimiteDoNome2`, no `.aux.inc`, que lê `TEAM_NAME_LEN_3` do time selecionado.

**O primeiro campo também fechou, e o que faltava era um `dec`.**
`0x00403c0c` termina com um caso especial testado em `0x00403d59` — linha 0 e
coluna 0, que é exatamente o lote kanji:

```text
dec  [0x00433a10 + linha*312 + coluna*52]
mov  [0x00433a14 + ...], 1
```

**O lote kanji guarda a largura menos um**, e o campo `+8` recebe `1` em vez do
`2` dos outros — é o modo do decodificador de texto (`0x00403598` compara com
`0x82`, o byte-líder Shift-JIS): 1 = dois bytes por caractere, 2 = um byte.
Como a largura é `TEAM_NAME_KANJI_LEN × 2`, o `div 2` do valor decrementado dá
`TEAM_NAME_KANJI_LEN − 1`.

Medido pela [CORR-WTE-064](../../../docs/tasks/CORR-WTE-064.md) em três times
de larguras diferentes: `LEN` 6 → 5, 8 → 7, 14 → 13, com oráculo e port
mostrando o mesmo em todos. A diferença contra a derivação ingênua era
**constante em 1**, não proporcional — foi isso que apontou um decremento em
vez de erro de escala.

**O que mantinha o veredito `aberto` era outra coisa, e ela foi medida em
2026-08-18 pela [CORR-WTE-060](../../../docs/tasks/CORR-WTE-060.md): não é
defeito do port.** A
[CORR-WTE-057](../../../docs/tasks/CORR-WTE-057.md) tinha medido que o port
**não desabilita** o `iguala_nombres` no time-modelo — 518 px de mudança no
oráculo, **0** no port — com a linha presente no `.inc` do
`lista_equiposChange` e o vizinho `boton_nombres2iso` acinzentando certo.

A causa é o **widgetset**, não o código:

- a LCL desenha o glifo desabilitado aplicando `gdeDisabled`, que é uma
  **conversão para tons de cinza**. Pixel com `R = G = B` é ponto fixo dela;
- o glifo do `iguala_nombres` tem **três cores** — `#000000` (275 px),
  `#FFFFFF` (306 px) e `#76B6FF`, que é a cor transparente. Todo pixel
  desenhado é preto ou branco puro, logo já é cinza, logo a conversão não muda
  nada. **0 px, e é o resultado correto da regra da LCL**;
- o Win32 não faz grayscale: o `comctl32` monta o glifo desabilitado de uma
  máscara monocromática. Medido no recorte do oráculo — preto vira `#A6A6A6`
  (275 px) e 123 px brancos viram fundo, o que dá exatamente os 518.

As **duas hipóteses** que a CORR-WTE-057 tinha levantado estão **refutadas**,
cada uma por uma medição isolada num harness LCL de 90×40 px:

| variável trocada | mudança ao desabilitar |
|---|---|
| nada (como está hoje) | 0 px |
| `ParentFont := True` | 0 px — a fonte não é a causa; o botão não tem `Caption` |
| glifo recolorido para fundo `C0C0C0` | 257 px — muda porque isso torna os 394 px de `#76B6FF` **opacos**, não porque a cor transparente importe |
| vizinho recolorido para fundo `FFB676` | 513 px — continua acinzentando, o que sozinho derruba a hipótese da cor |

**A prova de que a regra é o grayscale, e não outra coisa:** o
`boton_nombres2iso` tem **280 pixels não-cinza** no glifo, e muda **280 px** no
`compara_tela.sh --habilitacao` do app rodando. O mesmo número dos dois lados.

O conjunto é fechado e tem conferidor:
[`check_glifos_disabled.py`](../../tools/check_glifos_disabled.py) varre os 59
botões com glifo dos 18 formulários e acha **5** invariantes — `iguala_nombres`,
`parriba` e `pabajo` no `MainForm`, `oscurecer` e `aclarar` no `color`. Entrar
ou sair desse conjunto derruba o `make -C wte check`.

Registrado como **divergência deliberada** na
[WTE-TASK-35](../../../docs/tasks/35-divergencias-deliberadas.md): é limitação
de plataforma, atinge cinco botões, e o estado lógico está certo nos dois lados
— o que difere é só o desenho.

Pascal em
[`../../src/impl/ep2002_mainform.iguala_nombresClick.inc`](../../src/impl/ep2002_mainform.iguala_nombresClick.inc).
