---
handler: SpeedButton2Click
formulario: MainForm
endereco: 0x00410fa4
veredito: implementado
---

# MainForm.SpeedButton2Click

O ` Sair    ` da tela principal: pergunta, e sai se a resposta for sim.
Vinte e sete bytes.

**Evidência:** disassembly lido

## Entrada

A global `_ficha_salida` (`0x00432E4C`), e o resultado do modal dela.

**Evidência:** disassembly lido

## Saída

```text
se ficha_salida.ShowModal() = 6:     ' mrYes
    exit(0)
```

O 6 é `mrYes`, e casa com o `.dfm`: o `BitBtn1` do `ficha_salida` é ` Sim` com
`ModalResult = 6` e o `BitBtn2` é `Nao` com `7`. Nenhum dos dois tem
`OnClick` — a janela inteira é dois botões e o rótulo
`Voce deseja realmente sair?`.

**A saída é a `exit()` da RTL de C, não a da VCL.** O `0x0041BEAC` empilha o
código e cai na `0x0041BE40`, que roda os `atexit`, descarrega e chama a saída
do processo. Não passa por `Application.Terminate` — o laço de mensagens não
volta a rodar.

**Evidência:** disassembly lido

## Bytes tocados

**Nenhum diretamente** — e é aqui que a distinção importa. O editor grava
in-place a cada operação, então não há "salvar ao sair": o que estava para ser
gravado já foi. Sair não descarta nem confirma nada.

**Evidência:** disassembly lido

## Pré-condições

Nenhuma. Não confere imagem aberta nem edição pendente.

**Evidência:** disassembly lido

## Comportamento de erro

Não trata. Qualquer resultado modal diferente de 6 — inclusive fechar a janela
pela cruz do gerenciador — cai no ramo de não sair.

**Evidência:** disassembly lido

## Notas

**O port usa `Application.Terminate`, e a diferença é de fecho, não de
efeito.** A `exit()` da RTL mata o processo de dentro do `OnClick`, com o
formulário ainda na tela; o `Terminate` da LCL encerra o laço de mensagens e
desmonta os formulários. As duas terminam o app com código zero, e a imagem de
CD já está fechada nos dois casos — o port abre e fecha o `TCdImage` em cada
gravação, e não mantém descritor entre operações.

Matar o processo de dentro de um `OnClick` da LCL deixaria o GTK sem chance de
liberar a janela, e o `:98` guardaria a janela órfã — que é exatamente a
armadilha 5 da lista do prompt: janela esquecida derruba o golden seguinte.
