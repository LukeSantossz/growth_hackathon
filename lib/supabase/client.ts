import { createBrowserClient } from "@supabase/ssr";

// For MVP, we use any typing to avoid complex Supabase type issues
// In production, generate types with: npx supabase gen types typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
