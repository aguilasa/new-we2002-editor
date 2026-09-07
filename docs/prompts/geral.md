# Geral — WE2002 Team Editor: de `.exe` a editor em Lazarus

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/01-executar.md`,
sempre releia o arquivo.
Após atualize o `progresso.md` da pasta do ciclo com o progresso da task,
incluindo a data de conclusão na tabela de resumo.
```

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/02-revisar.md`,
sempre releia o arquivo
```

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/03-corrigir.md`,
sempre releia o arquivo
```

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/04-corrigir-tudo.md`,
sempre releia o arquivo
```

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/05-executar-lote.md`,
sempre releia o arquivo
```

**Ciclo em subpasta.** Os cinco comandos aceitam, como primeira palavra do
argumento, o nome de uma subpasta de `docs/tasks/` que tenha `progresso.md`
próprio — é a **pasta do ciclo**, e todos os caminhos passam a sair dela
(`/executar <subpasta>`, `/revisar <subpasta>`). Sem argumento, a pasta é
`docs/tasks/`, como sempre. A regra está no **Passo 0** de cada prompt.

**Dois pares, a mesma forma.** Em cada par o prompt em lote relaxa exatamente
uma regra do singular — "uma por invocação" — e nenhuma outra:

| Singular | Lote | Tamanho do lote |
| --- | --- | --- |
| `01-executar.md` — uma task | `05-executar-lote.md` | **2** por padrão, ou o número pedido. Nunca "tudo" |
| `03-corrigir.md` — uma CORR | `04-corrigir-tudo.md` | todas as pendentes |

Os dois lotes paralelizam só o que a matriz de conflito autoriza, e o `:98` é
sempre sequencial. As demais regras do singular valem palavra por palavra nos
dois.

**Duas regras que valem nos quatro prompts:**

1. **Commits em inglês, conventional commit** (`docs:`, `feat:`, `fix:`…), sem
   footer de co-autoria.
2. **Existe remote** (`git@github.com:aguilasa/new-we2002-editor.git`). `push`
   é possível, mas **não é automático**: só quando o usuário pedir.
