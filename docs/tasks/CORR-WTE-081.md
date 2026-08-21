---
id: CORR-WTE-081
title: "Correção: três gravações na imagem sem dono — o OK do ficha_color, o Comple. do jugador e o Accept do estrategia"
type: correção
category: comportamento
status: pendente
depends_on: []
---

# CORR-WTE-081: três gravações na imagem sem dono

## Problema identificado

A [WTE-TASK-30](/docs/tasks/30-handlers-auxiliares.md) mediu os 17 handlers do
grupo `auxiliar` e achou o que o enunciado dela não previa: **três deles
escrevem na imagem de CD**, e nenhuma task do backlog os carrega.

| handler | endereço | o que grava |
|---|---|---|
| `ficha_color.BitBtn3Click` | `0x004069e8` | 383 B do bloco de cor do time, via `0x004051A4` |
| `jugador.BitBtn3Click` | `0x00408548` | o jogador (`0x00404820`) e o número de camisa (`0x00404048`) |
| `estrategia.BitBtn3Click` | `0x0040a660` | as duas cores de radar e a tática |

A [WTE-TASK-27](/docs/tasks/27-handlers-de-gravacao.md) contava **seis**
gravações e listava as duas que passaram para a 28 e a 29. Medido, são
**nove**: as seis dela mais estas três. As três ficaram com veredito `aberto`,
spec completa e justificativa escrita — implementá-las dentro de uma task cujo
escopo declarado era *"abrir, fechar, OK/Cancelar"* significaria entregar
gravação sem o gate que a fase 4 exige, e a régua de gravação é **byte**.

**Por que isso não pode ficar como está.** A
[WTE-TASK-31](/docs/tasks/31-fechamento-fase-4.md) é o fechamento da fase e o
primeiro critério dela é *"96 entradas no índice, nenhuma `aberto`"*. Ela
**não implementa nada** — o objetivo declarado é *"provar o critério, ou listar
o que falta"*. Sem dono, as três seriam listadas como falta e a fase 4 não
fecharia; com dono, a 31 volta a ser o que é.

## Evidência

Os três chamam a escritora `0x00403400`, direta ou indiretamente. Medido com o
decodificador do
[`dump_auxiliares.py`](../../wte/tools/dump_auxiliares.py) sobre o `.text`:

```text
callers de 0x004051A4 (o gravador do bloco de cor)  ->  ['0x4069f9']
```

Um chamador só, e ele está dentro do `ficha_color.BitBtn3Click`. As specs
trazem o resto:

- [`ficha_color.BitBtn3Click`](../../wte/re/spec/ficha_color.BitBtn3Click.md) —
  a `0x004051A4` é o **espelho exato** da carga `0x004050D0`, bloco por bloco,
  com a mesma global de offset em cada um; troca a `0x004033BC` (ler) pela
  `0x00403400` (gravar). São sete regiões por time: bandeira, forma, os dois
  uniformes, oito paletas de chuteira, a quarta paleta e o par de bytes de
  padrão de camisa;
- [`jugador.BitBtn3Click`](../../wte/re/spec/jugador.BitBtn3Click.md) — valida
  créditos (1…250) e número de camisa, e então chama a `0x00404820` e a
  `0x00404048`. **As duas já estão portadas** como `GravaJogador` e
  `GravaNumeroDaCamisa`, pela WTE-TASK-27;
- [`estrategia.BitBtn3Click`](../../wte/re/spec/estrategia.BitBtn3Click.md) —
  1.931 bytes: valida as cores do radar, grava duas regiões de 2 bytes por
  time, e converte as posições dos componentes `bola`/`tirador`/`simbolo` de
  pixel para célula da malha.

Duas assimetrias da primeira, que a task mediu e que qualquer implementação tem
de honrar:

1. **lê 32 bytes e grava 30** em quatro dos sete blocos — a última palavra de
   cada paleta é carregada e nunca devolvida. Gravar 32 mudaria bytes que o
   original nunca mudou;
