from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(email="admin@chu.com").first()
    if u:
        u.role = 'admin'
        db.session.commit()
        print("✅ Rôle changé en ADMIN pour admin@chu.com")
    else:
        print("❌ Utilisateur non trouvé. Vous devez d'abord créer un compte sur le site.")
