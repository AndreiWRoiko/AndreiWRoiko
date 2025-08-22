import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from flask import make_response
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.utils
from models import Equipment
from app import db
import json
from datetime import datetime

def export_to_excel(equipment_list):
    """Export equipment list to Excel format"""
    # Check if equipment_list contains objects or dictionaries
    data = []
    for equipment in equipment_list:
        if isinstance(equipment, dict):
            # If it's already a dictionary (for templates), use as-is
            data.append(equipment)
        else:
            # Convert equipment objects to dictionaries
            data.append({
                'ID': equipment.id,
                'Responsável': equipment.responsavel,
                'UF': equipment.uf,
                'Centro de Custo': equipment.cc,
                'CNPJ': equipment.cnpj,
                'Modelo': equipment.modelo,
                'Status': equipment.status,
                'Patrimônio': equipment.patrimonio,
                'Valor': equipment.valor,
                'Segmento': equipment.marca,
                'Processador': equipment.processador,
                'Memória RAM': equipment.memoria_ram,
                'HD/SSD': equipment.hd_ssd,
                'Sistema Operacional': equipment.sistema_operacional,
                'Antivírus': 'Sim' if equipment.antivirus else 'Não',
                'Termo Assinado': 'Sim' if equipment.termo_assinado else 'Não',
                'Milvus Funcionando': 'Sim' if equipment.milvus_funcionando else 'Não',
                'Data Aquisição': equipment.data_aquisicao.strftime('%d/%m/%Y') if equipment.data_aquisicao else '',
                'Data Baixa': equipment.data_baixa.strftime('%d/%m/%Y') if equipment.data_baixa else '',
                'Endereço': equipment.endereco,
                'Telefone': equipment.telefone,
                'Email': equipment.email
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Equipamentos', index=False)
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=equipamentos.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response

def export_to_pdf(equipment_list):
    """Export equipment list to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Add title
    title = Paragraph("Relatório de Equipamentos", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Prepare table data
    data = [['ID', 'Responsável', 'UF', 'CC', 'CNPJ', 'Modelo', 'Status', 'Patrimônio', 'Valor']]
    
    for equipment in equipment_list:
        data.append([
            str(equipment.id),
            equipment.responsavel,
            equipment.uf,
            equipment.cc,
            equipment.cnpj,
            equipment.modelo,
            equipment.status,
            equipment.patrimonio,
            f'R$ {equipment.valor:,.2f}'
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    
    # Create response
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=equipamentos.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    
    return response

def create_uf_chart(uf_data):
    """Create chart for equipment distribution by UF"""
    ufs = [item[0] for item in uf_data]
    counts = [item[1] for item in uf_data]
    
    fig = go.Figure(data=[go.Bar(x=ufs, y=counts, marker_color='steelblue')])
    fig.update_layout(
        title='Equipamentos por UF',
        xaxis_title='UF',
        yaxis_title='Quantidade',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_value_chart(cnpj_data):
    """Create chart for total value by CNPJ"""
    cnpjs = [item[0] for item in cnpj_data]
    values = [float(item[1]) for item in cnpj_data]
    
    fig = go.Figure(data=[go.Pie(labels=cnpjs, values=values)])
    fig.update_layout(
        title='Valor Total por CNPJ',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def filter_equipment(search_form):
    """Filter equipment based on search criteria"""
    query = Equipment.query
    
    if search_form.search_term.data:
        search_term = f"%{search_form.search_term.data}%"
        query = query.filter(
            Equipment.responsavel.like(search_term) |
            Equipment.modelo.like(search_term) |
            Equipment.patrimonio.like(search_term) |
            Equipment.marca.like(search_term)
        )
    
    if search_form.uf.data:
        query = query.filter(Equipment.uf == search_form.uf.data)
    
    if search_form.status.data:
        query = query.filter(Equipment.status == search_form.status.data)
    
    if search_form.cnpj.data:
        query = query.filter(Equipment.cnpj.like(f"%{search_form.cnpj.data}%"))
    
    if search_form.cc.data:
        query = query.filter(Equipment.cc.like(f"%{search_form.cc.data}%"))
    
    return query.all()

def import_from_excel(file_path):
    """Import equipment data from Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Define column mapping (Excel columns to model fields)
        column_mapping = {
            'Responsável': 'responsavel',
            'UF': 'uf',
            'Centro de Custo': 'cc',
            'CNPJ': 'cnpj',
            'Modelo': 'modelo',
            'Status': 'status',
            'Patrimônio': 'patrimonio',
            'Valor': 'valor',
            'Segmento': 'Segmento',
            'Processador': 'processador',
            'Memória RAM': 'memoria_ram',
            'HD/SSD': 'hd_ssd',
            'Sistema Operacional': 'sistema_operacional',
            'Antivírus': 'antivirus',
            'Termo Assinado': 'termo_assinado',
            'Milvus Funcionando': 'milvus_funcionando',
            'Data Aquisição': 'data_aquisicao',
            'Data Baixa': 'data_baixa',
            'Endereço': 'endereco',
            'Telefone': 'telefone',
            'Email': 'email'
        }
        
        imported_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if equipment already exists by patrimonio
                patrimonio = str(row.get('Patrimônio', '')).strip()
                if not patrimonio:
                    errors.append(f'Linha {index + 2}: Patrimônio é obrigatório')
                    error_count += 1
                    continue
                
                existing = Equipment.query.filter_by(patrimonio=patrimonio).first()
                if existing:
                    errors.append(f'Linha {index + 2}: Equipamento com patrimônio {patrimonio} já existe')
                    error_count += 1
                    continue
                
                # Create new equipment instance
                equipment_data = {}
                
                # Process each column
                for excel_col, model_field in column_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        
                        # Handle different data types
                        if pd.isna(value):
                            value = None
                        elif model_field in ['antivirus', 'termo_assinado', 'milvus_funcionando']:
                            # Convert to boolean
                            if isinstance(value, str):
                                value = value.lower() in ['sim', 'yes', 'true', '1', 'verdadeiro']
                            else:
                                value = bool(value)
                        elif model_field in ['data_aquisicao', 'data_baixa']:
                            # Convert to date
                            if pd.notna(value):
                                if isinstance(value, str):
                                    try:
                                        value = datetime.strptime(value, '%d/%m/%Y').date()
                                    except ValueError:
                                        try:
                                            value = datetime.strptime(value, '%Y-%m-%d').date()
                                        except ValueError:
                                            value = None
                                elif hasattr(value, 'date'):
                                    value = value.date()
                        elif model_field == 'valor':
                            # Convert to float
                            if pd.notna(value):
                                try:
                                    if isinstance(value, str):
                                        # Remove currency symbols and convert
                                        value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
                                    value = float(value)
                                except (ValueError, AttributeError):
                                    value = 0.0
                        else:
                            # Convert to string for text fields
                            if pd.notna(value):
                                value = str(value).strip()
                        
                        equipment_data[model_field] = value
                
                # Validate required fields
                required_fields = ['responsavel', 'uf', 'cc', 'cnpj', 'modelo', 'patrimonio']
                missing_fields = []
                for field in required_fields:
                    if not equipment_data.get(field):
                        missing_fields.append(field)
                
                if missing_fields:
                    errors.append(f'Linha {index + 2}: Campos obrigatórios faltando: {", ".join(missing_fields)}')
                    error_count += 1
                    continue
                
                # Set default values
                equipment_data.setdefault('status', 'Em uso')
                equipment_data.setdefault('valor', 0.0)
                equipment_data.setdefault('antivirus', False)
                equipment_data.setdefault('termo_assinado', False)
                equipment_data.setdefault('milvus_funcionando', False)
                
                # Create equipment instance
                equipment = Equipment(**equipment_data)
                db.session.add(equipment)
                imported_count += 1
                
            except Exception as e:
                errors.append(f'Linha {index + 2}: Erro ao processar - {str(e)}')
                error_count += 1
                continue
        
        # Commit all changes if there were successful imports
        if imported_count > 0:
            db.session.commit()
        else:
            db.session.rollback()
        
        return {
            'success': imported_count > 0,
            'imported_count': imported_count,
            'error_count': error_count,
            'errors': errors,
            'total_processed': len(df)
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'imported_count': 0,
            'error_count': 1,
            'errors': [f'Erro ao processar arquivo: {str(e)}'],
            'total_processed': 0
        }
