"""
Equipment Service - Business logic for equipment management
"""
from sqlalchemy import and_, or_
from inventory_app.extensions import db
from inventory_app.models.equipment import Equipment, CentroCusto


class EquipmentService:
    """Service class for equipment operations"""
    
    @staticmethod
    def create_equipment(data, user=None):
        """Create new equipment"""
        equipment = Equipment(**data)
        if user:
            equipment.add_to_history("Equipamento criado", user)
        
        db.session.add(equipment)
        db.session.commit()
        return equipment
    
    @staticmethod
    def update_equipment(equipment_id, data, user=None):
        """Update existing equipment"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise ValueError("Equipamento não encontrado")
        
        # Track changes
        changes = []
        for key, value in data.items():
            if hasattr(equipment, key):
                old_value = getattr(equipment, key)
                if old_value != value:
                    changes.append(f"{key}: {old_value} → {value}")
                    setattr(equipment, key, value)
        
        if changes and user:
            equipment.add_to_history(f"Modificações: {', '.join(changes)}", user)
        
        db.session.commit()
        return equipment
    
    @staticmethod
    def delete_equipment(equipment_id, user=None):
        """Delete equipment"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            raise ValueError("Equipamento não encontrado")
        
        if user:
            equipment.add_to_history("Equipamento removido do sistema", user)
        
        db.session.delete(equipment)
        db.session.commit()
        return True
    
    @staticmethod
    def search_equipment(query, filters=None, page=1, per_page=50):
        """Search equipment with filters and pagination"""
        base_query = Equipment.query
        
        # Apply text search
        if query:
            search_filter = or_(
                Equipment.patrimonio.ilike(f'%{query}%'),
                Equipment.responsavel.ilike(f'%{query}%'),
                Equipment.modelo.ilike(f'%{query}%'),
                Equipment.marca.ilike(f'%{query}%'),
                Equipment.fornecedor.ilike(f'%{query}%')
            )
            base_query = base_query.filter(search_filter)
        
        # Apply additional filters
        if filters:
            if filters.get('uf'):
                base_query = base_query.filter(Equipment.uf == filters['uf'])
            if filters.get('status'):
                base_query = base_query.filter(Equipment.status == filters['status'])
            if filters.get('tipo_equipamento'):
                base_query = base_query.filter(Equipment.tipo_equipamento == filters['tipo_equipamento'])
            if filters.get('centro_custo_id'):
                base_query = base_query.filter(Equipment.centro_custo_id == filters['centro_custo_id'])
            if filters.get('antivirus') is not None:
                base_query = base_query.filter(Equipment.antivirus == filters['antivirus'])
            if filters.get('termo_assinado') is not None:
                base_query = base_query.filter(Equipment.termo_assinado == filters['termo_assinado'])
        
        return base_query.order_by(Equipment.patrimonio).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_equipment_by_patrimonio(patrimonio):
        """Get equipment by patrimonio number"""
        return Equipment.query.filter_by(patrimonio=patrimonio).first()
    
    @staticmethod
    def get_dashboard_data():
        """Get comprehensive dashboard data"""
        stats = Equipment.get_dashboard_stats()
        stats.update({
            'by_uf': Equipment.get_by_uf(),
            'by_status': Equipment.get_by_status(),
            'by_tipo': Equipment.get_by_tipo(),
            'by_fornecedor': Equipment.get_by_fornecedor(),
            'by_segmento': Equipment.get_by_segmento(),
            'valor_by_cnpj': Equipment.get_valor_by_cnpj()
        })
        return stats
    
    @staticmethod
    def import_from_excel(file_path, user=None):
        """Import equipment data from Excel file"""
        import pandas as pd
        
        try:
            df = pd.read_excel(file_path)
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Map Excel columns to model fields
                    equipment_data = {
                        'patrimonio': str(row.get('Patrimônio', '')).strip(),
                        'responsavel': str(row.get('Responsável', '')).strip(),
                        'uf': str(row.get('UF', '')).strip()[:2],
                        'modelo': str(row.get('Modelo', '')).strip(),
                        'status': str(row.get('Status', 'Em uso')).strip(),
                        'valor': float(row.get('Valor', 0) or 0),
                        'marca': str(row.get('Marca', '')).strip(),
                        'fornecedor': str(row.get('Fornecedor', '')).strip(),
                        'cnpj': str(row.get('CNPJ', '')).strip(),
                        'tipo_equipamento': str(row.get('Tipo', 'notebook')).strip().lower()
                    }
                    
                    # Skip empty patrimonio
                    if not equipment_data['patrimonio']:
                        continue
                    
                    # Check if equipment already exists
                    existing = Equipment.query.filter_by(patrimonio=equipment_data['patrimonio']).first()
                    if existing:
                        errors.append(f"Linha {index + 1}: Patrimônio {equipment_data['patrimonio']} já existe")
                        continue
                    
                    # Create equipment
                    equipment = Equipment(**equipment_data)
                    if user:
                        equipment.add_to_history("Importado via Excel", user)
                    
                    db.session.add(equipment)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Linha {index + 1}: {str(e)}")
            
            if imported_count > 0:
                db.session.commit()
            
            return {
                'success': True,
                'imported_count': imported_count,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'imported_count': 0,
                'errors': []
            }