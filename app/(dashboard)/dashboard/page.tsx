import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Mail, MousePointer, Calendar } from "lucide-react";
import type { Entrepreneur } from "@/types/database";

export default async function DashboardPage() {
  const supabase = await createClient();

  // Get current user
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return null;
  }

  // Get entrepreneur
  const { data } = await supabase
    .from("entrepreneurs")
    .select("id")
    .eq("auth_user_id", user.id)
    .single();

  const entrepreneur = data as Pick<Entrepreneur, "id"> | null;

  if (!entrepreneur) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Complete seu briefing para começar</p>
      </div>
    );
  }

  // Get metrics
  const [leadsResult, emailsResult, openedResult, meetingsResult] = await Promise.all([
    supabase
      .from("leads")
      .select("id", { count: "exact", head: true })
      .eq("entrepreneur_id", entrepreneur.id),
    supabase
      .from("interactions")
      .select("id", { count: "exact", head: true })
      .eq("type", "email"),
    supabase
      .from("interactions")
      .select("id", { count: "exact", head: true })
      .eq("type", "email")
      .not("opened_at", "is", null),
    supabase
      .from("meetings")
      .select("id", { count: "exact", head: true })
      .eq("entrepreneur_id", entrepreneur.id),
  ]);

  const totalLeads = leadsResult.count || 0;
  const totalEmails = emailsResult.count || 0;
  const openedEmails = openedResult.count || 0;
  const totalMeetings = meetingsResult.count || 0;
  const openRate = totalEmails > 0 ? Math.round((openedEmails / totalEmails) * 100) : 0;

  const metrics = [
    {
      title: "Total de Leads",
      value: totalLeads,
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      title: "Emails Enviados",
      value: totalEmails,
      icon: Mail,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      title: "Taxa de Abertura",
      value: `${openRate}%`,
      icon: MousePointer,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      title: "Reuniões",
      value: totalMeetings,
      icon: Calendar,
      color: "text-orange-600",
      bgColor: "bg-orange-100",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Visão geral da sua prospecção</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                {metric.title}
              </CardTitle>
              <div className={`p-2 rounded-full ${metric.bgColor}`}>
                <metric.icon className={`h-4 w-4 ${metric.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Próximas Reuniões</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              Nenhuma reunião agendada
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Atividade Recente</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              Nenhuma atividade recente
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
