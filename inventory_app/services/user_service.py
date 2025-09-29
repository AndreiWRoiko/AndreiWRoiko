"""
User Service - Business logic for user management
"""
from inventory_app.extensions import db
from inventory_app.models.user import User


class UserService:
    """Service class for user management operations"""
    
    @staticmethod
    def get_all_users(page=1, per_page=50):
        """Get paginated list of all users"""
        return User.query.order_by(User.username).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_pending_users():
        """Get users pending approval"""
        return User.get_pending_users()
    
    @staticmethod
    def get_users_by_role(role):
        """Get users by role"""
        return User.get_users_by_role(role)
    
    @staticmethod
    def update_user_role(user_id, new_role, updated_by_user):
        """Update user role"""
        if not updated_by_user.has_permission('manage_users'):
            raise ValueError("Sem permissão para gerenciar usuários")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        return user, old_role
    
    @staticmethod
    def deactivate_user(user_id, deactivated_by_user):
        """Deactivate a user"""
        if not deactivated_by_user.has_permission('manage_users'):
            raise ValueError("Sem permissão para desativar usuários")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        user.is_active = False
        db.session.commit()
        return user
    
    @staticmethod
    def activate_user(user_id, activated_by_user):
        """Activate a user"""
        if not activated_by_user.has_permission('manage_users'):
            raise ValueError("Sem permissão para ativar usuários")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        user.is_active = True
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True, status='Aprovado').count()
        pending_users = User.query.filter_by(status='Pendente').count()
        rejected_users = User.query.filter_by(status='Recusado').count()
        
        return {
            'total': total_users,
            'active': active_users,
            'pending': pending_users,
            'rejected': rejected_users
        }
    
    @staticmethod
    def search_users(query, page=1, per_page=50):
        """Search users"""
        if query:
            search_query = User.query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%'),
                    User.first_name.ilike(f'%{query}%'),
                    User.last_name.ilike(f'%{query}%')
                )
            )
        else:
            search_query = User.query
        
        return search_query.order_by(User.username).paginate(
            page=page, per_page=per_page, error_out=False
        )