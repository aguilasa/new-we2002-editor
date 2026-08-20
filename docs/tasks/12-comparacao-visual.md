---
id: WTE-TASK-12
title: "Comparação visual dos 18 formulários contra o original"
type: verificação
category: ui
phase: 2
depends_on: ["WTE-TASK-11"]
status: concluído
---

# WTE-TASK-12: Comparação visual

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §6 e Fase 2 item 3.
- **Não automatizar com tolerância de pixel.** `MS Sans Serif` não está
  instalada no host, o Qt e o GTK2 substituem por fontes diferentes, e o próprio
  `wte.exe` sob Wine já renderiza com fonte substituta. Diferença de pixel é
  garantida e não informa nada. É inspeção humana, uma vez por formulário.

O `newWe2002` já passou por isto: rótulo apertado corta ("Position" vira
"Positior") tanto no port quanto no `ed.exe` sob Wine, pelo mesmo motivo.

---

## Objetivo

Capturar os 18 formulários dos dois lados e conferir, um a um, que a diferença é
só de fonte — não de posição, tamanho, cor, ordem ou controle faltando.

### Método

1. `make wte` no `:99`, navegar até cada formulário, `import -window <id>`.
2. O app Lazarus no `:99`. **Ele não navega** — na fase 2 os handlers são stub
   ([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md), problema 3). O
   andaime é `--show`: `./wte/build/wte --show all` abre os 18 de uma vez,
   `--show <nome>` abre um só, `--list` dá os nomes. Mesma captura.
3. Lado a lado em `wte/re/visual/<formulario>/`.

**`import -window` falha com janela obscurecida por modal** — o aviso de
tamanho aparece na carga dos dois lados. Dispensar o modal antes, ou capturar
`-window root`.

### O que procurar, em ordem de gravidade

| Achado | Gravidade |
|---|---|
| controle faltando ou sobrando | bug do gerador — volta para a WTE-TASK-10 |
| posição ou tamanho errado | bug do gerador |
| cor de fundo diferente | provável `TStaticText` (§8.9) — 37 candidatos |
| bitmap não aparece | **não é perda na conversão** — a preservação dos 118 blobs está medida (WTE-TASK-10). É defeito de exibição: LCL/GTK2 ou pai do componente |
| rótulo cortado | **esperado**, registrar e seguir |

### As 37 instâncias de `TStaticText`

