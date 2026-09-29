from app.database import SessionLocal
from app.models.user import User
from app.auth import hash_password

db = SessionLocal()

existing_user = db.query(User).filter(User.username == "admin1").first()

if existing_user:
    existing_user.password = hash_password("admin123")
    existing_user.role = "admin"
    db.commit()
    print("Admin account updated successfully")
else:
    user = User(
        username="admin1",
        password=hash_password("admin123"),
        role="admin"
    )
    db.add(user)
    db.commit()
    print("Admin account created successfully")

db.close()

