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

- [ ] `jugador.BitBtn3Click`: controle verde no roteiro novo, e golden
      byte-idêntico com uma edição de tela antes da gravação
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

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
