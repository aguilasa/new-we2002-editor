# `re/spec/` — a especificação recuperada, um arquivo por handler

**Regra dura, da §2 do plano:** o decompilador serve para *responder
perguntas*. A resposta vem para cá em prosa, com o campo de **evidência**; o
Pascal é escrito a partir deste `.md`. **Nunca colar C++ decompilado aqui** —
nem na spec, nem no código.

Desde a **WTE-TASK-23** isso não é honra: o [`GABARITO.md`](GABARITO.md) fixa o
formato e o vocabulário de veredito, e o
[`../../tools/spec_index.py`](../../tools/spec_index.py) **recusa** o arquivo
que quebre a regra — bloco marcado `c`/`cpp`, nome inventado pelo Ghidra
(`undefined4`, `uVar1`, `local_1c`, `param_1`, `DAT_…`, `FUN_…`),
`__fastcall`, seção faltando, evidência fora do vocabulário, `nao portado` sem
justificativa, ou `implementado` sustentado só por observação de tela.

| Arquivo | O que é |
|---|---|
| [`GABARITO.md`](GABARITO.md) | o gabarito e o vocabulário — leia antes de escrever a primeira |
| [`INDICE.md`](INDICE.md) | **gerado.** Os 96 com o veredito corrente |
| `<formulario>.<handler>.md` | uma spec. O par é único; o nome solto não — há 16 `FormCreate` |

```sh
python3 wte/tools/spec_index.py           # regera o INDICE.md
python3 wte/tools/spec_index.py --check   # o que `make -C wte check` roda
```

As 96 entradas chegam nas **WTE-TASK-25 a 33**. Hoje são 96 `aberto`, e é a
[WTE-TASK-31](../../../docs/tasks/concluidos/31-fechamento-fase-4.md) que exige que nenhum
sobre.
