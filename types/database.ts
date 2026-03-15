export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      entrepreneurs: {
        Row: {
          id: string;
          auth_user_id: string;
          email: string;
          name: string;
          company: string;
          briefing_json: Json | null;
          calendar_token: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          auth_user_id: string;
          email: string;
          name: string;
          company: string;
          briefing_json?: Json | null;
          calendar_token?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          auth_user_id?: string;
          email?: string;
          name?: string;
          company?: string;
          briefing_json?: Json | null;
          calendar_token?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      campaigns: {
        Row: {
          id: string;
          entrepreneur_id: string;
          name: string | null;
          queries_json: Json | null;
          status: string;
          leads_found: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          entrepreneur_id: string;
          name?: string | null;
          queries_json?: Json | null;
          status?: string;
          leads_found?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          entrepreneur_id?: string;
          name?: string | null;
          queries_json?: Json | null;
          status?: string;
          leads_found?: number;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      leads: {
        Row: {
          id: string;
          entrepreneur_id: string;
          places_id: string | null;
          name: string;
          company: string | null;
          email: string | null;
          phone: string | null;
          source: string;
          status: string;
          classification: string;
          profile_url: string | null;
          raw_data: Json | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          entrepreneur_id: string;
          places_id?: string | null;
          name: string;
          company?: string | null;
          email?: string | null;
          phone?: string | null;
          source?: string;
          status?: string;
          classification?: string;
          profile_url?: string | null;
          raw_data?: Json | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          entrepreneur_id?: string;
          places_id?: string | null;
          name?: string;
          company?: string | null;
          email?: string | null;
          phone?: string | null;
          source?: string;
          status?: string;
          classification?: string;
          profile_url?: string | null;
          raw_data?: Json | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      interactions: {
        Row: {
          id: string;
          lead_id: string;
          type: string;
          subject: string | null;
          content: string;
          message_id: string | null;
          opened_at: string | null;
          clicked_at: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          lead_id: string;
          type: string;
          subject?: string | null;
          content: string;
          message_id?: string | null;
          opened_at?: string | null;
          clicked_at?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          lead_id?: string;
          type?: string;
          subject?: string | null;
          content?: string;
          message_id?: string | null;
          opened_at?: string | null;
          clicked_at?: string | null;
          created_at?: string;
        };
        Relationships: [];
      };
      meetings: {
        Row: {
          id: string;
          lead_id: string;
          entrepreneur_id: string;
          calendar_event_id: string | null;
          scheduled_at: string;
          meet_link: string | null;
          status: string;
          notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          lead_id: string;
          entrepreneur_id: string;
          calendar_event_id?: string | null;
          scheduled_at: string;
          meet_link?: string | null;
          status?: string;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          lead_id?: string;
          entrepreneur_id?: string;
          calendar_event_id?: string | null;
          scheduled_at?: string;
          meet_link?: string | null;
          status?: string;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      places: {
        Row: {
          id: string;
          termo_buscado: string | null;
          nome: string | null;
          horario_funcionamento: string | null;
          estado: string | null;
          cidade: string | null;
          email: string | null;
          numero_telefone: string | null;
          categoria: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          termo_buscado?: string | null;
          nome?: string | null;
          horario_funcionamento?: string | null;
          estado?: string | null;
          cidade?: string | null;
          email?: string | null;
          numero_telefone?: string | null;
          categoria?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          termo_buscado?: string | null;
          nome?: string | null;
          horario_funcionamento?: string | null;
          estado?: string | null;
          cidade?: string | null;
          email?: string | null;
          numero_telefone?: string | null;
          categoria?: string | null;
          created_at?: string;
        };
        Relationships: [];
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
}

// Helper types
export type Entrepreneur = Database["public"]["Tables"]["entrepreneurs"]["Row"];
export type Campaign = Database["public"]["Tables"]["campaigns"]["Row"];
export type Lead = Database["public"]["Tables"]["leads"]["Row"];
export type Interaction = Database["public"]["Tables"]["interactions"]["Row"];
export type Meeting = Database["public"]["Tables"]["meetings"]["Row"];
export type Place = Database["public"]["Tables"]["places"]["Row"];

// Insert types
export type EntrepreneurInsert = Database["public"]["Tables"]["entrepreneurs"]["Insert"];
export type CampaignInsert = Database["public"]["Tables"]["campaigns"]["Insert"];
export type LeadInsert = Database["public"]["Tables"]["leads"]["Insert"];
export type InteractionInsert = Database["public"]["Tables"]["interactions"]["Insert"];
export type MeetingInsert = Database["public"]["Tables"]["meetings"]["Insert"];

// Briefing JSON structure
export interface BriefingData {
  produto: string;
  icp: {
    cargo?: string;
    setor?: string;
    tamanho_empresa?: string;
  };
  regiao: string;
  ticket_medio: string;
  dores: string[];
  keywords?: string[];
}
