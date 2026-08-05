---
id: WTE-TASK-01
title: "Instalar e verificar o ferramental (Lazarus, FPC, Ghidra)"
type: infra
category: infra
phase: 0
depends_on: []
status: pendente
---

# WTE-TASK-01: Ferramental

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §3 e Fase 0.
- Esta task **abre o projeto**. Nada mais pode começar sem ela.

Medido em 2026-08-05: **nada do que o projeto precisa está instalado**. Não há
Lazarus, FPC, Ghidra, IDA, radare2, rizin, retdec nem `pefile`. O que existe é
`objdump`, `strings`, Python 3.13, Wine 32-bit via runner do Bottles, o Xvfb
`:99` com `xdotool`/`import`, e o `we2002_core` deste repositório.

`lazarus` 3.0+dfsg1-8build3 e `fpc` 3.2.2+dfsg-32 estão no `noble/universe`.
Ghidra **não** é empacotado pelo Ubuntu — instalação manual, e precisa de JDK.

---

## Objetivo

Deixar a máquina pronta, e **provar** que está, em vez de supor.

### 1. Instalar

| Pacote | Origem | Para quê |
|---|---|---|
| `lazarus`, `fpc`, `fpc-src` | `apt` | o alvo |
| `python3-pefile` | `apt` | parsing de PE em script |
| Ghidra ≥ 11 | download manual | decompilador (Fase 4 e 5) |
| JDK 17 ou 21 | `apt` | requisito do Ghidra |

Conferir qual JDK já existe antes de instalar outro.

### 2. Provar que o Lazarus funciona no alvo real

Compilar um projeto LCL vazio por **linha de comando** (`lazbuild`, não a IDE) e
abrir a janela no `:99`, seguindo a regra do `CLAUDE.md`: `DISPLAY=:99` e
`XAUTHORITY` resolvido pelo `ps`.

A IDE gráfica é opcional para o projeto; `lazbuild` **não** é — todo o
faseamento assume build reproduzível por linha de comando.

### 3. Provar que o oráculo A continua de pé

`make wte` tem de abrir a janela do editor do Obocaman. Ele depende do stack X
**i386** no host; se quebrar, a Fase 4 inteira perde o oráculo comportamental e
o plano muda. Descobrir isso agora, não na Fase 4.

### 4. Registrar as versões

Versão exata de `fpc`, `lazbuild`, widgetset padrão, Ghidra e JDK, num arquivo
que as tasks seguintes possam citar. Versão de compilador muda layout de
`bitpacked record` (§8.11) — não é detalhe cosmético.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/progresso.md` | modificar (status) |
| `wte/re/ambiente.md` | criar — versões medidas, com a data |

---

## Critério de conclusão

- [ ] `lazbuild` compila projeto LCL vazio sem erro, widgetset GTK2 confirmado
- [ ] A janela desse projeto abre no `:99` e é capturada por `import`
- [ ] `make wte` abre a janela do editor original
- [ ] Ghidra abre e importa o `we-team-editor.exe` sem erro
- [ ] `wte/re/ambiente.md` com as versões medidas
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
