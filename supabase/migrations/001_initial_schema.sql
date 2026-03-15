-- Migration: Initial Schema for AI Sales Team
-- Extends existing 'places' table with new tables for the sales platform

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Entrepreneurs table (users of the platform)
CREATE TABLE IF NOT EXISTS entrepreneurs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    briefing_json JSONB,
    calendar_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaigns table (prospecting campaigns)
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entrepreneur_id UUID NOT NULL REFERENCES entrepreneurs(id) ON DELETE CASCADE,
    name TEXT,
    queries_json JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    leads_found INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leads table (prospects imported from places or other sources)
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entrepreneur_id UUID NOT NULL REFERENCES entrepreneurs(id) ON DELETE CASCADE,
    places_id UUID REFERENCES places(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    company TEXT,
    email TEXT,
    phone TEXT,
    source TEXT NOT NULL DEFAULT 'google_maps' CHECK (source IN ('google_maps', 'linkedin', 'manual', 'import')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'responded', 'meeting', 'converted', 'trash')),
    classification TEXT NOT NULL DEFAULT 'cold' CHECK (classification IN ('cold', 'engaged', 'trash')),
    profile_url TEXT,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interactions table (emails, responses, etc.)
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('email', 'response', 'note')),
    subject TEXT,
    content TEXT NOT NULL,
    message_id TEXT,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Meetings table (scheduled meetings)
CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    entrepreneur_id UUID NOT NULL REFERENCES entrepreneurs(id) ON DELETE CASCADE,
    calendar_event_id TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    meet_link TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_leads_entrepreneur ON leads(entrepreneur_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_classification ON leads(classification);
CREATE INDEX IF NOT EXISTS idx_interactions_lead ON interactions(lead_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(type);
CREATE INDEX IF NOT EXISTS idx_meetings_entrepreneur ON meetings(entrepreneur_id);
CREATE INDEX IF NOT EXISTS idx_meetings_scheduled ON meetings(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_campaigns_entrepreneur ON campaigns(entrepreneur_id);

-- Enable Row Level Security
ALTER TABLE entrepreneurs ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for entrepreneurs
CREATE POLICY "Users can view own entrepreneur profile"
    ON entrepreneurs FOR SELECT
    USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can update own entrepreneur profile"
    ON entrepreneurs FOR UPDATE
    USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can insert own entrepreneur profile"
    ON entrepreneurs FOR INSERT
    WITH CHECK (auth.uid() = auth_user_id);

-- RLS Policies for campaigns
CREATE POLICY "Users can view own campaigns"
    ON campaigns FOR SELECT
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can insert own campaigns"
    ON campaigns FOR INSERT
    WITH CHECK (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can update own campaigns"
    ON campaigns FOR UPDATE
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can delete own campaigns"
    ON campaigns FOR DELETE
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

-- RLS Policies for leads
CREATE POLICY "Users can view own leads"
    ON leads FOR SELECT
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can insert own leads"
    ON leads FOR INSERT
    WITH CHECK (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can update own leads"
    ON leads FOR UPDATE
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can delete own leads"
    ON leads FOR DELETE
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

-- RLS Policies for interactions
CREATE POLICY "Users can view own interactions"
    ON interactions FOR SELECT
    USING (lead_id IN (
        SELECT l.id FROM leads l
        JOIN entrepreneurs e ON l.entrepreneur_id = e.id
        WHERE e.auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can insert own interactions"
    ON interactions FOR INSERT
    WITH CHECK (lead_id IN (
        SELECT l.id FROM leads l
        JOIN entrepreneurs e ON l.entrepreneur_id = e.id
        WHERE e.auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can update own interactions"
    ON interactions FOR UPDATE
    USING (lead_id IN (
        SELECT l.id FROM leads l
        JOIN entrepreneurs e ON l.entrepreneur_id = e.id
        WHERE e.auth_user_id = auth.uid()
    ));

-- RLS Policies for meetings
CREATE POLICY "Users can view own meetings"
    ON meetings FOR SELECT
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can insert own meetings"
    ON meetings FOR INSERT
    WITH CHECK (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

CREATE POLICY "Users can update own meetings"
    ON meetings FOR UPDATE
    USING (entrepreneur_id IN (SELECT id FROM entrepreneurs WHERE auth_user_id = auth.uid()));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_entrepreneurs_updated_at
    BEFORE UPDATE ON entrepreneurs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at
    BEFORE UPDATE ON meetings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
