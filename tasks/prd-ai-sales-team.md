# PRD: AI Sales Team — MVP

## Introduction

Plataforma web onde agentes de IA executam o ciclo completo de pré-vendas para pequenos empresários — do briefing até a reunião agendada no Google Calendar. O empresário não tem equipe nem recursos para contratar SDRs, então a IA assume a prospecção, qualificação, outreach e agendamento de forma automatizada.

**Pipeline:** Cadastro → Briefing (chat IA) → Prospecção (LinkedIn + Google Maps) → CRM → Outreach (email) → Nurturing → Agendamento

---

## Goals

- Permitir que um empresário configure sua prospecção em menos de 5 minutos via chat
- Automatizar busca de leads em LinkedIn e Google Maps (≥30 leads/dia)
- Enviar emails personalizados gerados por IA com tracking de abertura/clique
- Executar sequência de follow-ups automáticos (3, 7, 14 dias)
- Detectar interesse positivo e agendar reuniões diretamente no Google Calendar
- Suportar 1-10 empresários simultâneos (beta fechado)

---

## User Stories

### Fase 1 — Onboarding + Briefing

#### US-001: Cadastro com email e senha
**Description:** As a small business owner, I want to create an account with my email and password so that I can access the platform.

**Acceptance Criteria:**
- [ ] Form com campos: email, senha, nome da empresa
- [ ] Validação de email único
- [ ] Senha com mínimo 8 caracteres
- [ ] Criação de workspace isolado (row-level security no Supabase)
- [ ] Redirect automático para tela de briefing após cadastro
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-002: Tela de chat para briefing
**Description:** As a small business owner, I want to have a chat conversation with an AI so that I can describe my business and ideal customer profile.

**Acceptance Criteria:**
- [ ] Interface de chat com histórico de mensagens
- [ ] Input de texto com botão de enviar
- [ ] Indicador de "digitando" enquanto IA processa
- [ ] Mensagens do usuário alinhadas à direita, IA à esquerda
- [ ] Scroll automático para última mensagem
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-003: Fluxo de perguntas do briefing (híbrido)
**Description:** As a system, I need to collect mandatory information through fixed questions and allow dynamic follow-ups so that the briefing is complete and useful.

**Acceptance Criteria:**
- [ ] Perguntas obrigatórias coletadas: produto/serviço, ICP (cargo/setor), região de atuação, ticket médio, principais dores do cliente
- [ ] IA faz follow-ups dinâmicos quando resposta é vaga ou incompleta
- [ ] Guardrail: não avança sem informações mínimas
- [ ] Mensagem clara indicando quando briefing está completo
- [ ] Typecheck/lint passes

---

#### US-004: Salvar briefing estruturado
**Description:** As a system, I need to save the briefing as structured JSON so that it can be used for prospecting and email generation.

**Acceptance Criteria:**
- [ ] Briefing salvo como JSON no campo `briefing_json` da tabela Entrepreneur
- [ ] JSON contém: produto, icp, regiao, ticket_medio, dores, keywords
- [ ] Claude gera queries de busca (cargos LinkedIn + categorias Google Maps)
- [ ] Queries salvas em nova Campaign vinculada ao Entrepreneur
- [ ] Typecheck/lint passes

---

### Fase 2 — Prospecção

#### US-005: Iniciar job de prospecção
**Description:** As a small business owner, I want to start prospecting after completing the briefing so that leads are found automatically.

**Acceptance Criteria:**
- [ ] Botão "Iniciar Prospecção" aparece após briefing completo
- [ ] Click dispara job na fila (Inngest/BullMQ)
- [ ] UI mostra status simples: "Buscando leads..." / "Finalizado"
- [ ] Job roda em background, não bloqueia navegação
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-006: Buscar leads no LinkedIn via RapidAPI
**Description:** As a system, I need to search LinkedIn profiles based on briefing queries so that relevant leads are found.

**Acceptance Criteria:**
- [ ] Worker Python consome job da fila
- [ ] Executa busca na RapidAPI LinkedIn Profile Search
- [ ] Parâmetros: cargo, setor, localização (do briefing)
- [ ] Extrai: nome, cargo, empresa, URL do perfil, email (se disponível)
- [ ] Respeita rate limits da API
- [ ] Typecheck/lint passes

---

#### US-007: Buscar leads no Google Maps via Places API
**Description:** As a system, I need to search Google Maps for businesses matching the ICP so that local leads are found.

