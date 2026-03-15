from core.database import SessionLocal
from models.user import User
import json

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "teste@teste3.com").first()
    if user:
        print(f"Context: {user.onboarding_context}")
    else:
        print("User not found")
finally:
    db.close()
