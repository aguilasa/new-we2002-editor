---
id: WTE-TASK-22
title: "golden_check.sh — o gate: wte.exe contra o app Lazarus"
type: ferramenta
category: verificação
phase: 4
depends_on: ["WTE-TASK-11", "WTE-TASK-21"]
status: pendente
---

# WTE-TASK-22: Harness golden

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §6.
- **É o gate da fase 4.** Nenhum handler entra sem ele verde. Vem antes dos
  handlers de propósito: sem gate, cada implementação é opinião.

A estrutura já existe neste repositório — `tools/golden_check.sh` faz duas
cópias da imagem, passa uma pelo oráculo sob Wine e a outra pelo port, e
compara. Aqui é o mesmo, trocando o oráculo:

```
copia_A.bin --> we-team-editor.exe (Wine 32-bit, :99, xdotool) --+
                                                                  |-- cmp
copia_B.bin --> app Lazarus (nativo, :99, xdotool) --------------+
```

---

## Objetivo

`wte/tools/golden_check.sh`, herdando **todas** as guardas do existente.

### As guardas, e por que cada uma existe

| Guarda | Custo que ela evita |
|---|---|
| fixar `DISPLAY=:99` dentro do script | o runner de teste repassa o `DISPLAY` do shell (`:1` aqui), e as janelas da sessão real derrubam a detecção |
| recusar-se a começar com janela grande já aberta no `:99` | uma janela esquecida de teste manual é dirigida em vez da que está sob teste, e o resultado é um diff que parece bug do port |
| restringir candidatos ao `_NET_WM_PID` do processo lançado | mesma causa, outra defesa |
| nunca apontar para `roms/` | os três editores gravam in-place, e cada imagem tem ~474 MB |

### O que muda em relação ao original

**O `wte.exe` tem título de janela** (`W11 Team Editor...`), ao contrário do
`IDD_ED_DIALOG` do `ed.exe`, que só se acha pelo tamanho. Isso simplifica —
mas exige que o app Lazarus tenha título **diferente** (WTE-TASK-11), senão os
dois lados se confundem.

### Dirigir a janela: as armadilhas já pagas

- Sem window manager no `:99`: `xdotool windowactivate` falha. Dirigir por
  coordenada absoluta.
- `xdotool type --window` usa `XSendEvent` e **embaralha string longa**. Digitar
  curto.
- **`Ctrl+A` não seleciona tudo num `TEdit`.** Limpar campo com `End`,
  `shift+Home`, `BackSpace`. Com `ctrl+a` os dois lados recebem textos
  diferentes e o diff acusa divergência que não existe.
- O diálogo de abrir do original não engole caminho longo digitado — o
  `make wte` mapeia `E:` para `work/` por isso. Reusar o truque.

### Roteiro de edição

Como o `GOLDEN_EDIT` do `golden_run.sh` existente: um trecho de shell que faz a
edição na tela antes de gravar, para os dois lados. Um roteiro por operação.

### Ordem de grandeza do custo

O script existente usa ~950 MB de temporário por rodada. Este usa o dobro,
porque são duas imagens de ~474 MB. Não roda em CI, e o plano já registra isso.

---

## Três medidas da WTE-TASK-12 e da 13 que esta task herda

### 1. ~~**Bloqueante:**~~ o oráculo A quebra ao selecionar um time — **com a imagem europeia**

Medido na WTE-TASK-12, com cópia byte-idêntica a `roms/`: escolher um time no
combo do `MainForm` dispara **310 `EXCEPTION_ACCESS_VIOLATION`** e o processo
morre. A primeira é leitura em ponteiro nulo + `0x1c` em `ip=0x005f5ea0`; as
seguintes são chamada para o endereço 0, até `stack overflow`. Determinístico.
As janelas X sobrevivem órfãs sob o `wineserver`, então **o app parece vivo numa
captura** — não confie na tela para decidir se ele está de pé.

Descartados como causa: cópia corrompida, os cliques em `TSpeedButton` (sem
time, `Sobre...` e `Sair` abrem seus formulários normalmente) e estado sujo do
Wine. Confundidor que esta máquina não consegue eliminar: o único runner é
`wine-experimental.bleeding.edge…(TkG Plain)`, que o log anuncia como versão de
teste, e não há Wine de sistema.

**Quase toda operação do editor começa por escolher um time**, então isto foi
bloqueante do dia da WTE-TASK-12 até a
[CORR-WTE-044](/docs/tasks/CORR-WTE-044.md). Diagnóstico e comando de
reprodução em [`../../wte/re/visual.md`](../../wte/re/visual.md), achado 1.

