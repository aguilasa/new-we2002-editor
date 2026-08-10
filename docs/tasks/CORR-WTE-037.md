---
id: CORR-WTE-037
title: "Correção: a linha das recusas medidas na saída está deslocada, e o worklist da WTE-TASK-18 aponta para a linha errada"
type: correção
category: verificação
status: envelhecida
depends_on: []
---

# CORR-WTE-037: 493 das 498 recusas trazem número de linha da saída, não da entrada

## Problema identificado

`wte/tools/port_database_pas.py` roda dois conjuntos de recusa:

- `FORBIDDEN_ENTRADA`, sobre o texto **original** — 5 recusas hoje;
- `FORBIDDEN`, sobre o texto **já traduzido** — as outras 493, entre elas as 288
  de bloco, as 160 de cabeçalho de `for` e as 33 de `std::` sobrando.

O relatório e o `wte/re/transpilador.md` publicam `arquivo:linha` nos dois casos
como se a linha fosse a do arquivo em `src/core/`. Para o segundo conjunto ela é
a linha do texto traduzido, e **nada garante que os dois tenham a mesma
numeração**. Hoje não têm: `aplicar_subs` devolve `Database.cpp` com 1.698
linhas contra 1.704 da entrada.

O sintoma aparece de graça na própria tabela publicada, na única construção que
os dois conjuntos pegam:

| Motivo | Onde |
|---|---|
| `fallthrough de switch na entrada` | `Database.cpp:450`, `Database.cpp:**1258**` |
| `fallthrough de switch: o case do Pascal NAO cai…` | `Database.cpp:450`, `Database.cpp:**1256**` |

`1258` é onde o `[[fallthrough]];` está. `1256` é `case 52:`. Quem abrir o
worklist da WTE-TASK-18 pelo segundo número lê outra linha.

**Isto não é o mesmo defeito da [CORR-WTE-036](/docs/tasks/CORR-WTE-036.md), e
não morre com ela.** Consertar a regra 7 faz as contagens coincidirem *hoje*;
não existe invariante nenhum que impeça a próxima regra de reintroduzir o
deslocamento, e o teste que promete o contrário —
`test_a_linha_reportada_e_a_real` — exercita só o caminho da entrada
(`self.conferir("int a;\nint b;\ngoto fim;\n")`, sem tradução). O outro,
`test_o_relatorio_de_recusa_nomeia_arquivo_e_linha`, assere apenas `linha > 0`.

Junto vai um segundo desacerto do mesmo relatório: os cinco itens de
`FORBIDDEN_ENTRADA` são o **mesmo sítio físico** de cinco dos itens de
`FORBIDDEN` (os dois `[[fallthrough]]` e o `std::vector` de `Player.hpp:41`),
e a tabela os lista como linhas separadas sem dizer que uma é a varredura da
entrada e a outra a da saída. O "498 recusa(s), em 13 motivo(s)" conta registro,
não construção — e o texto não diz isso.

## Evidência

Deslocamento medido:

```console
$ python3 -c "... P.aplicar_subs(Database.cpp) ..."
linhas entrada: 1704
linhas saida  : 1698
entrada 1256: '\t\t\tcase 52:'
entrada 1258: '\t\t\t[[fallthrough]];'
saida  1256: '\t\t\t[[fallthrough]];'
```

O que o `--check` publica, com os dois números para a mesma construção:

```
2x fallthrough de switch na entrada
    src/core/Database.cpp:450, src/core/Database.cpp:1258
2x fallthrough de switch: o `case` do Pascal NAO cai para o proximo ramo. …
    src/core/Database.cpp:450, src/core/Database.cpp:1256
```

O teste que promete a linha real, e o caminho que ele não cobre:

```python
def test_a_linha_reportada_e_a_real(self) -> None:
    notas = self.conferir("int a;\nint b;\ngoto fim;\n")   # texto NAO traduzido
    self.assertEqual([n.linha for n in notas if "goto" in n.motivo], [3])
```

## Causa raiz

