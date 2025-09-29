"""
Authentication Forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from inventory_app.models.user import User


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Usuário', validators=[
        DataRequired(), 
        Length(min=3, max=64, message='Usuário deve ter entre 3 e 64 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Email inválido'),
        Length(max=120)
    ])
    first_name = StringField('Nome', validators=[Length(max=100)])
    last_name = StringField('Sobrenome', validators=[Length(max=100)])
    password = PasswordField('Senha', validators=[
        DataRequired(), 
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Senha', validators=[
        DataRequired(), 
        EqualTo('password', message='Senhas devem ser iguais')
    ])
    role = SelectField('Perfil', choices=[
        ('Controladoria', 'Controladoria - Apenas visualização'),
        ('Suporte', 'Suporte - Visualização e edição'),
    ], default='Controladoria')
    submit = SubmitField('Cadastrar')
    
    def validate_username(self, username):
        """Validate username uniqueness"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nome de usuário já está em uso. Escolha outro.')
    
    def validate_email(self, email):
        """Validate email uniqueness"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email já está cadastrado. Use outro email.')