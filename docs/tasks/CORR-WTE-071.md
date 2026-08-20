---
id: CORR-WTE-071
title: "Correção: o mapa do .mcr diz 16 destinos, e a tabela dele tem 17"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-WTE-071: o mapa do `.mcr` diz 16 destinos, e a tabela dele tem 17

## Problema identificado

O `LAYOUT` do [`wte/tools/dump_mcr.py`](../../wte/tools/dump_mcr.py) tem **17**
destinos de escrita. Cinco lugares afirmam **16** — e um deles é o título de
seção do markdown gerado, logo acima da tabela que lista os 17.

O número não é computado: é literal escrito na prosa do gerador, ao lado de
vizinhos que são computados (`min(off for off, *_ in LAYOUT)` na mesma seção).
Por isso o `--check` não o alcança — ele confere que a saída bate com o
gerador, e o gerador é a fonte do erro.

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor/wte/tools
python3 -c "
import dump_mcr as m
from collections import Counter
print('total:', len(m.LAYOUT))
print('por bloco:', dict(Counter(o // m.BLOCO_BYTES for o, *_ in m.LAYOUT)))"
```

## Evidência

Medido:

```text
total: 17
por bloco: {2: 3, 3: 14}
```

Afirmado, nos cinco lugares:

| arquivo | linha | texto |
|---|---:|---|
| `wte/tools/dump_mcr.py` | 30 | "O editor grava 14 dos **16** destinos num bloco que o proprio diretorio..." |
| `wte/tools/dump_mcr.py` | 528 | `w("## O achado: 14 dos 16 destinos caem num bloco que o diretório diz livre\n")` |
| `wte/re/mcr.md` | 96 | o mesmo título, **gerado** pela linha acima |
| `wte/src/we2002_mcr.pas` | 13 | "dos **16** destinos, 14 caem no..." |
| `docs/tasks/28-import-de-mcr.md` | 145, 301 | "**16 destinos**, os dois lados"; "14 dos 16 destinos" |

A parte medida do enunciado está certa: os 14 do bloco 3 são exatos, e os
outros 3 caem no bloco 2 — `0x5404` (16 B de números), `0x5904` (276 B de
atributos) e `0x5910` (230 B de nomes). `14 + 3 = 17`.

`git show` mostra que o `LAYOUT` nasceu com 17 entradas no commit `923d587`,
que é o mesmo que introduziu o título. O número nunca bateu:

```bash
for c in 923d587 046fd71 939e369; do
  echo -n "$c LAYOUT="
  git show "${c}:wte/tools/dump_mcr.py" \
    | sed -n '/^LAYOUT = \[/,/^\]/p' | grep -cE '^\s+\(0x'
done
# 923d587 LAYOUT=17
# 046fd71 LAYOUT=17
# 939e369 LAYOUT=17
```

## Causa raiz

Contagem escrita à mão numa prosa cujos vizinhos são computados, e nenhum teste
fixa `len(LAYOUT)`.

## Correção

### Arquivo: `wte/tools/dump_mcr.py`

O título e o docstring passam a computar, como o `min(...)` da mesma seção já
faz. Algo na forma:

```python
fora = [o for o, *_ in LAYOUT if o // BLOCO_BYTES not in blocos_do_save(dire)]
w(f"## O achado: {len(fora)} dos {len(LAYOUT)} destinos caem num bloco "
  f"que o diretório diz livre\n")
```

O docstring do módulo (linha 30) não tem acesso a contagem em tempo de import
de forma limpa; a saída mais barata é trocar o número por "a maior parte dos
destinos", ou repetir a conta numa linha de `__doc__` montada. Qualquer das
duas serve — o que não pode continuar é o literal.

### Arquivo: `wte/tools/test_dump_mcr.py`

Um caso que fixa a contagem, para o próximo destino novo não envelhecer o texto
de novo:

```python
def test_o_titulo_conta_o_layout(self) -> None:
    md = M.gerar_markdown()          # ou o nome que o gerador usa
    self.assertIn(f"dos {len(M.LAYOUT)} destinos", md)
```

### Arquivo: `wte/src/we2002_mcr.pas`

Comentário do cabeçalho: `dos 16 destinos, 14 caem no` → `dos 17 destinos`.

### Arquivo: `docs/tasks/28-import-de-mcr.md`

Linhas 145 e 301: `16 destinos` → `17 destinos`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_mcr.py` | modificar |
| `wte/tools/test_dump_mcr.py` | modificar |
| `wte/re/mcr.md` | regerar (não editar à mão) |
| `wte/src/we2002_mcr.pas` | modificar |
| `docs/tasks/28-import-de-mcr.md` | modificar |

## Verificação

- [ ] `python3 -c "import dump_mcr as m; print(len(m.LAYOUT))"` e o número do
      título de `wte/re/mcr.md` são o mesmo
- [ ] `python3 wte/tools/dump_mcr.py --check` continua verde
- [ ] `python3 -m unittest test_dump_mcr` verde, com o caso novo
- [ ] `grep -rn '16 destinos' wte docs` não devolve nada
- [ ] `lazbuild wte/wte.lpi` compila
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