**Acceptance Criteria:**
- [ ] Worker executa busca na Google Places API
- [ ] Parâmetros: tipo de negócio, localização (do briefing)
- [ ] Extrai: nome do negócio, endereço, telefone, website, rating
- [ ] Respeita rate limits da API
- [ ] Typecheck/lint passes

---

#### US-008: Salvar leads com deduplicação
**Description:** As a system, I need to save leads without duplicates so that the CRM stays clean.

**Acceptance Criteria:**
- [ ] Leads salvos na tabela Lead com entrepreneur_id
- [ ] Deduplicação por email OU telefone OU profile_url
- [ ] Campo `source` indica origem: 'linkedin' | 'google_maps'
- [ ] Campo `raw_data` guarda JSON original da API
- [ ] Status inicial: 'new'
- [ ] Atualiza Campaign com total de leads_found
- [ ] Typecheck/lint passes

---

#### US-009: Classificação inicial de leads
**Description:** As a system, I need to classify new leads automatically so that outreach is prioritized correctly.

**Acceptance Criteria:**
- [ ] Claude Haiku analisa dados do lead (cargo, tamanho empresa, completude)
- [ ] Classifica como: 'trash' | 'cold' | 'engaged'
- [ ] Leads sem email/telefone válido → trash
- [ ] Leads com cargo matching ICP → cold ou engaged
- [ ] Classificação salva no campo `classification`
- [ ] Typecheck/lint passes

---

### Fase 3 — CRM + Dashboard

#### US-010: Tabela de leads (CRM)
**Description:** As a small business owner, I want to see all my leads in a table so that I can track prospecting progress.

**Acceptance Criteria:**
- [ ] Tabela com colunas: nome, empresa, origem, status, classificação, última interação
- [ ] Paginação (20 leads por página)
- [ ] Ordenação por data de criação (mais recente primeiro)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-011: Filtros e busca no CRM
**Description:** As a small business owner, I want to filter and search leads so that I can find specific prospects.

**Acceptance Criteria:**
- [ ] Dropdown filtro por status: all | new | contacted | responded | meeting | trash
- [ ] Dropdown filtro por origem: all | linkedin | google_maps
- [ ] Dropdown filtro por classificação: all | cold | engaged | trash
- [ ] Campo de busca por nome/empresa
- [ ] Filtros persistem na URL (query params)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-012: Perfil completo do lead
**Description:** As a small business owner, I want to click on a lead to see full details and interaction history so that I understand the context before a meeting.

**Acceptance Criteria:**
- [ ] Click na linha abre modal ou página de detalhes
- [ ] Mostra todos os dados do lead (nome, empresa, cargo, email, telefone, etc.)
- [ ] Lista histórico de interações (emails enviados, aberturas, respostas)
- [ ] Mostra reuniões agendadas (se houver)
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-013: Dashboard com métricas principais
**Description:** As a small business owner, I want to see key metrics on a dashboard so that I understand my sales pipeline performance.

**Acceptance Criteria:**
- [ ] Cards no topo: Total leads, Emails enviados, Taxa de abertura (%), Reuniões agendadas
- [ ] Funil visual: Leads → Contatados → Responderam → Reunião
- [ ] Lista "Próximas reuniões" (data, lead, empresa)
- [ ] Lista "Atividade recente" (últimas 10 interações)
- [ ] Dados atualizados ao carregar página
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

### Fase 4 — Outreach + Agendamento

#### US-014: Gerar email personalizado com IA
**Description:** As a system, I need to generate personalized cold emails using AI so that outreach is relevant and effective.

**Acceptance Criteria:**
- [ ] Claude Sonnet recebe: briefing do empresário + dados do lead
- [ ] Gera email com subject e body personalizados
- [ ] Tom profissional, direto, sem spam words
- [ ] Inclui CTA claro (responder ou agendar)
- [ ] Email tem menos de 150 palavras
- [ ] Typecheck/lint passes

---

#### US-015: Enviar email via Resend
**Description:** As a system, I need to send emails through Resend so that leads receive personalized outreach.

**Acceptance Criteria:**
- [ ] Integração com Resend API configurada
- [ ] Email enviado com from: domínio do empresário ou domínio da plataforma
- [ ] Tracking pixel inserido para detectar abertura
- [ ] Links com tracking para detectar cliques
- [ ] Interaction criada com type='email', content=email enviado
- [ ] Lead status atualizado para 'contacted'
- [ ] Typecheck/lint passes

