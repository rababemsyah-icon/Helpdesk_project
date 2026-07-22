from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Ticket, Category, Priority, TicketMessage, User
from app.tickets.forms import TicketForm, TicketMessageForm, AssignForm

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


@tickets_bp.route('/')
@login_required
def list_tickets():
    if current_user.role == 'admin':
        tickets = Ticket.query.all()
    elif current_user.role == 'agent':
        tickets = Ticket.query.filter_by(agent_id=current_user.id).all()
    else:
        tickets = Ticket.query.filter_by(requester_id=current_user.id).all()

    return render_template('tickets/list.html', tickets=tickets)


@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.priority_id.choices = [(p.id, p.name) for p in Priority.query.all()]

    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            category_id=form.category_id.data,
            priority_id=form.priority_id.data,
            requester_id=current_user.id,
            status='open'
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket créé avec succès.', 'success')
        return redirect(url_for('tickets.list_tickets'))

    return render_template('tickets/create.html', form=form)


@tickets_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role == 'requester' and ticket.requester_id != current_user.id:
        abort(403)
    if current_user.role == 'agent' and ticket.agent_id != current_user.id:
        abort(403)

    form = TicketMessageForm()
    if form.validate_on_submit():
        message = TicketMessage(
            content=form.content.data,
            ticket_id=ticket.id,
            author_id=current_user.id
        )
        db.session.add(message)
        db.session.commit()
        flash('Message ajouté.', 'success')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket.id))

    assign_form = AssignForm()
    assign_form.agent_id.choices = [(u.id, u.full_name) for u in User.query.filter_by(role='agent').all()]

    if current_user.role in ('agent', 'admin') and assign_form.validate_on_submit() and assign_form.submit.data:
        ticket.agent_id = assign_form.agent_id.data
        db.session.commit()
        flash('Agent assigné.', 'success')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket.id))

    return render_template('tickets/detail.html', ticket=ticket, form=form, assign_form=assign_form)


@tickets_bp.route('/<int:ticket_id>/status/<string:new_status>')
@login_required
def change_status(ticket_id, new_status):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role not in ('agent', 'admin'):
        abort(403)

    allowed_statuses = ('open', 'in_progress', 'resolved', 'closed')
    if new_status not in allowed_statuses:
        abort(400)

    ticket.status = new_status
    db.session.commit()
    flash(f'Statut mis à jour : {new_status}', 'success')
    return redirect(url_for('tickets.ticket_detail', ticket_id=ticket.id))