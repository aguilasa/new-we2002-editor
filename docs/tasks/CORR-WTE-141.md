---
id: CORR-WTE-141
title: "Correção: `Return` na janela principal encerra o `ed.exe` e não faz nada no port"
type: correção
category: comportamento
status: concluído
depends_on: []
---

# CORR-WTE-141: o `Return` que fecha o editor original

## Problema identificado

Com o diálogo principal carregado e o foco nele, `Return`:

| | efeito |
|---|---|
| `ed.exe` | **encerra o editor** — `IDD_ED_DIALOG` não tem `DEFPUSHBUTTON`, e no MFC o Enter cai em `CDialog::OnOK`, que roda `EndDialog`. Nada é gravado |
| port | **nada** — a janela fica, e a imagem gravada depois é byte-idêntica à de um `Load`+`Save` sem tecla nenhuma |

**A metade que o item 4 da §8.10 afirma está cumprida nos dois**: nenhum dos
dois dispara ação de edição, que é o risco com história — dentro de um
`QDialog` o Qt torna todo botão auto-default, e num diálogo com 86 botões o
`Return` clicaria o primeiro da ordem de tabulação, sendo que um dos candidatos
aplica formação predefinida. O `autoDefault=false` do `rc2ui.py` segura isso, e
esta medição é a guarda de regressão dele.

O que diverge é o **ciclo de vida**: um editor fecha, o outro não.

## Evidência

Medido em 2026-08-31 sobre `ptbr-remaster.bin`, roteiro
`tools/par/8.10-return-nao-dispara.sh` (ponteiro no meio do diálogo, `Return`,
e o harness tenta gravar em seguida).

Oráculo — a janela some antes da gravação, e a cópia fica intacta:

```text
tools/golden_run.sh: nao consegui focar a janela 0xe00001
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin ora.bin
IDENTICAL
```

Port — grava normalmente, e o resultado é **igual ao do controle sem tecla
nenhuma**:

```text
$ python3 tools/golden_compare.py roms/ptbr-remaster.bin port.bin
5 run(s), 41 byte(s) differ
$ cmp port.bin port-ctl.bin && echo iguais
iguais
```

As 5 faixas são as não-idempotências conhecidas do `Load`+`Save`; nenhuma delas
é de formação ou de time.

## Causa raiz

`CDialog::OnOK` é o destino padrão do Enter num diálogo MFC sem
`DEFPUSHBUTTON`. No Qt, sem botão default (todos com `autoDefault=false`), o
`Return` não encontra destino e é ignorado.

**Correção do enunciado, medida na execução:** esta seção dizia que "o `CEdDlg`
não sobrescreve `OnOK`". Ele sobrescreve — `legacy/mfc/edDlg.cpp:1529`:

```cpp
void CEdDlg::OnOK()
{
    if (CanExit())
        CDialog::OnOK();
}

BOOL CEdDlg::CanExit()
{
    return TRUE;
}
```

O efeito medido não muda (o `CanExit()` devolve `TRUE` sempre, e o editor
fecha), mas a frase estava errada, e a §7 do `PARIDADE-FUNCIONAL.md` já
registrava a versão certa — "`IDOK` implícito do `CDialog`, com `CanExit()`
sempre `TRUE`". O `CanExit()` é um gancho que o autor deixou preparado para
perguntar "salvar antes de sair?" e nunca preencheu.

Note a assimetria com o `Escape`, que **concorda**: fecha nos dois
(`IDCANCEL`/`CDialog::OnCancel` lá, `QDialog::reject` aqui) — a §8.10 item 5
mediu isso.

E note também a assimetria interna do próprio port: o
`DefaultTacticsDialog` **fecha** com `Return`, e deve
([CORR-WTE-139](/docs/tasks/CORR-WTE-139.md)), porque ali o `.rc` declara um
`DEFPUSHBUTTON` — invisível, mas declarado. Aqui não há nenhum. As duas
decisões são coerentes entre si, e a segunda foi escrita em 2026-08-31: §6
linha 8 do `PARIDADE-FUNCIONAL.md`.

## Correção

**Decidir, e a decisão é do usuário.** As duas saídas se defendem:

1. **Reproduzir** — `Return` fecha a janela principal do port também. É a régua
   de paridade aplicada ao pé da letra. O custo é real: uma tecla acidental
   descarta o trabalho não gravado, que é exatamente o motivo de o original ser
   ruim nisso.
2. **Manter** e registrar como **divergência deliberada**, ao lado das quatro
   da Fase 5.

