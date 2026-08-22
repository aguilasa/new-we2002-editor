---
handler: BitBtn3Click
formulario: estrategia
endereco: 0x0040a660
veredito: implementado
---

# estrategia.BitBtn3Click

O ` Accept` da tela de tática — no componente chamado `BitBtn6`. 1.931 bytes, o
maior handler que sobrou dos 96, e **grava na imagem**.

**Evidência:** disassembly lido

## Entrada

- os dois combos de cor do radar, campos `+0x43C` e `+0x440`, que o
  [`campos.tsv`](../campos.tsv) nomeia;
- uma tabela de 20 palavras copiada de `0x00423F14` para a pilha logo no
  prólogo (`rep movs`, `ecx = 0x14`);
- as posições dos componentes `bola`, `tirador` e `simbolo`, achados por
  `FindComponent` com o índice no nome;
- a global do time em edição (`0x004335CC`) e o `_estrategia`
  (`0x00433E50`).

**Evidência:** disassembly lido

## Saída

Três blocos:

1. **Validação das cores do radar.** Percorre dez pares da tabela da pilha; se
   o par escolhido casar com um deles, abre o `ficha_warning_2` e desiste se a
   resposta não for `6` (`mrYes`). Se as duas cores forem **iguais**, põe
   `You should use different Home && Away radar colours...` no `ficha_error2`,
   mostra, devolve o foco ao primeiro combo e sai.
2. **As duas cores de radar, gravadas.** Duas chamadas à `0x00403400` de dois
   bytes cada. O offset é um endereço de *payload* — `time * 2 + 0x3F534` para
   a primeira cor, `0x3F634` para a segunda — convertido em endereço de setor
   ali mesmo:

   ```text
   payload := time * 2 + base          ' base = 0x3F534 ou 0x3F634
   destino := (payload div 2048) * 304 + payload + 0x1E8178
   ```

   Os 304 saem de `lea/lea/shl` sobre o quociente (`x*9`, depois `x*2+x`,
   depois `shl 4` — 19 × 16), e o arredondamento negativo tem a correção
   `+0x7FF` antes do `sar`, que o compilador emite para divisão com sinal.
3. **As posições, lidas da tela.** Para cada um dos dez jogadores e para os
   três grupos de componente, `(Left - Left_do_campo + 2) div 8` e o mesmo para
   `Top`, e o resultado vai byte a byte para um buffer local — a conversão de
   pixel para célula da malha.

O terceiro bloco alimenta as escritas restantes do handler.

**Evidência:** disassembly lido

## Bytes tocados

**Cinco regiões, 45 bytes por time.** Todas endereçadas em índice lógico sobre
o setor 850 — o `0x1E8178` que o handler soma em forma fechada —, e todas com o
salto de 304 quando o índice cruza os 2048 de payload:

| região | índice lógico | bytes | como |
|---|---:|---:|---|
| cor de radar 1 | `2*t + 0x3F534` | 2 | `0x00403400` |
| cor de radar 2 | `2*t + 0x3F634` | 2 | `0x00403400` |
| formação | `30*t + 2*(t div 95) + 0x40C2C` | 30 | `fseek`/`fputc` crus |
| cobrador | `6*t + 2*(t div 95) + 0x46228` | 6 | idem |
| tática | `5*t + 0x408A8` | 5 | idem |

**Os 30 bytes da formação saem de TRÊS laços de dez**, não de um de trinta:
`0x0040ABA8`, `0x0040ABF0` e `0x0040AC36`. O primeiro copia de um buffer
apontado por `[0x00434224]`, a partir do índice **1** — o elemento zero fica de
fora —, e os outros dois de dois buffers locais que o bloco 3 encheu com as
posições convertidas em célula. Dez jogadores, três bytes cada, intercalados
por linha e não por jogador.

**Os três últimos NÃO passam pela `0x00403400`.** Eles chamam `fseek` e `fputc`
da RTL diretamente, um byte por vez, e resolvem a fronteira de setor à mão:
antes de cada `fputc` comparam o índice corrente com `0x800` e, se bateu, dão
`fseek(+0x130, SEEK_CUR)`. É a mesma geometria da `0x00403388`, com o teste
escrito no laço em vez de dentro de uma rotina. Um port que procurasse a
escritora comum aqui não a encontraria — e é a segunda vez que este handler
mistura os dois caminhos, como a nota do fim já registrava para o cálculo de
endereço.

