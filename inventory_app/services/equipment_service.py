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
            'valor_by_cnpj': Equipment.get_valor_by_cnpj(),
            'by_marca': Equipment.get_by_marca(),
            'by_cnpj': Equipment.get_by_cnpj(),
            'antivirus_stats': Equipment.get_antivirus_stats(),
            'termo_stats': Equipment.get_termo_stats(),
            'value_distribution': Equipment.get_value_distribution(),
            'top_responsaveis': Equipment.get_top_responsaveis(limit=10),
            'recent_additions': Equipment.get_recent_additions(limit=5),
            'status_by_tipo': Equipment.get_status_by_tipo()
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

    @staticmethod
    def export_to_excel(query="", filters=None):
        """Export equipment to Excel file"""
        import pandas as pd
        from io import BytesIO
        from datetime import datetime
        
        # Get filtered equipment
        base_query = Equipment.query
        
        if query:
            from sqlalchemy import or_
            search_filter = or_(
                Equipment.patrimonio.ilike(f"%{query}%"),
                Equipment.responsavel.ilike(f"%{query}%"),
                Equipment.modelo.ilike(f"%{query}%"),
                Equipment.marca.ilike(f"%{query}%"),
                Equipment.fornecedor.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)
        
        if filters:
            if filters.get("uf"):
                base_query = base_query.filter(Equipment.uf == filters["uf"])
            if filters.get("status"):
                base_query = base_query.filter(Equipment.status == filters["status"])
            if filters.get("tipo_equipamento"):
                base_query = base_query.filter(Equipment.tipo_equipamento == filters["tipo_equipamento"])
            if filters.get("centro_custo_id"):
                base_query = base_query.filter(Equipment.centro_custo_id == filters["centro_custo_id"])
        
        equipment_list = base_query.all()
        
        # Prepare data for export
        data = []
        for eq in equipment_list:
            data.append({
                "Patrimônio": eq.patrimonio,
                "Tipo": eq.tipo_equipamento,
                "Responsável": eq.responsavel,
                "UF": eq.uf,
                "Centro de Custo": eq.centro_custo.codigo if eq.centro_custo else "",
                "CNPJ": eq.cnpj,
                "Fornecedor": eq.fornecedor,
                "Marca": eq.marca,
                "Modelo": eq.modelo,
                "Status": eq.status,
                "Valor": eq.valor,
                "Processador": eq.processador,
                "Memória RAM": eq.memoria_ram,
                "HD/SSD": eq.hd_ssd,
                "Sistema Operacional": eq.sistema_operacional,
                "Licença Microsoft": eq.licenca_microsoft,
                "Antivírus": "Sim" if eq.antivirus else "Não",
                "Termo Assinado": "Sim" if eq.termo_assinado else "Não",
                "Data de Aquisição": eq.data_aquisicao.strftime("%d/%m/%Y") if eq.data_aquisicao else "",
                "Data de Baixa": eq.data_baixa.strftime("%d/%m/%Y") if eq.data_baixa else "",
            })
        
        # Create DataFrame and export to BytesIO
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        
        return output

    @staticmethod
    def export_to_pdf(query="", filters=None):
        """Export equipment to PDF file"""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        from datetime import datetime
        
        # Get filtered equipment
        base_query = Equipment.query
        
        if query:
            from sqlalchemy import or_
            search_filter = or_(
                Equipment.patrimonio.ilike(f"%{query}%"),
                Equipment.responsavel.ilike(f"%{query}%"),
                Equipment.modelo.ilike(f"%{query}%"),
                Equipment.marca.ilike(f"%{query}%"),
                Equipment.fornecedor.ilike(f"%{query}%")
            )
            base_query = base_query.filter(search_filter)
        
        if filters:
            if filters.get("uf"):
                base_query = base_query.filter(Equipment.uf == filters["uf"])
            if filters.get("status"):
                base_query = base_query.filter(Equipment.status == filters["status"])
            if filters.get("tipo_equipamento"):
                base_query = base_query.filter(Equipment.tipo_equipamento == filters["tipo_equipamento"])
            if filters.get("centro_custo_id"):
                base_query = base_query.filter(Equipment.centro_custo_id == filters["centro_custo_id"])
        
        equipment_list = base_query.all()
        
        # Create PDF in memory
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4))
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        title = Paragraph(f"<b>Relatório de Equipamentos</b><br/>Gerado em: {data_hora}", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Table data
        data = [["Patrimônio", "Tipo", "Responsável", "UF", "Modelo", "Status", "Valor"]]
        for eq in equipment_list:
            data.append([
                eq.patrimonio,
                eq.tipo_equipamento,
                eq.responsavel[:20] if eq.responsavel else "",
                eq.uf,
                eq.modelo[:25] if eq.modelo else "",
                eq.status,
                f"R$ {eq.valor:.2f}" if eq.valor else ""
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        return output
