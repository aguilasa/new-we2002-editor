# Receita — iniciar o ciclo `kits` no Rite

Como sair do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) para um ciclo de tasks
rodando pelo plugin Rite. As convenções do repositório estão em
[.claude/rules/tasks.md](../.claude/rules/tasks.md); a configuração, em
[rite.toml](../rite.toml).

## Antes de começar: dois ajustes no plano — **feitos em 2026-09-30**

Ficam registrados para quem refizer a receita com outro plano.

Os dois precisam estar feitos **antes** do `plan-to-tasks`, porque as tasks
nascem apontando para o plano e herdam o que ele disser.

### 1. O `looks` está arquivado

O ciclo `looks` foi para `docs/tasks/concluidos/` (commit `b22543c4`). O plano
ainda fala de "tasks do ciclo `looks`" (§2 e fase 5 da §7) e de "o `looks` está
com o ciclo aberto" (§6).

- `depends_on` não atravessa pasta, e não existe mais ciclo `looks` para receber
  as duas mudanças do §2 (`scene.Builder(kit=...)` e o parâmetro `kit_set`).
- **Solução recomendada:** a fase 5 vira task **do ciclo `kits`**, que toca
  `tools/looks/` para expor o que precisa. Reabrir o `looks` é mais caro.
- Ajustar no plano: §2 ("As duas mudanças no `looks`"), §6 (primeiro item) e a
  linha da fase 5 na §7.

### 2. Dar âncora a cada incógnita da §4

Hoje (a)…(f) são parágrafos em negrito dentro da §4, e o Rite só gera a âncora
`#4`. Toda task de medição apontaria para a seção inteira.

- Transformar cada uma em subtítulo: `### 4.1 (a) Titular e suplente…` até
  `### 4.6 (f) A zona do mapa…`.
- Conferir as âncoras:

  ```sh
  rite anchors docs/PLAN-KITS-PY.md
  ```

  Tem de aparecer `#4.1` … `#4.6`, ao lado das que já existem (`#1.1`, `#2.1`,
  `#3.1`…`#3.5`, `#5`, `#7`).
- Atualizar as referências cruzadas do plano que dizem "§4 (b)", "§4 (c)" etc.

Commitar os dois ajustes antes de seguir. (Aqui: já no commit que trouxe esta
receita.)

## Passo 1 — criar o ciclo

```
/rite:new-cycle kits
```

Cria:

- `docs/tasks/kits/progresso.md` e `docs/tasks/kits/correcoes-progresso.md`;
- `docs/prompts/perfil-kits.md` e `docs/prompts/perfil-kits.armadilhas.md`.

**O perfil é o que importa aqui** — todo comando do ciclo o lê. Preencher com:

| o quê | de onde |
|---|---|
| a regra núcleo × interface: `core/` sem Qt, sem `print`, sem estado global; a UI e a CLI só importam `core/api.py` | §3 e §3.1 |
| endereço só em um módulo (`generated/` para nomes de time, `layout.py` do `looks` para o resto) | §3.1 |
| estilo visual: Fusion, `QPalette` fixa, fonte em pixels, igual no Windows e no Linux, **não** o do `looks` | §3.4 |
| venv `work/venv-looks/` chamado por caminho; variáveis `WE2002_LOOKS_IMAGE` (geometria) e `WE2002_KITS_CORPUS` (pares de bandeira do Superpack) | §3.5, §6 |
| gates do `ctest`: `kits_selftest`, `kits_image`, `kits_ui`, o `--check` do gerador; *skip* 77 | §3.5 |
| recursos serializados: `tela` (fase 4), `emulador` e `save-states` (fase 7) | `rite.toml` |
| armadilhas já conhecidas: os 18 TEX com cauda marcada Form 2, o `TEX_A4` com titular = suplente, `MSYS_NO_PATHCONV=1` no Git Bash | §1.1, §2.1 |

As armadilhas vão no arquivo `.armadilhas.md`, não no perfil — o perfil tem
limite de tamanho (`max_kb` no `rite.toml`).

## Passo 2 — gerar as tasks

```
/rite:plan-to-tasks kits docs/PLAN-KITS-PY.md
```

Quebra as fases da §7 em tasks, cada uma com:

- critério de pronto verificável;
- `depends_on` (a coluna "depende de" da §7);
- `source_of_truth` com âncora — ex.: `/docs/PLAN-KITS-PY.md#4.1` para a medição
  de titular e suplente;
- uma task de fechamento por fase.

O que conferir no resultado:

- as fases 1 a 3 **não** têm janela; nenhuma task delas cria arquivo em `ui/`;
- a fase 7 (emulador) existe e não está marcada como opcional — é a que não pode
  ser pulada;
- a linha "manga longa, braçadeira e árbitro" da §7 **não** vira task ainda: ela
  depende das medições (c) e (e).

## Passo 3 — conferir e commitar

```sh
ctest -R tasks
```

(ou `rite.py check`). Confere frontmatter, âncoras de `source_of_truth`,
`depends_on`, links, tabelas geradas em dia e a entrada de cada fase no perfil.
Verde, commitar o ciclo inteiro de uma vez.

## Passo 4 — rodar

| comando | faz |
|---|---|
| `/rite:status` | onde cada ciclo está e qual comando rodar a seguir |
| `/rite:execute kits` | executa **uma** task, commita e registra |
| `/rite:execute-batch kits 2` | duas por vez, em ondas sem conflito |
| `/rite:review kits` | revisão independente de uma task concluída; abre CORR para o que falhar |
| `/rite:fix kits` / `/rite:fix-all kits` | corrige uma CORR / todas |
| `/rite:close-cycle kits` | arquiva o ciclo em `docs/tasks/concluidos/` quando tudo fechar |
| `/rite:retro kits` | retrospectiva: agrupa as CORRs por causa e propõe o que promover ao perfil |

Ordem natural, que já está na §7: fase 0 (medições no disco) → núcleo sem janela
(fases 1–3) → janela (fase 4) → mudanças no `looks` (fase 5) → 3D (fase 6) →
emulador (fase 7).

## Regras que valem o ciclo todo

- Estado de task e CORR **só** pelo CLI do Rite (`rite close`, `rite mark*`,
  `rite new-fix`); nunca editar à mão o frontmatter nem a região entre
  `<!-- rite:begin -->` e `<!-- rite:end -->`.
- ID de CORR nova sai do `rite new-fix`, nunca "o maior + 1".
- Links nos arquivos do ciclo são sempre a partir da raiz (`/docs/…`,
  `/tools/…`) — o `rite.py check` reprova relativo.
