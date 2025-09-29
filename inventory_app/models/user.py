"""
User Model - Equipment Inventory System
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from inventory_app.extensions import db


class User(UserMixin, db.Model):
    """User model with role-based access control (RBAC)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Sistema de Controle de Acesso
    role = db.Column(db.String(20), nullable=False, default='Controladoria', index=True)
    status = db.Column(db.String(20), nullable=False, default='Pendente', index=True)
    
    # Controle de Aprovação
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    rejection_date = db.Column(db.DateTime, nullable=True)
    
    # Campos de auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    approved_users = db.relationship('User', 
                                   backref=db.backref('approver', remote_side=[id]), 
                                   lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def display_name(self):
        """Return display name for the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return f"User {self.id}"
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    # Métodos de Controle de Acesso
    @property
    def is_approved(self):
        """Verifica se o usuário foi aprovado"""
        return self.status == 'Aprovado'
    
    @property
    def is_pending(self):
        """Verifica se o usuário está pendente de aprovação"""
        return self.status == 'Pendente'
    
    @property
    def is_rejected(self):
        """Verifica se o usuário foi recusado"""
        return self.status == 'Recusado'
    
    def can_access_system(self):
        """Verifica se o usuário pode acessar o sistema"""
        return self.is_active and self.is_approved and self.role != 'Recusado'
    
    def has_permission(self, action):
        """Verifica se o usuário tem permissão para uma ação específica"""
        if not self.can_access_system():
            return False
        
        permissions = {
            'ADM': ['view', 'create', 'edit', 'delete', 'approve', 'admin', 'manage_users'],
            'Suporte': ['view', 'create', 'edit', 'manage_users'],
            'Controladoria': ['view'],
            'Recusado': []
        }
        
        return action in permissions.get(self.role, [])
    
    def approve(self, approved_by_user):
        """Aprova o usuário"""
        self.status = 'Aprovado'
        self.approved_by = approved_by_user.id
        self.approved_at = datetime.utcnow()
        self.rejection_reason = None
        self.rejection_date = None
    
    def reject(self, rejected_by_user, reason):
        """Recusa o usuário"""
        self.status = 'Recusado'
        self.role = 'Recusado'
        self.rejection_reason = reason
        self.rejection_date = datetime.utcnow()
        self.approved_by = rejected_by_user.id
        self.approved_at = datetime.utcnow()
    
    def update_last_login(self):
        """Atualiza o último login do usuário"""
        self.last_login = datetime.utcnow()
    
    @staticmethod
    def get_pending_users():
        """Retorna usuários pendentes de aprovação"""
        return User.query.filter_by(status='Pendente').order_by(User.created_at.desc()).all()
    
    @staticmethod
    def get_rejected_users_for_cleanup():
        """Retorna usuários recusados há mais de 30 dias para limpeza"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        return User.query.filter(
            User.status == 'Recusado',
            User.rejection_date < cutoff_date
        ).all()
    
    @staticmethod
    def get_users_by_role(role):
        """Retorna usuários por role"""
        return User.query.filter_by(role=role, status='Aprovado').order_by(User.username).all()
    
    @staticmethod
    def create_admin_user(username, email, password, first_name=None, last_name=None):
        """Cria um usuário administrador (aprovado automaticamente)"""
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='ADM',
            status='Aprovado',
            approved_at=datetime.utcnow()
        )
        user.set_password(password)
        return user