-- Tabelas principais da Operacao IA — ZX Control Semana 2

CREATE TABLE IF NOT EXISTS contacts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text,
  phone text UNIQUE NOT NULL,
  email text,
  tags text[],
  status text DEFAULT 'new',
  source text DEFAULT 'import',
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dispatches (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  contact_phone text NOT NULL,
  message text NOT NULL,
  provider text,
  status text DEFAULT 'pending',
  sent_at timestamptz,
  error_message text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_key text UNIQUE NOT NULL,
  data jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- RLS
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispatches ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Politicas permissivas para service_role
DROP POLICY IF EXISTS "service_role_all_contacts" ON contacts;
DROP POLICY IF EXISTS "service_role_all_dispatches" ON dispatches;
DROP POLICY IF EXISTS "service_role_all_sessions" ON sessions;
CREATE POLICY "service_role_all_contacts" ON contacts FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_dispatches" ON dispatches FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_sessions" ON sessions FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Politicas para usuarios autenticados (CRM via browser)
DROP POLICY IF EXISTS "authenticated_all_contacts" ON contacts;
DROP POLICY IF EXISTS "authenticated_all_dispatches" ON dispatches;
DROP POLICY IF EXISTS "authenticated_all_sessions" ON sessions;
CREATE POLICY "authenticated_all_contacts" ON contacts FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "authenticated_all_dispatches" ON dispatches FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "authenticated_all_sessions" ON sessions FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Funcao para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS contacts_updated_at ON contacts;
CREATE TRIGGER contacts_updated_at
  BEFORE UPDATE ON contacts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS sessions_updated_at ON sessions;
CREATE TRIGGER sessions_updated_at
  BEFORE UPDATE ON sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
