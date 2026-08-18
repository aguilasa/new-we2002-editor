---
id: CORR-WTE-062
title: "Correção: o `lista_formacionesClick` ficou entre duas tasks concluídas e continua `REStub`"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-062: o handler que as duas tasks apontaram uma para a outra

## Problema identificado

`estrategia.lista_formacionesClick` (`0x00409aa0`) pertence ao grupo **carga**,
da [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md). A spec dele fecha assim:

> **Veredito `aberto`, com dono nomeado:** o efeito está nas duas rotinas não
> lidas, e o que elas fazem é editar tática — que é a WTE-TASK-26.

A [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) fechou **sem portá-lo**, e
com razão: ele não está entre os 28 handlers dela — o grupo dele é `carga`. As
duas tasks estão `✅ Concluído`, e o corpo continua `REStub`.

**Não é só um handler parado.** Dois handlers da 26 ficaram `aberto` por
dependerem dele: é o `lista_formacionesClick` que preenche o vetor bola→zona
(`0x00434230`) e as seis tabelas da animação. Enquanto ele não existir:

- o `bolaMouseDown` desenha o retângulo **sempre da zona 0**, porque o vetor
  nasce zerado;
- o `relojTimer` **nunca roda**, porque ninguém habilita o `reloj`;
- os handlers de arrastar precisam de uma guarda de `nil` que o original não
  tem, porque é o `relojTimer` que semeia os dois globais.

É o padrão que este projeto já pagou e escreveu no enunciado da 25: **exclusão
sem dono nomeado é buraco.** Aqui o dono foi nomeado — e nomeado errado.

## Evidência

```
$ awk -F'\t' '$2=="lista_formacionesClick"{print $1"\t"$3"\t"$6}' \
    wte/re/published_methods.tsv
0x00409aa0	estrategia	carga

$ sed -n '212,215p' wte/src/ep2002_estrategia.pas
procedure Testrategia.lista_formacionesClick(Sender: TObject);
begin
  REStub('estrategia.lista_formacionesClick');
end;

$ grep -E 'WTE-TASK-2[56]\]' docs/tasks/progresso.md | cut -d'|' -f2,6,7
 [WTE-TASK-25](/docs/tasks/25-handlers-de-carga.md) | ✅ Concluído | 2026-08-11
 [WTE-TASK-26](/docs/tasks/26-handlers-de-edicao.md) | ✅ Concluído | 2026-08-18
```

E as duas auxiliares que a spec chama de "não lidas" já estão inventariadas:

```
$ grep -E "^0x0040(97d4|99bc)" wte/re/auxiliares.tsv | cut -f1,3,4
0x004097d4	474	estrategia.lista_formacionesClick,0x0040a0b4
0x004099bc	227	estrategia.lista_formacionesClick,0x0040a0b4
```

## Causa raiz

A spec da 25 encaminhou pelo **efeito** ("o que elas fazem é editar tática") e
não pelo **grupo**. A 26 seleciona os handlers dela pela coluna `grupo` do
`published_methods.tsv`, que diz `carga` — então o encaminhamento nunca teve
como ser recebido. Nenhuma das duas tasks tinha como notar: a 25 fechou antes de
a 26 existir em detalhe, e a 26 conferiu a própria lista, que estava certa.

## Correção

Portar o `lista_formacionesClick`, com as duas auxiliares (`0x004097d4`, 474 B e
`0x004099bc`, 227 B — as duas já com tamanho medido).

**Onde ela mora não é óbvio, e a escolha tem de ser escrita:** o handler é da
25, o efeito é da 26, e as duas estão fechadas. Executar esta correção é a
terceira opção, e é a que não reabre task nenhuma — mas o Log dela precisa dizer
qual spec foi atualizada e por quê.

Ao fechar, três vereditos mudam de estado e **têm de ser revistos na mesma
passagem**: o `estrategia.lista_formacionesClick`, o `estrategia.bolaMouseDown` e
o `estrategia.relojTimer`. Se os três não forem tocados, a correção deixou
metade do efeito para trás.

