// Imprime a assinatura recuperada de UMA funcao -- WTE-TASK-24.
//
// Existe por dois motivos:
//
//  1. PROVA da convencao (§8.1). Com o cspec de Borland, `colorearClick` tem de
//     aparecer com parametro em EAX, e nao como funcao sem argumento lendo
//     lixo. A assinatura e a evidencia.
//  2. CONSULTA na fase 4 -- "que assinatura tem este handler", sem abrir a GUI.
//
// LIMITE, e ele e duro: o que sai daqui responde PERGUNTA. Nunca colar em
// `wte/re/spec/` nem em Pascal -- recuperacao de especificacao, nao
// transcricao (PLAN-WTE-LAZARUS §2, §8.10). Por isso este script imprime a
// ASSINATURA e as chamadas virtuais, e NAO o corpo decompilado: a ferramenta
// nao entrega o material que a decisao proibe usar.
//
//@category WTE

import java.util.ArrayList;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Parameter;

public class decompile_one extends GhidraScript {

    // Quantas instrucoes olhar para tras atras do carregamento do
    // ponteiro de objeto. Seis cobre o par MOV campo / MOV vmt com folga.
    private static final int CONTEXTO = 6;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("decompile_one: uso: decompile_one.java <simbolo|0xEndereco>");
            throw new IllegalArgumentException("sem alvo");
        }
        String alvo = args[0];

        Function fn = null;
        if (alvo.startsWith("0x")) {
            fn = getFunctionAt(toAddr(alvo));
        } else {
            for (Function f : currentProgram.getFunctionManager()
                    .getFunctions(true)) {
                if (f.getName().equals(alvo)
                        || f.getName().endsWith("__" + alvo)) {
                    fn = f;
                    break;
                }
            }
        }
        if (fn == null) {
            println("decompile_one: '" + alvo + "' nao encontrado");
            throw new IllegalStateException("alvo nao encontrado");
        }

        println("decompile_one: " + fn.getName() + " @ " + fn.getEntryPoint());
        println("decompile_one: convencao  = " + fn.getCallingConventionName());
        println("decompile_one: assinatura = "
                + fn.getPrototypeString(true, false));
        println("decompile_one: parametros = " + fn.getParameterCount());
        for (Parameter p : fn.getParameters()) {
            println("  " + p.getName() + "  " + p.getDataType().getName()
                    + "  em " + p.getVariableStorage());
        }

        // Chamada virtual: `CALL dword ptr [ECX + 0xNN]`, o padrao da §8.2.
        //
        // O slot sozinho nao diz de quem e o VMT. O que diz e o CONTEXTO: as
        // instrucoes que carregam o ponteiro de objeto logo antes -- tipicamente
        // `MOV reg,[EBX + 0xNNN]` (o campo do formulario) seguido de
        // `MOV reg,[reg]` (o VMT). O deslocamento do campo e o que a rota 2
        // cruza com o DFM. Imprimir isso e o material do teste das cinco
        // chamadas da vmt.md -- e nao e decompilado: e listagem.
        List<Instruction> corpo = new ArrayList<>();
        for (Instruction ins : currentProgram.getListing()
                .getInstructions(fn.getBody(), true)) {
            corpo.add(ins);
        }
        int n = 0;
        for (int i = 0; i < corpo.size(); i++) {
            String txt = corpo.get(i).toString();
            if (!(txt.startsWith("CALL") && txt.contains("[")
                    && txt.contains("+"))) {
                continue;
            }
            n++;
            println("  virtual #" + n + "  " + corpo.get(i).getAddress()
                    + "  " + txt);
            for (int k = Math.max(0, i - CONTEXTO); k < i; k++) {
                String c = corpo.get(k).toString();
                if (c.startsWith("MOV") || c.startsWith("LEA")) {
                    println("      contexto  " + corpo.get(k).getAddress()
                            + "  " + c);
                }
            }
        }
        println("decompile_one: " + n + " chamada(s) virtual(is) no corpo");
    }
}
