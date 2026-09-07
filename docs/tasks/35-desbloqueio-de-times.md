---
id: PES2-TASK-35
title: "Desbloqueio de times secretos e da lista de Master League, pelo disco"
type: engenharia-reversa
category: engenharia-reversa
phase: 4
depends_on: []
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §1.15"
status: pendente
---

# PES2-TASK-35: Desbloqueio de times secretos e da lista de ML

## Contexto

- **Referência:** [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md) §1.15 —
  escrita em 2026-09-07 para esta task, porque o plano não tinha onde
  pendurar a pergunta. Ela traz o medido, as quatro hipóteses e o critério;
  este arquivo traz o roteiro.
- Fase 4 **por proximidade**, não por pertencimento: é dado de disco fora do
  texto, como o resto da Fase 4, mas não é banco — é o que decide o que a
  grade percorre. Não trava a
  [PES2-TASK-16](/docs/tasks/16-fechamento-fase-4.md) e não é travado por ela.
- `depends_on` vazio **de propósito**: as quatro ferramentas de que ela
  precisa já estão de pé — `tools/pes2/mcp_drive.py` e `fork.py` (rotas e
  breakpoint por MCP, [PES2-TASK-34](/docs/tasks/34-rotas-mcp-no-lugar-do-drive.md)),
  `savestate.py` (busca de valor e diff de RAM), `memcard.py` (o `PES-OPT`) e
  `iso.py` (extrair, reinjetar, round-trip). Se a
  [PES2-TASK-05](/docs/tasks/05-diferencial-de-cartao.md) fechar antes, o
  harness de diferencial de cartão dela **substitui** o passo 1 abaixo; não
  espere por ele.

### O que o usuário pediu, em uma frase

Fazer o jogo exibir **os nove times secretos** (7 *classic* + `WORLD
ALLSTARS` + `EURO ALLSTARS`) e **os times de Master League** na tela de
seleção de times, **a partir da imagem** — remendo no `.bin`, não estado de
save, não sequência de partidas ganhas.

### O que o WE2002 tem a dizer sobre isso: nada

Medido, e o resultado é curto:

```sh
grep -rniE 'sblocc|segret|nascost|unlock|secret|abilita' legacy/mfc/
# legacy/mfc/graf.cpp:272:  //disabilita colori bandiera classic
# legacy/mfc/edDlg.cpp:6057: //salvare abilita - decodifica
```

Dois acertos, os dois sobre outra coisa. O `ed.exe` edita **conteúdo** —
nome, atributo, uniforme, bandeira, elenco — e nunca progresso de jogo. O
editor do Obocaman também não: o que ele tem de mais próximo é o contador de
slots livres de ML. **Não há técnica herdada para copiar**, e é isto que
responde o "não sei como isso é feito no WE2002": não é feito.

Consequência prática para esta task: ela não tem oráculo nem precedente. O
que a sustenta é a mesma coisa que sustenta o resto do projeto — medir no
jogo vivo e provar em tela.

---

## Objetivo

Nomear o mecanismo que decide quais times a grade de seleção percorre, e
remendá-lo na imagem de modo que os nove secretos e os times de ML apareçam
**com o cartão vazio**.

Se a resposta for *"não dá pelo disco"*, o objetivo é a **evidência disso**,
com o mecanismo nomeado do mesmo jeito. Um "não" medido fecha a task; um
"não" por cansaço, não.

---

## Roteiro

Quatro passos, do mais barato ao mais caro. **Pare no primeiro que responder**
— os seguintes existem para o caso de ele não responder.

### 1. O gate está no cartão? E de onde o cartão o herda?

**Meia resposta já existe, medida em 2026-09-07** (§1.15 do plano): o
`PES-OPT` do cartão carrega quatro blocos que estão **byte a byte no
executável de boot** — 865 B, 732 B, 508 B e 172 B, em quatro deltas
**diferentes**. Ou seja: o *option file* padrão não é um blob de 16 KiB no
disco; o save é **semeado** por tabelas de default espalhadas pelo
`SLES_039.57`, a maior delas emendando exatamente onde a tabela de 1.449
nomes do executável termina (299210 → 299211).

Isso muda o alvo: procurar "o option file padrão" não leva a lugar nenhum;
procurar **a tabela que semeia o campo de desbloqueio** leva.

O que falta medir aqui:

- um `PES-OPT` de cartão **virgem** contra o do usuário
  (`~/.local/share/duckstation/memcards/…(Es,It)_1.mcd`, que já tem uma Copa
  ganha). O virgem sai de bootar com cartão vazio e deixar o jogo criar o
  save — rota do `mcp_drive.py`, cartão de cópia;
- a faixa candidata: fora dos 1.242 nomes (516..12936) sobram o cabeçalho
  (0..516, que tem uma **tabela de máscara de bit** em 256..370) e a cauda
  (12936..16384), com 2.445 bytes não nulos;
- para cada byte que diferir, se ele cai dentro de um dos quatro blocos de
  default, o endereço no `.exe` sai por subtração — e é ali que o remendo
  vai.

**Não escreva no cartão do usuário.** Cópia, sempre — inclusive dele.

