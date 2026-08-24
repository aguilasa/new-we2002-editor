---
id: CORR-WTE-095
title: "Investigar: o editor do Obocaman nunca preça o slot 22, e o `ed.exe` diz que ele tem preço"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-095: os dois editores discordam sobre o 23º slot

## Problema identificado

O `MainForm.base_teamClick` do editor do Obocaman percorre os 23 slots de um
time e grava o preço de **22**. O slot 22 nunca é escrito.

Isso foi medido pela [WTE-TASK-32](/docs/tasks/32-preco-do-jogador.md) e o port
o reproduz — o gate é byte a byte contra o oráculo, então reproduzir é
obrigatório. **O que não se sabe é por quê**, e é isso que esta correção
investiga.

## Evidência

O laço vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em `0x00411178`), e cada
volta começa com:

```text
call 0x4046e8                        ' carrega_jogador(time, slot, buffer 2)
cmp  DWORD PTR ds:0x43366c,0x0       ' a terceira coluna do buffer 2
je   0x411175                        ' pula o slot
```

Para o slot 22 a coluna sai **zero**, e o slot é pulado.

**Medido em seis times da ROM japonesa** (0, 2, 9, 17, 30, 48): os bytes
gravados vão de `CONDICIONAL_BASE + 23·t` até `+ 21`, e o do slot 22 fica com o
valor de fábrica em todos os seis.

**O conteúdo do jogador não explica.** No time 9 o slot 21 e o slot 22 têm a
**mesma** soma de habilidades (36) e a **mesma** posição (0, goleiro), e só o 21
é gravado.

**E o outro editor discorda.** A conta de offset que este port herdou —
`CONDICIONAL_BASE + 23·indice + 2·(indice div 56) + slot`, em
`wte/src/wte_ficha.pas` — dá coluna **não nula** para o slot 22. Ela veio do
`we2002_core`, que é byte-idêntico ao `ed.exe`, e o `ed.exe` lê e grava custo
para os 1.449 jogadores de seleção sem pular nenhum
(`src/core/Database.cpp:756-764`, que só salta os 46 dos times 54 e 55).

## Causa raiz

**Desconhecida.** É o que esta correção tem de estabelecer.

## Correção

Determinar de onde vem o zero, e então decidir o que fazer com ele.

### As perguntas, na ordem em que se respondem barato

1. **A ficha concorda com a gravação?** Se o `casilla_precio` nascer
   desabilitado para o slot 22 no oráculo, então a `0x00404374` inteira acha
   que aquele slot não tem campo condicional — e o efeito é bem maior que
   preço: alcança o `casilla_dorsalKeyPress`, que só encadeia o foco quando a
   coluna não é zero. Custa uma corrida de tela.
2. **É todo time, ou só time de seleção?** Clube de Master League resolve o
   slot por vínculo, e o slot 22 de um clube pode apontar para outro lugar.
3. **É o slot 22 ou é "o último"?** Um clube de ML com menos jogadores diria.
4. **Onde a `0x00404374` calcula a terceira coluna**, e se há um `cmp` contra
   22 ou um limite de tabela ali.

### O que fazer depois de saber

Se for defeito do editor do Obocaman, ele entra na
[WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md) como divergência
**do original contra o formato**, e o port continua reproduzindo-o — com a
razão escrita em vez de "medido, não explicado".

Se for propriedade do formato que o `we2002_core` lê errado, a conta de offset
do port está errada para o slot 22 **em toda operação**, não só em preço, e aí
é achado grande.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/preco.md` | modificar (a seção do achado ganha a causa) |
| `wte/re/spec/MainForm.base_teamClick.md` | modificar |
| `wte/src/impl/ep2002_mainform.base_teamClick.inc` | modificar, se a causa mudar o `ULTIMO_SLOT_PRECADO` |
| `wte/tools/check_preco.py` | modificar, idem |

## Verificação

- [ ] a causa escrita, com o endereço que a produz — **não atingido**, e o que
      falta está nomeado no Log
- [x] `golden-22-precos` verde depois, com o controle fechando antes
- [x] `check_preco.py --check` verde
- [ ] se a conclusão for "defeito do original", linha na WTE-TASK-35 — sem
      conclusão ainda, então sem linha

## Log de Execução

**PARCIAL.** A correção segue **pendente**: a pergunta 4 da seção *Correção* —
*onde a `0x00404374` calcula a terceira coluna, e se há um `cmp` contra 22 ou um
limite de tabela ali* — foi respondida, e a resposta **exclui** a hipótese que a
correção mais temia, mas não produz a causa. As perguntas 1, 2 e 3 (a ficha, o
clube de ML, "o slot 22 ou o último") continuam por medir.

**Executado em:** 2026-08-24 *(medição parcial; a correção não fecha)*

**O que foi medido**

**1. O salto é real — não é byte que já estava certo.** Esta era a explicação
barata e ninguém a tinha descartado: se o preço do slot 22 já fosse o valor
gravado, o diff não veria mudança e a leitura seria a mesma. Plantados `0xFF`
nos três últimos slots do time 2 e rodado o oráculo pelo
[`golden-22-precos`](../../wte/tests/roteiros/golden-22-precos.txt) sobre a
cópia:

```text
slot  offset   antes   plantado   depois
  20  3067470     19        255       26     <- previsto no preco.tsv: 26
  21  3067471     14        255       21     <- previsto no preco.tsv: 21
  22  3067472     19        255      255     <- nao tocado
