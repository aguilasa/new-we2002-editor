---
handler: BitBtn3Click
formulario: estrategia
endereco: 0x0040a660
veredito: aberto
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

Duas regiões de 2 bytes por time para as cores de radar, com base
`0x3F534`/`0x3F634` mais o deslocamento de setor, e a região da tática. Os
tamanhos exatos da tática saem da segunda metade do corpo, que esta spec não
percorreu instrução a instrução.

**Evidência:** não medido

## Pré-condições

As três do bloco 1: par de cores em uso, cores iguais, e a confirmação do
`ficha_warning_2` no primeiro caso.

**Evidência:** disassembly lido

## Comportamento de erro

Cores iguais é recusa dura, com foco devolvido. Par de cores já usado é aviso
com pergunta. Fora isso, não trata.

**Evidência:** disassembly lido

## Justificativa do veredito `aberto`

**É a oitava rota de escrita na imagem**, e a que grava a tática — o dado que a
[`wte_formacoes`](../../src/wte_formacoes.pas) e a
[`wte_zonas`](../../src/wte_zonas.pas) descrevem e que nenhum handler do port
grava hoje. Ela precisa da mesma régua das outras: golden com controle, nas
duas ROMs.

**Dono: [CORR-WTE-081](../../../docs/tasks/CORR-WTE-081.md)**, que a põe por **último** das três, justamente pelo
pré-requisito abaixo.

E precisa de mais uma coisa que não existe: **a tela de tática do port não é
enchida** — a `0x0040A0B4` continua sem port, como a
[`estrategia.BitBtn1Click`](estrategia.BitBtn1Click.md) registra. Gravar as
posições dos componentes de uma tela que ninguém posicionou gravaria as
coordenadas de tempo de projeto do `.lfm`. A ordem certa é encher primeiro.

**O pré-requisito virou correção própria em 2026-08-21:** a
[CORR-WTE-082](../../../docs/tasks/CORR-WTE-082.md), aberta quando a
CORR-WTE-081 chegou aqui e mediu os dois buracos. O primeiro é a leitora, 1.443
bytes com dois chamadores `aberto`; o segundo é esta spec, cuja seção *Bytes
tocados* ainda diz `não medido`. Os dois têm de fechar antes deste handler.

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
