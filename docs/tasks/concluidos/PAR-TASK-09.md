---
id: PAR-TASK-09
title: "Ciclo de vida da janela"
type: verificação
category: ui
projeto: newWe2002
depends_on: []
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.10"
status: concluído
---

# PAR-TASK-09: Ciclo de vida da janela

## Contexto

- **Referência:** [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.10.
- **Projeto:** `newWe2002` (port Qt do `ed.exe`), **não** o `wte/` Lazarus.

---

## Método

O mesmo para toda a série, e é o que a §8 do inventário já fixa: **fazer a
mesma coisa no `ed.exe` sob Wine e no port, gravar as duas cópias e comparar
com `tools/golden_compare.py`.**

```sh
cp roms/ptbr-remaster.bin  "$SCRATCH/v.bin"
DISPLAY=:98 ./build/src/app/newWe2002 "$SCRATCH/v.bin"
```

**Critério de aprovação:** a única divergência é `405724..405739`, o slot 64 do
array de 63. Qualquer outra faixa é achado, e vira CORR.

**Sempre sobre cópia, sempre no `:98`.** O `roms/` nunca é alvo. Feche qualquer
editor aberto no display antes: os dois lados acham o diálogo principal pelo
tamanho, e uma janela esquecida é dirigida no lugar da que está sob teste.

**A imagem preferida desta série é a `ptbr-remaster.bin`.** Ela é a única com
oráculo vivo nos dois editores e com os ramos do codec exercitados — medido na
[PROPOSTA-IMAGEM-GOLDEN](/docs/PROPOSTA-IMAGEM-GOLDEN.md) §8.4. Onde o item
pedir nome latino legível, é ela; onde pedir kanji, a `japanese-shift-jis.bin`.

---

## Itens a conferir

- [x] Cancelar o diálogo de abertura — **DIVERGE**, [CORR-WTE-140](/docs/tasks/concluidos/CORR-WTE-140.md)
- [x] Abrir arquivo com tamanho errado → aviso, e carrega — concordam
- [x] `CMB_RELOAD` depois de editar → descarta as edições — golden `OK`
- [x] `Return` na janela principal não pode disparar nada — cumprido nos dois;
      o ciclo de vida **DIVERGE**, [CORR-WTE-141](/docs/tasks/concluidos/CORR-WTE-141.md)
- [x] `Escape` fecha — concordam

O quarto item é guarda de regressão com história: dentro de um `QDialog` o Qt
torna todo botão auto-default, e num diálogo com 86 botões e nenhum
`DEFPUSHBUTTON` o `Return` clicaria o primeiro da ordem de tabulação — um dos
candidatos aplica formação predefinida sobre o time selecionado. O `rc2ui.py`
emite `autoDefault=false` por isso. **Este item é o que impede a emenda de
apodrecer em silêncio.**

O segundo confirma que o aviso de "não tem 474.431.328 bytes" é só aviso: o
original carrega assim mesmo, e o port tem de carregar também.

---

## Definição de pronto

- [x] Todo item acima marcado no [/docs/PARIDADE-FUNCIONAL.md](/docs/PARIDADE-FUNCIONAL.md) §8.10
- [x] Cada item com evidência: o comando, a faixa que saiu do `golden_compare.py`,
      e o veredito — os quatro roteiros estão em `tools/par/8.10-*.sh`
- [x] Divergência fora de `405724..405739` registrada como CORR — **duas**, a
      [140](/docs/tasks/concluidos/CORR-WTE-140.md) e a [141](/docs/tasks/concluidos/CORR-WTE-141.md).
      Nenhuma das duas tem faixa nem offset simbólico, e **isso é o achado**:
      são divergências de ciclo de vida, em que um lado grava zero byte porque
      já não há janela
- [x] `roms/` intocada — md5 `7d49ff4e50a951dacd456096df4a2896`

## Log de Execução

**Executado em:** 2026-08-31 — **COMPLETA, 5 de 5.**

**Resumo do que foi feito:**

| item | oráculo | port | veredito |
|---|---|---|---|
| 1 cancelar abertura | aviso, e **fica com o diálogo vazio** | aviso, e **encerra** | **DIVERGE** |
| 2 tamanho errado | avisa e carrega | avisa e carrega | concordam |
| 3 `CMB_RELOAD` | descarta a edição | descarta a edição | golden `OK` |
| 4 `Return` | **encerra o editor** | não faz nada | edição: nenhum dispara. Ciclo de vida: **DIVERGE** |
| 5 `Escape` | fecha | fecha | concordam |

**O que se aprendeu, e é o achado da task: `BOOL OnInitDialog()` não é
"deu certo".** É "eu mesmo cuidei do foco". O `return FALSE` do
`legacy/mfc/edDlg.cpp:1331` não fecha diálogo nenhum — quem fecharia é
`EndDialog`, que não é chamado —, e o `ed.exe` segue de pé com a janela inteira
vazia. O `main.cpp` do port tinha um comentário afirmando o contrário
("bailed out of the dialog if the user cancelled"), escrito por quem leu o
`BOOL` como aborto — corrigido em 2026-08-31 pela
[CORR-WTE-140](/docs/tasks/concluidos/CORR-WTE-140.md), que também registrou o
encerramento do port como divergência deliberada. As duas divergências desta seção saem daí e de uma prima:
no item 4, `CDialog::OnOK` é o destino do Enter num diálogo sem
`DEFPUSHBUTTON`, e ele encerra o editor.

**Nenhuma das duas divergências grava byte.** É por isso que elas nunca
apareceram em golden nenhum, e é por isso que a Definição de pronto desta task
pede faixa e offset simbólico e não recebe: um dos lados simplesmente já não
tem janela para clicar `CMB_WRITE`.

**Problemas encontrados:**

**O item 3 precisava de controle, e o controle é a metade que quase não se
escreve.** "A edição não chegou ao disco" é indistinguível de "o roteiro não
chegou a digitar". A corrida gêmea com `PAR_SEM_RELOAD=1` fecha isso: mesmo
estímulo, sem o `CMB_RELOAD`, e a edição aparece em `OFS_TEAM_NAME_1_A+200` —
6 faixas / 46 bytes contra as 5 / 41 da corrida com reload.

**Dois dos cinco itens não cabiam no harness golden**, e não por limitação
dele: arranque e encerramento estão fora do que ele expõe, porque ele já entra
pelo diálogo de abertura e já sai gravando. Daí os dois roteiros que rodam
sozinhos.

**`grep` no `ed.rc` precisa de `-a`.** O arquivo é ISO-8859-1 e o grep o trata
como binário, engolindo toda saída — foi assim que o `CMD_CALCFORZA2` da
PAR-TASK-08 pareceu ausente do `.rc` por um momento. Ele está lá, na linha 370.

**Arquivos criados/modificados:**

- `tools/par/8.10-reload-descarta.sh` — item 3, com o `PAR_SEM_RELOAD` do controle
- `tools/par/8.10-return-nao-dispara.sh` — item 4
- `tools/par/8.10-ciclo-oraculo.sh` e `tools/par/8.10-ciclo-port.sh` — itens 1, 2 e 5
- `docs/PARIDADE-FUNCIONAL.md` — a §8.10 inteira
- `docs/tasks/concluidos/CORR-WTE-140.md` e `docs/tasks/concluidos/CORR-WTE-141.md` — as duas divergências
- `docs/tasks/concluidos/correcoes-progresso.md` — as duas linhas novas
- `docs/tasks/concluidos/progresso.md` — a linha da tabela
- `docs/tasks/concluidos/PAR-TASK-09.md` — este Log

### Nota posterior — 2026-08-31, [CORR-WTE-142](/docs/tasks/concluidos/CORR-WTE-142.md)

**A evidência dos itens 1, 2 e 5 não era reproduzível, e o roteiro do oráculo
anunciava captura que não fez.** Os dois roteiros de ciclo de vida escreviam em
`/tmp/c09`, que nenhum deles criava, com o `import` calado por `2>/dev/null`;
dois dos três `echo` do lado do oráculo estavam fora do `&&`. Numa árvore limpa
saíam zero imagens — e são justamente os três itens sem veredito de
`golden_compare.py`, cuja prova é a tela.

Consertado: destino em `work/par-8.10/` (`PAR_OUT` muda), criado pelos próprios
roteiros; nenhuma linha de confirmação fora do `&&`; e a mensagem de erro do
`import` passa a aparecer em vez de sumir. Foram dois defeitos, não um — o
segundo só apareceu porque o primeiro deixou de ser silencioso:

1. **O destino não existia.** Nenhum `mkdir`, e o erro ia para `/dev/null`.
2. **`import -window <id>` falhava** com `Resource temporarily unavailable` —
   a janela estava obscurecida pelo modal, que é a armadilha do `:98` que o
   `CLAUDE.md` já registra. O `capturar()` tenta a janela e cai para
   `-window root`, dizendo qual das duas produziu o arquivo. E o
   `esperar_titulo`/`janela_por_titulo` passou a filtrar por `--onlyvisible`:
   sem isso ele devolvia uma janela **não mapeada** de mesmo nome, que não se
   captura nem se dirige.

Seis capturas saem agora, e os vereditos não mudaram: `ed.exe` de pé com o
diálogo principal vazio depois do cancelamento (`ora-cancelar-janela.png`, nova
nesta correção), port encerrado, os dois carregando a imagem de tamanho errado,
`Escape` encerrando os dois.

### Nota posterior — 2026-08-31, [CORR-WTE-143](/docs/tasks/concluidos/CORR-WTE-143.md)

**Este Log listava os quatro roteiros como se fossem duas duplas, e são quatro
coisas diferentes.** O `8.10-return-nao-dispara.sh` é hook de **um lado só**: com
`GOLDEN_EDIT` o oráculo recebe o `Return`, encerra — o achado do próprio item —
e o `golden_run.sh` morre antes de gravar, então `golden_check.sh` com ele
reprova sempre. O cabeçalho do roteiro passou a dizer isso, e o veredito do item
(que é `cmp` contra uma corrida sem tecla, não o `OK` do golden) ficou escrito
junto com o comando. A §8.10 traz a tabela dos quatro.

