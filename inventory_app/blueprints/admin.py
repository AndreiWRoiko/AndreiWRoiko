"""
Admin Blueprint - User management and administration routes
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

from inventory_app.services.auth_service import AuthService
from inventory_app.services.user_service import UserService
from inventory_app.forms.user_forms import UserApprovalForm, UserRoleForm, UserSearchForm
from inventory_app.models.user import User

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.has_permission('admin'):
        flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get admin statistics
    stats = UserService.get_user_stats()
    pending_users = UserService.get_pending_users()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         pending_users=pending_users)


@admin_bp.route('/users')
@login_required
def users():
    """User management page"""
    if not current_user.has_permission('manage_users'):
        flash('Sem permissão para gerenciar usuários.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = UserSearchForm()
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    
    if query:
        users_pagination = UserService.search_users(query, page)
    else:
        users_pagination = UserService.get_all_users(page)
    
    return render_template('admin/users.html', 
                         users=users_pagination,
                         form=form,
                         query=query)


@admin_bp.route('/users/pending')
@login_required
def pending_users():
    """Pending users approval page"""
    if not current_user.has_permission('approve'):
        flash('Sem permissão para aprovar usuários.', 'error')
        return redirect(url_for('main.dashboard'))
    
    pending_users = UserService.get_pending_users()
    return render_template('admin/pending_users.html', users=pending_users)


@admin_bp.route('/users/<int:user_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_user(user_id):
    """Approve or reject user"""
    if not current_user.has_permission('approve'):
        flash('Sem permissão para aprovar usuários.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    form = UserApprovalForm()
    
    if form.validate_on_submit():
        try:
            if form.action.data == 'approve':
                AuthService.approve_user(user_id, current_user)
                flash(f'Usuário {user.username} aprovado com sucesso!', 'success')
            elif form.action.data == 'reject':
                if not form.rejection_reason.data:
                    flash('Motivo da recusa é obrigatório.', 'error')
                    return render_template('admin/approve_user.html', user=user, form=form)
                AuthService.reject_user(user_id, current_user, form.rejection_reason.data)
                flash(f'Usuário {user.username} recusado.', 'info')
            
            return redirect(url_for('admin.pending_users'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Erro ao processar solicitação: {str(e)}', 'error')
    
    return render_template('admin/approve_user.html', user=user, form=form)


@admin_bp.route('/users/<int:user_id>/role', methods=['GET', 'POST'])
@login_required
def update_user_role(user_id):
    """Update user role"""
    if not current_user.has_permission('manage_users'):
        flash('Sem permissão para alterar perfis de usuários.', 'error')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    form = UserRoleForm(obj=user)
    
    if form.validate_on_submit():
        try:
            old_role = user.role
            UserService.update_user_role(user_id, form.role.data, current_user)
            flash(f'Perfil do usuário {user.username} alterado de {old_role} para {form.role.data}.', 'success')
            return redirect(url_for('admin.users'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    
    return render_template('admin/update_role.html', user=user, form=form)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    if not current_user.has_permission('manage_users'):
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        if user.is_active:
            UserService.deactivate_user(user_id, current_user)
            message = f'Usuário {user.username} desativado.'
        else:
            UserService.activate_user(user_id, current_user)
            message = f'Usuário {user.username} ativado.'
        
        return jsonify({
            'success': True,
            'message': message,
            'is_active': user.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required  
def create_user():
    """Create new user (admin only)"""
    if not current_user.has_permission('admin'):
        flash('Apenas administradores podem criar usuários diretamente.', 'error')
        return redirect(url_for('admin.users'))
    
    from inventory_app.forms.auth_forms import RegistrationForm
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = AuthService.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data
            )
            
            # Admin can auto-approve users
            if form.role.data in ['ADM', 'Suporte']:
                AuthService.approve_user(user.id, current_user)
            
            flash(f'Usuário {user.username} criado com sucesso!', 'success')
            return redirect(url_for('admin.users'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return render_template('admin/create_user.html', form=form)


@admin_bp.route('/system/info')
@login_required
def system_info():
    """System information page"""
    if not current_user.has_permission('admin'):
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    import os
    from inventory_app.models.equipment import Equipment
    
    system_info = {
        'database_url': bool(os.environ.get('DATABASE_URL')),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'total_equipment': Equipment.query.count(),
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True, status='Aprovado').count(),
        'pending_approvals': User.query.filter_by(status='Pendente').count()
    }
    
    return render_template('admin/system_info.html', info=system_info)