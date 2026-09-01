from app import create_app, db
from app.models import Category, Priority

app = create_app()
with app.app_context():
    # Créer les catégories
    cat1 = Category(name="Matériel", description="Problèmes d'équipements informatiques")
    cat2 = Category(name="Logiciel", description="Problèmes de logiciels et applications")
    cat3 = Category(name="Réseau", description="Problèmes de connexion et réseau")
    cat4 = Category(name="Compte utilisateur", description="Problèmes de comptes et accès")
    
    # Créer les priorités
    prio1 = Priority(name="Basse", level=1, color="green")
    prio2 = Priority(name="Moyenne", level=2, color="orange")
    prio3 = Priority(name="Haute", level=3, color="red")
    prio4 = Priority(name="Urgente", level=4, color="darkred")
    
    db.session.add_all([cat1, cat2, cat3, cat4])
    db.session.add_all([prio1, prio2, prio3, prio4])
    db.session.commit()
    
    print("✅ Catégories et priorités créées avec succès !")
