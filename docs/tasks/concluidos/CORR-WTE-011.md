---
id: CORR-WTE-011
title: "Correção: o critério de limite do dump_offsets.py aborta num sentido só, e a janela de plausibilidade sai do nosso próprio header"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-011: o `offsets.md` promete mais guarda do que o script tem

## Problema identificado

O `wte/re/offsets.md` descreve o limite superior da tabela assim:

> O limite superior é medido por **dois testes independentes que têm de
> concordar**, e o script aborta se não concordarem [...] o script aborta se os
> dois limites não coincidirem.

O `check_table_bounds()` do `dump_offsets.py` aborta em **um** dos dois sentidos:

```python
            agrees = nxt == table.end_va
            self.bounds.append((table, nxt, agrees))
            if nxt is not None and not agrees and nxt < table.end_va:
                raise DumpError(...)
```

Quando o código referencia um endereço **além** do fim medido pelo conteúdo,
`agrees` fica `False`, nada aborta e o markdown é gerado com a tabela do jeito
que o conteúdo disse. Hoje os dois sentidos coincidem nas duas tabelas, então o
comportamento não muda nada — o defeito é a promessa, não a medida.

O sentido que aborta é o que importa para a §8.7 (conteúdo dizendo *mais* do que
o código sustenta), e é defensável abortar só nele. O que não é defensável é o
texto gerado prometer as duas direções: quem confiar nele vai supor que
`agrees=False` não passa, quando passa em silêncio.

**Segundo problema, no mesmo critério.** O "primeiro dword que não é plausível
nem zero" depende de `Plausible`, que é construído a partir dos valores do
**nosso** `Offsets.hpp`:

```python
        values = [v for _, v in declared]
        self.plausible = Plausible(values)

        bad = [n for n, v in declared if not self.plausible(v)]
        if bad:
            raise DumpError(... "O filtro so vale enquanto aceita 100% do que "
                            "ja se sabe ser offset" ...)
```

A guarda que confere "o filtro aceita 100% do que já se sabe" é **tautológica na
parte de faixa**: a faixa é o `[min, max]` desses mesmos valores. Ela só morde
nas partes que não vêm dali (geometria de setor, "não é texto").

A consequência prática é uma **acoplagem não documentada**: o limite medido da
tabela do Obocaman se move quando alguém mexe no `Offsets.hpp` do `newWe2002` —
e a WTE-TASK-19 existe justamente para acrescentar offsets lá. Um valor novo
fora da faixa atual alarga a janela e pode fazer a corrida engolir o dword
seguinte, que é a armadilha §8.7 entrando pela porta dos fundos.

## Evidência

**Sentido que não aborta**, medido nesta revisão removendo do índice de
referências as que caem logo após a tabela 1 (o resto intocado):

```
B) proxima ref alem do fim: [('0x4231a0', '0x4231e8', '0x423247', False),
                             ('0x423634', '0x423648', '0x423648', True)]
```

`agrees=False` na tabela 1 e **nenhum aborto** — o `generate()` seguiria e o
`offsets.md` sairia normalmente.

**Sentido que aborta**, com uma referência plantada dentro da tabela:

```
A) ABORT -> a tabela em 0x4231a0 vai ate 0x4231e8 pelo conteudo, mas o codigo
   referencia 0x4231d0 antes disso. Os dois criterios de limite discordam [...]
```

**A janela move o limite.** Acrescentando ao header um valor implausível
(`OFS_PLANTADO = 999999999`), a guarda de plausibilidade **não** dispara — ela
não pode, porque a faixa acabou de ser esticada por esse mesmo valor. O que
dispara é a guarda de limite, e o motivo é revelador: a tabela passou a terminar
em `0x4231ec`, um dword adiante:

```
C) ABORT -> a tabela em 0x4231a0 vai ate 0x4231ec pelo conteudo, mas o codigo
   referencia 0x4231e8 antes disso.
```

Neste caso a segunda guarda salvou a medida. Ela salva porque a referência de
código estava lá; uma corrida sem referência logo adiante não teria esse anteparo.

Estado atual, para registro — as duas tabelas concordam nos dois critérios, e a
medida publicada está certa:

```
tabela 0x4231a0 end=0x4231e8 | proxima ref de .data: 0x4231e8 | concorda: True
tabela 0x423634 end=0x423648 | proxima ref de .data: 0x423648 | concorda: True
```

## Causa raiz

O texto do `offsets.md` descreve a intenção da guarda; o código implementa a
metade que importa, e a janela de plausibilidade herda os limites do arquivo que
ela deveria julgar.

## Correção

`wte/re/offsets.md` é **gerado** — as duas correções entram no
`wte/tools/dump_offsets.py`.

### Arquivo: `wte/tools/dump_offsets.py`

1. **Dizer a regra que existe.** Em `render_md()`, trocar "o script aborta se os
   dois limites não coincidirem" por a regra real: aborta quando o código
   referencia endereço **antes** do fim medido pelo conteúdo — o sentido que
   caracteriza a armadilha §8.7 —, e o sentido oposto sai como aviso, não como
   falha. Ajustar o docstring de `check_table_bounds()` junto, que promete o
   mesmo.
2. **Emitir o aviso.** Quando `agrees` for falso no sentido que não aborta,
   imprimir uma linha na saída padrão (como o `dfm_extract.py` faz para blob não
   materializado, [CORR-WTE-004](/docs/tasks/concluidos/CORR-WTE-004.md)) e registrar a
   discordância no markdown, em vez de ela sumir dentro de `self.bounds`.
