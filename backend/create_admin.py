from backend.app import create_app, db
from backend.models import User

app = create_app()
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(
            username="admin",
            email="admin@parkingapp.local",
            role="admin"
        )
        admin.set_password("adminadmin")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created")
    else:
        print("ℹ️  Admin already exists")