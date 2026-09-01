---
id: CORR-WTE-044
title: "Correção: o oráculo comportamental está morto e a fase 4 é circular"
type: correção
category: comportamento
status: concluído
depends_on: ["WTE-TASK-24"]
---

# CORR-WTE-044: quebrar a circularidade do oráculo A

## Problema identificado

O `wte.exe` morre ao trocar de time com as duas ROMs deste repositório. Ele é o
**oráculo A** do projeto (plano §4.2), e a
[WTE-TASK-22](/docs/tasks/concluidos/22-harness-golden.md) monta o gate golden em cima
dele. Sem gate, nenhum handler da fase 4 pode ser verificado.

A saída natural — entender por que ele morre — cai numa **circularidade**:

```text
22 (gate golden)          precisa do wte.exe vivo
wte.exe vivo              precisa entender lista_equiposChange
lista_equiposChange       é WTE-TASK-25
25                        depends_on 22
```

Nada nessa cadeia se resolve na ordem em que as fases foram escritas. O plano
supõe, sem dizer, que o oráculo A funciona; com estas ROMs, não funciona.

## Evidência

Medida na WTE-TASK-19, gerada por
[`wte/tools/analisar_crash.py`](../../../wte/tools/analisar_crash.py) e escrita em
[`wte/re/crash.md`](../../../wte/re/crash.md):

| | |
|---|---|
| exceção | `c0000005`, endereço que faltou `0x1c` |
| onde cai | `vcl60.bpl` realocado para `0x005f0000`, RVA `0x5ea0` |
| símbolo | `Graphics::TFont::SetSize` + 8, com `this` **nulo** |
| sítio de chamada | `0x0040b1ac`, identificado pelo `EDX` = 8 |
| rotina | privada, em `0x0040b188` — `FindComponent("dorsal" + N)` e reestiliza |
| chamadores | `lista_equiposChange`, `lista_jugadores_1Change`, `dorsalClick`, `dorsalMouseDown` (todos `MainForm`) |

A atribuição é medida, não lida da tela: os roteiros
[07](../../../wte/tests/roteiros/07-controle-sem-time.txt) e
[08](../../../wte/tests/roteiros/08-so-troca-de-time.txt) são iguais linha a linha
até `= ARRANQUE` e o 08 só acrescenta a troca de time — **0 violações de acesso
contra 309**.

**Duas hipóteses de causa já caíram, as duas por experimento:** o tamanho da
imagem (truncar para os 474.431.328 bytes exatos não muda uma faixa do mapa de
I/O e o app cai igual) e a região vazia em `14368636` (é a última leitura antes
da falha, mas a falha é de estado de interface — o `analisar_io.py` só enxerga
I/O e não tinha como distinguir vizinho de causa).

## Causa raiz

Duas, e é preciso separá-las:

1. **do defeito:** desconhecida — é o que esta correção manda descobrir;
2. **da circularidade:** a fase 4 foi escrita supondo o gate como pré-requisito
   de *toda* análise de handler. Isso é certo para **implementar** um handler e
   errado para **diagnosticar** um. Diagnóstico não grava byte nenhum, não
   precisa de comparação golden, e é justamente o que destrava o gate.

## Correção

**Só diagnóstico. Nada de implementação, nada de spec.** O produto é uma
resposta escrita; o Pascal continua sendo assunto da fase 4.

O ferramental já existe: a [WTE-TASK-24](/docs/tasks/concluidos/24-ghidra-convencao-borland.md)
está concluída, com a convenção Borland (`EAX, EDX, ECX`) aplicada e os 96
nomes no Ghidra. O alvo é pequeno — uma rotina de ~340 bytes e quatro
chamadores.

### As quatro perguntas, em ordem de custo

1. **O campo em `+0x68` é mesmo `TControl.FFont` nesta VCL?** A rotina lê
   `[obj+0x68]` e passa direto para `TFont::SetSize`. Os vizinhos (`+0x40`,
   `+0x44`, `+0x48`, `+0x4c`) vão para `SetLeft`/`SetTop`/`SetWidth`/
   `SetHeight`, o que casa com `TControl`. Confirmar pelo `vcl60.bpl`, não por
   memória: se `+0x68` for outro campo para a classe que chega ali, o resto da
   análise muda de rumo.

