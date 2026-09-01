---
id: CORR-WTE-106
title: "Correção: o check_divergencias.py é o único gate de recusa sem teste — as \"três recusas vistas\" não deixaram artefato"
type: correção
category: verificação
status: concluído
depends_on: []
---

# CORR-WTE-106: o gate das divergências não tem teste

## Problema identificado

A [WTE-TASK-35](/docs/tasks/concluidos/35-divergencias-deliberadas.md) mecanizou a metade
mecanizável do registro no
[`check_divergencias.py`](../../../wte/tools/check_divergencias.py), e o critério
de conclusão afirma:

> **Mecanizado nos dois sentidos, com as três recusas vistas**

**Ver não é o mesmo que deixar visto.** O arquivo `wte/tools/test_check_divergencias.py`
**não existe**, e a palavra `recusa` não aparece no gerador. As recusas foram
observadas na execução e não sobreviveram a ela: nada no repositório volta a
exercitá-las.

É a regra que o próprio projeto escreveu, no cabeçalho do
`test_check_fase4.py`: *"Guarda nunca exercitada e guarda ausente."* Todo irmão
desta família tem o par — `check_fase1/2/3/4`, `check_golden`, `check_preco`,
`check_edicao`, `check_glifos_disabled`, `cobertura_gate`, `gravacao_controle`,
`spec_index`. As nove ferramentas sem teste são medidoras do `.exe`
(`check_barras`, `check_bitfields`, `sonda_dorsal`, os `dump_*`), cuja saída é
a própria medição; **esta é a única guarda de recusa sem teste.**

**O gate funciona hoje — foi conferido nesta revisão**, com as quatro recusas
plantadas num espelho do repositório. O que falta é a versão versionada disso,
para que a próxima refatoração não o desligue em silêncio.

## Evidência

O que não existe:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
ls wte/tools/test_check_divergencias.py; grep -c recusa wte/tools/check_divergencias.py
```

```text
ls: cannot access 'wte/tools/test_check_divergencias.py': No such file or directory
0
```

As quatro recusas, exercitadas em 2026-08-25 sobre uma cópia da árvore em
`/tmp` (o repositório não foi tocado) — **as quatro saem com código 2**:

```text
EXIT_1=2  a excecao `glifo_cinza` sumiu de compara_tela.py, e a secao 2 de
          divergencias.md continua a explicando. [...] PROSA VENCIDA
EXIT_2=2  a excecao `ULTIMO_SLOT_PRECADO` (em check_preco.py) nao tem secao 5
          em divergencias.md. Excecao no golden sem entrada aqui e BURACO
EXIT_3=2  a excecao `pendente_32` VOLTOU a compara_tela.py, e a secao 9 de
          divergencias.md diz que ela foi retirada
EXIT_4=2  roteiro declarando faixa `conhecida:` sem entrada em divergencias.md:
          golden-01-arranque
```

Cada uma foi plantada assim, no espelho:

| # | O que se planta | Sentido que ele prova |
|---|---|---|
| 1 | renomear `"glifo_cinza"` no `compara_tela.py` | isenção some e a entrada fica → prosa vencida |
| 2 | renumerar `## 5.` no `divergencias.md` | isenção viva e entrada some → buraco |
| 3 | acrescentar `"pendente_32"` ao `compara_tela.py` | retirada que volta pela porta dos fundos |
| 4 | acrescentar `conhecida: 1..2` a um roteiro | faixa nova sem entrada, e a §8 vira mentira |

## Causa raiz

O gerador nasceu junto com o documento, e o par de teste que todos os irmãos
têm não foi escrito.

## Correção

### Arquivo: `wte/tools/test_check_divergencias.py` *(criar)*

Os quatro casos acima, cada um montando a entrada **em memória ou em
`tempfile`**, no molde do `test_check_fase4.py` — que já monta fonte falsa e
roda o detector sobre ela, sem abrir o `.exe` e sem precisar de `DISPLAY`.

Mais dois casos baratos, que amarram a tabela ao mundo:

- **o estado de hoje passa** — `EXCECOES` e `RETIRADAS` conferidos contra a
  árvore real, que é o teste que pega alguém removendo uma isenção sem passar
  por aqui;
