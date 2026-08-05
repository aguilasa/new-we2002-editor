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
- [ ] Controle verde: original contra original dá zero divergência
- [ ] Positivo: byte plantado é detectado, e o script reporta o offset
- [ ] Roteiro de edição parametrizável, um por operação
- [ ] `roms/` nunca tocada; temporário limpo no fim
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