2. **De onde vem o `N` de `"dorsal" + N`?** Se for derivado de dado da imagem,
   a região vazia em `14368636` volta a ser candidata — agora como *causa da
   causa*, com mecanismo. `dorsal1..dorsal23` existem no `MainForm` e são todos
   `TStaticText`; qualquer `N` fora disso faz `FindComponent` devolver `nil`.

3. **Quem escreve no global `0x004335e4`?** A rotina testa `if (obj != nil)`
   antes de mexer na fonte, então o objeto que chega ali **passou** no teste e
   mesmo assim tem `Font` nulo. As sete referências ao global no `.text` já
   estão localizadas. Duas leituras possíveis: `FindComponent` devolveu um
   componente que não é `TControl`, ou o global foi sobrescrito por estouro de
   buffer vizinho — e este repositório já pagou por um `strcpy` de um byte a
   mais (§8.10, e o `_FORTIFY_SOURCE` do `newWe2002`).

4. **Existe condição de entrada que evita o caminho?** Se sim, o oráculo volta
   a ser dirigível e a WTE-TASK-19 destrava sem depender de outro dump.

### Os dois desfechos, e os dois são legítimos

- **Achou condição de contorno** → registrar, ajustar os roteiros, e a
  WTE-TASK-19 e a 22 seguem.
- **Não achou** → o oráculo A é inutilizável com estas ROMs, e isso **muda a
  WTE-TASK-22**: o gate precisa ser redesenhado ou declarado dependente de uma
  release que ainda não temos. Resultado negativo é resultado (prompt de
  execução, §3).

