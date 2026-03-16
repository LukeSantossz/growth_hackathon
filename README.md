# AI Sales Team

Sistema de automacao de vendas com IA para pequenas empresas.

## Requisitos

### Frontend (Next.js)
- Node.js 18+

### Backend (Python)
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes Python)

### Servicos
- Conta no [Supabase](https://supabase.com)
- Conta na [OpenAI](https://platform.openai.com) (para chat do briefing)
- Conta no [Groq](https://console.groq.com) (para SDR Agent)
- Conta no [LangSmith](https://smith.langchain.com) (para monitoramento do agent - opcional)
- Conta no [Resend](https://resend.com) (para envio de emails - opcional)
- Conta no [Google Cloud](https://console.cloud.google.com) (para integracao com Calendar - opcional)

## Configuracao

### 1. Instalar dependencias

**Frontend (Next.js):**
```bash
npm install
```

**Backend (Python):**
```bash
cd backend
uv sync
```

### 2. Configurar variaveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as seguintes configuracoes:

#### Supabase

1. Acesse [Supabase Dashboard](https://supabase.com/dashboard)
2. Crie um novo projeto ou selecione um existente
3. Va em **Project Settings** > **API**
4. Copie a **URL** e a **anon/public key**

```env
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua_anon_key
```

#### Supabase - Configuracao de Autenticacao

Para ambiente de desenvolvimento, recomenda-se desabilitar a confirmacao de email:

1. No Supabase Dashboard, va em **Authentication** > **Providers** > **Email**
2. Desabilite **"Confirm email"**
3. Salve as alteracoes

#### Supabase - Banco de Dados

Execute as migrations no Supabase:

1. Va em **SQL Editor** no Supabase Dashboard
2. Cole e execute o conteudo do arquivo `supabase/migrations/001_initial_schema.sql`

#### OpenAI

1. Acesse [OpenAI Platform](https://platform.openai.com)
2. Crie uma API Key em **API Keys**

```env
OPENAI_API_KEY=sk-...
```

#### Resend (Email)

1. Acesse [Resend Dashboard](https://resend.com)
2. Crie uma API Key

```env
RESEND_API_KEY=re_...
```

#### Google OAuth (Calendar)

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto ou selecione um existente
3. Va em **APIs & Services** > **Credentials**
4. Crie um **OAuth 2.0 Client ID** (tipo: Web Application)
5. Adicione `http://localhost:3000/api/auth/google/callback` como **Authorized redirect URI**

```env
GOOGLE_CLIENT_ID=seu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/google/callback
```

#### Groq (SDR Agent)

1. Acesse [Groq Console](https://console.groq.com)
2. Crie uma API Key

```env
GROQ_API_KEY=gsk_...
```

#### LangSmith (Monitoramento - opcional)

1. Acesse [LangSmith](https://smith.langchain.com)
2. Crie uma API Key

```env
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_TRACING=true
```

### 3. Executar o projeto

**Frontend (Next.js):**
```bash
npm run dev
```
Acesse [http://localhost:3000](http://localhost:3000)

**Backend CRM (Python):**
```bash
cd backend/crm_system
uv run python app.py
```
API disponivel em [http://localhost:8000](http://localhost:8000)

**SDR Agent (LangGraph):**
```bash
cd backend/sdr_agent
uv sync
uv run python agent.py
```

## Scripts Disponiveis

| Comando | Descricao |
|---------|-----------|
| `npm run dev` | Inicia o servidor de desenvolvimento |
| `npm run build` | Gera build de producao |
| `npm run start` | Inicia o servidor de producao |
| `npm run lint` | Executa o linter |
| `npm run typecheck` | Verifica tipos TypeScript |

## Estrutura do Projeto

```
app/                  # Rotas e paginas (Next.js App Router)
  (auth)/             # Paginas de autenticacao (login, signup)
  (dashboard)/        # Paginas do dashboard
  api/                # API Routes
backend/              # Backend Python
  crm_system/         # Sistema CRM (FastAPI)
    api/              # Endpoints da API
    core/             # Configuracoes e database
    models/           # Modelos SQLAlchemy
    schemas/          # Schemas Pydantic
  sdr_agent/          # Agente SDR (LangGraph)
    agent/            # Nodes e estados do grafo
    evaluation/       # Scripts de avaliacao
components/           # Componentes React reutilizaveis
  ui/                 # Componentes de UI (shadcn/ui)
lib/                  # Utilitarios e configuracoes
  supabase/           # Cliente Supabase
supabase/             # Migrations e configuracoes do Supabase
types/                # Tipos TypeScript
tasks/                # Documentacao de tarefas (PRD)
```

## Criando Usuario de Teste

Apos configurar o Supabase, voce pode criar um usuario de teste:

```bash
node scripts/create-test-user.js
```

Credenciais padrao:
- **Email:** teste@teste.com
- **Senha:** teste123

> **Nota:** Certifique-se de desabilitar a confirmacao de email no Supabase (veja secao de configuracao).

## Tecnologias

### Frontend
- [Next.js 14](https://nextjs.org) - Framework React
- [Tailwind CSS](https://tailwindcss.com) - Estilizacao
- [shadcn/ui](https://ui.shadcn.com) - Componentes de UI

### Backend
- [FastAPI](https://fastapi.tiangolo.com) - Framework Python para APIs
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Framework para agentes com estado
- [LangChain](https://langchain.com) - Framework para aplicacoes com LLMs
- [SQLAlchemy](https://sqlalchemy.org) - ORM Python

### Servicos
- [Supabase](https://supabase.com) - Backend as a Service (Auth + Database)
- [OpenAI API](https://openai.com) - IA para chat do briefing
- [Groq](https://groq.com) - LLMs de alta velocidade para SDR Agent
- [LangSmith](https://smith.langchain.com) - Monitoramento de agentes
- [Resend](https://resend.com) - Envio de emails
