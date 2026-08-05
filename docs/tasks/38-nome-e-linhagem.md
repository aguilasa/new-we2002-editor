---
id: WTE-TASK-38
title: "Decidir o nome do produto e registrar a linhagem"
type: decisão
category: empacotamento
phase: 7
depends_on: ["WTE-TASK-35"]
status: pendente
---

# WTE-TASK-38: Nome e linhagem

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §2 e Fase 7.
- Decisão adiada de propósito até aqui, porque **não bloqueava nada antes**.
  Agora bloqueia: o empacotamento escreve o nome em sete lugares.

O `we-team-editor.exe` é obra do **Obocaman (2002)**, sem licença concedida —
mesma situação do código herdado do Moriero e do thyddralisk que o
[`NOTICE.md`](../../NOTICE.md) já registra. O repositório **não tem `LICENSE`** e
não deve ganhar um.

---

## Objetivo

Fechar duas coisas, com a razão escrita.

### 1. O nome

O plano diz: **não reusar "WE2002 Team Editor" tal e qual**. Razões, e vale
escrever qual pesa:

- é o nome do produto de outro autor
- confunde com o binário original, que continua no disco e é oráculo dos testes
- os scripts de teste acham janela por título, e nome igual quebra a WTE-TASK-22

Herdar do `newWe2002` a distinção que já funciona: **nome de produto** e **nome
de formato** são coisas diferentes. Lá, `newWe2002` é o produto e `we2002` é o
formato — o executável e o `share/` usam um, o namespace e as unidades usam o
outro. Aqui vale a mesma separação.

O nome escolhido entra em: binário, `share/`, `.desktop`, appid, ícone, título
da janela, e o `README.md` de `wte/`.

### 2. A linhagem no `NOTICE.md`

Se o app for publicado, o `NOTICE.md` ganha uma seção sobre a linhagem do
Obocaman, no mesmo tom das existentes: quem escreveu o original, quando, que
relação este trabalho tem com ele, e o que **não** foi copiado.

O que a seção deve poder afirmar, e que as fases anteriores construíram:

- o código é escrito a partir de `re/spec/`, não transcrito de decompilado
- a camada de dados vem do `we2002_core` deste repositório
- os formulários vêm de conversão de formato, não de cópia de código
- os assets (`image/`, `data/`) **não** são redistribuídos

O último item precisa de decisão: sem os 197 BMP o app não desenha camisa. O
usuário mantém a pasta, como faz com `roms/` — mas isso tem de estar escrito, e
o app tem de falhar com mensagem clara quando a pasta faltar.

### Decisão que não é minha

**Publicar é decisão do usuário.** Esta task prepara o texto e a decisão; não
publica, não empurra para remote público sem confirmação explícita.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `NOTICE.md` | modificar |
| `wte/README.md` | modificar |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§2 e Fase 7) |

---

## Critério de conclusão

- [ ] Nome do produto escolhido, com razão, e a separação produto/formato definida
- [ ] Seção de linhagem escrita no `NOTICE.md`
- [ ] Decidido o que acontece quando a pasta de assets falta
- [ ] Registrado que publicar depende de confirmação do usuário
- [ ] Nenhum `LICENSE` adicionado
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
