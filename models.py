from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User model with role-based access control (RBAC)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Sistema de Controle de Acesso
    role = db.Column(db.String(20), nullable=False, default='Controladoria')  # ADM, Suporte, Controladoria, Recusado
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Pendente, Aprovado, Recusado
    
    # Controle de Aprovação
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    rejection_date = db.Column(db.DateTime, nullable=True)
    
    # Campos de auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    approved_users = db.relationship('User', backref=db.backref('approver', remote_side=[id]), lazy=True)
    
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

class CentroCusto(db.Model):
    __tablename__ = 'centro_custo'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com Equipment
    equipment = db.relationship('Equipment', backref='centro_custo', lazy=True)
    
    def __repr__(self):
        return f'<CentroCusto {self.codigo}: {self.descricao}>'
    
    @staticmethod
    def get_all_active():
        """Get all active cost centers"""
        return CentroCusto.query.filter_by(ativo=True).order_by(CentroCusto.codigo).all()

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    # Novo campo para identificar tipo de equipamento
    tipo_equipamento = db.Column(db.String(20), nullable=False, default='notebook')  # 'notebook' ou 'celular'
    
    responsavel = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centro_custo.id'), nullable=False)
    cnpj = db.Column(db.Text, nullable=False)  # Mudando para Text para permitir múltiplos CNPJs
    fornecedor = db.Column(db.String(100), nullable=True)  # Novo campo fornecedor
    modelo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Em uso')
    patrimonio = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    
    # Additional fields for comprehensive tracking
    marca = db.Column(db.String(50), nullable=True)
    processador = db.Column(db.String(100), nullable=True)
    memoria_ram = db.Column(db.String(20), nullable=True)
    hd_ssd = db.Column(db.String(50), nullable=True)
    sistema_operacional = db.Column(db.String(50), nullable=True)
    licenca_microsoft = db.Column(db.String(50), nullable=True)
    antivirus = db.Column(db.Boolean, default=False)
    termo_assinado = db.Column(db.Boolean, default=False)
    milvus_funcionando = db.Column(db.Boolean, default=False)
    
    # Campos específicos para celulares
    imei = db.Column(db.String(20), nullable=True)  # Identificador único do celular
    linha_telefonica = db.Column(db.String(20), nullable=True)  # Número da linha (se houver chip)
    sistema_operacional_celular = db.Column(db.String(20), nullable=True)  # Android/iOS (separado do campo de notebook)
    
    # Dates
    data_aquisicao = db.Column(db.Date, nullable=True)
    data_baixa = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Location and contact
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # Novos campos
    link_termos = db.Column(db.String(500), nullable=True)  # Link dos termos assinados
    historico_modificacoes = db.Column(db.Text, nullable=True)  # Histórico de modificações
    senha = db.Column(db.String(255), nullable=True)  # Campo senha
    cc = db.Column(db.String(300), nullable=True)  # Centro de custo texto (legacy field)
    
    def __repr__(self):
        return f'<Equipment {self.patrimonio}: {self.modelo}>'
    
    def add_to_history(self, modificacao, user=None):
        """Adiciona uma modificação ao histórico com informação do usuário"""
        import json
        from datetime import datetime
        from flask_login import current_user
        
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Get user info - prefer parameter, then current_user, then 'Sistema'
        if user:
            user_info = user.display_name if hasattr(user, 'display_name') else str(user)
        elif current_user.is_authenticated:
            user_info = current_user.display_name
        else:
            user_info = "Sistema"
        
        entry = f"[{timestamp}] {user_info}: {modificacao}"
        
        if self.historico_modificacoes:
            try:
                historico = json.loads(self.historico_modificacoes)
                if not isinstance(historico, list):
                    historico = [str(historico)]
            except:
                historico = [self.historico_modificacoes]  # Fallback for non-JSON data
        else:
            historico = []
        
        historico.append(entry)
        # Manter apenas os últimos 20 registros
        if len(historico) > 20:
            historico = historico[-20:]
        
        self.historico_modificacoes = json.dumps(historico, ensure_ascii=False)
    
    def get_history(self):
        """Retorna o histórico de modificações formatado"""
        import json
        if not self.historico_modificacoes:
            return []
        
        try:
            historico = json.loads(self.historico_modificacoes)
            if isinstance(historico, list):
                return historico
            else:
                return [str(historico)]
        except:
            return [str(self.historico_modificacoes)]  # Fallback for non-JSON data
    
    def to_dict(self):
        return {
            'id': self.id,
            'responsavel': self.responsavel,
            'uf': self.uf,
            'cc': f"{self.centro_custo.codigo} - {self.centro_custo.descricao}" if self.centro_custo else '',
            'cnpj': self.cnpj,
            'fornecedor': self.fornecedor,
            'modelo': self.modelo,
            'status': self.status,
            'patrimonio': self.patrimonio,
            'valor': self.valor,
            'Segmento': self.marca,
            'processador': self.processador,
            'memoria_ram': self.memoria_ram,
            'hd_ssd': self.hd_ssd,
            'sistema_operacional': self.sistema_operacional,
            'antivirus': self.antivirus,
            'termo_assinado': self.termo_assinado,
            'milvus_funcionando': self.milvus_funcionando,
            'data_aquisicao': self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            'data_baixa': self.data_baixa.isoformat() if self.data_baixa else None,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email,
            'link_termos': self.link_termos,
            'senha': self.senha,
            'historico_modificacoes': self.historico_modificacoes
        }
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        total = Equipment.query.count()
        em_uso = Equipment.query.filter_by(status='Em uso').count()
        sem_antivirus = Equipment.query.filter_by(antivirus=False).count()
        sem_termo = Equipment.query.filter_by(termo_assinado=False).count()
        valor_total = db.session.query(func.sum(Equipment.valor)).scalar() or 0
        
        return {
            'total': total,
            'em_uso': em_uso,
            'sem_antivirus': sem_antivirus,
            'sem_termo': sem_termo,
            'valor_total': valor_total
        }
    
    @staticmethod
    def get_by_uf():
        """Get equipment count by UF"""
        return db.session.query(
            Equipment.uf, 
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.uf).all()
    
    @staticmethod
    def get_valor_by_cnpj():
        """Get total value by CNPJ"""
        return db.session.query(
            Equipment.cnpj,
            func.sum(Equipment.valor).label('total_valor')
        ).group_by(Equipment.cnpj).all()
    
    @staticmethod
    def get_by_fornecedor():
        """Get equipment count by supplier/fornecedor"""
        return db.session.query(
            Equipment.fornecedor,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.fornecedor.isnot(None)).group_by(Equipment.fornecedor).order_by(func.count(Equipment.id).desc()).all()
    
    @staticmethod
    def get_by_status():
        """Get equipment count by status"""
        return db.session.query(
            Equipment.status,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.status).order_by(func.count(Equipment.id).desc()).all()
    
    @staticmethod
    def get_by_tipo():
        """Get equipment count by type (notebook/celular)"""
        return db.session.query(
            Equipment.tipo_equipamento,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.tipo_equipamento).order_by(func.count(Equipment.id).desc()).all()
    
    @staticmethod
    def get_celulares():
        """Get all mobile devices"""
        return Equipment.query.filter_by(tipo_equipamento='celular').order_by(Equipment.patrimonio).all()
    
    @staticmethod
    def get_notebooks():
        """Get all notebooks"""
        return Equipment.query.filter_by(tipo_equipamento='notebook').order_by(Equipment.patrimonio).all()
    
    @staticmethod
    def get_by_segmento():
        """Get equipment count by segment (marca/brand)"""
        return db.session.query(
            Equipment.marca,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.marca.isnot(None)).group_by(Equipment.marca).order_by(func.count(Equipment.id).desc()).all()


