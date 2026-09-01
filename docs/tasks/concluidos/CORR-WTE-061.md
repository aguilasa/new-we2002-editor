---
id: CORR-WTE-061
title: "Correção: o `MaxLength` de `edit_nombre1` é o literal 5, lido da tela, sem lastro no formato"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-061: um limite que só a tela sustenta

## Problema identificado

O `MainForm.FormShow` do port faz:

```pascal
edit_nombre1.MaxLength := 5;
edit_nombre2.MaxLength := SizeOf(Jogo.teams[0].mixed_case_name) - 1;
```

**As duas linhas não têm o mesmo lastro.** A segunda sai da camada de dados e o
[`dump_truncamento.py`](../../../wte/tools/dump_truncamento.py) confere a cada
`make check`. A primeira é **um literal**, e o único apoio dele é uma leitura de
tela: o oráculo mostra `ABC.D` quando se digita `AB-C.D E`.

A leitura está certa — foi ela que achou a divergência que a passagem anterior
tinha introduzido. O que falta é o **porquê**: o original calcula
`[0x00433a10] div 2`, logo aquela global vale 10, e **qual campo do formato tem
10 bytes não foi medido**. Enquanto isso, o 5 é número mágico: sobrevive por
coincidência de medição, e nada avisa se o campo mudar.

## Evidência

O que o gerador emite hoje, e ele já se declara:

```
$ cut -f2,3,5,6 wte/re/truncamento.tsv | head -3
campo	maxlength	expressao	destino
edit_nombre1	5	[0x00433a10] div 2	
edit_nombre2	19	[0x00433b48] - 1	mixed_case_name
```

A coluna `destino` do `edit_nombre1` sai **vazia**, e a `nota` da mesma linha
diz por quê: *"valor medido na tela (compara_tela.sh --nomes, 2026-08-18); o
destino no formato continua **nao medido**"*.

A tentativa anterior e por que ela passou:

```
DESTINOS["edit_nombre1"] = ("wte/src/we2002_team.pas", "raw_kanji_name")
# 40 bytes, div 2 = 20 -- a conferencia PASSOU, e a tela diz 5
```

A conferência do gerador compara a **aritmética** contra o destino que a tabela
`DESTINOS` declara, e a tabela é escrita à mão. Ela não prova o mapeamento — e
foi exatamente assim que 20 entrou no port.

## Causa raiz

`0x00433a10` é `.bss`, e **nenhum `mov` direto a escreve**. Ela é lida como base
de uma tabela de 312 bytes por linha (`lea ecx,[eax*8+0x433a10]` em
`0x00403cf4`), e o `0x0040cc2b` lê a **coluna 0 da linha 0** dela. A origem é a
tabela de offsets em `0x004231a0`, que o `0x0040db76` copia — os dois endereços
aparecem lado a lado, um em `[ebp-0xd0]` e o outro em `[ebp-0xcc]`.

Ou seja: o número existe no formato e o caminho até ele está mapeado. O que não
foi feito é percorrê-lo.

## Correção

1. ler o `0x0040cbc8` — a rotina que preenche a tabela de `0x00433a10` a partir
   de `0x004231a0` — e descobrir **o que é a coluna 0**. Se for comprimento de
   campo, o `dump_offsets.py` já tem a linha 0 e o número sai de lá;
2. com o destino nomeado, devolver `DESTINOS["edit_nombre1"]` ao gerador e
   deixar a conferência voltar a valer — **e conferir que o resultado é 5**, não
   escolher o campo que dê 5;
3. trocar o literal do `FormShow` pela mesma expressão da linha vizinha.

Se a leitura mostrar que a coluna 0 **não** é largura de campo, o resultado é
que a expressão do original não é derivável do formato, e o literal 5 fica —
mas com a razão escrita. **Também fecha.**

### Arquivos

- [`wte/tools/dump_truncamento.py`](../../../wte/tools/dump_truncamento.py) — a
  tabela `DESTINOS` e o `MEDIDO_NA_TELA`
- [`wte/src/impl/ep2002_mainform.FormShow.inc`](../../../wte/src/impl/ep2002_mainform.FormShow.inc)

---

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-18

**Resumo do que foi feito:**

A pergunta da correção — *o que é a coluna 0* — está respondida, e a resposta
mudou mais do que o campo que a motivou.

**A "coluna 0" não é o número que o port usa.** `lista_equiposChange` chama
`0x0040cbc8`, que percorre a tabela de lotes de `0x004231a0` (3×6 offsets, 11
não-zero, e **as 11 são `OFS_*` que o `we2002_core` já conhecia**) e, para cada
lote, **anda pelo arquivo** até o registro do time selecionado, pulando o
rodapé de cada setor MODE2/2352. Grava três campos por lote em `0x00433a0c`:

```text
+0  o offset do registro          <- a "coluna 0" da correção
+4  a LARGURA dele, em bytes      <- o que o port lê
+8  os bytes
```

Passo 312 por linha e 52 por coluna, lidos do `lea ecx,[eax*8+0x433a0c]` com
`eax = linha*39`. Logo `[0x00433a10]` é a largura de `[0][0]` e `[0x00433b48]`
a de `[1][0]`, 312 bytes adiante. **Nenhuma das duas é constante.**

