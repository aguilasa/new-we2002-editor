---
id: CORR-WTE-093
title: "Correção: os dois últimos corpos da fase 4 — a tela de tática e o diálogo de textura"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-093: os dois corpos que sobravam fora de preço

## Problema identificado

- **`estrategia.FormCreate`** (`0x004090fc`, 1.351 bytes — o maior dos 18) não
  tinha corpo, e a spec dizia por quê: quatro laços de 11 iterações em
  `0x004092fe`..`0x00409344` **sem leitura escrita**. A spec recusava adivinhar:
  *"11 é o número de jogadores em campo… mas 'provavelmente' não é spec, e
  escrever o corpo a partir daí seria inventar."*
- **`MainForm.boton_dialogo_texClick`** (`0x0040dfe8`) estava `aberto` com o
  dono nomeado na WTE-TASK-29 — **que fechou sem ele**.

## Evidência

### Os quatro laços, lidos

```text
0x004092fe   11 bytes  [eax]      -> [esi+0x00]
0x00409312   11 bytes  [ebp-0x60] -> [esi+0x0b]
0x00409326   11 bytes  [ebp-0x64] -> [esi+0x16]
0x0040933a   11 bytes  [ebp-0x68] -> [esi+0x21]
0x00409355   add esi,0x2c ; cmp DWORD PTR [ebp-0x5c],0x12 ; jl
```

Quatro colunas de 11 intercaladas num registro de **44**, dezoito vezes. É a
**tabela de formações de `0x00433f0c`** — e as quatro cópias de 51 dwords que a
spec listava *"sem saber quem as lia"* (`0x00423be4`, `0x00423cb0`,
`0x00423d7c`, `0x00423e48`) são as quatro colunas.

A suspeita da spec era razoável e estava errada: não são as 11 bolas, são as 11
posições de **cada uma das 18 formações**.

**O port não reproduz os laços**, e não deve: o
[`dump_formacoes.py`](../../../wte/tools/dump_formacoes.py) já extrai a mesma
tabela para `wte_formacoes.pas`. Reproduzi-los seria montar à mão o que já é
gerado.

### O slot virtual, medido

A rotina termina com `call DWORD PTR [ecx+0xcc]` e `edx=1` sobre a
`lista_formaciones`. Lendo o VMT de `TListBox` no `vcl60.bpl`, o slot `0xcc`
guarda `@Stdctrls@TCustomListBox@SetItemIndex$qqrxi`: é `ItemIndex := 1`, o
mesmo `FORMACAO_DEFAULT` que a `wte_tatica` já declarava por outro caminho.
Mesmo método da medida de `SetEnabled = VMT[0x64]` do `sonda_dorsal.py`.

### A zebra

Contador de 0 a 10 (`cmp DWORD PTR [ebp-0x5c],0xb`), sufixo = contador + 1,
paridade por `and eax,0x80000001`. Contador par → `$00D78228`; ímpar →
`$00E68F41`. Os três prefixos (`etiqestr`, `jugador`, `etiqpos`) aparecem
**duas vezes** na `.data` — em `0x00424b66` e em `0x00424b7f` —, porque são dois
ramos de código distintos, não dois conjuntos de controles.

## Correção

`estrategia.FormCreate` → `implementado`. O corpo faz o que sobra das tabelas
geradas: cor do formulário, zebra dos onze trios, os dois ponteiros de foco
(`0x00434340`, `0x00434344`) e a cor e o item inicial da lista.

`MainForm.boton_dialogo_texClick` → `divergencia deliberada`, espelhando o
irmão `boton_dialogo_weClick`. A divergência **já estava tomada e escrita**
antes deste corpo: o original guarda um `FILE*` aberto pela sessão, o port
guarda caminho e tamanho e abre por operação. Por isso a `0x00417170` deixou de
ser pré-requisito — ela é o par abrir/medir que o caminho substitui, e o que se
faz com os bytes do `.tex` é do `boton_tex2isoClick`, que tem gate próprio.

## Verificação

- [x] `lazbuild` do zero — 16.698 linhas
- [x] `make -C wte check` verde
- [x] `golden-17-tatica` e `golden-21-arrasto` **re-rodados depois do corpo
      novo** e byte-idênticos — necessário porque o `FormCreate` mexe no
      `ItemIndex` que alimenta o ` Accept`
- [x] `golden-06-textura` byte-idêntico depois do corpo do diálogo
- [x] `roms/` intocada

## Log de Execução

- **Executado em:** 2026-08-24

- **Resumo:** o placar da fase 4 foi de **91 para 93 de 96**, e os três que
  sobram são exatamente os da
  [WTE-TASK-32](/docs/tasks/concluidos/32-preco-do-jogador.md).

  **A lição é sobre o que "portar" quer dizer quando há gerador.** Metade do
  maior `FormCreate` do projeto é construção de tabela, e o port tem as duas
  tabelas geradas de fonte melhor. Ler o disassembly foi necessário — sem ele
  não dava para saber que os laços eram *aquela* tabela e não outra coisa —, mas
  o resultado da leitura foi **decidir não escrever código**. Uma spec que
  fechasse a pergunta e mandasse reproduzir os laços teria produzido 40 linhas
  de Pascal para chegar ao mesmo array.

- **Problemas encontrados:** o `golden-06-textura` reprovou na primeira corrida
  com *"depois de uma ação cara, o caso é de `espera:`"* — o roteiro precisa de
  `WTE_TEXTURA` apontando para a fixture de 5.000 bytes, e sem ela o editor
  engasga. É a **mesma** armadilha que a primeira passagem da WTE-TASK-31
  registrou, e ela continua se disfarçando de falha de tempo.
