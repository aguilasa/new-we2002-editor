---
id: WTE-TASK-25
title: "Handlers de carga — abrir a imagem e popular as telas"
type: implementação
category: comportamento
phase: 4
depends_on: ["WTE-TASK-22", "WTE-TASK-23", "WTE-TASK-24"]
status: pendente
---

# WTE-TASK-25: Handlers de carga

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 4.
- **Ordem por dependência, não por endereço.** Estes vêm primeiro porque tudo
  depende deles: sem carga, nenhum handler de edição tem estado para editar.

Estes handlers **leem** a imagem e **não gravam**. O golden test não os mede
diretamente — o que os mede é a tela. Por isso a verificação aqui é dupla:
comparar o que aparece na janela dos dois lados, e comparar o estado interno
contra o dump da WTE-TASK-20.

---

## Objetivo

Implementar o grupo de carga, com spec e verificação por handler.

### Alvos

| Handler | Endereço | Papel |
|---|---|---|
| `boton_dialogo_weClick` | `0x0040bd60` | abre a imagem de CD |
| `lista_equiposChange` | `0x0040cd6c` | carrega o time selecionado |
| `lista_equipos_2Change` | `0x0040e1a8` | segunda lista de times |
| `lista_jugadores_1Change` | `0x0040f8b8` | seleção de jogador |
| `mostrar_jugadorClick` | `0x0040f8d4` | abre a ficha do jogador |
| `mostrar_estrategiaClick` | `0x00410220` | abre a tela de tática |
| `lista_formacionesClick` | `0x00409aa0` | aplica formação predefinida |
| `ComboBoxDrawItem` | `0x0040adec` | owner-draw do combo |
| `FormCreate` / `FormShow` | 18 endereços | inicialização de cada formulário |

São **16 `FormCreate` mais 2 `FormShow`** — não um por formulário:
`ficha_error` e `ficha_error2` não publicam nenhum dos dois. A coluna
`formulario` do `published_methods.tsv` diz qual é qual.

### Duas armadilhas de framework

**`ItemIndex` dispara `OnChange` na LCL.** Se o original dependia de não
disparar (o `SetCurSel` do Win32 não dispara `CBN_SELCHANGE`), a carga de time
entra em recursão ou recarrega duas vezes. A WTE-TASK-13 já deve ter respondido
isso; se não respondeu, responder aqui antes de escrever código.

**`lista_formacionesClick` aplica formação sobre o time selecionado** — é ação
destrutiva disparada por clique em lista. Conferir que ela não roda durante a
carga.

### Verificação

1. **Estado interno** — depois de carregar o time N, o dump da WTE-TASK-20 do
   app tem de bater com o do `we2002_core`.
2. **Tela** — captura dos dois lados, mesmo time selecionado, comparação humana
   dos campos preenchidos (não de pixel).
3. ~~**Sem gravação** — provar que nenhum destes escreve na imagem: rodar
   todos, fechar sem salvar, e `cmp` contra a cópia limpa tem de dar zero.~~

**O item 3 está errado, e a medição é que diz.** Abrir a imagem **grava**:
`boton_dialogo_weClick` injeta sete setores vindos de `dat.bin[0x20000..]` a
partir de `0x2e08`, com salto de `0x130` entre um e o seguinte
([`assets.md` §8.2](../../wte/re/assets.md)). São 11.952 bytes em 7 faixas na
ROM japonesa, e são exatamente as sete primeiras `conhecida:` que a
[WTE-TASK-22](/docs/tasks/22-harness-golden.md) declarou no roteiro do gate.