- **`RETIRADAS` não casa menção em comentário.** O predicado é
  `re.search(rf'"{nome}"')`, e o `compara_tela.py` **cita** `pendente_32` na
  prosa que explica a remoção — passa hoje só porque a citação usa crase e não
  aspas. Um caso que planta a menção entre aspas num comentário documenta que
  o casamento é por aspas, de propósito, em vez de deixar isso ao acaso.

### Arquivo: `docs/tasks/concluidos/35-divergencias-deliberadas.md`

Trocar *"com as três recusas vistas"* por a referência ao teste, quando ele
existir. Recusa vista sem artefato é afirmação sobre o passado; recusa em teste
é afirmação sobre o futuro, e é essa que o critério quer.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/test_check_divergencias.py` | criar |
| `docs/tasks/concluidos/35-divergencias-deliberadas.md` | modificar |

## Verificação

- [x] `python3 -m unittest discover -p 'test_*.py'` em `wte/tools` conta os
      casos novos, e todos passam — a bateria foi de **789** para **809**
- [x] Cada um dos quatro reprova quando a plantação é feita, e passa sem ela —
      os quatro rodados isoladamente, mais o controle sem plantação
- [x] `make -C wte check` verde (809 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

Criado o `wte/tools/test_check_divergencias.py` com **20 casos**, no molde do
`test_check_golden.py`: espelho da árvore em `tempfile`, caminhos do módulo
repontados, nada de `.exe`, `DISPLAY` ou Wine. A bateria do `make -C wte check`
foi de 789 para 809.

Os quatro sentidos da recusa estão plantados e cada um foi rodado isoladamente
para provar que reprova **por causa** da plantação, com o controle sem
plantação passando: exceção que some (prosa vencida), seção que some (buraco),
retirada que volta, faixa `conhecida:` nova. Mais os dois casos baratos que a
CORR pedia — o estado de hoje passando contra a árvore real, e o casamento por
aspas do `RETIRADAS`.

**O espelho é montado a partir das tabelas reais do módulo**, não de uma cópia
literal delas: exceção nova no `EXCECOES` entra nos testes sozinha, em vez de
os deixar medindo um mundo que não existe mais. Foi escolha deliberada — a
alternativa era um espelho fixo que envelhece exatamente como o documento que
este gate protege.

O critério da WTE-TASK-35 e o espelho dele no `progresso.md` trocaram *"com as
três recusas vistas"* pela referência ao teste.

**Problemas encontrados:**

**A enumeração da CORR não bate, e a conclusão dela sim.** Ela diz que as nove
ferramentas sem teste são medidoras do `.exe` (`check_barras`,
`check_bitfields`, `sonda_dorsal`, os `dump_*`). Medido, há uma décima:
o `check_lcl_combo.py`, que não é nenhuma dessas. Ele mede a **LCL instalada**
— se o `TComboBox` do gtk2 dispara `OnChange` em `ItemIndex :=` — e o cabeçalho
dele diz o mesmo contrato do `check_barras`: confere e sai 2. É medidor do
mundo de fora, mesma família; a saída dele *é* a medição. A afirmação
*"esta é a única guarda de recusa sem teste"* continua verdadeira; só a lista
de exemplos era incompleta.

Três casos estouraram com `ValueError` na primeira corrida: o módulo relata o
caminho como `DOC.relative_to(ROOT)`, e um espelho em `/tmp` não é subpath da
árvore real. É artefato do espelho, **não defeito do gate** — em uso normal o
documento mora sempre sob a raiz —, e o conserto foi repontar `ROOT` junto, não
afrouxar a ferramenta. Está escrito no teste para a próxima pessoa não hesitar.

A saída do `main()` é engolida nos casos de código de saída: sem isso o
relatório de uma recusa **plantada** aparecia no meio do `make -C wte check`, e
quem lesse o gate veria a mensagem de um problema que não existe.

**Arquivos criados/modificados:**

- `wte/tools/test_check_divergencias.py` — criado, 20 casos
- `docs/tasks/concluidos/35-divergencias-deliberadas.md` — o critério
- `docs/tasks/concluidos/progresso.md` — o espelho do critério (varredura)