2. **a forma da bandeira é lida de um offset e gravada em cinco** —
   `[0x004331E8]` na carga (o do meio), `[0x004331E0 + i*4]` com `i` de 0 a 4
   na gravação. O byte mora replicado na imagem.

## Causa raiz

**Escopo escrito antes de o corpo ser lido.** O enunciado da WTE-TASK-30
descreveu o grupo `auxiliar` como *"avisos e confirmações"* e previu que *"a
maioria receba veredito `trivial`"* — e o próprio enunciado avisava que
*"'espera-se' não é veredito"*. A previsão errou para doze dos dezessete, e
para quatro deles errou na direção que importa: eles tocam a imagem.

Não é falha da 30 nem da 27: é a divisão por **formulário** encontrando a
divisão por **grupo de comportamento**. O `BitBtn3` de um formulário é o botão
`OK` dele, e o `OK` de um editor é onde a edição vira byte no disco.

## Correção

Implementar as três, cada uma com o gate de gravação fechando antes de passar
para a seguinte — a mesma disciplina da WTE-TASK-27, e pelo mesmo motivo: com
duas gravações novas em voo, um golden vermelho tem duas causas possíveis.

**A ordem não é livre**, e ela sai das dependências medidas:

1. **`jugador.BitBtn3Click`** primeiro. É a mais barata: as duas rotinas de
   escrita já existem no port, e o que falta é a validação, a cópia dos campos
   e o roteiro. Ela também esbarra no ciclo de `uses` que o
   [`jugador.BitBtn1Click`](../../wte/re/spec/jugador.BitBtn1Click.md) descreve
   — `GravaJogador` e `GravaNumeroDaCamisa` moram no `.aux.inc` do `MainForm` —,
   e resolver esse ciclo uma vez destrava os dois handlers;
2. **`ficha_color.BitBtn3Click`** depois. Precisa que o `we2002_offsets` exponha
   as sete colunas por time que a carga usa, e precisa **carregar** as duas
   famílias não portadas (chuteira e quarta paleta) para poder devolvê-las
   intactas: pular os 288 bytes delas gravaria menos que o original, e gravar
   zeros corromperia a imagem. O slot 0, o vetor de edição e o `PadraoDaCamisa`
   já existem na [`wte_cor`](../../wte/src/wte_cor.pas);
3. **`estrategia.BitBtn3Click`** por último, e **ela tem um pré-requisito fora
   desta correção**: a `0x0040A0B4`, que enche a tela de tática, não está
   portada. Gravar as posições dos componentes de uma tela que ninguém
   posicionou gravaria as coordenadas de tempo de projeto do `.lfm`. Portar
   aquela rotina fecha três `aberto` de uma vez — este, o
   [`estrategia.BitBtn1Click`](../../wte/re/spec/estrategia.BitBtn1Click.md) e
   o [`mostrar_estrategiaClick`](../../wte/re/spec/MainForm.mostrar_estrategiaClick.md)
   — e é dívida herdada da WTE-TASK-26.

Cada uma precisa de **roteiro golden dos dois lados**, na forma dos que já
existem em [`wte/tests/roteiros/`](../../wte/tests/roteiros/): editar pela tela
antes de gravar, e comparar as duas imagens byte a byte. Nenhuma delas emite
arquivo, então nenhuma precisa de `--artefato`.

**A imagem é a japonesa.** Com a europeia o `wte.exe` morre ao trocar de time —
49.749 violações de acesso contra 0 — e o oráculo não existe daquele lado; ver
[`wte/re/gravacao-controle.md`](../../wte/re/gravacao-controle.md).

**O controle vem antes do teste, em cada uma.** Original contra original tem de
dar zero divergência no roteiro novo antes de o lado port entrar. Sem ele,
verde e vermelho não significam nada.