### Arquivos

- [`wte/src/impl/`](../../wte/src/impl/) — o `.inc` novo e o estado no `.aux.inc`
- [`wte/re/spec/estrategia.lista_formacionesClick.md`](../../wte/re/spec/estrategia.lista_formacionesClick.md)
- as specs do `bolaMouseDown` e do `relojTimer`

---

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-18

**Resumo do que foi feito:**

Portado, com as duas auxiliares — e a leitura desmentiu a spec em quatro
pontos, três deles em specs de **outros** handlers.

**Onde a correção mora:** a spec do `lista_formacionesClick` foi reescrita, e as
do `bolaMouseDown` e do `relojTimer` tiveram a razão do veredito trocada. A
escolha era entre reabrir a 25, reabrir a 26 ou fechar aqui; fechei aqui, que é
a única que não reabre task nenhuma, e a spec do handler agora diz de quem é
cada metade.

**O corpo não é "quase só encaminhamento".** Ele aponta **quatro** ponteiros
globais para dentro de um registro e tem **dois ramos** — `ItemIndex = 1`
(`DEFAULT`) não usa a tabela, lê o buffer da formação viva do time.

**O `0x00434230` não é um vetor, é um ponteiro.** A spec do `bolaMouseDown`
dizia que o handler *preenchia* um vetor; ele aponta para os 11 bytes de zona
do registro escolhido, dentro de uma tabela de 18 × 44 em `0x00433f0c` que o
`estrategia.FormCreate` monta a partir de quatro blobs de `.data`.

**Foi preciso um gerador, e não transcrição.** São **792 números**
interleavados — papel em `reg+0x00`, x em `+0x0b`, y em `+0x16`, zona em
`+0x21` —, e trocar X por Y a olho não faria nada reclamar. O
`dump_formacoes.py` é irmão do `dump_zonas.py`, com **cinco** conferências, e
a mais forte não é de faixa:

> **O nome do item diz a contagem.** `4 - 5 - 1  A` tem de ter quatro
> defensores, cinco de meio e um atacante entre os jogadores 1..10. O texto vem
> do `.lfm` e os papéis vêm de `.data`. É a única conferência que pega ordem de
> registro trocada ou coluna lida errada — as faixas das quatro colunas se
> sobrepõem o bastante para que nenhuma das outras notasse. Passa nas 16
> formações nomeadas.

**Uma conferência é vácua sobre o dado, e isso está escrito em vez de
escondido.** A da grade do arrasto (`x*8 − 2` ≡ 6 mod 8, e a grade tem passo 8
fase 5 com raio 7) vale para **qualquer** byte: nenhum dado a derruba. O que
ela confere é a coincidência entre duas leituras independentes — o `8`/`−2`
saiu de `0x004097d4` e o `8`/`5`/`7` do `rectanguloDragOver` —, e o teste a
exercita mexendo na constante, não no dado. Chamá-la de conferência da tabela
seria mentira.

**O registro 1 é um buraco, e o dado prova o ramo.** As quatro colunas dele são
zero — porque `ItemIndex = 1` desvia para o buffer vivo e nunca o lê. A isenção
que ele ganha na conferência de campo tem guarda própria: se deixar de ser
zero, o gerador aborta.

**O `0.2` muda a leitura do encaixe.** É um `long double` de 80 bits em
`0x004099b0`, decodificado e não escrito à mão. Com os quatro quadros do
`relojTimer` a interpolação cobre **80%** do trajeto e o encaixe dá o último
quinto de uma vez — o `.inc` dizia "um pixel fora, sempre no mesmo sentido", e
foi corrigido.

**Verificado na tela**, e não só compilado. No `:99`, sobre cópia da imagem
japonesa: as onze bolas assumem a formação, e os dez `etiqposN` ganham texto e
cor. A cor foi medida por pixel em **três** formações e bateu com a tabela nas
três:

