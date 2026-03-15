"use client";

import { useState, useEffect } from "react";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Calendar, CheckCircle, ExternalLink } from "lucide-react";

export default function SettingsPage() {
  const [entrepreneur, setEntrepreneur] = useState<{ company: string; email: string; calendar_token: string | null } | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  useEffect(() => {
    async function loadData() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data } = await supabase
        .from("entrepreneurs")
        .select("company, email, calendar_token")
        .eq("auth_user_id", user.id)
        .single();

      setEntrepreneur(data);
      setLoading(false);
    }
    loadData();
  }, [supabase]);

  const handleConnectCalendar = () => {
    // In production, this would redirect to Google OAuth
    alert("Integração com Google Calendar será implementada em breve!");
  };

  if (loading) {
    return <div className="animate-pulse">Carregando...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
        <p className="text-gray-500 mt-1">Gerencie sua conta e integrações</p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Perfil</CardTitle>
          <CardDescription>Informações da sua conta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Empresa</label>
            <p className="text-gray-900">{entrepreneur?.company || "-"}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Email</label>
            <p className="text-gray-900">{entrepreneur?.email || "-"}</p>
          </div>
        </CardContent>
      </Card>

      {/* Integrations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Integrações</CardTitle>
          <CardDescription>Conecte serviços externos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Google Calendar */}
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Calendar className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="font-medium">Google Calendar</p>
                <p className="text-sm text-gray-500">
                  Agende reuniões automaticamente
                </p>
              </div>
            </div>
            {entrepreneur?.calendar_token ? (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                <span className="text-sm font-medium">Conectado</span>
              </div>
            ) : (
              <Button variant="outline" onClick={handleConnectCalendar}>
                <ExternalLink className="w-4 h-4 mr-2" />
                Conectar
              </Button>
            )}
          </div>

          {/* Resend */}
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-5 h-5 text-purple-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
              </div>
              <div>
                <p className="font-medium">Email (Resend)</p>
                <p className="text-sm text-gray-500">
                  Envio de emails personalizados
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Configurado</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* API Keys Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Chaves de API</CardTitle>
          <CardDescription>Gerenciadas via variáveis de ambiente</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">
            As chaves de API (Anthropic, Resend, Google) são configuradas no servidor via variáveis de ambiente para maior segurança.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
