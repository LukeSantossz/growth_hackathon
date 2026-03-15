import { NextResponse } from "next/server";
import OpenAI from "openai";
import { createClient } from "@/lib/supabase/server";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const SYSTEM_PROMPT = `Você é um assistente de vendas que ajuda empresários a configurar sua prospecção de clientes.

Seu objetivo é coletar as seguintes informações através de uma conversa natural:
1. Produto/Serviço que a empresa vende
2. ICP (Perfil de Cliente Ideal): cargo, setor, tamanho da empresa
3. Região de atuação (cidade/estado)
4. Ticket médio aproximado
5. Principais dores/problemas que o produto resolve

Instruções:
- Faça UMA pergunta por vez
- Seja conversacional e amigável
- Se a resposta for vaga, peça mais detalhes
- Quando tiver TODAS as 5 informações, resuma o briefing e pergunte se está correto
- Após confirmação, responda EXATAMENTE com: "BRIEFING_COMPLETE" seguido do JSON estruturado

Formato do JSON final:
{
  "produto": "descrição do produto/serviço",
  "icp": {
    "cargo": "cargo alvo",
    "setor": "setor/indústria",
    "tamanho_empresa": "porte da empresa"
  },
  "regiao": "região de atuação",
  "ticket_medio": "valor aproximado",
  "dores": ["dor 1", "dor 2", "dor 3"]
}`;

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { messages } = await request.json();

    // Convert messages to OpenAI format
    const openaiMessages = [
      { role: "system" as const, content: SYSTEM_PROMPT },
      ...messages.map((m: { role: string; content: string }) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      })),
    ];

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: openaiMessages,
      max_tokens: 1024,
    });

    const assistantMessage = response.choices[0]?.message?.content || "";

    // Check if briefing is complete
    const isComplete = assistantMessage.includes("BRIEFING_COMPLETE");

    let cleanedResponse = assistantMessage;
    let briefingData = null;

    if (isComplete) {
      // Extract JSON from response
      const jsonMatch = assistantMessage.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          briefingData = JSON.parse(jsonMatch[0]);
          // Remove JSON from displayed message
          cleanedResponse = assistantMessage.replace("BRIEFING_COMPLETE", "").replace(jsonMatch[0], "").trim();
          if (!cleanedResponse) {
            cleanedResponse = "Perfeito! Seu briefing está completo. Clique em 'Salvar e Continuar' para começar a prospecção.";
          }
        } catch {
          // JSON parsing failed, not complete
        }
      }
    }

    return NextResponse.json({
      response: cleanedResponse,
      isComplete: isComplete && briefingData !== null,
      briefingData,
    });
  } catch (error) {
    console.error("Error in briefing chat:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
