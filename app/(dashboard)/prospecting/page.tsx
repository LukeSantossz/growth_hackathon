"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Loader2, CheckCircle, AlertCircle } from "lucide-react";

const CATEGORIES = [
  { value: "alimentacao", label: "Alimentação (restaurantes, bares, etc.)" },
  { value: "beleza_estetica", label: "Beleza e Estética" },
  { value: "saude", label: "Saúde (clínicas, dentistas, etc.)" },
  { value: "fitness_esportes", label: "Fitness e Esportes" },
  { value: "comercio_varejo", label: "Comércio e Varejo" },
  { value: "construcao_casa", label: "Construção e Casa" },
  { value: "automotivo", label: "Automotivo" },
  { value: "educacao", label: "Educação" },
  { value: "servicos_empresariais", label: "Serviços Empresariais" },
  { value: "turismo_lazer", label: "Turismo e Lazer" },
  { value: "servicos_gerais", label: "Serviços Gerais" },
  { value: "logistica_transporte", label: "Logística e Transporte" },
];

export default function ProspectingPage() {
  const [category, setCategory] = useState("");
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; count?: number; error?: string } | null>(null);
  const [briefing, setBriefing] = useState<Record<string, unknown> | null>(null);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    async function loadBriefing() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: entrepreneur } = await supabase
        .from("entrepreneurs")
        .select("briefing_json")
        .eq("auth_user_id", user.id)
        .single();

      if (entrepreneur?.briefing_json) {
        setBriefing(entrepreneur.briefing_json as Record<string, unknown>);
      }
    }
    loadBriefing();
  }, [supabase]);

  const handleImport = async () => {
    if (!category) {
      alert("Selecione uma categoria");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("/api/leads/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, limit }),
      });

      const data = await response.json();

      if (response.ok) {
        setResult({ success: true, count: data.count });
        setTimeout(() => {
          router.push("/leads");
        }, 2000);
      } else {
        setResult({ success: false, error: data.error });
      }
    } catch (error) {
      console.error("Error importing:", error);
      setResult({ success: false, error: "Erro ao importar leads" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Importar Leads</h1>
        <p className="text-gray-500 mt-1">
          Importe leads do banco de dados existente
        </p>
      </div>

      {briefing && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Seu Briefing</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Produto:</strong> {String(briefing.produto || "Não definido")}</p>
            <p><strong>Região:</strong> {String(briefing.regiao || "Não definido")}</p>
            <p><strong>Ticket Médio:</strong> {String(briefing.ticket_medio || "Não definido")}</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Configurar Importação</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoria
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Selecione uma categoria</option>
              {CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantidade máxima
            </label>
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value={25}>25 leads</option>
              <option value={50}>50 leads</option>
              <option value={100}>100 leads</option>
              <option value={200}>200 leads</option>
            </select>
          </div>

          {result && (
            <div
              className={`p-4 rounded-md flex items-center gap-2 ${
                result.success
                  ? "bg-green-50 text-green-800"
                  : "bg-red-50 text-red-800"
              }`}
            >
              {result.success ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span>{result.count} leads importados com sucesso! Redirecionando...</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5" />
                  <span>{result.error}</span>
                </>
              )}
            </div>
          )}

          <Button
            onClick={handleImport}
            disabled={loading || !category}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Importando...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Importar Leads
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
