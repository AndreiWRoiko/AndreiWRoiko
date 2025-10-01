"""
Equipment Models - Equipment Inventory System
"""
import json
from datetime import datetime
from sqlalchemy import func
from flask_login import current_user
from inventory_app.extensions import db


class CentroCusto(db.Model):
    """Centro de Custo (Cost Center) Model"""
    __tablename__ = 'centro_custo'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    descricao = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamento com Equipment
    equipment = db.relationship('Equipment', backref='centro_custo', lazy='dynamic')
    
    def __repr__(self):
        return f'<CentroCusto {self.codigo}: {self.descricao}>'
    
    @staticmethod
    def get_all_active():
        """Get all active cost centers"""
        return CentroCusto.query.filter_by(ativo=True).order_by(CentroCusto.codigo).all()


class Equipment(db.Model):
    """Equipment Model - Core inventory tracking"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Tipo de equipamento
    tipo_equipamento = db.Column(db.String(20), nullable=False, default='notebook', index=True)
    
    # Informações básicas
    responsavel = db.Column(db.String(100), nullable=False, index=True)
    uf = db.Column(db.String(2), nullable=False, index=True)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centro_custo.id'), nullable=False, index=True)
    cnpj = db.Column(db.Text, nullable=False)
    fornecedor = db.Column(db.String(100), nullable=True, index=True)
    modelo = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='Em uso', index=True)
    patrimonio = db.Column(db.String(50), unique=True, nullable=False, index=True)
    valor = db.Column(db.Float, nullable=False, default=0.0, index=True)
    
    # Especificações técnicas
    marca = db.Column(db.String(50), nullable=True, index=True)
    processador = db.Column(db.String(100), nullable=True)
    memoria_ram = db.Column(db.String(20), nullable=True)
    hd_ssd = db.Column(db.String(50), nullable=True)
    sistema_operacional = db.Column(db.String(50), nullable=True)
    licenca_microsoft = db.Column(db.String(50), nullable=True)
    
    # Flags de controle
    antivirus = db.Column(db.Boolean, default=False, nullable=False, index=True)
    termo_assinado = db.Column(db.Boolean, default=False, nullable=False, index=True)
    milvus_funcionando = db.Column(db.Boolean, default=False, nullable=False)
    
    # Campos específicos para celulares
    imei = db.Column(db.String(20), nullable=True, index=True)
    linha_telefonica = db.Column(db.String(20), nullable=True)
    sistema_operacional_celular = db.Column(db.String(20), nullable=True)
    
    # Datas
    data_aquisicao = db.Column(db.Date, nullable=True, index=True)
    data_baixa = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Informações de contato e localização
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # Controle de documentação
    link_termos = db.Column(db.String(500), nullable=True)
    historico_modificacoes = db.Column(db.Text, nullable=True)
    cc = db.Column(db.String(300), nullable=True)  # Legacy field
    
    def __repr__(self):
        return f'<Equipment {self.patrimonio}: {self.modelo}>'
    
    def add_to_history(self, modificacao, user=None):
        """Adiciona uma modificação ao histórico com informação do usuário"""
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
        """Convert model to dictionary"""
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
        results = db.session.query(
            Equipment.uf, 
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.uf).all()
        return [(row[0], row[1]) for row in results]
    
    @staticmethod
    def get_valor_by_cnpj():
        """Get total value by CNPJ"""
        results = db.session.query(
            Equipment.cnpj,
            func.sum(Equipment.valor).label('total_valor')
        ).group_by(Equipment.cnpj).all()
        return [(row[0], float(row[1]) if row[1] else 0) for row in results]
    
    @staticmethod
    def get_by_fornecedor():
        """Get equipment count by supplier/fornecedor"""
        results = db.session.query(
            Equipment.fornecedor,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.fornecedor.isnot(None)).group_by(Equipment.fornecedor).order_by(func.count(Equipment.id).desc()).all()
        return [(row[0], row[1]) for row in results]
    
    @staticmethod
    def get_by_status():
        """Get equipment count by status"""
        results = db.session.query(
            Equipment.status,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.status).order_by(func.count(Equipment.id).desc()).all()
        return [(row[0], row[1]) for row in results]
    
    @staticmethod
    def get_by_tipo():
        """Get equipment count by type (notebook/celular)"""
        results = db.session.query(
            Equipment.tipo_equipamento,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.tipo_equipamento).order_by(func.count(Equipment.id).desc()).all()
        return [(row[0], row[1]) for row in results]
    
    @staticmethod
    def get_celulares():
        """Get all mobile devices"""
        return Equipment.query.filter_by(tipo_equipamento='celular').order_by(Equipment.patrimonio).all()
    
    @staticmethod
    def get_by_marca():
        """Get equipment count by brand"""
        results = db.session.query(
            Equipment.marca,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.marca.isnot(None)).group_by(Equipment.marca).order_by(func.count(Equipment.id).desc()).limit(10).all()
        return [(row[0], row[1]) for row in results]
    
    @staticmethod
    def get_by_cnpj(limit=10):
        """Get top equipment count by CNPJ (limited for performance)"""
        # Get top CNPJs by count
        top_cnpjs = db.session.query(
            Equipment.cnpj,
            func.count(Equipment.id).label('count'),
            func.sum(Equipment.valor).label('total_value')
        ).filter(
            Equipment.cnpj.isnot(None), 
            Equipment.cnpj != ''
        ).group_by(Equipment.cnpj).order_by(func.sum(Equipment.valor).desc()).limit(limit).all()
        
        # Convert to list of tuples
        result = [(row[0], row[1], float(row[2]) if row[2] else 0) for row in top_cnpjs]
        
        # Calculate "Outros" bucket for remaining CNPJs
        if result:
            top_cnpj_values = [item[0] for item in result]
            outros = db.session.query(
                func.count(Equipment.id).label('count'),
                func.sum(Equipment.valor).label('total_value')
            ).filter(
                Equipment.cnpj.isnot(None),
                Equipment.cnpj != '',
                Equipment.cnpj.notin_(top_cnpj_values)
            ).first()
            
            if outros and outros[0] > 0:
                result.append(('Outros', outros[0], float(outros[1]) if outros[1] else 0))
        
        return result
    
    @staticmethod
    def get_antivirus_stats():
        """Get antivirus statistics"""
        com_antivirus = Equipment.query.filter_by(antivirus=True).count()
        sem_antivirus = Equipment.query.filter_by(antivirus=False).count()
        return {
            'com_antivirus': com_antivirus,
            'sem_antivirus': sem_antivirus,
            'total': com_antivirus + sem_antivirus,
            'percentual_com': round((com_antivirus / (com_antivirus + sem_antivirus) * 100), 1) if (com_antivirus + sem_antivirus) > 0 else 0
        }
    
    @staticmethod
    def get_termo_stats():
        """Get termo assinado statistics"""
        com_termo = Equipment.query.filter_by(termo_assinado=True).count()
        sem_termo = Equipment.query.filter_by(termo_assinado=False).count()
        return {
            'com_termo': com_termo,
            'sem_termo': sem_termo,
            'total': com_termo + sem_termo,
            'percentual_com': round((com_termo / (com_termo + sem_termo) * 100), 1) if (com_termo + sem_termo) > 0 else 0
        }
    
    @staticmethod
    def get_value_distribution():
        """Get value distribution by ranges"""
        ranges = [
            ('0-1000', 0, 1000),
            ('1000-3000', 1000, 3000),
            ('3000-5000', 3000, 5000),
            ('5000-10000', 5000, 10000),
            ('10000+', 10000, float('inf'))
        ]
        result = []
        for label, min_val, max_val in ranges:
            if max_val == float('inf'):
                count = Equipment.query.filter(Equipment.valor >= min_val).count()
            else:
                count = Equipment.query.filter(Equipment.valor >= min_val, Equipment.valor < max_val).count()
            if count > 0:
                result.append((label, count))
        return result
    
    @staticmethod
    def get_top_responsaveis(limit=10):
        """Get top equipment holders"""
        results = db.session.query(
            Equipment.responsavel,
            func.count(Equipment.id).label('count'),
            func.sum(Equipment.valor).label('total_value')
        ).group_by(Equipment.responsavel).order_by(func.count(Equipment.id).desc()).limit(limit).all()
        return [(row[0], row[1], float(row[2]) if row[2] else 0) for row in results]
    
    @staticmethod
    def get_recent_additions(limit=10):
        """Get recently added equipment"""
        return Equipment.query.order_by(Equipment.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_status_by_tipo():
        """Get status distribution by equipment type"""
        results = db.session.query(
            Equipment.tipo_equipamento,
            Equipment.status,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.tipo_equipamento, Equipment.status).all()
        return [(row[0], row[1], row[2]) for row in results]
    
    @staticmethod
    def get_notebooks():
        """Get all notebooks"""
        return Equipment.query.filter_by(tipo_equipamento='notebook').order_by(Equipment.patrimonio).all()
    
    @staticmethod
    def get_by_segmento():
        """Get equipment count by segment (marca/brand)"""
        results = db.session.query(
            Equipment.marca,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.marca.isnot(None)).group_by(Equipment.marca).order_by(func.count(Equipment.id).desc()).all()
        return [(row[0], row[1]) for row in results]