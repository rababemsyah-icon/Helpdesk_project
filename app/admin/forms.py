from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField('Nom de la catégorie', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Enregistrer')


class PriorityForm(FlaskForm):
    name = StringField('Nom de la priorité', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Enregistrer')


class AssignAgentForm(FlaskForm):
    agent_id = SelectField('Assigner à', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assigner')


class ChangeRoleForm(FlaskForm):
    role = SelectField(
        'Rôle',
        choices=[('requester', 'Demandeur'), ('agent', 'Agent'), ('admin', 'Admin')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Modifier le rôle')