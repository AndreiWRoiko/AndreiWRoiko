"""
Authentication Service - Business logic for user authentication
"""
from flask_login import current_user
from inventory_app.extensions import db
from inventory_app.models.user import User


class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.can_access_system():
                user.update_last_login()
                db.session.commit()
                return user
        return None
    
    @staticmethod
    def create_user(username, email, password, first_name=None, last_name=None, role='Controladoria'):
        """Create a new user account"""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            raise ValueError("Nome de usuário já existe")
        if User.query.filter_by(email=email).first():
            raise ValueError("Email já existe")
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            status='Pendente'  # Requires approval
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def approve_user(user_id, approved_by_user):
        """Approve a pending user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        if not approved_by_user.has_permission('approve'):
            raise ValueError("Sem permissão para aprovar usuários")
        
        user.approve(approved_by_user)
        db.session.commit()
        return user
    
    @staticmethod
    def reject_user(user_id, rejected_by_user, reason):
        """Reject a pending user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        if not rejected_by_user.has_permission('approve'):
            raise ValueError("Sem permissão para recusar usuários")
        
        user.reject(rejected_by_user, reason)
        db.session.commit()
        return user


def inject_user_permissions():
    """Context processor to inject user permissions into templates"""
    if current_user.is_authenticated:
        return dict(
            can_view=current_user.has_permission('view'),
            can_create=current_user.has_permission('create'),
            can_edit=current_user.has_permission('edit'),
            can_delete=current_user.has_permission('delete'),
            can_approve=current_user.has_permission('approve'),
            can_admin=current_user.has_permission('admin'),
            can_manage_users=current_user.has_permission('manage_users'),
            user_role=current_user.role,
            user_status=current_user.status
        )
    return dict(
        can_view=False,
        can_create=False,
        can_edit=False,
        can_delete=False,
        can_approve=False,
        can_admin=False,
        can_manage_users=False,
        user_role=None,
        user_status=None
    )