class KanbanList(db.Model):
    __tablename__ = 'kanban_list'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String(7), default='#6c757d')  # Cor hexadecimal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com tarefas
    tasks = db.relationship('KanbanTask', backref='list', lazy=True, cascade='all, delete-orphan', order_by='KanbanTask.position')
    
    def __repr__(self):
        return f'<KanbanList {self.name}>'
    
    @staticmethod
    def get_all_ordered():
        """Retorna todas as listas ordenadas por posição"""
        return KanbanList.query.order_by(KanbanList.position).all()


class KanbanTask(db.Model):
    __tablename__ = 'kanban_task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    due_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key para a lista
    list_id = db.Column(db.Integer, db.ForeignKey('kanban_list.id'), nullable=False)
    
    # Relacionamento com checklist
    checklist_items = db.relationship('KanbanChecklist', backref='task', lazy=True, cascade='all, delete-orphan', order_by='KanbanChecklist.position')
    
    def __repr__(self):
        return f'<KanbanTask {self.title}>'
    
    @property
    def priority_color(self):
        """Retorna a cor baseada na prioridade"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#dc3545'
        }
        return colors.get(self.priority, '#6c757d')
    
    @property
    def is_overdue(self):
        """Verifica se a tarefa está atrasada"""
        if self.due_date and not self.completed:
            return self.due_date < datetime.now().date()
        return False
    
    @property
    def checklist_progress(self):
        """Retorna o progresso do checklist (itens completados / total)"""
        if not self.checklist_items:
            return None
        total = len(self.checklist_items)
        completed = sum(1 for item in self.checklist_items if item.completed)
        return {'completed': completed, 'total': total, 'percentage': (completed / total) * 100 if total > 0 else 0}


class KanbanChecklist(db.Model):
    __tablename__ = 'kanban_checklist'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key para a tarefa
    task_id = db.Column(db.Integer, db.ForeignKey('kanban_task.id'), nullable=False)
    
    def __repr__(self):
        return f'<KanbanChecklist {self.text}>'
