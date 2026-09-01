from app import create_app, db
from app.models import Ticket

app = create_app()
with app.app_context():
    db.create_all()
    print("Base de données mise à jour avec succès !")