| formação | esperado | medido |
|---|---|---|
| `4 - 5 - 1` | `CCCCGGGGGR` | `CCCCGGGGGR` |
| `4 - 3 - 3  A` | `CCCCGGGRRR` | `CCCCGGGRRR` |

O `trace.log` registra `lista_formacionesClick` a cada clique e
`relojTimer` **cinco** vezes por aplicação — quatro quadros mais o encaixe,
que é o que `QUADROS_DA_ANIMACAO = 4` prevê.

O primeiro padrão medido pareceu bug — um rótulo verde onde a tabela pedia
vermelho. Não era: eu tinha clicado na linha errada da lista, e o padrão medido
era exatamente o de um `4 - 5 - 1`. **A tabela gerada foi o que permitiu
descobrir isso**, comparando o padrão com as 18 linhas em vez de com a
expectativa.

**Problemas encontrados:**

O `golden_check.sh` **não se aplica**, e isso agora está medido em vez de
delegado: as três rotinas não abrem arquivo — só alcançam `FindComponent`,
`CurrToStr`, `TTimer::SetEnabled`, `TFont::SetColor`, `TControl::SetText` e
helpers de `AnsiString`/`Currency`. A spec dizia "bytes tocados: não medido,
pergunte à WTE-TASK-27"; a resposta é **nenhum byte**.

O `compara_tela.sh` também não alcança: os três modos dele partem da janela do
`MainForm`, e o `estrategia` é sub-diálogo. A verificação acima foi dirigida à
mão, e está descrita para poder ser repetida.

**O que ficou de fora, com dono nomeado:** o item `DEFAULT` não faz nada no
port. Ele precisa do buffer da formação viva do time (`0x00432e88`), preenchido
por `0x0040a0b4` — a rotina que enche a tela de tática ao abrir o formulário,
chamada pelo `MainForm.mostrar_estrategiaClick`, do grupo de **carga**, e não
portada. Aplicar o registro zerado poria as dez bolas em `(−2, −12)`, fora do
campo, o que é pior do que não fazer nada. A **mesma** rotina causa a segunda
divergência, e é a que se vê primeiro: no original a tela de tática já abre com
a formação do time aplicada e a animação rodada uma vez. As duas caem juntas
quando `0x0040a0b4` for portada.

**Arquivos criados/modificados:**

- `wte/tools/dump_formacoes.py` — **novo**; extrai os quatro blobs e o `0.2`,
  emite `wte/re/formacoes.{md,tsv}` e `wte/src/wte_formacoes.pas`
- `wte/tools/test_dump_formacoes.py` — **novo**; 18 testes, todas as guardas
  exercitadas com dado plantado
- `wte/re/formacoes.md`, `wte/re/formacoes.tsv`, `wte/src/wte_formacoes.pas` —
  **novos**, gerados
- `wte/src/impl/ep2002_estrategia.lista_formacionesClick.inc` — **novo**
- `wte/src/impl/ep2002_estrategia.aux.inc` — `PreparaAnimacao`,
  `PintaPosicoes`, `ZonaDaBola` (agora função), `FormacaoAplicada` e as
  constantes de cor
- `wte/src/impl/ep2002_estrategia.bolaMouseDown.inc` — a zona sai da função
- `wte/src/impl/ep2002_estrategia.relojTimer.inc` — o comentário do encaixe
- `wte/src/impl/ep2002_estrategia.uses`, `wte/src/ep2002_estrategia.pas`
  (regerado — o stub saiu)
- `wte/re/spec/estrategia.lista_formacionesClick.md` — reescrita, veredito
  `aberto` → `implementado`
- `wte/re/spec/estrategia.bolaMouseDown.md`, `.relojTimer.md` — a razão do
  veredito trocada; os dois continuam `aberto`, agora por `0x0040a0b4`
- `wte/re/spec/INDICE.md`, `wte/re/fase-2.md` — regerados
- `docs/PLAN-WTE-LAZARUS.md` §4.4 — a fração remedida (74,9% → 74,1%)
- `docs/tasks/26-handlers-de-edicao.md` — a pendência encaminhada, fechada
