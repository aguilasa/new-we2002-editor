---
id: CORR-WTE-126
title: "Correção: os itens 1 e 2 da §8.2 não têm roteiro versionado, e a §8.2 é a única seção fora da convenção que a CORR-WTE-123 fixou"
type: correção
category: verificação
status: pendente
depends_on: []
---

# CORR-WTE-126: dois terços da §8.2 continuam sem o comando que a "Definição de pronto" promete

## Problema identificado

A [PAR-TASK-02](/docs/tasks/PAR-TASK-02.md) fecha com este item marcado:

```markdown
- [x] Cada item com evidência: o comando, a faixa que saiu do golden_compare.py,
      e o veredito
```

**O item 3 cumpre** — a [CORR-WTE-124](/docs/tasks/CORR-WTE-124.md) criou o
`tools/par/8.2-numeros-default.sh`, e a §8.2 o cita ao lado da faixa. **Os itens
1 e 2 não.** Nenhum dos dois nomeia roteiro, e não existe arquivo em
`tools/par/` que os produza:

| item da §8.2 | roteiro |
|---|---|
| 1 — digitar 33 numa seleção → 32 na tela, 31 no disco | **nenhum** |
| 2 — digitar 33 num clube de ML → 32 no disco (sem clamp) | **nenhum** |
| 3 — `CMD_DEFAULT_NUMBERS` | `tools/par/8.2-numeros-default.sh` |

Isto é a [CORR-WTE-123](/docs/tasks/CORR-WTE-123.md) de novo, e desta vez
**depois** de a convenção existir: a 123 foi concluída em **2026-08-28**,
criando `tools/par/` exatamente para que corrida verde tivesse estímulo
versionado; a PAR-TASK-02 fechou em **2026-08-29**.

A §8.2 é hoje a **única** seção fora da convenção:

```text
$ for s in 8.1 8.2 8.3 8.4; do
    printf "%s: %s roteiro(s)\n" "$s" "$(ls tools/par/$s-*.sh | wc -l)"; done
8.1: 6 roteiro(s)      (5 itens)
8.2: 1 roteiro(s)      (3 itens)   <-- aqui
8.3: 3 roteiro(s)      (3 itens)
8.4: 5 roteiro(s)      (5 itens)
```

O que se perde é específico, não cerimonial. Os itens 1 e 2 são os que medem o
**clamp e a assimetria** — o comportamento que a §8.2 existe para fixar — e os
números que a §8.2 afirma (`32` na tela, `31` no disco na seleção, `32` no clube
de ML) não podem ser re-derivados por ninguém. São também os dois itens cuja
medição **não passa por byte cru**: o Log registra que ler o disco à mão dava
`63`, "um número que não significa nada", e que só o `dump_estado` decodifica o
bitfield empacotado. Uma medição que precisa de instrumento e não registra a
invocação do instrumento não é repetível por construção.

## Evidência

O que existe:

```text
$ ls tools/par/8.2-*
tools/par/8.2-numeros-default.sh
```

O que a §8.2 diz nos dois itens sem roteiro:

```text
$ sed -n '/^### 8.2/,/^### 8.3/p' docs/PARIDADE-FUNCIONAL.md | grep -E '^- \[x\]'
- [x] Digitar 33 numa seleção → tem que virar 32 na tela e no disco — **a tela
- [x] Digitar num clube de ML (sem clamp) e conferir — o mesmo 33 grava **32**
- [x] `CMD_DEFAULT_NUMBERS` e conferir que o `number` do jogador seguiu
      (`tools/par/8.2-numeros-default.sh`) — ...
```

Só o terceiro traz o parêntese com o arquivo.

**O comportamento que os dois itens afirmam está correto** — esta revisão o
conferiu no código dos dois lados, que são linha a linha o mesmo:

```text
$ sed -n '6644,6653p' legacy/mfc/edDlg.cpp
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc1.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_1 = i-1;
		gioc[462+((id-1)*23)].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[0] = i-1;
```

