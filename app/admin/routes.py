from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Category, Priority, User, Ticket
from app.admin.forms import CategoryForm, PriorityForm, ChangeRoleForm
from app.admin.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


# ---------- CATEGORIES ----------

@admin_bp.route('/categories')
@login_required
@admin_required
def list_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data))
        db.session.commit()
        flash('Catégorie créée.', 'success')
        return redirect(url_for('admin.list_categories'))
    return render_template('admin/category_form.html', form=form)


@admin_bp.route('/categories/<int:category_id>/delete')
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Catégorie supprimée.', 'info')
    return redirect(url_for('admin.list_categories'))


# ---------- PRIORITIES ----------

@admin_bp.route('/priorities')
@login_required
@admin_required
def list_priorities():
    priorities = Priority.query.all()
    return render_template('admin/priorities.html', priorities=priorities)


@admin_bp.route('/priorities/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_priority():
    form = PriorityForm()
    if form.validate_on_submit():
        db.session.add(Priority(name=form.name.data))
        db.session.commit()
        flash('Priorité créée.', 'success')
        return redirect(url_for('admin.list_priorities'))
    return render_template('admin/priority_form.html', form=form)


@admin_bp.route('/priorities/<int:priority_id>/delete')
@login_required
@admin_required
def delete_priority(priority_id):
    priority = Priority.query.get_or_404(priority_id)
    db.session.delete(priority)
    db.session.commit()
    flash('Priorité supprimée.', 'info')
    return redirect(url_for('admin.list_priorities'))


# ---------- USERS ----------

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/role', methods=['GET', 'POST'])
@login_required
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    form = ChangeRoleForm(obj=user)
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.commit()
        flash(f'Rôle de {user.full_name} mis à jour.', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_role_form.html', form=form, user=user)