A §8.9 manda conferir agora, não na Fase 6. Corrigir 37 controles no fim é
retrabalho.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/visual/lazarus/*.png` | criar (18 capturas) |
| `wte/re/visual/original/*.png` | criar (4 capturas — ver o resultado abaixo) |
| `wte/re/visual.md` | criar — um veredito por formulário |
| `wte/tools/capture_forms.sh` | criar — reproduz o lado port |

O `capture_forms.sh` não estava previsto e entrou porque a captura tem duas
armadilhas que ninguém acerta de memória (janela preta por obscurecimento,
janela do Wine que não pinta quando mapeada por fora). Ele **não** é gerador e
fica fora de `tools/*.py` de propósito: PNG não é byte-estável entre versões de
GTK e de ImageMagick, e um `--check` ali quebraria por atualização de
biblioteca. Mesmo raciocínio que deixou o `make_icon.py` do `newWe2002` fora da
bateria.

---

## Resultado medido: o original só mostra 4 dos 18, porque **quebra**

Não é falta de saber o gatilho — o gatilho de cada janela está no DFM, e o mapa
de coordenadas foi levantado dali. **Selecionar um time derruba o original**:
310 `EXCEPTION_ACCESS_VIOLATION`, começando por leitura em ponteiro nulo + `0x1c`
em `ip=0x005f5ea0` e terminando em `stack overflow`. Determinístico, com cópia
byte-idêntica a `roms/`. Diagnóstico completo, o que foi descartado como causa e
o comando de reprodução em [`../../wte/re/visual.md`](../../wte/re/visual.md),
achado 1.

Sem time, o original só habilita `Sobre...` e `Sair` — e ambos funcionam, o que
prova que o clique chega. Daí as 4: `MainForm`, `ficha_warning` e `ficha_about`
pelo caminho de carga, e `ficha_salida` pelo `Sair`.

**Resultado negativo é resultado legítimo.** O que esta task existe para
responder — controle faltando, posição, tamanho, cor, blob, `TStaticText`,
rótulo cortado — está respondido nos 18, porque geometria e presença se
conferem contra o DFM com o `dfm2lfm.py --check`, que é evidência mais forte que
screenshot. As 14 capturas do original vão para a
[WTE-TASK-37](/docs/tasks/37-reconferencia-de-ui.md), **se** o crash se
resolver; o crash em si é bloqueio da
[WTE-TASK-22](/docs/tasks/22-harness-golden.md), onde está registrado.

---

## Critério de conclusão

- [x] Os 18 capturados dos dois lados — **18 do port, 4 do original.** Os 14
      restantes são inalcançáveis por defeito do oráculo, não por método; ver
      acima
- [x] Um veredito escrito por formulário
- [x] Os 118 blobs aparecem na janela — critério herdado da
      [WTE-TASK-10](/docs/tasks/10-conversor-dfm-para-lfm.md), que provou a
      preservação byte a byte e não podia provar a exibição. Os 100 desenháveis
      (`Glyph` + `Picture`) aparecem; os 18 `Icon.Data` não são julgáveis sem
      window manager, nos dois lados
- [x] O sufixo ` [Lazarus]` no `Caption` **não** foi contado como achado — é
      divergência deliberada da WTE-TASK-11, registrada na
      [WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md). No `:99` não há
      window manager e a captura nem chega a mostrá-lo
- [x] Nenhum controle faltando ou fora de lugar
- [x] Comportamento das 37 `TStaticText` decidido
- [x] Rótulos cortados listados, com a nota de que é esperado
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  Os 18 formulários do port capturados e inspecionados um a um, 4 do original,
  e cinco achados em [`../../wte/re/visual.md`](../../wte/re/visual.md).

  O que decidiu a task foi parar de clicar às cegas e **levantar o gatilho do
  DFM**: cada controle tem `Left`/`Top` e `OnClick` no DFM extraído, então dá
  para clicar no centro exato de `colorear`, `mostrar_jugador_1`,
  `mostrar_estrategia_1` e `dorsal1..23`. Foi isso que revelou o problema real.

  1. **O original quebra ao selecionar um time, e por isso 14 formulários são
     inalcançáveis.** 310 `EXCEPTION_ACCESS_VIOLATION`: a primeira é leitura em
     ponteiro nulo + `0x1c` em `ip=0x005f5ea0`, as seguintes são chamada para o
     endereço 0, até `stack overflow`. O processo fica `<defunct>` e as janelas
     X sobrevivem órfãs sob o `wineserver` — o app **parece vivo numa captura**,
     que foi o que despistou a primeira rodada desta task. Descartados como
     causa: cópia corrompida (repetido com cópia recém-tirada de `roms/`, mesmas
     310), meus cliques (sem time, `Sobre...` e `Sair` abrem normalmente) e
     estado sujo do Wine. Confundidor que a máquina não elimina: o único runner
     é um build TkG experimental. **Bloqueio entregue à WTE-TASK-22.**

  2. **Aceitar o aviso de tamanho grava 11.952 bytes na imagem**, faixa
     `11796..26527` (offsets 0-based, inclusivos — o `cmp -l` imprime
     `11797..26528` porque numera a partir de 1), setores 5 a 11, antes de
     qualquer edição. Isolado passo a
     passo: escolher o arquivo não grava, o "Sim" do aviso grava, splash e
     seleção de time não acrescentam nada. E o aviso dispara **sempre** com as
     imagens deste repositório. Muda o desenho do golden test, e foi para a
     WTE-TASK-22 com o critério novo.

  3. **A cor de fundo em runtime é mais larga do que a primeira heurística
     dizia.** O `ficha_salida` sai **amarelo** no original e não tem rótulo
     branco nenhum — a heurística "clBtnFace + rótulo `clWhite`", que dava cinco
     candidatos, é piso e não teto.

  4. §8.9 fecha sem custo: **nenhum dos 37 `TStaticText` usa `Transparent`**.
     Nenhuma ação, nenhum item para a fase 6. De quebra, 25 dos 37 têm
     `OnClick` — no original é widget clicável, não rótulo.

  5. Os **100 blobs desenháveis** aparecem; os 18 `Icon.Data` não são julgáveis
     sem window manager, dos dois lados.

- **Problemas encontrados:**

  1. **`import -window <id>` devolve PNG preto sem erro nenhum.** Sem window
     manager não há empilhamento garantido, e quase todo formulário nasce
     dentro da área do `MainForm`. As 18 primeiras capturas saíram pretas e
     pareciam bug de renderização da LCL. Saída: `windowraise` + recorte de
     `-window root`, no `capture_forms.sh`.
  2. **Mapear as janelas do original por fora não funciona, nem com expose
     forçado.** `xdotool windowmap` deixa a janela `IsViewable` e a captura
     sai preta; repetido com `xrefresh`, o que aparece é o `MainForm` por trás,
     repintado. A VCL não pinta o que não considera exibido. Medido duas vezes.
  3. **`Enabled` no DFM é estado de projeto, não de runtime.** Quase todo
     controle do `MainForm` nasce `Enabled = False` e o app habilita ao carregar
     um time — por isso a primeira rodada de cliques "não fazia nada". Os
     `dorsal1..23` são a exceção no DFM e, ainda assim, não abrem nada sem time.
  4. **O `:99` desta máquina subiu sem `-auth`.** O `CLAUDE.md` descreve o Xvfb
     de `xvfb-run`, com cookie próprio; o processo atual não tem. O
     `make -C wte run-98` erra falso nesse estado. O `capture_forms.sh` trata os
     dois casos.
  5. **Um hardlink meu em `work/` deslocou a listagem do diálogo de abrir** e
     uma sessão abriu a cópia errada. As cópias de `work/` são descartáveis e
     foram restauradas de `roms/`; `roms/` nunca foi tocada. Lição para o
     harness: não criar arquivo em `work/` entre rodadas — o diálogo é dirigido
     por coordenada, e a coordenada depende da listagem.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/capture_forms.sh` | criar |
  | `wte/re/visual.md` | criar |
  | `wte/re/visual/lazarus/*.png` | criar (18) |
  | `wte/re/visual/original/*.png` | criar (4) |
  | `docs/tasks/22-harness-golden.md` | modificar — os três hand-offs e o critério |
  | `docs/tasks/12-comparacao-visual.md` | modificar — resultado e Log |
