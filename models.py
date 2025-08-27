from app import db
from datetime import datetime
from sqlalchemy import func

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
    antivirus = db.Column(db.Boolean, default=False)
    termo_assinado = db.Column(db.Boolean, default=False)
    milvus_funcionando = db.Column(db.Boolean, default=False)
    
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
    
    def __repr__(self):
        return f'<Equipment {self.patrimonio}: {self.modelo}>'
    
    def add_to_history(self, modificacao):
        """Adiciona uma modificação ao histórico"""
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        entry = f"[{timestamp}] {modificacao}"
        
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
    def get_by_segmento():
        """Get equipment count by segment (marca/brand)"""
        return db.session.query(
            Equipment.marca,
            func.count(Equipment.id).label('count')
        ).filter(Equipment.marca.isnot(None)).group_by(Equipment.marca).order_by(func.count(Equipment.id).desc()).all()