**Duas das cinco bases têm nome no `we2002_core`, e elas fecham a conferência:**
para o time 0, a formação dá **2303700** = `OFS_FORMATIONS`, e o cobrador dá
**2329056** = `OFS_KICKER`. As outras três não têm nome — as duas de radar são
da v0.99 e a de tática nunca foi batizada —, mas as três constantes já estavam
versionadas no `.aux.inc` do `MainForm` desde a WTE-TASK-25
(`FORMACAO_LOGICO_BASE`, `TATICA_LOGICO_BASE`, `COBRADOR_LOGICO_BASE`, com
`30`, `5` e `6` de passo), medidas por outro caminho e batendo uma a uma.

A faixa lida é `0x0040A7C0`..`0x0040ADCD`, e as duas âncoras foram conferidas
contra o `wte/src/we2002_offsets.pas`.

**Evidência:** disassembly lido

## Pré-condições

As três do bloco 1: par de cores em uso, cores iguais, e a confirmação do
`ficha_warning_2` no primeiro caso.

**Evidência:** disassembly lido

## Comportamento de erro

Cores iguais é recusa dura, com foco devolvido. Par de cores já usado é aviso
com pergunta. Fora isso, não trata.

**Evidência:** disassembly lido

## Como o veredito fechou

Fechou pela [CORR-WTE-081](../../../docs/tasks/CORR-WTE-081.md), terceira e
última das três gravações órfãs, com o par
[`golden-17-tatica`](../../tests/roteiros/golden-17-tatica.txt) nos três modos
do [`golden_check.sh`](../../tools/golden_check.sh): `controle` byte-idêntico,
`positivo` detectando o byte plantado em 405228, `golden` byte-idêntico.

**Ele dependia de uma correção inteira, e ela veio antes.** A tela de tática do
port não era enchida — a `0x0040A0B4` não tinha port —, e ler a posição de
componentes que ninguém posicionou gravaria as coordenadas de tempo de projeto
do `.lfm`. A [CORR-WTE-082](../../../docs/tasks/CORR-WTE-082.md) portou a
leitora e mediu a metade de tática desta spec, que dizia `não medido`.

**A edição do roteiro é o clique na `malla1` que o `compara_tela.sh --malha` já
media**, e a escolha tem um motivo negativo: clicar na lista de formações — que
seria a edição mais visível — não serve, porque a altura de linha do `TListBox`
não bate entre os dois widgetsets (~11 px sob Wine contra ~13 px no gtk2), e o
mesmo `y` cairia em itens diferentes.

**O round-trip da tela é LOSSY, e isso apareceu no gate como igualdade.** O `Y`
vai para a tela por `DestinoY = ((y - 3) div 2) * 5 - 7` e volta por
`y = ((Top - campo.Top + 7) div 5) * 2 + 3`; a divisão por dois joga fora o bit
baixo, e um `Y` ímpar volta um a menos. Medido no time 2: `32 52 72 17 87 50 30
62 42 62` na imagem viram `31 51 71 17 87 49 29 61 41 61` depois de um
` Accept` que não editou nenhuma bola — **nos dois lados**. O `X` é
sem perda (`x*8 - 2` contra `(Left + 2) div 8`).

**Os dois últimos bytes de tática não vêm da tela.** O byte 3 sai zero e o byte
4 é `cobrador[0]`: o buffer de tática do original tem quatro bytes na pilha
(`[ebp-0x58]`) e o de cobrador começa logo depois (`[ebp-0x54]`), e a gravação
pede cinco. Medido: `[1, 14, 148, 56, 82]` na imagem vira `[1, 94, 148, 0, 7]`
nos dois lados. A carga nunca lê esses dois de volta — ela lê quatro.

## Notas

**A aritmética de setor está inline aqui, e é a mesma geometria.** Os outros
caminhos de escrita chamam a `0x00403388`, que pergunta ao `ftell` onde está e
pula 304 bytes ao cruzar a fronteira; este resolve a mesma coisa em forma
fechada — 2048 de payload por setor, 304 de cabeçalho mais EDC/ECC —, o que dá
o mesmo endereço sem depender da posição corrente do arquivo. Os dois números
são os que a [`auxiliares.md`](../auxiliares.md) já tinha decodificado do corpo
da `0x00403388`, e a conferência de lá aborta se deixarem de bater.

Vale registrar porque o caminho **incremental** e o **fechado** convivem no
mesmo binário: um port que assumisse só o primeiro procuraria uma chamada que
aqui não existe.
