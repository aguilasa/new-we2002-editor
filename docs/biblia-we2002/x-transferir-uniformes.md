# X — Transferindo todos os uniformes de uma ISO para outra de uma só vez

> Dicas e manhas especiais. Voltar ao [índice geral](/docs/biblia-we2002/README.md).

**Programas usados nesse tutorial:** editor hexadecimal HEDIT.

## Introdução

Para transferir todos os **times** de uma ISO (com ou sem patch) para outra, é só
usar o **WEMANIA editor** com a opção **EXPORTAR** e depois **IMPORTAR TODOS**.
Porém, até hoje não existe software capaz de exportar e importar os
**uniformes**. Se você desejar fazer isso com um só uniforme de um único time,
deverá usar o WE TEAM EDITOR; porém, para transferência total de todos os
uniformes 3D, só através de hexadecimal. Portanto, lá vai como fazer.

## Executando

**a)** Execute seu programa hexadecimal e mande abrir a **ISO destino** (a ISO
onde você irá salvar os times que importou da outra).

**b)** Vá agora até o offset **`0x12D76FC`** e marque-o. (Para fazer isso no HEDIT
basta clicar em `CTRL+G`, indicar o offset no campo e apertar OK; ele irá
automaticamente pra lá.)

**c)** Agora vá para a **ISO de origem** (a ISO de onde irá pegar os times para
colocar na outra).

**d)** Vá também para o offset **`0x12D76FC`**, clique nele, segure a tecla
`SHIFT` e vá descendo até encontrar o offset **`0x178AA48`**.

**e)** O trecho será marcado; agora copie-o (`CTRL+C`).

**f)** Volte à ISO de destino anteriormente aberta e já deixada no offset correto,
e mande colar (`CTRL+V`).

**g)** Mande salvar.

Pronto, pode entrar no emulador e testar.

---

Próxima seção: [X1 — Mudando a ordem ou retirando times do menu](/docs/biblia-we2002/x1-ordem-times-menu.md)
