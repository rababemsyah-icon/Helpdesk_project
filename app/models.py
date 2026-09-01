from datetime import datetime
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='requester')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    tickets_created = db.relationship('Ticket', foreign_keys='Ticket.requester_id', backref='requester', lazy=True)
    tickets_assigned = db.relationship('Ticket', foreign_keys='Ticket.assignee_id', backref='assignee', lazy=True)
    # CORRECTION ICI : On change 'user' par 'author' pour éviter le conflit avec user_id
    logs = db.relationship('TicketLog', backref='author', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    tickets = db.relationship('Ticket', backref='category', lazy=True)


class Priority(db.Model):
    __tablename__ = 'priorities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    
    tickets = db.relationship('Ticket', backref='priority', lazy=True)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relations
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True)
    logs = db.relationship('TicketLog', backref='ticket', lazy=True) # C'est ICI que se crée la relation 'ticket'


class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    author = db.relationship('User', backref='ticket_messages', lazy=True)


class TicketLog(db.Model):
    __tablename__ = 'ticket_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # CORRECTION MAJEURE ICI : On SUPPRIME la ligne 'ticket = db.relationship(...)' 
    # car la relation 'ticket' est déjà gérée par le backref dans la classe Ticket.
    # Cela évite l'erreur "ArgumentError" au démarrage.


# ===== USER LOADER =====
from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))