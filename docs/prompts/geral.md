# Geral — WE2002 Team Editor: de `.exe` a editor em Lazarus

```
Execute o que está em `/home/ingmar/desenvolvimento/github/new-we2002-editor/docs/prompts/01-executar.md`,
sempre releia o arquivo.
Após atualize o arquivo /home/ingmar/desenvolvimento/github/new-we2002-editor/docs/tasks/progresso.md
com o progresso da task, incluindo a data de conclusão na tabela de resumo.
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

O `03` executa **uma** correção por invocação; o `04` executa o lote inteiro,
em ordem de dependência, paralelizando só o que a matriz de conflito autoriza.
As demais regras do `03` valem nos dois.

**Duas regras que valem nos quatro prompts:**

1. **Commits em inglês, conventional commit** (`docs:`, `feat:`, `fix:`…), sem
   footer de co-autoria.
2. **Existe remote** (`git@github.com:aguilasa/new-we2002-editor.git`). `push`
   é possível, mas **não é automático**: só quando o usuário pedir.
