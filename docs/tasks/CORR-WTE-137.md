---
id: CORR-WTE-137
title: "Correção: `8.8-b2002-exportar.sh` não reproduz, não confere nada e deixa o modal aberto"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-137: o roteiro de exportação da §8.8 é um falso verde à espera

## Problema identificado

O item 3 da §8.8 — "`.b2002` e `.m2002`: exportar do port e importar no
`ed.exe`, e vice-versa" — se apoia em
[`tools/par/8.8-b2002-exportar.sh`](../../tools/par/8.8-b2002-exportar.sh), e o
roteiro tem três defeitos que se somam:

1. **Não reproduz.** Quatro corridas idênticas desta revisão deram quatro
   resultados diferentes.
2. **Não confere nada.** Não há guarda de que o arquivo apareceu, nem de que
   tem 41 / 40 bytes. Corrida que não exportou é indistinguível de corrida que
   exportou.
3. **Não fecha o `FlagKitDialog`**, que é modal nos dois lados — ao contrário do
   `8.8-cores-teto.sh` e do `8.8-b2002-importar.sh`, que terminam com
   `fk_click 196 26 36 14` no botão "Close". Com o modal de pé o clique em
   `CMB_WRITE` não alcança o diálogo principal, o `Database::Save()` não roda —
   **e o harness diz que gravou**.

O terceiro é o mais perigoso, porque é exatamente a armadilha que a §8.7 já
tinha pago (CORR-WTE-131): dois lados que **não** gravam produzem imagens
idênticas, e um `golden_check.sh` com este roteiro sai verde sem ter medido
nada.

## Evidência

**As quatro corridas**, mesmo roteiro, mesmas variáveis, `ptbr-remaster.bin`:

| corrida | `.b2002` | `.m2002` | saída do harness |
|---|---|---|---|
| 1 | 41 bytes, conteúdo correto | — | `X Error … BadWindow`, exit 1 |
| 2 | — | — | `gui: gravado`, **exit 0** |
| 3 | — | — | `gui: gravado`, **exit 0** |
| 4 | **0 bytes** | — | `X Error … BadWindow`, exit 1 |

O `.m2002` **não saiu em nenhuma**. O único arquivo bom, o da corrida 1, está
certo — 41 bytes, `f.m.band`, estilo `0x00` e `flag_colours[0] = 0x0dc3` =
3523, que é o valor da imagem:

```text
00000000: 662e 6d2e 6261 6e64 00c3 0d82 89bd f718  f.m.band........
00000010: e359 8ef6 8dcb aedc 8ebd f7bd f7bd f7bd  .Y..............
00000020: f700 8000 8020 cd00 00                   ..... ...
```

**O falso verde, medido:** nas corridas que saíram `exit 0` dizendo
`gui: gravado`, a imagem **não foi gravada**:

```text
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin "$S/c883.bin"
IDENTICAL
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin "$S/c884.bin"
IDENTICAL
```

## Causa raiz

O roteiro dirige por coordenada relativa à janela (`fk_click` faz
`xdotool mousemove --window "$FK"`), mas o clique cai em **quem estiver por
cima naquele ponto** — e depois de cada export sobe um `AfxMessageBox` /
`QMessageBox` ("Flag exported !"). Quando o `Return` de dispensa não chega a
tempo, o clique seguinte (`CMD_EXPORT_KIT1`) acerta a caixa de mensagem, e daí
para frente o roteiro digita no vazio. Nada disso é detectado, porque o roteiro
não confere efeito e não fecha o diálogo.

## Correção

### Arquivo: `tools/par/8.8-b2002-exportar.sh`

1. **Fechar o modal ao fim**, como os outros dois roteiros da seção:
   `fk_click 196 26 36 14` no "Close". Sem isso o roteiro é inseguro para
   `golden_check.sh`, e o cabeçalho deve dizer por quê.
2. **Esperar o efeito em vez de dormir**: depois de cada `Return` de confirmação,
   aguardar o arquivo aparecer com o tamanho esperado (41 para o `.b2002`, 40
   para o `.m2002`) antes de seguir, e **falhar alto** se não aparecer — o
   padrão de `tact_win`/`flag_win`, que já retornam erro quando a janela não
   surge.
3. Dispensar a caixa de mensagem por espera de janela, não por `sleep` fixo.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md` e `docs/tasks/PAR-TASK-07.md`

Re-medir o item 3 com o roteiro consertado e registrar os dois tamanhos e o
`cmp` entre o arquivo do port e o do `ed.exe` — a afirmação "byte-idênticos" é
a que precisa de corrida reproduzível para valer.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.8-b2002-exportar.sh` | modificar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — item 3 da §8.8 |
| `docs/tasks/PAR-TASK-07.md` | modificar — o Log do item 3 |

## Verificação

- [ ] Três corridas seguidas do roteiro produzem **os dois** arquivos, com 41 e
      40 bytes, e `cmp` idêntico entre elas
- [ ] Uma corrida em que o export falha **falha alto**, em vez de sair `exit 0`
- [ ] Com o roteiro no `golden_check.sh`, o controle positivo do port contra a
      imagem original **não** sai `IDENTICAL`
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
