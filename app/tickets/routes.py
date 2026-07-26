from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Category, Priority, Ticket, TicketMessage

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


@tickets_bp.route('/')
@login_required
def list_tickets():
    if current_user.role == 'admin':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.filter_by(requester_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('tickets/list.html', tickets=tickets)


@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        priority_id = request.form.get('priority_id')
        
        if not title or not description:
            flash('Le titre et la description sont obligatoires.', 'danger')
            return redirect(url_for('tickets.new_ticket'))
        
        ticket = Ticket(
            title=title,
            description=description,
            category_id=int(category_id) if category_id else None,
            priority_id=int(priority_id) if priority_id else None,
            requester_id=current_user.id,
            status='open'
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket créé avec succès !', 'success')
        return redirect(url_for('tickets.list_tickets'))
    
    # Catégories et priorités en dur (pour éviter les problèmes MySQL)
    categories = [
        {'id': 1, 'name': 'Informatique'},
        {'id': 2, 'name': 'Réseau'},
        {'id': 3, 'name': 'Email'},
        {'id': 4, 'name': 'Téléphonie'},
        {'id': 5, 'name': 'Imprimante'},
        {'id': 6, 'name': 'Autre'}
    ]
    priorities = [
        {'id': 1, 'name': 'Basse'},
        {'id': 2, 'name': 'Moyenne'},
        {'id': 3, 'name': 'Haute'},
        {'id': 4, 'name': 'Critique'}
    ]
    
    return render_template('tickets/create.html', categories=categories, priorities=priorities)


@tickets_bp.route('/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('tickets.list_tickets'))
    
    messages = TicketMessage.query.filter_by(ticket_id=ticket.id).order_by(TicketMessage.created_at.asc()).all()
    return render_template('tickets/detail.html', ticket=ticket, messages=messages)


@tickets_bp.route('/<int:ticket_id>/message', methods=['POST'])
@login_required
def add_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('tickets.list_tickets'))
    
    content = request.form.get('content')
    if content and content.strip():
        try:
            message = TicketMessage(
                ticket_id=ticket.id,
                author_id=current_user.id,
                content=content.strip()
            )
            db.session.add(message)
            db.session.commit()
            flash('Message ajouté avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du message: {str(e)}', 'danger')
    else:
        flash('Le message ne peut pas être vide.', 'danger')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))


@tickets_bp.route('/<int:ticket_id>/close')
@login_required
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('tickets.list_tickets'))
    
    ticket.status = 'closed'
    db.session.commit()
    flash('Ticket fermé.', 'info')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))