from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user, login_required
from models import User

# Decorator para verificar permissões específicas
def requires_permission(permission):
    """Decorator que verifica se o usuário tem uma permissão específica"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar logado para acessar esta página.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.can_access_system():
                flash('Seu acesso ao sistema está bloqueado ou pendente de aprovação.', 'error')
                return redirect(url_for('access_denied'))
            
            if not current_user.has_permission(permission):
                flash('Você não tem permissão para acessar esta funcionalidade.', 'error')
                return redirect(url_for('access_denied'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorator para roles específicas
def requires_role(*roles):
    """Decorator que verifica se o usuário tem uma das roles especificadas"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar logado para acessar esta página.', 'error')
                return redirect(url_for('login'))
            
            if not current_user.can_access_system():
                flash('Seu acesso ao sistema está bloqueado ou pendente de aprovação.', 'error')
                return redirect(url_for('access_denied'))
            
            if current_user.role not in roles:
                flash('Você não tem o nível de acesso necessário para esta funcionalidade.', 'error')
                return redirect(url_for('access_denied'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorator para administradores apenas
def admin_required(f):
    """Decorator que requer acesso de administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        if not current_user.can_access_system():
            flash('Seu acesso ao sistema está bloqueado ou pendente de aprovação.', 'error')
            return redirect(url_for('access_denied'))
        
        if current_user.role != 'ADM':
            flash('Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('access_denied'))
        
        return f(*args, **kwargs)
    return decorated_function

# Decorator para suporte e administradores
def support_or_admin_required(f):
    """Decorator que requer acesso de suporte ou administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        if not current_user.can_access_system():
            flash('Seu acesso ao sistema está bloqueado ou pendente de aprovação.', 'error')
            return redirect(url_for('access_denied'))
        
        if current_user.role not in ['ADM', 'Suporte']:
            flash('Você não tem permissão para acessar esta funcionalidade.', 'error')
            return redirect(url_for('access_denied'))
        
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar aprovação pendente
def approved_user_required(f):
    """Decorator que verifica se o usuário foi aprovado"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        if current_user.is_pending:
            flash('Sua conta está pendente de aprovação. Aguarde a liberação de um administrador.', 'warning')
            return redirect(url_for('pending_approval'))
        
        if current_user.is_rejected:
            flash('Sua conta foi recusada. Entre em contato com o suporte para mais informações.', 'error')
            return redirect(url_for('access_denied'))
        
        if not current_user.can_access_system():
            flash('Seu acesso ao sistema está bloqueado.', 'error')
            return redirect(url_for('access_denied'))
        
        return f(*args, **kwargs)
    return decorated_function

# Função auxiliar para verificar se equipamentos precisam de aprovação
def equipment_requires_approval():
    """Verifica se novos equipamentos precisam de aprovação"""
    # Por enquanto, todos os equipamentos precisam de aprovação
    # Pode ser configurável no futuro
    return True

# Middleware para logs de acesso
def log_user_access(route_name, action=None):
    """Log de acesso do usuário para auditoria"""
    if current_user.is_authenticated:
        print(f"[AUDIT] User {current_user.username} ({current_user.role}) accessed {route_name}" + 
              (f" - Action: {action}" if action else ""))

# Context processor para disponibilizar dados do usuário nos templates
def inject_user_permissions():
    """Injeta permissões do usuário nos templates"""
    if current_user.is_authenticated:
        context = {
            'user_permissions': {
                'can_view': current_user.has_permission('view'),
                'can_create': current_user.has_permission('create'),
                'can_edit': current_user.has_permission('edit'),
                'can_delete': current_user.has_permission('delete'),
                'can_approve': current_user.has_permission('approve'),
                'can_admin': current_user.has_permission('admin'),
                'can_manage_users': current_user.has_permission('manage_users'),
                'is_admin': current_user.role == 'ADM',
                'is_support': current_user.role == 'Suporte',
                'is_controladoria': current_user.role == 'Controladoria',
                'user_role': current_user.role,
                'user_status': current_user.status
            }
        }
        
        # Adicionar contagem de usuários pendentes para admins
        if current_user.role == 'ADM':
            from models import User
            context['pending_users_count'] = User.query.filter_by(status='Pendente').count()
        
        return context
    return {}