### 2. Quem lê a lista, e sob que condição

É o fluxo A da §6.14, já percorrido ponta a ponta:

1. rota `team-select` do `mcp_drive.py` com `--keep-alive`, para deixar a
   grade na tela;
2. localizar a lista de nomes **em RAM** — o texto de `SELECT.BIN` @3128
   está carregado, e `savestate.py scan` acha o endereço pelo próprio nome
   (`PATAGONIA` serve; `CLASSIC ENGLAND` é o alvo interessante, porque a
   pergunta é se ele **chega** a ser lido);
3. breakpoint de **leitura** nesse endereço, `read_registers` e
   `disassemble` em volta: quem itera, com que limite, e o que testa antes de
   incluir uma entrada;
4. do endereço da rotina ao arquivo do ISO — o overlay que a contém — e ao
   offset relativo dentro dele.

O sinal a procurar é o da hipótese 2 da §1.15: uma constante de limite
(`slti`/`addiu`) ou um teste de bit por entrada.

### 3. O que muda quando o desbloqueio acontece de verdade

Se o passo 2 não fechar, a alavanca cara é a comparação **antes × depois** no
jogo vivo. O usuário já jogou uma Copa inteira e ganhou 7-0 (a rota `ending`
existe por causa disso), então há um estado "com progresso" alcançável:

- `savestate.py diff` entre um estado antes e outro depois de um
  desbloqueio real, restrito à faixa que o passo 1 apontar;
- `savestate.py scan` por candidato de 1, 2 e 4 bytes, com os dois estados
  como filtro.

### 4. O remendo, e a prova

- `iso.py extract` do overlay identificado, remendo no arquivo extraído,
  `iso.py inject` de volta numa **cópia** da release `(EsIt)`;
- `iso.py roundtrip` na cópia remendada — a guarda que prova que nada além
  do remendo mudou, com EDC/ECC preservado (§6.7);
- boot da cópia pelo `fork.py` e rota `team-select` do `mcp_drive.py`, com
  **cartão vazio**, capturando a grade;
- repetir na `(EnFrDe)`, ou escrever por que o offset não se transporta
  (§1.13 — offset constante entre releases grava lixo).

---

## Critério de conclusão

- [ ] O mecanismo nomeado: **arquivo do ISO + offset relativo**, e o que o
      byte significa. Offset absoluto sozinho não serve (§6.4).
- [ ] Dito, com evidência, **onde mora o estado de desbloqueio** — disco,
      cartão, ou os dois — e, se for cartão, **quem o lê** e onde essa
      leitura mora no disco.
- [ ] Uma cópia remendada em que a grade exibe os **nove secretos**, com
      **cartão vazio**, provada por captura de tela da rota `team-select`.
- [ ] O mesmo para os **times de Master League** na tela de seleção — ou a
      constatação medida de que não é gate e sim outro fluxo de UI
      (hipótese 4 da §1.15), com o que se viu.
- [ ] `iso.py roundtrip` verde na cópia remendada.
- [ ] A medição repetida na `(EnFrDe)`, ou a razão escrita de ela não valer
      lá.
- [ ] `tools/pes2/optfile.py` — a ferramenta que **reproduz a medição de
      2026-09-07**: lê o `PES-OPT` de um cartão, mapeia as faixas, e localiza
      os blocos de default no executável. Os quatro deltas da §1.15 saíram de
      script de scratchpad e só viram fato versionado por aqui; se a
      ferramenta discordar, quem manda é ela.
- [ ] Uma ferramenta versionada em `tools/pes2/` que aplique o remendo —
      Python, pela regra do ferramental —, com `--check` e um **caso
      vermelho**: imagem já remendada, ou overlay que não casa a assinatura,
      têm de falhar alto.
- [ ] A §1.15 do plano atualizada com o que se mediu: as hipóteses
      descartadas ficam, com o motivo, e a que venceu ganha o endereço.
- [ ] `roms/` intocada; tudo sobre cópia. Cartão do usuário intocado.

---

## Armadilhas que esta task herda

- **O conjunto de cópias não se declara, se varre** (§6.1). São oito listas
  de nome de time com comprimentos diferentes; se o remendo mexer numa
  contagem, confira se a mesma contagem não vive em outra cópia.
- **Fronteira de setor morde** (§6.3). Remendo por `iso.py extract`/`inject`,
  nunca por escrita direta no offset absoluto.
- **Não recalcular EDC/ECC** (§6.7). Preservar é o comportamento correto.
- **O cartão é estado do usuário.** Diferencial sobre cópia; um `PES-OPT`
  sobrescrito custa as partidas dele.
- **Uma instância de emulador por vez**, e são dois binários — o `kill` do
  `fork.py` alcança os três nomes (§6.11).
- **O emulador roda no `:98`** (§6.10). `:1` só a pedido explícito, e é para
  isso que existe o `pad.py`.
- **`pgrep -f` casa a linha de comando do próprio shell** (armadilha 25 da
  §6.11), e `pkill -f` sobre ela mata o próprio shell.

---

## Log de Execução

*(a preencher)*
