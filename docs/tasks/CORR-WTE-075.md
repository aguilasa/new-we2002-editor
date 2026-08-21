---
id: CORR-WTE-075
title: "Correção: o teste do round-trip sobrescreve a medição versionada e a repõe na mão"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-075: o teste do round-trip sobrescreve a medição versionada e a repõe na mão

## Problema identificado

`do_roundtrip()` do [`wte/tools/dump_mcr.py`](../../wte/tools/dump_mcr.py)
grava num destino fixo, que é arquivo **versionado**:

```python
IDA_E_VOLTA = ROOT / "wte" / "re" / "mcr-roundtrip.tsv"
...
IDA_E_VOLTA.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
```

Como não há como redirecionar a saída, o teste que exercita a rotina
(`TestRoundTrip.test_a_medicao_e_escrita`) escreve **por cima da medição
versionada** com dois cartões sintéticos, e a repõe num `finally`:

```python
antigo = (M.IDA_E_VOLTA.read_text(encoding="utf-8")
          if M.IDA_E_VOLTA.is_file() else None)
try:
    ...
finally:
    if antigo is None:
        M.IDA_E_VOLTA.unlink(missing_ok=True)
    else:
        M.IDA_E_VOLTA.write_text(antigo, encoding="utf-8")
```

Duas consequências:

1. **`make -C wte check` reescreve um arquivo de `wte/re/` toda vez.** O alvo
   roda os testes antes dos `--check`, e a árvore só volta ao lugar porque o
   `finally` roda. Interrupção que não deixa o `finally` correr — `SIGKILL`,
   falta de espaço, o disco cheio de uma corrida de golden — deixa a medição
   **substituída por dado sintético**, com uma linha `numeros ... 1` que parece
   medição de verdade;
2. **o ruído vaza para a bateria.** A saída de `do_roundtrip` é `print` direto,
   e sai no meio do relatório do `unittest`:

   ```text
   Ran 31 tests in 0.486s
   OK (skipped=2)
     nomes: 230/230 iguais
     ...
     arquivo inteiro: 1 bytes diferentes
     wte/re/mcr-roundtrip.tsv
   ```

Nenhum outro medidor do `wte/tools/` faz isso: os que escrevem em `wte/re/`
recebem o destino ou são exercitados contra `tempfile`.

## Evidência

A linha que o teste planta, e que ficaria no disco se o `finally` não corresse
(`M.do_roundtrip` sobre dois cartões que diferem em um byte de `0x5404`):

```text
numeros	16	15	1	deslocamentos 0
arquivo inteiro	131072	131071	1	a.mcr contra b.mcr
```

A medição de verdade, versionada, que ela substitui:

```text
numeros	16	16	0	-
arquivo inteiro	131072	131072	0	entrada.mcr contra volta.mcr
```

Os dois arquivos têm o mesmo nome, o mesmo cabeçalho e a mesma forma. Só o
conteúdo distingue medição de fixture de teste.

## Causa raiz

Destino embutido na função em vez de parâmetro, e o teste consertando o efeito
em vez da causa.

## Correção

### Arquivo: `wte/tools/dump_mcr.py`

`do_roundtrip` recebe o destino, com o versionado de default:

```python
def do_roundtrip(antes: str, depois: str,
                 destino: Path = IDA_E_VOLTA) -> int:
    ...
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8",
                       newline="\n")
```

`linhas_do_roundtrip()` ganha o mesmo parâmetro, pelo mesmo motivo.

### Arquivo: `wte/tools/test_dump_mcr.py`

O teste passa a apontar para o `tempfile` que já cria, e o `try/finally` de
reposição some junto:

```python
def test_a_medicao_e_escrita(self) -> None:
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.mcr", Path(td) / "b.mcr"
        destino = Path(td) / "mcr-roundtrip.tsv"
        a.write_bytes(self.cartao(x5404=b"\x01\x02"))
        b.write_bytes(self.cartao(x5404=b"\x01\x03"))
        self.assertEqual(M.do_roundtrip(str(a), str(b), destino), 0)
        por_campo = {ln[0]: ln for ln in M.linhas_do_roundtrip(destino)}
    self.assertEqual(por_campo["numeros"][3], "1")
    self.assertEqual(por_campo["nomes"][3], "0")
```

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/dump_mcr.py` | modificar |
| `wte/tools/test_dump_mcr.py` | modificar |

## Verificação

- [x] `git status --porcelain wte/re/mcr-roundtrip.tsv` fica vazio durante a
      bateria — `mtime` idêntico antes e depois
      (`2026-08-20 22:08:23.917254716`, 207 bytes)
- [x] `python3 -m unittest test_dump_mcr` verde, sem o `try/finally` — 33
      testes, `OK`, e sem o resumo vazando no relatório
- [x] `python3 wte/tools/dump_mcr.py --roundtrip work/entrada.mcr work/volta.mcr`
      continua escrevendo em `wte/re/mcr-roundtrip.tsv` — reescreveu byte a
      byte igual
- [x] `make -C wte check` verde — 645 testes, `OK (skipped=1)`, rc=0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-20

**Resumo do que foi feito:**

`do_roundtrip(antes, depois, destino=IDA_E_VOLTA)` e
`linhas_do_roundtrip(destino=IDA_E_VOLTA)`. O default mantém a linha de comando
como estava; o teste passa a apontar para o `tempfile` que já cria, e o
`try/finally` de reposição sumiu junto.

O `print` da rotina fica — ele é para quem a chama da linha de comando —, e o
teste o contém num `contextlib.redirect_stdout`. O relatório do `unittest`
voltou a terminar no `OK`.

Um caso novo (`test_a_medicao_versionada_nao_e_tocada`) roda o anterior entre
duas leituras de `wte/re/mcr-roundtrip.tsv` e compara os bytes: se alguém
reintroduzir o destino fixo, ele acusa.

**Problemas encontrados:**

Nenhum. O `_curto()` foi acrescentado ao `dump_mcr.py` pela mesma razão que já
existe no `gravacao_controle.py`: o `relative_to(ROOT)` do `print` final
estouraria com o destino em `/tmp`.

**Arquivos criados/modificados:**

- `wte/tools/dump_mcr.py`
- `wte/tools/test_dump_mcr.py`