```

Antes disso a hipótese tinha até um apoio: os bytes de fábrica do slot 22 não
batem com o `previsto` em nenhum dos seis times (0: 14 contra 16; 2: 19/20;
9: 18/20; 17: 17/26; 30: 14/20; 48: 18/43). O plantio é que fecha, porque
`0xFF` não é preço de ninguém.

**2. Também está descartado o "escreve duas vezes no slot 21".** Se o `je` não
fosse tomado e o `0x43366c` ficasse com o offset da volta anterior, o slot 21
receberia o preço do 22 por último. Ele voltou com **21**, que é o preço dele,
e não com 20, que é o do 22.

**3. A `0x00404374` não tem ramo por slot.** Lida inteira — `0x00404374` a
`0x004046e2`, as duas rotas e a cauda comum:

| Endereço | Teste | Sobre |
|---|---|---|
| `0x00404389` | `cmp ecx,0x3f` | **time** — separa seleção de clube de ML |
| `0x00404433` + `0x00404454` | `cmp ecx,0x35` / `jle` | **time** |
| `0x00404456` | `cmp ecx,0x38` / `jge` | **time** — só 54 e 55 caem no `xor eax,eax` de `0x00404463` |
| `0x0040452e` | `cmp BYTE [+0x17],0x17` | só na rota de **ML**, e sobre o slot **lido do vínculo**, não o pedido |
| `0x004046c1` | `cmp ebx,0x2` | **buffer**, não slot |

Na rota de seleção ela escreve `0x2ece0c + 23·time + 2·(time div 56) + slot` em
`[esi+ecx*4+0x28]` (`0x004046c1` acima é a cauda; a escrita é `0x00404490`), e
`[esi+ecx*4+0x28]` com `ecx = 11·buffer = 22` é exatamente o `0x43366c` que o
laço do `base_teamClick` testa. Os times 54 e 55 são os mesmos 46 jogadores que
o `src/core/Database.cpp:756-764` pula.

**O que isso fecha, e é a parte que importa**

A correção previa dois desfechos, e o segundo era o grande: *"se for propriedade
do formato que o `we2002_core` lê errado, a conta de offset do port está errada
para o slot 22 **em toda operação**"*. **Esse ramo está fechado.** A conta do
oráculo é a mesma do port, linear no slot, sem caso especial — o port não lê o
jogador errado no slot 22, nem em preço nem em nada.

**O que sobra, dito com precisão**

Uma contradição estreita: o `cmp DWORD PTR ds:0x43366c,0x0` de `0x004110a6`
observa **zero** num campo que a `0x00404374`, chamada três instruções antes
pela `0x004046e8`, acaba de preencher com valor **não nulo** — e a
`0x004046e8` não escreve nesse campo (ela o lê em `0x00404748`, e o que ela
escreve é o byte condicional em `0x0043365c`). Uma das três é falsa, e a
medição não diz qual:

1. a rota de seleção da `0x00404374` é a tomada para o slot 22;
2. `[esi+ecx*4+0x28]` com buffer 2 é `0x43366c`;
3. nada entre a escrita e o `cmp` zera o campo.

**Quem continuar começa daqui, e não da estaca zero.** O instrumento que falta é
o que a leitura estática não dá: `0x43366c` observado **em execução** na volta
do slot 22 — depurador sob Wine, ou a `0x00404374` decompilada no projeto do
Ghidra, que é o que a §8.10 do plano reserva para este tipo de pergunta. As
perguntas 1 (a ficha do slot 22 no oráculo) e 2 (clube de ML) continuam válidas
e continuam custando uma corrida de tela cada.

**Gates rodados**

- `golden-22-precos`, modo controle: `PASSOU: byte-identico`
- `golden_run_wte.sh` sobre a cópia plantada: `oraculo: fim, sem violacao de
  acesso`, saída 0
- `check_preco.py --check`: verde, 132 jogadores em 6 times
- `roms/` intocada; a cópia `work/p95.bin` apagada

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `wte/re/preco.md` | modificado — as duas medições e o ramo fechado |
| `wte/re/spec/MainForm.base_teamClick.md` | modificado — idem, resumido |

O `ULTIMO_SLOT_PRECADO = 21` **não muda**: o salto está confirmado, e agora com
plantio. O `.inc` e o `check_preco.py` ficam como estão.
