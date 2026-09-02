# X3 — Destravando o menu Copas

> Dicas e manhas especiais. Voltar ao [índice geral](/docs/biblia-we2002/README.md).

**Programas usados nesse tutorial:** editor hexadecimal HEDIT, emulador ePSXe.

## Introdução

Quando jogamos Winning Eleven originalmente, as copas são **travadas**: na Copa
América você só pode pegar clubes americanos, na Africana clubes da África, e
assim sucessivamente. Isso impede que, em campeonatos como o Brasileiro, você
possa disputar as copas com o time que quiser. Mas, utilizando o método abaixo,
você poderá liberar o jogo pra poder jogar em qualquer copa com qualquer time.

## Executando

**a)** Execute o editor hexadecimal (usaremos o HEDIT) e mande abrir a ISO do seu
jogo.

**b)** Abra a caixa **GO TO** (no HEDIT basta apertar `CTRL+G`) e informe que
deseja ir para o offset **`0x25CA9C`**.

**c)** Lá você encontrará os valores hexadecimais **`78 0F`**; mude-os para
**`64 0F`**.

Pronto, agora é só salvar e executar no emulador para testar. A partir de agora
você poderá escolher qualquer time ou seleção quando for jogar uma copa.

---

Fim do manual. Voltar ao [índice geral](/docs/biblia-we2002/README.md).
