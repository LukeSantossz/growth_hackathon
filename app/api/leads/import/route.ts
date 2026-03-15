import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { category, limit = 50 } = await request.json();

    if (!category) {
      return NextResponse.json({ error: "Category is required" }, { status: 400 });
    }

    // Get entrepreneur
    const { data: entrepreneur } = await supabase
      .from("entrepreneurs")
      .select("id")
      .eq("auth_user_id", user.id)
      .single();

    if (!entrepreneur) {
      return NextResponse.json({ error: "Entrepreneur not found" }, { status: 404 });
    }

    // Get places from the category
    const { data: places, error: placesError } = await supabase
      .from("places")
      .select("*")
      .eq("categoria", category)
      .limit(limit);

    if (placesError) {
      console.error("Error fetching places:", placesError);
      return NextResponse.json({ error: "Failed to fetch places" }, { status: 500 });
    }

    if (!places || places.length === 0) {
      return NextResponse.json({ error: "No places found for this category" }, { status: 404 });
    }

    // Get existing leads to check for duplicates
    const { data: existingLeads } = await supabase
      .from("leads")
      .select("phone")
      .eq("entrepreneur_id", entrepreneur.id);

    const existingPhones = new Set(existingLeads?.map(l => l.phone).filter(Boolean) || []);

    // Convert places to leads
    const leadsToInsert = places
      .filter(place => {
        // Skip if phone already exists
        if (place.numero_telefone && existingPhones.has(place.numero_telefone)) {
          return false;
        }
        return true;
      })
      .map(place => ({
        entrepreneur_id: entrepreneur.id,
        places_id: place.id,
        name: place.nome || "Sem nome",
        company: place.termo_buscado || category,
        email: place.email || null,
        phone: place.numero_telefone || null,
        source: "google_maps",
        status: "new",
        classification: "cold",
        raw_data: {
          horario_funcionamento: place.horario_funcionamento,
          estado: place.estado,
          cidade: place.cidade,
          categoria: place.categoria,
        },
      }));

    if (leadsToInsert.length === 0) {
      return NextResponse.json({
        error: "All leads from this category already exist"
      }, { status: 400 });
    }

    // Insert leads
    const { data: insertedLeads, error: insertError } = await supabase
      .from("leads")
      .insert(leadsToInsert)
      .select();

    if (insertError) {
      console.error("Error inserting leads:", insertError);
      return NextResponse.json({ error: "Failed to insert leads" }, { status: 500 });
    }

    // Update campaign leads_found if exists
    const { data: campaign } = await supabase
      .from("campaigns")
      .select("id, leads_found")
      .eq("entrepreneur_id", entrepreneur.id)
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (campaign) {
      await supabase
        .from("campaigns")
        .update({
          leads_found: (campaign.leads_found || 0) + insertedLeads.length,
          status: "completed"
        })
        .eq("id", campaign.id);
    }

    return NextResponse.json({
      success: true,
      count: insertedLeads.length,
    });
  } catch (error) {
    console.error("Error importing leads:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
