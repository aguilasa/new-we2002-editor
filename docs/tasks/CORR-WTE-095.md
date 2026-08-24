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

- [ ] a causa escrita, com o endereço que a produz
- [ ] `golden-22-precos` verde depois, com o controle fechando antes
- [ ] `check_preco.py --check` verde
- [ ] se a conclusão for "defeito do original", linha na WTE-TASK-35

## Log de Execução *(preenchido após execução)*
