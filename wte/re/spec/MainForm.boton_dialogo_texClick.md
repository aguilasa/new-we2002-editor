---
handler: boton_dialogo_texClick
formulario: MainForm
endereco: 0x0040dfe8
veredito: aberto
---

# MainForm.boton_dialogo_texClick

Abre o diálogo de arquivo do **uniforme** (`.tex`) e guarda o caminho
escolhido. 448 bytes.

## Entrada

- `dialogo_tex`, o `TOpenDialog` do formulário — o handler o executa e lê
  `FileName`;
- `lista_equipos.ItemIndex`, para compor o nome sugerido.

**Evidência:** disassembly lido

## Saída

```text
se dialogo_tex.Execute:
    monta o caminho a partir do FileName e do time selecionado
    texto_dialogo_tex.Caption := <nome do arquivo>
    abre o arquivo pelas rotinas de I/O da RTL (0x00417170, 0x00417210)
```

O `texto_dialogo_tex` é a etiqueta que mostra o arquivo escolhido, o irmão do
`texto_dialogo_we` do caminho da imagem.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum na imagem de CD.** O arquivo que ele abre é o `.tex` externo, não a
ROM. Quanto ao conteúdo desse arquivo, a leitura ainda não foi feita: as
rotinas `0x00417170` (159 B) e `0x0040423c` são de I/O da RTL e o que se faz
com os bytes está em `0x00417170`, não lida.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma além do diálogo ser cancelável: se `Execute` devolve falso, o corpo
sai sem tocar em nada.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Arquivo inexistente ou ilegível segue para a RTL sem checagem no
corpo do handler.

**Evidência:** disassembly lido

## Notas

**Veredito `aberto`: é do grupo de carga por afinidade, não por dependência.**
Ele não participa de carregar time — carrega *outro* arquivo. O port não
precisa dele para a navegação que a WTE-TASK-25 deve entregar, e o formato
`.tex` é assunto da [WTE-TASK-29](../../../docs/tasks/29-camisa-e-bandeira-2d.md),
que trata do uniforme. Fica especificado e sem corpo, com o dono nomeado.
