---
id: WTE-TASK-11
title: "App Lazarus abrindo os 18 formulários, com os 96 stubs logando"
type: implementação
category: ui
phase: 2
depends_on: ["WTE-TASK-10"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §4.3 e Fase 2 item 2"
status: concluído
---

# WTE-TASK-11: A casca completa

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.3 e Fase 2 item 2.
- A estratégia é **casca antes de recheio**: construir o app inteiro vazio e
  depois preencher handler a handler. O stub que loga transforma o app numa
  ferramenta de RE — clicar no original e no stub lado a lado mostra a **ordem
  real de disparo dos eventos**, que nenhuma análise estática dá.

**Nesta fase o app não toca a imagem de CD. Zero risco.**

---

## Objetivo

Aplicação que compila, abre, navega entre os 18 formulários, e registra cada
handler disparado.

### 1. Auto-create e navegação

O original cria as 18 instâncias globais no start (`_MainForm`, `_estrategia`,
`_jugador`, `_ficha_*`) — padrão auto-create do C++Builder. Reproduzir, e ligar
a navegação: qual botão abre qual formulário sai dos DFM.

Alguns formulários são modais de aviso (`ficha_error`, `ficha_warning`,
`ficha_info*`); outros são telas de trabalho (`estrategia`, `jugador`,
`ficha_color`). O DFM diz qual é qual pelo `BorderStyle` e `BorderIcons`.

### 2. `REStub` e o trace

```pascal
procedure REStub(const Nome: string);
```

Escreve em `wte/re/trace.log`: timestamp relativo, nome do handler, formulário.
Formato **estável e diffável** — a WTE-TASK-13 vai comparar duas execuções.

### 3. O que ainda não existe

Nenhum acesso a arquivo, nenhum `OpenDialog` funcional, nenhum desenho. Botão
que carregaria imagem só loga.

### Armadilha de plataforma

A regra do `:99` vale integralmente: `DISPLAY=:99`, `XAUTHORITY` resolvido pelo
`ps`, sem window manager, `xdotool windowactivate` não funciona — dirigir por
coordenada absoluta.

**O título da janela tem de ser diferente do original.** O `wte.exe` se chama
`W11 Team Editor...`; se o app Lazarus usar o mesmo, os scripts que acham janela
por título vão pegar o lado errado a partir da WTE-TASK-22.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/wtemain.pas` | criar — auto-create e linha de comando |
| `wte/src/retrace.pas` | criar — **não `restub.pas`**, ver o Log |
| `wte/wte.lpr` | modificar |
| `wte/wte.lpi` | modificar — as 20 unidades entram no projeto |
| `wte/src/WteMain.pas`, `wte/forms/WteMain.lfm` | remover — o provisório da WTE-TASK-02 |
| `.gitignore` | modificar — `wte/re/trace.log` é saída de execução |

---

## Critério de conclusão

- [x] `lazbuild` compila sem warning novo — `rm -rf wte/build && lazbuild -B
      wte/wte.lpi` dá `(1008) 2567 lines compiled` e `(1022) 2 hint(s) issued`,
      com **0 warning**. Os 2 hints que o contador do FPC soma são
      `11030`/`11031`, abrir e fechar `/etc/fpc.cfg` — nada do código. Os hints
      do Lazarus sobre diretório de pacote do sistema não writable são outros
      seis, saem **antes** do compilador e não entram nessa conta (viram sete
      quando a árvore já está construída, com o `Build Project: nothing to
      do.`). Medido em 2026-08-09.

      Dois cuidados ao reconferir. **`grep -ci warning` não serve**: casa
      `Compiling ./src/ep2002_warning.pas` e devolve 2 numa saída sem warning
      nenhum. O que vale é `(1023) N warning(s) issued` ausente, ou
      `grep -cE '^Warning'` = 0. E **o número de linhas se move com
      comentário**: eram 2.562 até a
      [CORR-WTE-022](/docs/tasks/concluidos/CORR-WTE-022.md) acrescentar 5 linhas ao
      cabeçalho de `wtemain.pas`. Quem o mudar diz por quê no seu Log — a
      partir da fase 3 ele sobe porque entram unidades novas.
- [x] Os 18 formulários abrem e fecham no `:99` — `--show all` mapeia 18
      janelas; depois do `kill`, zero
- [x] Os 96 stubs logam em `trace.log`, formato estável — carimbo **relativo**
      ao início do processo, não hora do dia, senão toda linha divergiria no
      `diff` da WTE-TASK-13
- [x] Título da janela distinto do original — sufixo ` [Lazarus]` posto em
      tempo de execução, ver o Log
- [x] Nenhum acesso a arquivo de imagem de CD no código
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-06

- **Resumo do que foi feito:**

  A ordem de auto-create **não foi escolhida, foi medida**. O `WinMain` do
  original chama `Application->CreateForm` 18 vezes entre `0x401a2e` e
  `0x401bc6`; cada sítio carrega a referência de classe de um endereço de
  `.data`, e resolvendo cada uma pelo `vmtClassName` (o mesmo `-44` do
  `dump_published.py`) sai a lista inteira:

  `TMainForm`, `Testrategia`, `Tjugador`, `Tficha_dorsal`, `Tficha_enlaza`,
  `Tficha_color`, `Tficha_info`, `Tficha_warning`, `Tficha_error`,
  `Tficha_info2`, `Tficha_about`, `Tficha_error2`, `Tficha_salida`,
  `Tficha_info4`, `Tficha_info3`, `Tficha_movertodos`,
  `Tficha_creditos_equipo`, `Tficha_warning_2`.

  Isso importa porque `OnCreate` dispara na criação: **os 18 primeiros
  `FormCreate` do `trace.log` são essa lista**, e é contra ela que a
  WTE-TASK-13 compara. Reproduzir:

  ```sh
  objdump -d -M intel we-team-editor/we-team-editor.exe \
    | sed -n '/401a22:/,/401bc6:/p' | grep -E 'mov +(ecx|edx),DWORD PTR ds:'
  ```

  A faixa começa em `0x401a22`, e não em `0x401a2e`, de propósito: as 18
  **chamadas** vão de `0x401a2e` a `0x401bc6`, mas os dois `mov` que carregam
  os operandos de cada sítio vêm **antes** da chamada dele. Começando na
  chamada, o primeiro par fica de fora e a saída traz 17 classes, sem
  `TMainForm`.

  O `trace.log` sai com **16** `FormCreate`, não 18, e está certo:
  `ficha_error` e `ficha_error2` não têm `OnCreate`. Bate com a WTE-TASK-04,
  que mediu `FormCreate` × 16 — e é a primeira confirmação dinâmica de um
  número que até aqui só tinha medida estática.

- **Problemas encontrados:**

  1. **`restub.pas` não pode existir com esse nome, e `RETrace` também não.**
     Identificador em Pascal não distingue maiúscula, então uma unidade
     `restub` exportando `REStub` não compila. A WTE-TASK-10 já tinha
     previsto e gerado os stubs chamando `retrace`. O que ela não previu é
     que a **segunda** rotina da unidade caía na mesma armadilha: `RETrace`
     colide com a unidade `retrace`, e o erro (`Syntax error, "." expected
     but "(" found`) só aparece no primeiro **uso**, não na declaração.
     Virou `REMark`.
  2. **`Application.Title` não torna a janela distinguível.** O critério
     "título distinto do original" parece resolvido pelo `.lpr`, e não é: o
     que os scripts leem é o `Caption`, que vem do DFM — e o do `MainForm` é
     literalmente `' W11 Team Editor PT by chagas_michel!'`, igual ao do
     original. A partir da WTE-TASK-22 os dois rodam no mesmo `:99`. O
     sufixo ` [Lazarus]` é posto **em tempo de execução** nos 18, não no
     `.lfm` (que é gerado, e editar saída de gerador está proibido). No
     `:99` não há window manager, então nenhuma barra de título é desenhada
     e a captura da WTE-TASK-12 não enxerga o sufixo. **Divergência
     deliberada — registrar na WTE-TASK-35.**
  3. **Não há navegação de verdade, e não podia haver.** Quem abre
     formulário são os handlers, e na fase 2 eles são stub. Ligar
     botão→formulário exige saber o que cada handler faz, que é da
     WTE-TASK-25 em diante. No lugar ficou `--show <nome>` / `--show all`,
     andaime explícito para a captura da WTE-TASK-12.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/src/retrace.pas` | criar |
  | `wte/src/wtemain.pas` | criar |
  | `wte/wte.lpr` | modificar |
  | `wte/wte.lpi` | modificar — 20 unidades |
  | `wte/src/WteMain.pas`, `wte/forms/WteMain.lfm` | remover |
  | `.gitignore` | modificar |