Em qualquer dos casos, o item 4 da §8.10 passa a dizer o que foi medido dos dois
lados — hoje ele só afirma "não pode disparar nada", que é verdade nos dois e
esconde a diferença.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `src/app/MainWindow.cpp` | modificar, se a decisão for 1 |
| `docs/PARIDADE-FUNCIONAL.md` | modificar — o item 4 da §8.10 e, se for o caso, a §6 |
| `docs/PLAN-LINUX.md` | modificar — a lista de divergências deliberadas, se for o caso |

## Verificação

- [x] A decisão está escrita, com a razão, em `/docs/PARIDADE-FUNCIONAL.md`
- [x] `tools/par/8.10-return-nao-dispara.sh` continua mostrando que **nenhum**
      dos dois dispara ação de edição — é a guarda do `autoDefault=false`. O
      roteiro não foi rerodado: a escolha foi a 2, nenhuma linha de código
      mudou, e a medição de 2026-08-31 que esta CORR cita continua sendo o
      estado do binário
- [x] ~~Se a escolha for reproduzir: o `DefaultTacticsDialog` **não** muda de
      comportamento~~ — **não se aplica**, a escolha foi a 2. O
      `DefaultTacticsDialog` segue fechando com `Return`, e a §6 linha 8 diz por
      que as duas decisões são coerentes entre si
- [x] `ctest --preset debug` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-31

**Resumo do que foi feito:** decisão do usuário, **opção 2** — o port continua
ignorando o `Return` na janela principal, e a diferença de ciclo de vida fica
registrada como divergência deliberada. Nenhuma linha de código mudou.

A razão escrita nos três sítios: reproduzir faria uma tecla acidental descartar
o trabalho não gravado, que é exatamente o defeito do original — a paridade não
vale o risco quando o comportamento copiado é o ruim e não grava byte nenhum.

Onde ficou:

1. `docs/PARIDADE-FUNCIONAL.md` — nova linha **8** na §6 (e o preâmbulo passa a
   contar oito); o item 4 da §8.10 troca "esperando decisão" pela decisão; e a
   linha do `Return` na §7 passa a apontar para a §6, em vez de repetir a razão
   num segundo lugar que envelheceria sozinho.
2. `docs/PLAN-LINUX.md` — entrada na lista de divergências deliberadas, ao lado
   da [CORR-WTE-140](/docs/tasks/CORR-WTE-140.md).

**Problemas encontrados:** a **Causa raiz** desta CORR estava errada num ponto —
afirmava que o `CEdDlg` não sobrescreve `OnOK`, e ele sobrescreve
(`legacy/mfc/edDlg.cpp:1529`), delegando por um `CanExit()` que devolve `TRUE`
sempre. O efeito medido é o mesmo, mas a frase não era verdade, e a §7 do
`PARIDADE-FUNCIONAL.md` já trazia a versão certa desde antes. A seção foi
corrigida com o trecho colado do legado, e a §6 e a §8.10 nomeiam o
`CanExit()` para a próxima leitura não repetir o engano.

A evidência foi reproduzida estaticamente, sem abrir o `:98`: `IDD_ED_DIALOG`
(`legacy/mfc/ed.rc:76`) tem **zero** `DEFPUSHBUTTON` e **nenhum** controle
`IDOK`/`IDCANCEL`; os dois únicos `DEFPUSHBUTTON` do `.rc` estão nas linhas 520
e 627, de outros diálogos. `MainWindow.cpp` não tem `keyPressEvent` nem
`Key_Return`. O `MainDialog.ui` traz **86** `autoDefault`. Nota de ferramenta: o
`ed.rc` é ISO-8859-1 e o `grep` o trata como binário — **sem `-a` ele não
imprime nada**, e a primeira leitura desta execução concluiu por engano que não
havia `DEFPUSHBUTTON` nenhum no arquivo.

**Gates:** `ctest --preset debug` — **9 testes, 5 rodaram, 5 passaram, 0
falharam**; os 4 pulados precisam de imagem ou do `:98`. Sem mudança de código,
sem golden, sem cópia em `work/`, `roms/` intocada.

**Arquivos criados/modificados:**

- `docs/PARIDADE-FUNCIONAL.md` — modificado (§6 linha 8 e preâmbulo, §7, §8.10 item 4 e preâmbulo)
- `docs/PLAN-LINUX.md` — modificado (divergências deliberadas)
- `docs/tasks/CORR-WTE-141.md` — modificado (causa raiz corrigida, verificação, log)
- `CLAUDE.md` — modificado (o parágrafo do `autoDefault=false` ganha a decisão,
  para ninguém "consertar" a ausência do `Return`)
- `docs/tasks/correcoes-progresso.md` — modificado (tabela e checklist)