---

#### US-016: Webhook de tracking (abertura/clique)
**Description:** As a system, I need to receive Resend webhooks so that email opens and clicks are tracked.

**Acceptance Criteria:**
- [ ] Endpoint /api/webhooks/resend recebe eventos
- [ ] Evento 'email.opened' → atualiza Interaction.opened_at
- [ ] Evento 'email.clicked' → atualiza Interaction.clicked_at
- [ ] Reclassifica lead: cold → engaged se abriu email
- [ ] Typecheck/lint passes

---

#### US-017: Sequência de follow-ups automáticos
**Description:** As a system, I need to send follow-up emails at 3, 7, and 14 days so that leads are nurtured over time.

**Acceptance Criteria:**
- [ ] Cron job diário verifica leads contacted sem resposta
- [ ] Calcula dias desde último contato
- [ ] 3 dias → envia follow-up 1
- [ ] 7 dias → envia follow-up 2
- [ ] 14 dias → envia follow-up 3
- [ ] Claude varia conteúdo a cada follow-up (não repetir)
- [ ] Para sequência se lead responder
- [ ] Após 3 follow-ups sem resposta → classification='trash'
- [ ] Typecheck/lint passes

---

#### US-018: Receber respostas de email (inbound)
**Description:** As a system, I need to receive email replies so that lead responses are captured.

**Acceptance Criteria:**
- [ ] Webhook Resend inbound configurado
- [ ] Resposta associada ao lead correto (por email do remetente)
- [ ] Interaction criada com type='response', content=texto da resposta
- [ ] Lead status atualizado para 'responded'
- [ ] Typecheck/lint passes

---

#### US-019: Detectar interesse positivo na resposta
**Description:** As a system, I need to analyze responses to detect positive intent so that meetings can be scheduled.

**Acceptance Criteria:**
- [ ] Claude Sonnet analisa texto da resposta
- [ ] Classifica intenção: 'positive' | 'negative' | 'neutral' | 'unsubscribe'
- [ ] Se negative/unsubscribe → classification='trash', para outreach
- [ ] Se positive → trigger fluxo de agendamento
- [ ] Se neutral → continua nurturing normal
- [ ] Typecheck/lint passes

---

#### US-020: Conectar Google Calendar do empresário
**Description:** As a small business owner, I want to connect my Google Calendar so that meetings can be scheduled automatically.

**Acceptance Criteria:**
- [ ] Botão "Conectar Google Calendar" nas configurações
- [ ] Fluxo OAuth2 com scopes: calendar.readonly, calendar.events
- [ ] Token salvo criptografado em Entrepreneur.calendar_token
- [ ] Indicador visual de calendário conectado
- [ ] Typecheck/lint passes
- [ ] Verify in browser using dev-browser skill

---

#### US-021: Buscar horários disponíveis
**Description:** As a system, I need to find available time slots so that meetings can be proposed to leads.

**Acceptance Criteria:**
- [ ] Consulta Google Calendar API com token do empresário
- [ ] Busca próximos 5 dias úteis
- [ ] Horário comercial: 9h-18h
- [ ] Retorna até 5 slots disponíveis de 30 minutos
- [ ] Exclui horários já ocupados
- [ ] Typecheck/lint passes

---

#### US-022: Propor horários ao lead por email
**Description:** As a system, I need to send available time slots to interested leads so that they can choose a meeting time.

**Acceptance Criteria:**
- [ ] Claude gera email com proposta de reunião
- [ ] Lista 3-5 horários disponíveis formatados (dia, data, hora)
- [ ] Links clicáveis para cada horário (confirma agendamento)
- [ ] Email enviado via Resend
- [ ] Interaction registrada
- [ ] Typecheck/lint passes

---

#### US-023: Confirmar agendamento e criar evento
**Description:** As a system, I need to create a calendar event when a lead confirms a time slot so that the meeting is scheduled.

**Acceptance Criteria:**
- [ ] Endpoint /api/schedule/confirm recebe click do lead
- [ ] Valida que slot ainda está disponível
- [ ] Cria evento no Google Calendar com:
  - Título: "Reunião com [Nome do Lead] - [Empresa]"
  - Descrição: contexto do briefing + dados do lead
  - Link Google Meet automático
  - Convite para email do lead
