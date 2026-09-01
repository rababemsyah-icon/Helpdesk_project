from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models import Category, Priority, Ticket, TicketMessage, TicketLog

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/')
@login_required
def list_tickets():
    if current_user.role == 'admin':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.filter_by(requester_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    
    current_filters = {
        'q': request.args.get('q', ''),
        'status': request.args.get('status', ''),
        'category': request.args.get('category', ''),
        'priority': request.args.get('priority', '')
    }
    
    return render_template('tickets/list.html', tickets=tickets, current_filters=current_filters)

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        priority_id = request.form.get('priority_id')
        
        if not title or not description:
            flash('Le titre et la description sont obligatoires.', 'danger')
            return redirect('/tickets/new')
        
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
        return redirect('/tickets/')
    
    categories = Category.query.all()
    priorities = Priority.query.all()
    
    return render_template('tickets/create.html', categories=categories, priorities=priorities)


@tickets_bp.route('/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect('/tickets/')
    
    messages = TicketMessage.query.filter_by(ticket_id=ticket.id).order_by(TicketMessage.created_at.asc()).all()
    logs = TicketLog.query.filter_by(ticket_id=ticket.id).order_by(TicketLog.created_at.desc()).all()
    
    return render_template('tickets/detail.html', ticket=ticket, messages=messages, logs=logs)


@tickets_bp.route('/<int:ticket_id>/message', methods=['POST'])
@login_required
def add_message(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect('/tickets/')
    
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
    
    return redirect(f'/tickets/{ticket.id}')


@tickets_bp.route('/<int:ticket_id>/close')
@login_required
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role != 'admin' and ticket.requester_id != current_user.id:
        flash('Accès non autorisé.', 'danger')
        return redirect('/tickets/')
    
    ticket.status = 'closed'
    ticket.closed_at = datetime.utcnow()
    db.session.commit()
    flash('Ticket fermé.', 'info')
    
    return redirect(f'/tickets/{ticket.id}')


@tickets_bp.route('/<int:ticket_id>/assign', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role not in ['agent', 'admin']:
        flash('Vous n\'avez pas les droits.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    if ticket.assignee_id and ticket.assignee_id != current_user.id:
        flash('Ce ticket est déjà pris en charge par un autre agent.', 'warning')
        return redirect(f'/tickets/{ticket.id}')
    
    ticket.assignee_id = current_user.id
    ticket.status = 'in_progress'
    
    log = TicketLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action='assign',
        new_value=f'Assigné à {current_user.full_name}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Ticket pris en charge avec succès !', 'success')
    return redirect(f'/tickets/{ticket.id}')


@tickets_bp.route('/<int:ticket_id>/status', methods=['POST'])
@login_required
def update_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role not in ['agent', 'admin']:
        flash('Vous n\'avez pas les droits.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    new_status = request.form.get('status')
    old_status = ticket.status
    
    if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
        flash('Statut invalide.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    if ticket.status == 'closed' and current_user.role != 'admin':
        flash('Ce ticket est fermé, vous ne pouvez plus le modifier.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    ticket.status = new_status
    
    if new_status == 'resolved':
        ticket.resolved_at = datetime.utcnow()
    elif new_status == 'closed':
        ticket.closed_at = datetime.utcnow()
    elif new_status == 'open':
        ticket.resolved_at = None
        ticket.closed_at = None
    
    log = TicketLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action='status_change',
        old_value=old_status,
        new_value=new_status
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Statut changé : {old_status} → {new_status}', 'success')
    return redirect(f'/tickets/{ticket.id}')


@tickets_bp.route('/<int:ticket_id>/unassign', methods=['POST'])
@login_required
def unassign_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if current_user.role not in ['agent', 'admin']:
        flash('Vous n\'avez pas les droits.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    if ticket.assignee_id != current_user.id and current_user.role != 'admin':
        flash('Vous n\'êtes pas assigné à ce ticket.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    ticket.assignee_id = None
    ticket.status = 'open'
    
    log = TicketLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action='unassign',
        new_value='Libéré'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Ticket libéré avec succès.', 'info')
    return redirect(f'/tickets/{ticket.id}')


@tickets_bp.route('/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Seul l'admin peut supprimer un ticket
    if current_user.role != 'admin':
        flash('Accès non autorisé. Seul un administrateur peut supprimer les tickets.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    try:
        # 1. Supprimer d'abord les logs associés à ce ticket
        TicketLog.query.filter_by(ticket_id=ticket.id).delete()
        # 2. Supprimer les messages associés à ce ticket
        TicketMessage.query.filter_by(ticket_id=ticket.id).delete()
        # 3. Enfin, supprimer le ticket lui-même
        db.session.delete(ticket)
        db.session.commit()
        flash('Ticket supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    
    return redirect('/tickets/')


@tickets_bp.route('/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Règles de droits d'accès :
    # 1. L'admin peut tout modifier.
    # 2. Le demandeur (requester) peut modifier son propre ticket s'il n'est pas fermé.
    # 3. L'agent ne peut modifier que la catégorie et la priorité (pas le titre ni la description).
    
    if not (current_user.role == 'admin' or ticket.requester_id == current_user.id):
        flash('Accès non autorisé.', 'danger')
        return redirect(f'/tickets/{ticket.id}')
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        priority_id = request.form.get('priority_id')
        
        # Si l'agent modifie, on ne change que la catégorie et la priorité
        if current_user.role == 'agent':
            ticket.category_id = int(category_id) if category_id else None
            ticket.priority_id = int(priority_id) if priority_id else None
            ticket.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Catégorie et priorité modifiées avec succès.', 'success')
            return redirect(f'/tickets/{ticket.id}')
        
        # Si le demandeur ou l'admin modifie, on change tout
        if not title or not description:
            flash('Le titre et la description sont obligatoires.', 'danger')
            return redirect(f'/tickets/{ticket.id}/edit')
        
        ticket.title = title
        ticket.description = description
        ticket.category_id = int(category_id) if category_id else None
        ticket.priority_id = int(priority_id) if priority_id else None
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Ticket modifié avec succès.', 'success')
        return redirect(f'/tickets/{ticket.id}')
    # Affichage du formulaire de modification
    categories = Category.query.all()
    priorities = Priority.query.all()
    return render_template('tickets/edit.html', ticket=ticket, categories=categories, priorities=priorities)