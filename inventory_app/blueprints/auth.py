"""
Authentication Blueprint - Login, logout, registration routes
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse

from inventory_app.services.auth_service import AuthService
from inventory_app.forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = AuthService.authenticate_user(form.username.data, form.password.data)
            if user:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.dashboard')
                flash(f'Bem-vindo, {user.display_name}!', 'success')
                return redirect(next_page)
            else:
                flash('Credenciais inválidas ou conta não aprovada.', 'danger')
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'danger')
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.display_name
    logout_user()
    flash(f'Logout realizado com sucesso. Até logo, {user_name}!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = AuthService.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            flash('Cadastro realizado com sucesso! Aguarde a aprovação do administrador.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)