- [ ] Meeting criada no banco com calendar_event_id
- [ ] Lead status='meeting'
- [ ] Typecheck/lint passes

---

#### US-024: Notificar empresário sobre reunião agendada
**Description:** As a small business owner, I want to receive an email notification when a meeting is scheduled so that I'm aware of upcoming calls.

**Acceptance Criteria:**
- [ ] Email enviado para empresário via Resend
- [ ] Contém: nome do lead, empresa, data/hora, link Google Meet
- [ ] Contém: resumo do contexto (de onde veio o lead, interações)
- [ ] Typecheck/lint passes

---

## Functional Requirements

### Autenticação & Multi-tenancy
- FR-01: Sistema deve usar Supabase Auth para cadastro/login com email e senha
- FR-02: Cada empresário tem workspace isolado via Row Level Security (RLS)
- FR-03: Todas as queries devem filtrar por entrepreneur_id automaticamente

### Briefing
- FR-04: Chat deve coletar obrigatoriamente: produto, ICP, região, ticket médio, dores
- FR-05: IA deve fazer follow-ups dinâmicos para respostas incompletas
- FR-06: Briefing só é considerado completo quando todos os campos obrigatórios estão preenchidos
- FR-07: Briefing é salvo como JSON estruturado no banco

### Prospecção
- FR-08: Jobs de prospecção rodam em background via fila (Inngest ou BullMQ)
- FR-09: LinkedIn: busca via RapidAPI respeitando rate limits
- FR-10: Google Maps: busca via Places API respeitando rate limits
- FR-11: Leads são deduplicados por email, telefone ou URL de perfil
- FR-12: Classificação inicial usa Claude Haiku para eficiência de custo

### CRM
- FR-13: Tabela de leads com filtros por status, origem e classificação
- FR-14: Busca textual por nome ou empresa
- FR-15: Paginação de 20 itens por página
- FR-16: Perfil do lead mostra histórico completo de interações

### Outreach
- FR-17: Emails gerados por Claude Sonnet, personalizados com briefing + dados do lead
- FR-18: Envio via Resend com tracking de abertura e clique
- FR-19: Webhooks atualizam status de interações em tempo real
- FR-20: Reclassificação dinâmica: cold → engaged quando lead abre email

### Nurturing
- FR-21: Sequência de follow-ups: 3, 7, 14 dias após contato sem resposta
- FR-22: Conteúdo dos follow-ups varia a cada envio
- FR-23: Sequência para se lead responde
- FR-24: Lead marcado como trash após 3 tentativas sem resposta

### Agendamento
- FR-25: Integração Google Calendar via OAuth2
- FR-26: Sistema propõe horários disponíveis automaticamente
- FR-27: Evento criado com link Google Meet automático
- FR-28: Empresário notificado por email quando reunião é agendada

### Dashboard
- FR-29: Cards de métricas: total leads, emails enviados, taxa abertura, reuniões
- FR-30: Funil visual de conversão
- FR-31: Lista de próximas reuniões
- FR-32: Feed de atividade recente

---

## Non-Goals (Out of Scope)

- Painel admin multi-tenant (gerenciamento direto no banco)
- WhatsApp / LinkedIn DMs (complexidade alta, compliance incerto)
- Templates editáveis de email pelo empresário
- Configuração manual de horários disponíveis (usa Google Calendar real)
- App mobile
- Billing/pagamentos
- Integração com CRM externo (Salesforce, HubSpot, etc.)
- Múltiplas campanhas simultâneas por empresário
- A/B testing de mensagens
- Importação de leads de outras fontes

---

## Design Considerations

### UI/UX
- Interface minimalista, foco em simplicidade
- Usar shadcn/ui para componentes consistentes
- Dashboard como tela principal após login
- Chat de briefing deve parecer conversa natural (estilo WhatsApp/iMessage)
- Status de prospecção: simples e não-intrusivo

### Componentes shadcn/ui sugeridos
- `Card` para métricas do dashboard
- `Table` para CRM
- `Dialog` para detalhes do lead
- `Input` + `Button` para chat
- `Select` para filtros
- `Badge` para status/classificação

### Cores de classificação
- Trash: gray
- Cold: blue
- Engaged: green

### Cores de status
- New: gray
- Contacted: yellow
- Responded: blue
- Meeting: green

---

## Technical Considerations

