---
handler: boton_barras2isoClick
formulario: MainForm
endereco: 0x0040cab8
veredito: implementado
---

# MainForm.boton_barras2isoClick

Grava na imagem as cinco barras do time selecionado. 272 bytes, do
`0x0040cab8` ao `0x0040cbc7` — o menor handler do grupo de gravação, e o
único cujo corpo cabe inteiro numa leitura.

## Entrada

Duas fontes, e a segunda é a que importa:

- `lista_equipos.ItemIndex` — o índice do time, lido pelo mesmo par
  (`[this+0x2f0]`, VMT+0xc8) que todo o resto do formulário usa;
- **o buffer de edição das barras**, `0x00434592`, cinco bytes. Não é a
  imagem e não é o modelo: é o buffer que a carga enche
  (`lista_equiposChange`, `0x0040cf79`) e que o `track_barraChange`
  (`0x0040caa1`) grava. Medido na WTE-TASK-26.

Não lê a imagem em ponto nenhum.

**Evidência:** disassembly lido

## Saída

Cinco bytes na imagem, do buffer de edição, na ordem
`ataque, defesa, força, velocidade, técnica` — a mesma em que a carga os leu.

Depois, `ficha_info3` (`0x00432e40`) recebe no rótulo `etiq1` a cadeia
`Barras inseridas no jogo!!!     ` (`0x00424d6f`, com os cinco espaços) e é
exibido modal. É a caixa `W11 TE PT!`, 276×81 de cliente.

Não mexe em mais nada da tela: as larguras já estavam desenhadas pelo
`track_barraChange`.

**Evidência:** disassembly lido

## Bytes tocados

`OFS_TEAM_BARS + 5·idx` na aritmética do formato, **5 bytes**, para
`idx` em `0..94`. Para `idx = 0`:

```
0x23BA78 +5  as cinco barras do time 0
```

O original não usa `OFS_TEAM_BARS`. Ele calcula, e o cálculo é o próprio
layout MODE2/2352 escrito à mão:

```text
logico  = 0x45FF0 + 5 * idx          indice de byte no fluxo de dados de
                                     usuario, contado a partir do setor 850
setor   = logico div 2048            (com o ajuste de sinal do compilador)
resto   = logico mod 2048
arquivo = 0x1E8178 + setor * 2352 + resto
```

`0x1E8178` = 1999224 = `850 * 2352 + 24`, o primeiro byte de dados do setor
850. `0x45FF0` = 286704 põe o time 0 em 2328184, que é `OFS_TEAM_BARS`.

**A aritmética foi conferida contra o `we2002_core`, que chega ao mesmo
lugar por outro caminho.** O core lê sequencialmente e **salta** na fronteira
de setor: 1 byte do time 3 em 2328199, e os outros quatro em
`OFS_TEAM_BARS_A` = 2328504. A fórmula do Obocaman devolve 2328199 para
`idx = 3` e 2328508 para `idx = 4` — os mesmos endereços, sem tabela de
salto. Duas fontes independentes, mesmo resultado.

**Evidência:** diff medido

## Pré-condições

**Nenhuma dentro do handler.** Ele não valida índice, não checa se há imagem
aberta e não checa se alguma barra foi editada.

Quem impede o caso ruim é o formulário: `boton_barras2iso` nasce
`Enabled = False` no DFM e só é habilitado pelo `lista_equiposChange`, com
`ItemIndex < 95`. Então `idx` só chega aqui em `0..94`, e `idx = -1` — que
gravaria 5 bytes **antes** do bloco, em 2328179 — é inalcançável por clique.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Sem imagem aberta o `FILE*` global (`0x00432e58`) é nulo e o
`fseek` seguinte é indefinido; o botão desabilitado é o que impede.

**Evidência:** disassembly lido

## Notas

**O clique não grava — quem grava é o `fseek` seguinte.** Os cinco bytes vão
para a saída bufferizada do runtime C e só chegam ao arquivo quando algo
depois procura noutro ponto do mesmo arquivo. Medido em
[`../gravacao-controle.md`](../gravacao-controle.md) com um par de sondas de
uma variável de diferença: sem descarga, **zero** byte no arquivo.

Isso não é detalhe de harness — é o que faz o `09-areas-com-time` ter
registrado, desde 2026-08-10, que este handler "não grava nada".

**O port também atualiza `Jogo.teams[].bar_*`, e o original não precisa.**
Os dois gravam os mesmos cinco bytes no mesmo lugar; a diferença é de
arquitetura, não de saída. O `wte.exe` relê a imagem a cada troca de time
(faixas de leitura em 2328060..2328695 na marca `SELECIONA_TIME`), então o
disco é a fonte dele. O port carrega uma vez, no `AbreImagem`, e desenha a
partir de `Jogo`: gravar só no disco faria a tela do próprio port discordar
do próprio arquivo na volta ao time. Não aparece no golden — é o mesmo byte
no mesmo offset.

**A régua desta task é o byte, e ela fechou nos dois sentidos.** Duas
corridas do `golden_check.sh`, com o par de roteiros de cada uma:

| roteiro | o que mede | resultado |
|---|---|---|
| `golden-03-barras` | gravar **sem editar** | passou — **byte-idêntico** (2026-08-20) |
| `golden-04-barras-editada` | editar pela tela e **então** gravar | passou — **byte-idêntico** (2026-08-20) |

As duas corridas são de 2026-08-20, com o **controle** (oráculo contra oráculo,
sobre a `golden-03`) fechando byte-idêntico antes — sem ele, zero divergência
também seria o que se veria se nenhum dos dois lados gravasse.

Até 2026-08-20 esta linha dizia *"só as duas faixas do arranque"*: o
oráculo gravava os dois remendos de arranque e o port não. A oitava
passagem da WTE-TASK-27 portou os dois (`PatchDeVinculoDeArranque`,
`PatchDeByteSoltoDeArranque`) e tirou as declarações `conhecida:` dos
roteiros; desde então o gate não tem faixa nenhuma para declarar.

A segunda é a que julga. Sem ela o gate não distingue "gravou certo" de "não
gravou": sem edição os dois lados escrevem os bytes que já estavam lá, e um
port que não gravasse nada passaria igual. Medido no lado oráculo da
`golden-04`: a gravação vai para 2328194 (o time 2, `OFS_TEAM_BARS + 10`) e
`bar_defence` muda de `0x04` para `0x06` — o `+2` de um clique na trilha, que
o `compara_tela.sh` já tinha medido nos dois widgetsets. O port produziu o
mesmo arquivo.

É o critério que a WTE-TASK-26 passou para cá em 2026-08-12: edição e gravação
julgadas juntas, porque pixel igual dos dois lados não prova que os dois
escreveram o mesmo byte do modelo.

O Pascal está em
[`../../src/impl/ep2002_mainform.boton_barras2isoClick.inc`](../../src/impl/ep2002_mainform.boton_barras2isoClick.inc).
