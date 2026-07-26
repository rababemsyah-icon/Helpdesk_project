from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='requester')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tickets = db.relationship('Ticket', foreign_keys='Ticket.requester_id', backref='requester', lazy=True)

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
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True)


class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    author = db.relationship('User', backref='ticket_messages', lazy=True)


# ===== AJOUTE CECI =====
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))