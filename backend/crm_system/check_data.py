from core.database import SessionLocal
from models.user import User
from models.client import Client
from models.client_base import ClientBaseList
import json

db = SessionLocal()
try:
    users = db.query(User).all()
    for u in users:
        print(f"User: {u.email}, Info: {u.user_info}")
        bases = db.query(ClientBaseList).filter(ClientBaseList.owner_id == u.id).all()
        for b in bases:
            count = db.query(Client).filter(Client.base_id == b.id).count()
            print(f"  Base: {b.name}, Clients: {count}")
finally:
    db.close()
