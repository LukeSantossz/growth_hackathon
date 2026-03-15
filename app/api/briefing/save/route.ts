import { NextResponse } from "next/server";
import OpenAI from "openai";
import { createClient } from "@/lib/supabase/server";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { messages } = await request.json();

    // Get entrepreneur
    const { data: entrepreneur } = await supabase
      .from("entrepreneurs")
      .select("id")
      .eq("auth_user_id", user.id)
      .single();

    if (!entrepreneur) {
      return NextResponse.json({ error: "Entrepreneur not found" }, { status: 404 });
    }

    // Extract briefing data from messages using OpenAI
    const extractionPrompt = `Analise a seguinte conversa e extraia as informações do briefing em formato JSON.

Conversa:
${messages.map((m: { role: string; content: string }) => `${m.role}: ${m.content}`).join("\n")}

Retorne APENAS um JSON válido no seguinte formato:
{
  "produto": "descrição do produto/serviço",
  "icp": {
    "cargo": "cargo alvo",
    "setor": "setor/indústria",
    "tamanho_empresa": "porte da empresa"
  },
  "regiao": "região de atuação",
  "ticket_medio": "valor aproximado",
  "dores": ["dor 1", "dor 2"],
  "keywords": ["palavra-chave 1", "palavra-chave 2"]
}`;

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: extractionPrompt }],
      max_tokens: 1024,
    });

    const responseText = response.choices[0]?.message?.content || "";

    // Parse JSON
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      return NextResponse.json({ error: "Failed to extract briefing data" }, { status: 500 });
    }

    const briefingData = JSON.parse(jsonMatch[0]);

    // Update entrepreneur with briefing
    const { error: updateError } = await supabase
      .from("entrepreneurs")
      .update({ briefing_json: briefingData })
      .eq("id", entrepreneur.id);

    if (updateError) {
      console.error("Error updating entrepreneur:", updateError);
      return NextResponse.json({ error: "Failed to save briefing" }, { status: 500 });
    }

    // Create campaign
    const { data: campaign, error: campaignError } = await supabase
      .from("campaigns")
      .insert({
        entrepreneur_id: entrepreneur.id,
        name: `Campanha - ${briefingData.produto}`,
        queries_json: {
          keywords: briefingData.keywords || [],
          regiao: briefingData.regiao,
          setor: briefingData.icp?.setor,
        },
        status: "pending",
      })
      .select()
      .single();

    if (campaignError) {
      console.error("Error creating campaign:", campaignError);
    }

    return NextResponse.json({
      success: true,
      briefingData,
      campaignId: campaign?.id,
    });
  } catch (error) {
    console.error("Error saving briefing:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