3. **Documentar a acoplagem com o `Offsets.hpp`.** A seção "O critério, escrito"
   passa a dizer que a faixa de plausibilidade sai do `[min, max]` dos 69 valores
   declarados, e que por isso a guarda de "aceita 100% do que já se sabe" cobre
   geometria de setor e texto, **não** a faixa. Com a consequência escrita: a
   WTE-TASK-19 acrescenta offsets, e um valor novo fora da faixa atual muda a
   janela — quem acrescentar tem de reconferir o limite das tabelas.

Alternativa considerada e **não** recomendada: congelar a faixa em constante. A
faixa derivada é o que faz o filtro acompanhar o que o projeto aprende; o que
falta não é rigidez, é a acoplagem escrita e um aviso quando ela mexe no limite.

### Arquivo: `wte/re/offsets.md`

Regerado, nunca editado à mão.

### Arquivo: `wte/tools/test_dump_offsets.py`

No molde do [`test_dump_strings.py`](../../../wte/tools/test_dump_strings.py), que a
[CORR-WTE-008](/docs/tasks/concluidos/CORR-WTE-008.md) criou: fixar os três casos que esta
revisão plantou à mão — referência antes do fim **aborta**, referência além do
fim **avisa e segue**, e valor implausível no header alarga a janela (com a
mensagem que sai hoje). Sem o `.exe`, montando as estruturas em memória; a parte
que precisar do binário fica sob `skipUnless`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_offsets.py` | modificar |
| `wte/re/offsets.md` | regerar (nunca editar à mão) |
| `wte/tools/test_dump_offsets.py` | criar |
| `wte/tools/README.md` | modificar — linha na tabela de testes |

## Verificação

- [x] O `offsets.md` gerado descreve a regra de aborto que o código tem
- [x] Discordância no sentido que não aborta sai como aviso e aparece no
      markdown — o bloco `> **Aviso.**` é emitido por tabela discordante.
      **Não aparece no `offsets.md` de hoje**, e não deveria: as duas tabelas
      concordam. O caminho está coberto por teste, não por observação
- [x] A seção do critério registra que a faixa vem do `Offsets.hpp` e o que isso
      implica para a WTE-TASK-19 — `offsets.md:49`
- [x] `python3 -m unittest` sobre `wte/tools/test_dump_offsets.py` verde, com os
      três casos plantados — **14 casos**, os três entre eles
- [x] `python3 wte/tools/dump_offsets.py --check` verde depois de regerar
- [x] Rodar o gerador duas vezes dá bytes iguais
- [x] `make -C wte check` verde
- [x] `roms/` intocada; `we-team-editor.exe` aberto só para leitura

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-06

**Resumo do que foi feito:**

As três correções entraram no gerador; o `offsets.md` foi regerado.

1. **A regra que existe, dita.** O texto e o docstring de
   `check_table_bounds()` passaram a descrever a assimetria em vez de prometer
   simetria: referência **antes** do fim medido pelo conteúdo aborta — é a §8.7
   em pessoa, publicar ali daria como offset um slot que ninguém aponta —, e
   referência **depois** avisa e segue, porque o intervalo publicado continua
   sendo o que o conteúdo sustenta e não há número errado a emitir.
2. **O aviso.** Sai como `AVISO:` na saída padrão, no molde da CORR-WTE-004, e
   como um bloco de citação na seção da tabela, para não sumir dentro de
   `self.bounds` — sem ele o único rastro seria a palavra "divergem" numa
   célula, que um leitor supõe impossível.
3. **A acoplagem, escrita.** A seção do critério agora diz que a faixa é
   literalmente o `[min, max]` dos 69 valores do nosso `Offsets.hpp`, que por
   isso a guarda de "aceita 100% do que já se sabe" é **tautológica na parte
   de faixa** (ela morde nos cortes de geometria e de texto), e que a
   WTE-TASK-19 move essa janela ao acrescentar offsets — quem acrescentar tem
   de reconferir o limite das duas tabelas. Congelar a faixa numa constante foi
   considerado e recusado, com o motivo escrito.

`wte/tools/test_dump_offsets.py`, **14 casos**. Os três plantados pela revisão
mais: sem referência alguma depois; referência à própria base não conta como
próxima (senão abortaria sempre); segunda tabela ainda conferida quando a
primeira passa; e a faixa de plausibilidade como propriedade — o `[min, max]`,
o alargamento por valor novo, a tautologia da guarda, e os dois cortes que
**não** vêm do header. A regra de confronto é exercitada chamando o método
desligado da classe sobre um objeto mínimo: monta-se `Run` em memória, sem
`.exe`. A medida real das duas tabelas fica sob `skipUnless`.

**Problemas encontrados:**

Nenhum. Oito mutações do gerador rodadas numa cópia em sandbox: abortar nos
dois sentidos, nunca abortar, apagar o aviso, contar a base como próxima
referência, tirar a faixa do header, desligar o corte de faixa e o de geometria
— as sete reprovam. A oitava era controle (`break` → `continue` num laço
inócuo) e **passa**, que é o resultado desejado: bateria que reprova qualquer
mudança não mede nada.

**Arquivos criados/modificados:**

- `wte/tools/dump_offsets.py` — `check_table_bounds()` e três trechos de
  `render_md()`
- `wte/re/offsets.md` — regerado
- `wte/tools/test_dump_offsets.py` — criado
- `wte/tools/README.md` — linha na tabela de testes
- `docs/tasks/concluidos/correcoes-progresso.md`
