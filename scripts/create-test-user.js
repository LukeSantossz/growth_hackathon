const { createClient } = require("@supabase/supabase-js");
require("dotenv").config();

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing Supabase credentials in .env file");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function createTestUser() {
  const email = "teste@teste.com";
  const password = "teste123";

  console.log("Creating test user...");
  console.log(`Email: ${email}`);
  console.log(`Password: ${password}`);

  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });

  if (error) {
    console.error("Error creating user:", error.message);
    process.exit(1);
  }

  console.log("\n✓ Test user created successfully!");
  console.log("User ID:", data.user?.id);

  if (data.user?.identities?.length === 0) {
    console.log("\n⚠ Note: User already exists. Use the credentials above to login.");
  }
}

createTestUser();