Ao fim, trocar o veredito das três no frontmatter da spec e regerar o
`re/spec/INDICE.md` pelo `spec_index.py`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/impl/ep2002_jugador.BitBtn3Click.inc` | criar |
| `wte/src/impl/ep2002_color.BitBtn3Click.inc` | criar |
| `wte/src/impl/ep2002_estrategia.BitBtn3Click.inc` | criar |
| `wte/src/impl/*.uses` | modificar |
| `wte/src/we2002_offsets.pas` (ou o gerador dele) | modificar |
| `wte/src/wte_cor.pas` | modificar |
| `wte/tests/roteiros/golden-15-*.txt` e `.port.txt` | criar |
| `wte/tests/roteiros/golden-16-*.txt` e `.port.txt` | criar |
| `wte/tests/roteiros/golden-17-*.txt` e `.port.txt` | criar |
| `wte/re/spec/ficha_color.BitBtn3Click.md` | modificar (veredito) |
| `wte/re/spec/jugador.BitBtn3Click.md` | modificar (veredito) |
| `wte/re/spec/estrategia.BitBtn3Click.md` | modificar (veredito) |
| `wte/re/spec/INDICE.md` | regenerar |
| `docs/tasks/progresso.md` | modificar |

## Verificação

- [x] `jugador.BitBtn3Click`: controle verde no roteiro novo, e golden
      byte-idêntico. **A edição de tela não foi necessária, e a razão é
      melhor do que a alternativa:** o `Comple.` é destrutivo sozinho — os dez
      bytes de nome saem do campo, o campo mostra o nome já filtrado pelo
      `0x0040b2d8`, e clicar sem tocar em nada grava `3f 3f 3f 3f` sobre
      `ba b0 d7 dd`. Um port que não gravasse nada reprova, que é a objeção
      que o `golden-03` teve de responder com um par editado
- [ ] `ficha_color.BitBtn3Click`: idem, e as duas famílias **não portadas**
      saem intactas — provado por gravar sem editar e comparar os 288 bytes
      delas
- [ ] `ficha_color.BitBtn3Click`: os 30 bytes gravados por bloco, não 32, e a
      forma da bandeira nos **cinco** offsets
- [ ] `estrategia.BitBtn3Click`: a `0x0040A0B4` portada antes, e a tela de
      tática conferida contra o original antes de qualquer gravação
- [ ] os três com veredito trocado e `spec_index.py --check` verde
- [ ] `make -C wte check` verde e `lazbuild wte/wte.lpi` verde
- [ ] `golden-03-barras` e `golden-08-dorsal-mcr` continuam verdes — nenhuma
      das três pode mexer no que já fechou
- [ ] `roms/` intocada; toda corrida sobre cópia

## Log de Execução

**PARCIAL — 1 das 3.** O `jugador.BitBtn3Click` está fechado e commitado; o
`ficha_color.BitBtn3Click` e o `estrategia.BitBtn3Click` continuam `aberto`. A
correção segue **pendente**, e a ordem que ela mesma fixou continua valendo
para o que falta.

**Executado em:** 2026-08-21 (primeira passagem)

**Resumo do que foi feito:**

Implementado o `jugador.BitBtn3Click` (`0x00408548`), o `Comple.` da ficha —
as duas validações, a cópia das 28 caixas de bit, dos dez bytes de nome e do
byte condicional para o buffer, e as duas gravações. Fechado pelo par novo
`golden-15-ficha`, nos três modos do `golden_check.sh`: `controle`
byte-idêntico, `positivo` detectando o byte plantado em 405228, `golden`
byte-idêntico contra o oráculo. Medido que a corrida **grava**: quatro bytes em
`OFS_PLAYER_NAME+774` mudam nos dois lados, além dos 11.955 do patch de
arranque.

O ciclo de `uses` foi resolvido como a spec do `BitBtn1` mandava — criando a
unidade neutra `wte/src/wte_ficha.pas` e descendo para ela o buffer de jogador
inteiro (`BufferJogador`, `PreparaBuffer`, `CarregaJogador`, `GravaJogador`,
`GravaJogadorEmMl`, `GravaNumeroDaCamisa` e o que elas alcançam). O corte foi
mecânico e verificável: **nenhuma rotina que desceu chama rotina que ficou**, e
o compilador diria se chamasse — as três únicas quebras foram `Cadeia`,
`soBeginning` e o `NomeDoJogador`, corrigidas na hora.

**Problemas encontrados:**

1. **O gate reprovou por quatro bytes, e o culpado era um doc que se dizia
   inofensivo.** O oráculo gravou `3f 3f 3f 3f` onde o port gravou zeros. A
   leitura do disassembly dizia que o campo de nome nasce vazio — há uma única
   escrita em `0x004335d4` no `.text`, dentro do próprio handler. A tela
   mostrou o contrário: o campo trazia `????`. O `grep` de `0x4335d4` que
   sustentava a conclusão tinha passado por `head -40` e escondido cinco
   sítios, entre eles o `0x0040fa8c`, que enche a global com o nome recortado
   do item da lista. **Screenshot resolveu em um minuto o que meia hora de
   disassembly tinha decidido errado.**
2. **Daí saiu a segunda:** o item da lista vem do filtro `0x0040b2d8`, e o port
   mostrava o byte cru. Isso estava registrado como divergência deliberada da
   WTE-TASK-35, com a justificativa *"ela é de TELA: nenhum dos dois grava"* —
   que deixou de valer exatamente aqui. O filtro foi portado (`NomeFiltrado`) e
   as três afirmações que diziam o contrário foram corrigidas, inclusive no
   gerador que emite uma delas.
3. **A pergunta `Calcular precos` não aparece nesta ordem**, e esperar por ela
   custou a primeira corrida de controle. Já estava medido no cabeçalho do
   `10-telas-que-faltavam.txt`: quem a provoca é o `base_team`.
4. `docs/PLAN-WTE-LAZARUS.md` §4.4 mede a fração de Pascal gerado, e uma
   unidade nova escrita à mão a move — 57,9% → 56,4%. O `check_fase2.py` pegou.

**O que falta, e como continuar:**

- **`ficha_color.BitBtn3Click`** — as sete regiões por time, os 30 bytes
  gravados por bloco contra os 32 lidos, e a forma da bandeira nos cinco
  offsets. Continua precisando carregar as duas famílias não portadas
  (chuteira e quarta paleta) para devolvê-las intactas;
- **`estrategia.BitBtn3Click`** — segue com o pré-requisito de fora: a
  `0x0040A0B4`, que enche a tela de tática, não está portada.

**Arquivos criados/modificados:**

- criados: `wte/src/wte_ficha.pas`,
  `wte/src/impl/ep2002_jugador.BitBtn3Click.inc`,
  `wte/tests/roteiros/golden-15-ficha.txt` e `.port.txt`
- modificados: `wte/src/impl/ep2002_mainform.aux.inc` (o corte, o
  `NomeFiltrado` e os dois campos do `PreencheFicha`),
  `wte/src/impl/ep2002_mainform.mostrar_jugadorClick.inc` (as três globais da
  ficha, a carga do buffer e a válvula `IgnoraJogadorRepetido`),
  `wte/src/impl/ep2002_mainform.uses`, `wte/src/impl/ep2002_jugador.uses`,
  `wte/tools/dump_mcr.py` e `wte/tools/test_dump_mcr.py` (as constantes do
  buffer mudaram de arquivo), `wte/re/spec/jugador.BitBtn3Click.md`,
  `wte/re/spec/INDICE.md`, `docs/PLAN-WTE-LAZARUS.md` §4.4, `wte/re/fase-2.md`,
  `wte/re/fase-3-fechamento.md`
- reconciliação de doc, em commit próprio: `wte/tools/dump_auxiliares.py` e
  `wte/re/auxiliares.md`, `wte/re/spec/MainForm.lista_equiposChange.md`,
  `wte/re/spec/jugador.BitBtn1Click.md`, `wte/tests/roteiros/README.md`,
  `docs/tasks/progresso.md`