**Deixou de ser bloqueante em 2026-08-10, e o que resolveu foi a imagem.** A
CORR-WTE-044 mediu a causa: o ponteiro global `0x004335e4`, que a rotina de
realce dos `dorsalN` usa, é sobrescrito pela carga do time com dado de uma
tabela vizinha, e o valor (`0x00010001`) passa no teste de nulo que a rotina
faz. Não é controle faltando — os 23 `dorsalN` estão vivos e com `Font`. Mesmo
roteiro, mesmas marcas, só a imagem muda:

| imagem | violações de acesso ao trocar de time |
|---|---:|
| `roms/golden-european-deluxe.bin` | 49.749 |
| `roms/japanese-shift-jis.bin` | **0** |

**Consequência dura para esta task: o harness fixa `roms/japanese-shift-jis.bin`
do lado do oráculo, e escreve no script por quê.** Trocar por hábito para a
imagem golden do `newWe2002` devolve dezenas de milhares de violações de acesso
e parece defeito do harness. E o gate deve tratar `code=c0000005` no
`wine.log` como **falha do lado do oráculo**, nunca silenciá-la: está provado
que este caminho é imune com a japonesa, não que a imagem inteira seja.

As três ressalvas e o que ficou sem resposta estão em
[`../../wte/re/crash-causa.md`](../../wte/re/crash-causa.md).

### 2. O controle **não** é "imagem intocada"

Aceitar o aviso de tamanho — o caminho normal, porque as imagens deste
repositório têm 474.784.128 bytes e o editor espera 474.431.328 — grava
**11.952 bytes** na imagem, faixa `11796..26527` — **offsets 0-based,
inclusivos** —, **setores 5 a 11**, antes de qualquer edição. Medido passo a
passo: o diálogo de arquivo não grava, o "Sim" do aviso grava, e nem o splash
nem a seleção de time acrescentam byte.

**Não copie os extremos do `cmp -l`:** ele numera bytes a partir de 1 e imprime
`11797..26528` para a mesma faixa. O comando que mede na base certa está em
[`../../wte/re/visual.md`](../../wte/re/visual.md), achado 2.

*Original contra original* continua dando zero — os dois lados gravam os mesmos
bytes. Mas o port terá de **reproduzir** essa gravação, ou o harness terá de
declarar a faixa como exceção conhecida, no mesmo espírito dos 16 bytes do slot
64 do `newWe2002`. Decidir qual, e escrever a razão.

### 3. O lado port não recebe teclado no `:99`

Da WTE-TASK-13: sem window manager o GTK2 nunca considera a janela ativa, e
**nenhuma tecla chega** — nem `xdotool key` depois de `windowfocus`, nem
`key --window`. O mouse funciona. O `wte.exe` não sofre disso, porque o Wine
implementa o próprio foco.

Some com o outro achado da 13 — **o original confirma texto por tecla, não ao
sair do campo; não existe `OnExit` em nenhum dos 96** — e a conta fecha assim:
sem teclado do lado port, a operação "editar nome" não tem como ser comparada.
Ou o harness dirige o port só por mouse, ou o `:99` ganha um window manager
(nenhum instalado; instalar é decisão do usuário).

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/golden_check.sh` | criar |
| `wte/tools/golden_run_wte.sh` | criar — lado do original |
| `wte/tools/golden_run_laz.sh` | criar — lado do port |
| `wte/tools/roteiros/*.sh` | criar |

---

## Critério de conclusão

- [ ] As quatro guardas da tabela implementadas
- [ ] **O crash do oráculo ao selecionar time resolvido, ou o gate declarado
      inviável por escrito** — ver a medida 1 acima; sem isso nada abaixo
      significa alguma coisa
- [ ] Controle verde: original contra original dá zero divergência —
      **atenção:** não confundir com "imagem intocada", que diverge em 11.952
      bytes já na abertura (medida 2)
- [ ] Decidido se o port reproduz a gravação do aviso de tamanho ou se a faixa
      `11796..26527` vira exceção declarada. Os limites são **offsets 0-based,
      inclusivos**, como `KNOWN_START`/`KNOWN_END` do
      [`tools/golden_check.sh`](../../tools/golden_check.sh) do `newWe2002` —
      **não** as posições 1-based que o `cmp -l` imprime (`11797..26528`)
- [ ] Positivo: byte plantado é detectado, e o script reporta o offset
- [ ] Roteiro de edição parametrizável, um por operação
- [ ] `roms/` nunca tocada; temporário limpo no fim
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