### Arquitetura
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│  Supabase DB    │◀────│  Python Worker  │
│  (Vercel)       │     │  (PostgreSQL)   │     │  (Railway)      │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Supabase      │     │     Resend      │     │   Claude API    │
│   Auth          │     │   (Email)       │     │   (LLM)         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│ Google Calendar │                             │    RapidAPI     │
│     (OAuth2)    │                             │   + Places API  │
└─────────────────┘                             └─────────────────┘
```

### Modelo de Dados
```sql
Entrepreneur (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  name TEXT,
  company TEXT,
  briefing_json JSONB,
  calendar_token TEXT ENCRYPTED,
  created_at TIMESTAMP
)

Lead (
  id UUID PRIMARY KEY,
  entrepreneur_id UUID REFERENCES Entrepreneur,
  name TEXT,
  company TEXT,
  email TEXT,
  phone TEXT,
  source TEXT, -- 'linkedin' | 'google_maps'
  status TEXT, -- 'new' | 'contacted' | 'responded' | 'meeting' | 'trash'
  classification TEXT, -- 'trash' | 'cold' | 'engaged'
  profile_url TEXT,
  raw_data JSONB,
  created_at TIMESTAMP
)

Interaction (
  id UUID PRIMARY KEY,
  lead_id UUID REFERENCES Lead,
  type TEXT, -- 'email' | 'response'
  content TEXT,
  opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  created_at TIMESTAMP
)

Meeting (
  id UUID PRIMARY KEY,
  lead_id UUID REFERENCES Lead,
  calendar_event_id TEXT,
  scheduled_at TIMESTAMP,
  status TEXT, -- 'scheduled' | 'completed' | 'cancelled'
  created_at TIMESTAMP
)

Campaign (
  id UUID PRIMARY KEY,
  entrepreneur_id UUID REFERENCES Entrepreneur,
  queries_json JSONB,
  status TEXT, -- 'pending' | 'running' | 'completed'
  leads_found INTEGER,
  created_at TIMESTAMP
)
```

### Segurança
- RLS habilitado em todas as tabelas
- Tokens OAuth2 criptografados em repouso
- Rate limiting em endpoints públicos
- Validação de webhooks (signature verification)

### Custos LLM
- Claude Haiku: classificação de leads, análise de intenção
- Claude Sonnet: geração de emails, briefing conversacional

### Infraestrutura parcialmente configurada
- Verificar: Supabase project, Vercel deployment, domínio
- Configurar: Resend, RapidAPI, Google Cloud (Places + Calendar)

---

## Success Metrics

| Métrica | Meta |
|---------|------|
| Tempo de briefing | < 5 minutos |
| Leads prospectados/dia | ≥ 30 |
| Taxa de entrega de email | > 95% |
| Taxa de abertura | > 20% |
| Taxa de resposta | > 3% |
| Taxa de agendamento | > 0.5% dos leads |
| Primeira reunião agendada | ≤ 10 dias após briefing |

---

## Open Questions

1. **Domínio de email:** Usar domínio próprio da plataforma ou exigir que empresário configure domínio próprio? (impacta deliverability)

2. **Limite de leads:** Definir limite máximo de leads por empresário no MVP? (controle de custos de API)

3. **Horário de envio:** Enviar emails em horário comercial do lead (baseado em timezone) ou do empresário?

4. **Fallback de email:** O que fazer quando lead do Google Maps não tem email? (tentar enriquecer via outras APIs?)

5. **Idioma:** MVP só em português ou suportar inglês também? (afeta prompts do Claude)

6. **Retry de APIs:** Quantas tentativas em caso de falha de API externa antes de marcar job como failed?

---

## Implementation Order

Seguindo a abordagem sequencial (resposta 1A):

### Sprint 1: Fase 1 (Onboarding + Briefing)
- US-001: Cadastro
- US-002: Tela de chat
- US-003: Fluxo de perguntas
- US-004: Salvar briefing

### Sprint 2: Fase 2 (Prospecção)
- US-005: Iniciar job
- US-006: LinkedIn API
- US-007: Google Maps API
- US-008: Salvar leads
- US-009: Classificação inicial

### Sprint 3: Fase 3 (CRM + Dashboard)
- US-010: Tabela de leads
- US-011: Filtros e busca
- US-012: Perfil do lead
- US-013: Dashboard

### Sprint 4: Fase 4 (Outreach + Agendamento)
- US-014 a US-019: Email + Nurturing
- US-020 a US-024: Calendar + Agendamento