```text
$ sed -n '464,473p' src/app/TeamView.cpp
        if (value > 32) {
            value = 32;
            txt_number_[slot]->setText(QStringLiteral("32"));
        }
        we2002::SetSquadNumberAt(db_.teams[id - 1].squad_numbers, slot,
                                 static_cast<std::uint32_t>(value - 1));
        db_.players[PLAYERS_NC + ((id - 1) * 23) + slot].number = value;
    } else if (id > 63 && id < 96) {
        db_.ml_teams[id - 64].raw_numbers[slot] = static_cast<char>(value - 1);
```

Clamp e `value - 1` na seleção, `value - 1` **sem clamp** no clube de ML: a
assimetria que os itens 1 e 2 afirmam está no código, e o `if(i>32)` aparece 23
vezes no legado, uma por slot. **O que falta não é a verdade do achado — é a
corrida que a demonstra pela tela.**

## Causa raiz

A PAR-TASK-02 mediu os itens 1 e 2 em 2026-08-28, antes de a CORR-WTE-123
criar `tools/par/` no mesmo dia, e o fechamento de 2026-08-29 versionou o
roteiro só do item que a CORR-WTE-124 tocou.

## Correção

### Arquivo: `tools/par/8.2-clamp-selecao.sh` (novo)

Selecionar uma seleção nacional, digitar `33` num `TXT_NUMBER*`, tirar o foco
(o commit é no `editingFinished`, como no `EN_KILLFOCUS` do original) e deixar
a tela pronta para gravação. O cabeçalho diz qual time seleciona e qual slot
usa — a §8.2 afirma um valor de disco, e ele depende dos dois.

### Arquivo: `tools/par/8.2-clamp-clube-ml.sh` (novo)

O mesmo `33`, num clube de ML, para medir a ausência de clamp.

Os dois no molde dos existentes: trecho de shell que os **dois** hooks recebem
sem alteração, `par_click` a partir das coordenadas do `.rc`, e a nota de que
`ed.exe` e port precisam de `End`/`shift+Home`/`BackSpace` para limpar campo —
`Ctrl+A` não seleciona tudo num `CEdit` do Win32.

### Arquivo: `docs/PARIDADE-FUNCIONAL.md` §8.2

Em cada um dos dois itens, o nome do roteiro ao lado da faixa, como o item 3 já
faz. **E a invocação do `dump_estado`** que produziu o `31` e o `32` — sem ela
os dois números continuam sem fonte re-executável, mesmo com roteiro.

### Arquivo: `docs/tasks/PAR-TASK-02.md`

Apontar cada item ao seu roteiro no Log.

**Remedir ao versionar.** Roteiro reconstruído com faixa remedida é evidência;
roteiro novo ao lado de faixa antiga só transporta a lembrança para um arquivo
com nome melhor.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/par/8.2-clamp-selecao.sh` | criar |
| `tools/par/8.2-clamp-clube-ml.sh` | criar |
| `docs/PARIDADE-FUNCIONAL.md` | modificar |
| `docs/tasks/PAR-TASK-02.md` | modificar |

## Verificação

- [ ] `ls tools/par/8.2-*` devolve três arquivos, um por item da §8.2
- [ ] Cada item da §8.2 nomeia o seu roteiro, e os dois primeiros também a
      invocação do `dump_estado` que dá o `31` e o `32`
- [ ] Os dois roteiros novos rodam nos dois hooks sem edição:
      `WE2002_GOLDEN_MODE=gui GOLDEN_EDIT="$(cat <roteiro>)"
      GOLDEN_GUI_EDIT="$GOLDEN_EDIT" bash tools/golden_check.sh
      roms/ptbr-remaster.bin` sai `OK`
- [ ] Cada um com **controle positivo** registrado — a cópia gravada contra a
      imagem original, com as faixas, não só o veredito do golden
- [ ] `ctest --preset debug -E golden` continua 4/4
- [ ] `roms/` intocada — toda corrida sobre cópia

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