A linha reportada vem do texto sobre o qual a varredura roda, e a varredura da
saída roda sobre um texto cuja numeração ninguém obriga a coincidir com a do
arquivo em `src/core/`.

## Correção

### Arquivo: `wte/tools/port_database_pas.py`

Uma das duas, e a primeira é mais barata:

1. **Invariante de numeração.** `aplicar_subs` passa a garantir que a saída tem
   exatamente as mesmas linhas da entrada, abortando com o nome da regra que
   quebrou. Com o invariante, `linha` da saída **é** a linha do fonte, e a
   promessa que o relatório já faz passa a ser verdade.
2. Ou mapear a posição da saída de volta para a linha da entrada, guardando o
   deslocamento acumulado por regra.

Na mesma passada, dizer no relatório e no `transpilador.md` **qual varredura
produziu cada recusa** (entrada / saída), para que as duas linhas da mesma
construção deixem de parecer dois trabalhos.

### Arquivo: `wte/tools/test_port_database_pas.py`

- `test_a_linha_reportada_e_a_real` ganha a metade que falta: planta a
  construção depois de linhas que a tradução encurta e confere a linha **do
  fonte**.
- Um teste do invariante sobre as seis unidades reais.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/port_database_pas.py` | modificar |
| `wte/tools/test_port_database_pas.py` | modificar |
| `wte/re/transpilador.md` | modificar (regerado) |

## Verificação

- [ ] As duas linhas de `fallthrough` do `Database.cpp` apontam para `1258` nos
      dois motivos, e `sed -n '1258p' src/core/Database.cpp` mostra
      `[[fallthrough]];`
- [ ] Cada recusa do `transpilador.md` diz se veio da varredura da entrada ou da
      saída
- [ ] `python3 wte/tools/port_database_pas.py --check` verde; duas execuções dão
      bytes iguais
- [ ] `python3 -m unittest discover -s wte/tools -p 'test_*.py'` verde
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução

**Envelhecida em:** 2026-08-10 (reprodução da evidência do lote `/corrigir-tudo`
de 036–043 — **não corrigida**, porque o sintoma não existe mais)

O commit `7b642f7` (WTE-TASK-18) reescreveu o relatório de recusa e a
divergência sumiu com ele. Três medidas:

1. **Não há mais recusa publicando `arquivo:linha` do fonte.** A varredura da
   saída passou a rodar sobre o Pascal e a reportar as coordenadas **dele**:

   ```python
   notas += conferir(FORBIDDEN, pascal, f"{unit}.pas", pascal=True)
   ```

   `pascal` é exatamente o texto que vai para o disco, então a linha publicada
   é a linha do `.pas`. A varredura da entrada continua sobre o texto original
   e soma o deslocamento do item (`tp.recusar(it.linha + nota.linha - 1, …)`),
   que é a linha do fonte. O rótulo entrada/saída que esta correção pedia ficou
   implícito no **nome do arquivo** de cada recusa.

2. **Não há recusa nenhuma.** As 498 foram fechadas:

   ```
   $ python3 wte/tools/port_database_pas.py --check
   port_database_pas: wte/re/transpilador.md: ok
   … (as seis unidades) …
   $ grep -c 'Database.cpp:' wte/re/transpilador.md
   0
   ```

   A seção "Recusas em aberto" do `transpilador.md` diz **"Nenhuma."**, e as
   duas linhas de `fallthrough` que a evidência confronta (`1256` contra `1258`)
   não são mais publicadas.

3. **O invariante de numeração que esta correção pedia foi entregue pela
   [CORR-WTE-036](/docs/tasks/CORR-WTE-036.md)**, no mesmo lote:
   `test_nenhuma_regra_reduz_a_contagem_de_linhas` roda o `SUBS` regra a regra
   sobre as seis unidades e reprova qualquer uma que mude a contagem de linhas.
   Medido depois dela: `aplicar_subs(Database.cpp)` sai com 1.704 linhas, as
   mesmas da entrada.

Corrigir o que já não está quebrado é como se introduz regressão; esta fica
registrada e fechada sem commit de código.

