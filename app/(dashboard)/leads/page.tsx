import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Users, Plus } from "lucide-react";

const statusColors: Record<string, string> = {
  new: "bg-gray-100 text-gray-800",
  contacted: "bg-yellow-100 text-yellow-800",
  responded: "bg-blue-100 text-blue-800",
  meeting: "bg-green-100 text-green-800",
  trash: "bg-red-100 text-red-800",
};

const classificationColors: Record<string, string> = {
  cold: "bg-blue-100 text-blue-800",
  engaged: "bg-green-100 text-green-800",
  trash: "bg-gray-100 text-gray-800",
};

export default async function LeadsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; status?: string; classification?: string }>;
}) {
  const params = await searchParams;
  const supabase = await createClient();

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  // Get entrepreneur
  const { data: entrepreneur } = await supabase
    .from("entrepreneurs")
    .select("id")
    .eq("auth_user_id", user.id)
    .single();

  if (!entrepreneur) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Complete seu briefing primeiro</p>
        <Link href="/briefing">
          <Button>Ir para Briefing</Button>
        </Link>
      </div>
    );
  }

  const page = parseInt(params.page || "1");
  const pageSize = 20;
  const offset = (page - 1) * pageSize;

  // Build query
  let query = supabase
    .from("leads")
    .select("*", { count: "exact" })
    .eq("entrepreneur_id", entrepreneur.id)
    .order("created_at", { ascending: false })
    .range(offset, offset + pageSize - 1);

  if (params.status && params.status !== "all") {
    query = query.eq("status", params.status);
  }
  if (params.classification && params.classification !== "all") {
    query = query.eq("classification", params.classification);
  }

  const { data: leads, count } = await query;
  const totalPages = Math.ceil((count || 0) / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">
            {count || 0} leads encontrados
          </p>
        </div>
        <Link href="/prospecting">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Importar Leads
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="py-4">
          <div className="flex gap-4 flex-wrap">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Status
              </label>
              <select
                className="border rounded-md px-3 py-2 text-sm"
                defaultValue={params.status || "all"}
                onChange={(e) => {
                  const url = new URL(window.location.href);
                  url.searchParams.set("status", e.target.value);
                  url.searchParams.set("page", "1");
                  window.location.href = url.toString();
                }}
              >
                <option value="all">Todos</option>
                <option value="new">Novo</option>
                <option value="contacted">Contatado</option>
                <option value="responded">Respondeu</option>
                <option value="meeting">Reunião</option>
                <option value="trash">Descartado</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Classificação
              </label>
              <select
                className="border rounded-md px-3 py-2 text-sm"
                defaultValue={params.classification || "all"}
                onChange={(e) => {
                  const url = new URL(window.location.href);
                  url.searchParams.set("classification", e.target.value);
                  url.searchParams.set("page", "1");
                  window.location.href = url.toString();
                }}
              >
                <option value="all">Todas</option>
                <option value="cold">Frio</option>
                <option value="engaged">Engajado</option>
                <option value="trash">Descartado</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Leads Table */}
      {leads && leads.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nome
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Empresa
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Telefone
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Classificação
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {lead.name}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {lead.company || "-"}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {lead.phone || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={statusColors[lead.status] || ""}>
                        {lead.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={classificationColors[lead.classification] || ""}>
                        {lead.classification}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t">
              <p className="text-sm text-gray-500">
                Página {page} de {totalPages}
              </p>
              <div className="flex gap-2">
                <Link
                  href={`/leads?page=${Math.max(1, page - 1)}&status=${params.status || ""}&classification=${params.classification || ""}`}
                >
                  <Button variant="outline" size="sm" disabled={page <= 1}>
                    Anterior
                  </Button>
                </Link>
                <Link
                  href={`/leads?page=${Math.min(totalPages, page + 1)}&status=${params.status || ""}&classification=${params.classification || ""}`}
                >
                  <Button variant="outline" size="sm" disabled={page >= totalPages}>
                    Próximo
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum lead encontrado
            </h3>
            <p className="text-gray-500 mb-4">
              Importe leads do banco de dados para começar
            </p>
            <Link href="/prospecting">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Importar Leads
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
