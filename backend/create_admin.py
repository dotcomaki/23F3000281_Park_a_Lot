# backend/create_admin.py

from backend.app import create_app, db
from backend.models import User

app = create_app()
with app.app_context():
    # Make sure tables exist
    db.create_all()

    # Only create if no admin exists
    if not User.query.filter_by(role="admin").first():
        admin = User(
            username="admin",
            email="admin@parkingapp.local",   # must satisfy NOT NULL
            role="admin"
        )
        admin.set_password("YourSecurePass")  # replace with a strong password
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created")
    else:
        print("ℹ️  Admin already exists")