from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class TicketForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Catégorie', coerce=int, validators=[DataRequired()])
    priority_id = SelectField('Priorité', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Créer le ticket')

class TicketMessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Envoyer')

class AssignForm(FlaskForm):
    agent_id = SelectField('Assigner à', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assigner')