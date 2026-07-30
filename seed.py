from app import create_app, db
from app.models import User, Category, Priority
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Supprimer les données existantes (optionnel)
    db.drop_all()
    db.create_all()
    
    # Créer les catégories
    categories = [
        Category(name='Informatique', description='Problèmes liés aux ordinateurs et logiciels'),
        Category(name='Réseau', description='Problèmes de connexion et réseau'),
        Category(name='Email', description='Problèmes de messagerie électronique'),
        Category(name='Téléphonie', description='Problèmes de téléphone et téléphonie'),
        Category(name='Imprimante', description='Problèmes d\'impression et scanneurs'),
        Category(name='Autre', description='Autres types de demandes'),
    ]
    db.session.add_all(categories)
    
    # Créer les priorités
    priorities = [
        Priority(name='Basse', level=1, color='#00ff00'),
        Priority(name='Moyenne', level=2, color='#ffff00'),
        Priority(name='Haute', level=3, color='#ff0000'),
        Priority(name='Critique', level=4, color='#ff00ff'),
    ]
    db.session.add_all(priorities)
    
    # Créer les utilisateurs
    users = [
        User(
            full_name='Admin Helpdesk',
            email='admin@helpdesk.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        ),
        User(
            full_name='Agent Support',
            email='agent@helpdesk.com',
            password_hash=generate_password_hash('agent123'),
            role='agent'
        ),
        User(
            full_name='Demandeur Test',
            email='demandeur@helpdesk.com',
            password_hash=generate_password_hash('demandeur123'),
            role='requester'
        ),
    ]
    db.session.add_all(users)
    
    db.session.commit()
    
    print(" Base de données initialisée avec succès !")
    print("\n Comptes créés :")
    print("   Admin  : admin@helpdesk.com  / admin123")
    print("   Agent  : agent@helpdesk.com  / agent123")
    print("   Demandeur : demandeur@helpdesk.com  / demandeur123")
    print("\n Catégories et priorités créées avec succès !")
    class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')  # open, in_progress, resolved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # ← AJOUTER
    
    requester = db.relationship('User', foreign_keys=[requester_id], backref='tickets_created')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='tickets_assigned')

class TicketLog(db.Model):  
    __tablename__ = 'ticket_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ticket = db.relationship('Ticket', backref='logs')
    user = db.relationship('User', backref='logs')