**O achado maior não era o campo da correção, era o vizinho.**
`DESTINOS["edit_nombre2"]` declarava `mixed_case_name` (20 → 19). O lote
`[1][0]` é `OFS_TEAM_NAME_3`, que o `Load` do core lê em `names[2]` com
`TEAM_NAME_LEN_3`; para o time 2 dá 8, logo **7**, não 19. O `mixed_case_name`
é `[0][1]`, outro lote. Emulada a travessia sobre a imagem japonesa, a largura
bate com a tabela do core em **95/95** times.

Isso foi **confirmado na tela**, e é a parte que fecha: com `A B-C.DEFG` os dois
lados mostram `A BC.DE`, sete caracteres. Antes o port mostrava nove.

**O primeiro campo não fechou, e por um.** Mesmo modelo, mesmo gerador: o lote
está provado (`OFS_TEAM_NAME_KANJI`) e a travessia dá largura 12 para o time 2,
logo `div 2` = 6 — e o oráculo corta em **5**. Segui a instrução da correção ao
pé da letra (*conferir que o resultado é 5, não escolher o campo que dê 5*): a
conferência **falhou**, então o literal fica, agora com o lote nomeado e a
discordância medida. Está aberta como
[CORR-WTE-064](/docs/tasks/concluidos/CORR-WTE-064.md), com cinco hipóteses já
descartadas.

**A régua de tela media tinta, não truncamento — e foi ela que produziu o 5.**
O texto era `AB-C.D E`, e o corte do `edit_nombre1` caía exatamente num
**espaço**: `ABC.D ` e `ABC.D` são o mesmo desenho. Trocado por `A B-C.DEFG`,
cujos três cortes caem em glifo visível e em posições diferentes. A conta de
disparos, que era o literal `10/10/9`, passou a sair de `${#NOMES_TEXTO}` —
quando o texto mudou, os literais derrubaram a corrida por um motivo que não
tinha nada a ver com o que estava sendo medido.

**Problemas encontrados:**

Três guardas do repositório dispararam depois das edições de Pascal, e as três
estavam certas:

1. **`dfm2lfm.py --check`** — eu tinha acrescentado `we2002_tables` ao `uses` de
   `ep2002_mainform.pas`, que é **gerado**. A entrada certa é
   `wte/src/impl/ep2002_mainform.uses`, e o `.pas` foi revertido e regerado.
   A regra pegou exatamente o que ela existe para pegar;
2. **`check_fase2.py`** — a fração de Pascal gerado da §4.4 do plano mudou
   (75,4% → **74,9%**, 9.188 geradas contra 3.072 à mão). Número de ferramenta,
   não somado à mão;
3. **`check_edicao.py`** — o `edicao-cobertura.md` saiu de dia. Regerado.

**Arquivos criados/modificados:**

- `wte/tools/dump_truncamento.py` — o modelo trocou: `DESTINOS` deixa de ser
  largura de struct e passa a ser (`OFS_*` do lote, tabela de comprimento), e o
  gerador **decodifica** o operando até a entrada de `0x004231a0` para provar o
  mapeamento. Mais `POR_TIME`, `TIME_DE_REFERENCIA` e `CONTRADIZ_A_TELA`
- `wte/tools/test_dump_truncamento.py` — 5 testes novos (19 no total): o lote
  provado, lote declarado errado, operando fora de um `+4`, operando num buraco
  da tabela, forma incompatível com o lote, e a exceção de tela sobrevivendo ao
  motivo dela
- `wte/tools/compara_tela.sh` — `NOMES_TEXTO`, e a conta de disparos derivada
- `wte/src/impl/ep2002_mainform.aux.inc` — `TAMANHO_DO_NOME` (que era 20 e
  estava errado) sai; entram `IndiceNaTabela`, `LimiteDoNome1`, `LimiteDoNome2`
- `wte/src/impl/ep2002_mainform.lista_equiposChange.inc` — os dois `MaxLength`
  passam a ser postos aqui, que é onde o original os põe
- `wte/src/impl/ep2002_mainform.FormShow.inc` — as duas linhas saem
- `wte/src/impl/ep2002_mainform.iguala_nombresClick.inc` — o truncamento passa
  a usar `LimiteDoNome2`
- `wte/src/impl/ep2002_mainform.uses`, `wte/src/ep2002_mainform.pas` (regerado)
- `wte/re/truncamento.{md,tsv}`, `wte/re/fase-2.md`, `wte/re/edicao-cobertura.md`,
  `wte/re/edicao-tela.tsv{,.nomes}` — regerados
- `wte/re/spec/MainForm.iguala_nombresClick.md` — o limite medido no lugar da
  inferência
- `docs/PLAN-WTE-LAZARUS.md` §4.4 — a fração remedida
- `docs/tasks/concluidos/26-handlers-de-edicao.md` — a pendência encaminhada, fechada
- `docs/tasks/concluidos/CORR-WTE-064.md` — **nova**
