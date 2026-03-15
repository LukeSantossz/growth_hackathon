from sqlalchemy import text
from core.database import engine

def migrate():
    with engine.connect() as conn:
        print("Migrating database...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN user_info VARCHAR"))
            print("Added user_info to users")
        except Exception as e:
            print(f"Skipping user_info: {e}")
            
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN onboarding_context VARCHAR"))
            print("Added onboarding_context to users")
        except Exception as e:
            print(f"Skipping onboarding_context: {e}")
            
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN nome VARCHAR"))
            print("Added nome to clients")
        except Exception as e:
            print(f"Skipping nome: {e}")
        
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