O item vira o seu contrário e continua barato: **o grupo grava, e grava só
isso** — nenhuma faixa além das que o oráculo grava pelo mesmo motivo.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/spec/<handler>.md` | criar (um por handler do grupo) |
| `wte/src/ep2002_*.pas` | modificar (corpo dos stubs) |
| `wte/re/spec/INDICE.md` | regenerar |
| `wte/src/wtemain.pas` | modificar — **remover o andaime `--show`** |

**O `--show` sai com esta task.** Ele existe porque na fase 2 nada navega: os
handlers são stub, e sem ele a
[WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) não conseguiria abrir
formulário para capturar
([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md), problema 3). Quando
a navegação de verdade entrar — que é aqui —, o andaime perde a razão de
existir; sem dono nomeado, ele fica para sempre. `--list` pode ficar, é barato
e não simula comportamento.

---

## Critério de conclusão

- [ ] Todo handler do grupo com spec no gabarito da WTE-TASK-23
- [ ] Estado interno batendo com o `we2002_core` após carga
- [ ] Tela conferida contra o original para pelo menos 3 times distintos
- [x] Medido **o que** o grupo escreve na imagem, e que não escreve mais que
      isso — 7 faixas, 11.952 B, as mesmas do oráculo
- [ ] Comportamento de `OnChange` na carga decidido e testado
- [ ] Andaime `--show` removido de `wtemain.pas`, com a navegação real no lugar
- [x] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:** 2026-08-11 — **parcial**, a tarefa continua em andamento.

- **Resumo do que foi feito:**

  Entrou a **infraestrutura sem a qual nenhum handler da fase 4 pode existir**,
  mais os dois handlers do caminho de abrir imagem.

  O problema que precisava ser resolvido antes de escrever a primeira linha de
  corpo: os 18 `ep2002_*.pas` são saída do `dfm2lfm.py` e dizem **NÃO EDITAR À
  MÃO**, com `make -C wte check` provando isso a cada rodada — e o enunciado
  desta task manda modificá-los. As duas coisas não cabem juntas. A saída foi
  o gerador passar a **referenciar** corpo escrito à mão em vez de emitir stub:
  `wte/src/impl/<unidade>.<handler>.inc` vira `{$I}` logo abaixo da assinatura,
  que continua gerada porque é mecânica. `.inc` órfão aborta o gerador — nome
  errado viraria stub em silêncio, e o sintoma seria "o handler não faz nada".

  **O achado que muda o enunciado:** abrir a imagem **grava**. A task previa
  provar `cmp` = zero para o grupo de carga; o que existe é uma injeção de sete
  setores vindos de `dat.bin[0x20000..]`, sentinela `0xFC` em `0x2e14`, salto
  de `0x130` sobre EDC/ECC. O port passou a fazer o mesmo e as **sete faixas
  saíram do `conhecida:` do roteiro do gate: de 9 divergências declaradas para
  2**. As duas que restam — um byte no setor 817, dois no 855 — continuam sem
  causa medida.

  Efeito colateral previsto e cobrado por teste: o `test_so_teste_consome_a_
  camada` do `check_fase3.py` existia dizendo que a casca não consome a camada
  de dados, e comentava que a WTE-TASK-25 o faria falhar. Falhou. A asserção
  virou de lado e o `fase-3-fechamento.md` foi regerado — o gerador já tinha os
  dois ramos escritos.

- **Arquivos criados/modificados:**
  - `wte/tools/dfm2lfm.py` — o mecanismo de corpo à mão (`le_impl`, `{$I}`,
    `uses` por unidade, `{$PUSH}` por handler em vez de por bloco)
  - `wte/tools/test_dfm2lfm.py` — 6 testes do mecanismo (70 no total, verdes)
  - `wte/src/impl/` — `README.md`, os dois `.inc`, `ep2002_mainform.uses`
  - `wte/src/we2002_estado.pas` — **escrito à mão**: `dat.bin`, injeção,
    `AbreImagem`, o `TDatabase` compartilhado
  - `wte/re/spec/MainForm.FormShow.md`, `MainForm.boton_dialogo_weClick.md`
  - `wte/tests/roteiros/golden-01-arranque.txt` — 9 `conhecida:` → 2
  - `wte/tools/check_fase2.py` — stub **ou** corpo, conta por soma
  - `wte/tools/check_fase3.py`, `test_check_fase3.py` — a asserção invertida
  - regerados: os 18 `.pas`, `fase-2.md`, `fase-3-fechamento.md`, `INDICE.md`

- **Problemas encontrados:**
  1. O `IMPL_DIR` nasceu como global de import e quebrou o
     `test_blob_ausente_...`: os testes trocam `SRC_OUT` por árvore temporária,
     e o global continuava apontando para a árvore real. Passou a ser derivado
     de `SRC_OUT` em tempo de chamada.
  2. O `{$PUSH}{$WARN 5024 OFF}` envolvia o bloco inteiro de stubs. Mantido
     assim, o primeiro corpo de verdade escrito ao lado herdaria o silêncio e
     um parâmetro esquecido passaria. Virou um par por stub.
  3. O cabeçalho gerado afirmava que todo corpo é stub. Vira mentira no dia em
     que deixa de ser; foi reescrito para descrever as duas formas.

- **O que falta para esta task fechar:**
  - `lista_equiposChange`, `lista_equipos_2Change`, `lista_jugadores_1Change`,
    `mostrar_jugadorClick`, `mostrar_estrategiaClick`, `lista_formacionesClick`,
    `ComboBoxDrawItem`, `MainForm.FormCreate` e os 16 `FormCreate`/`FormShow`
    dos `ficha_*` — 26 dos 28 do grupo;
  - a conferência de tela para 3 times e o dump de estado contra o `we2002_core`;
  - a decisão medida sobre `OnChange` disparar em `ItemIndex` na LCL;
  - a remoção do `--show` — que só pode sair **depois** da navegação real,
    senão os 17 formulários deixam de ser alcançáveis;
  - as duas faixas de arranque sem causa (`1921862`, `2012984..2012985`);
  - quais controles recebem `$00ffb676` no `FormShow`.