**O que esta correção não autoriza:** editar o `.exe` (leitura pura — plano
§2), colar decompilado em spec ou em código (§2, §8.10), e implementar
`lista_equiposChange` (isso é WTE-TASK-25, e continua atrás do gate).

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/crash-causa.md` | criar — a resposta escrita, à mão, com todo endereço citado vindo de ferramenta |
| `wte/tools/ghidra/` | modificar, se o diagnóstico produzir script reaproveitável |
| `docs/tasks/concluidos/22-harness-golden.md` | modificar **só no desfecho negativo** |
| `docs/tasks/concluidos/progresso.md` | modificar — a pendência externa passa a ter veredito |

## Verificação

- [x] As quatro perguntas com resposta escrita, ou com "não respondida" e a
      razão
      — as quatro respondidas; **uma sub-pergunta ficou aberta** e está
      declarada: *qual instrução* escreve `0x004335e4`
- [x] Todo endereço do `crash-causa.md` rastreável a saída de ferramenta —
      nenhum lido do Ghidra e transcrito à mão sem o comando ao lado
      — `objdump` para o código, `wte/tools/sonda_dorsal.py` para o processo
      vivo; o Ghidra não foi usado
- [x] Nenhum trecho de decompilado colado (`spec_index.py` recusa as oito
      marcas; aqui a regra vale por disciplina, já que o arquivo não é spec)
      — o único bloco citado é listagem de `objdump`, seis linhas
- [x] `we-team-editor/` intocada — `git status` e `sha256sum` do `.exe` antes e
      depois
      — `9cebce645b8e320c77b82db5b4683613c8ccde5123e6b0b08a59f0f1b8697fff`,
      igual nos dois momentos
- [x] `roms/` intocada; medição só sobre cópia em `work/`
      — o `diff_dirigido.sh` copia; `roms/` só foi lida
- [x] `make -C wte check` verde
      — 359 testes, `OK (skipped=1)`, saída 0, já com o `sonda_dorsal.py --check`
        na bateria
- [x] Desfecho declarado: condição de contorno **ou** veredito de oráculo
      inutilizável, com a consequência para a WTE-TASK-22 escrita
      — **condição de contorno**: a ROM japonesa
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-10

- **Resumo do que foi feito:**

  Diagnóstico, sem uma linha de implementação. As quatro perguntas foram
  respondidas por medição, e o desfecho é o **positivo**: existe condição de
  contorno, e ela é a imagem. Mesmo roteiro 08, mesmas marcas, só a imagem
  muda — **49.749 violações de acesso com `roms/golden-european-deluxe.bin`,
  0 com `roms/japanese-shift-jis.bin`**, refeito duas vezes. Com a japonesa o
  ponteiro global recebe o `dorsal1` certo (`classe=TStaticText`) e o realce
  segue sem exceção.

  A causa: `+0x68` **é** `TControl.FFont` (conferido no `vcl60.bpl`, em
  `TControl::SetFont`); o `N` de `"dorsal" + N` **não** vem da imagem (o
  chamador que trava empurra a constante 1); e o controle **existe** — os 23
  `dorsalN` estão vivos no `MainForm`, todos `TStaticText`, todos com `Font`
  não nula, lidos da memória do processo. O que não presta é o ponteiro em
  `0x004335e4`: a carga do time preenche uma tabela de pares de 16 bits em
  `0x00433580..0x004335bf` e, com a imagem europeia, escreve além do fim dela,
  deixando `0x00010001` no global. Esse valor passa no `if (obj != nil)` da
  rotina, e `[0x00010001+0x68]` lê zero. Das duas leituras que a correção pôs
  lado a lado, a de `FindComponent` devolvendo não-`TControl` está refutada e a
  de estouro em vizinho está medida.

  A ferramenta que mede isso ficou versionada (`wte/tools/sonda_dorsal.py`),
  com `--check` que remede os cinco deslocamentos de campo contra os `.bpl` —
  senão os números do documento não teriam rota de volta, que é a lição da
  CORR-WTE-002.

- **Arquivos criados/modificados:**

  - `wte/re/crash-causa.md` — criado, a resposta escrita
  - `wte/tools/sonda_dorsal.py` — criado; lê o processo vivo, e `--check`
    confere o layout nos `.bpl`
  - `wte/tools/analisar_crash.py` + `wte/re/crash.md` — a seção "O que isto
    muda" afirmava que o controle não existe e que a WTE-TASK-19 seguia
    bloqueada; as duas coisas ficaram falsas com esta medição
  - `docs/tasks/concluidos/progresso.md` — a pendência externa ganhou veredito
  - `docs/tasks/concluidos/CORR-WTE-044.md`, `docs/tasks/concluidos/correcoes-progresso.md`

  Em commit próprio, a reconciliação que a correção obrigou e a CORR não
  listava: `docs/tasks/concluidos/22-harness-golden.md` (o achado 1 dizia "Bloqueante"),
  `docs/tasks/concluidos/19-os-50-offsets-restantes.md` ("bloqueado por falta da imagem
  certa"), `wte/re/visual.md` e `wte/tools/analisar_io.py` +
  `wte/re/offsets-novos.md`.

- **Problemas encontrados:**

  1. **A contagem de violações de acesso não é propriedade do defeito.** O
     `crash.md` registra 309 na sessão medida; as corridas desta correção deram
     49.749 com o mesmo roteiro e a mesma imagem. Não há contradição: só a
     primeira exceção localiza, o manipulador do próprio app reentra em laço
     depois dela, e o número mede quanto tempo o processo ficou vivo. O que
     separa as sessões é zero contra não-zero, e o `sonda_dorsal.py` passou a
     dizer isso ao terminar.
  2. **`ptrace_scope=1`** nesta máquina só deixa ler `/proc/<pid>/mem` de
     descendente, então a sonda **lança** o `diff_dirigido.sh` em vez de se
     anexar a um processo já rodando — a mesma restrição que faz o
     `diff_dirigido.sh` lançar o `strace`.
  3. **Ficou sem resposta qual instrução escreve `0x004335e4`.** Pede
     watchpoint de hardware, e a mesma restrição de `ptrace` obriga o `gdb` a
     lançar o Wine — só que o endereço só existe depois do PE mapeado, quando
     já não dá para pôr o watchpoint pela linha de comando. Não foi tentado
     porque o desfecho não depende disso. Registrado no `crash-causa.md` como o
     próximo passo natural, para quem implementar a WTE-TASK-25.
