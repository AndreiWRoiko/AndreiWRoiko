"""
User Management Forms
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length


class UserApprovalForm(FlaskForm):
    """User approval/rejection form"""
    role = SelectField('Perfil', choices=[
        ('ADM', 'Administrador - Acesso total'),
        ('Suporte', 'Suporte - Visualização e edição'),
        ('Controladoria', 'Controladoria - Apenas visualização')
    ], validators=[DataRequired()])
    action = SelectField('Ação', choices=[
        ('approve', 'Aprovar'),
        ('reject', 'Recusar')
    ], validators=[DataRequired()])
    rejection_reason = TextAreaField('Motivo da Recusa', validators=[Length(max=500)])
    submit = SubmitField('Confirmar')


class UserRoleForm(FlaskForm):
    """User role update form"""
    role = SelectField('Perfil', choices=[
        ('ADM', 'Administrador - Acesso total'),
        ('Suporte', 'Suporte - Visualização e edição'),
        ('Controladoria', 'Controladoria - Apenas visualização')
    ], validators=[DataRequired()])
    submit = SubmitField('Atualizar Perfil')


class UserSearchForm(FlaskForm):
    """User search form"""
    query = StringField('Buscar usuário', validators=[Length(max=100)])
    role = SelectField('Perfil', choices=[('', 'Todos')] + [
        ('ADM', 'Administrador'),
        ('Suporte', 'Suporte'),
        ('Controladoria', 'Controladoria'),
        ('Recusado', 'Recusado')
    ])
    status = SelectField('Status', choices=[('', 'Todos')] + [
        ('Aprovado', 'Aprovado'),
        ('Pendente', 'Pendente'),
        ('Recusado', 'Recusado')
    ])
    submit = SubmitField('Buscar')