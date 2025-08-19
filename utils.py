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
from models import Equipment
import json

def export_to_excel(equipment_list):
    """Export equipment list to Excel format"""
    # Convert equipment objects to dictionaries
    data = []
    for equipment in equipment_list:
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
            'Marca': equipment.marca,
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
    
    return json.dumps(fig, cls=pyo.PlotlyJSONEncoder)

def create_value_chart(cnpj_data):
    """Create chart for total value by CNPJ"""
    cnpjs = [item[0] for item in cnpj_data]
    values = [float(item[1]) for item in cnpj_data]
    
    fig = go.Figure(data=[go.Pie(labels=cnpjs, values=values)])
    fig.update_layout(
        title='Valor Total por CNPJ',
        height=400
    )
    
    return json.dumps(fig, cls=pyo.PlotlyJSONEncoder)

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
