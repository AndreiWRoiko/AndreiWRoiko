from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Equipment
from forms import EquipmentForm, SearchForm, ImportForm
from utils import export_to_excel, export_to_pdf, create_uf_chart, create_value_chart, filter_equipment, import_from_excel
import json
import os
from werkzeug.utils import secure_filename

@app.route('/')
def dashboard():
    """Main dashboard route"""
    stats = Equipment.get_dashboard_stats()
    uf_data = Equipment.get_by_uf()
    cnpj_data = Equipment.get_valor_by_cnpj()
    
    # Create charts
    uf_chart = create_uf_chart(uf_data) if uf_data else '{}'
    value_chart = create_value_chart(cnpj_data) if cnpj_data else '{}'
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         uf_chart=uf_chart,
                         value_chart=value_chart)

@app.route('/equipment')
def equipment_list():
    """Equipment list with search and filtering"""
    search_form = SearchForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if search_form.validate():
        equipment = filter_equipment(search_form)
        # Manual pagination for filtered results
        total = len(equipment)
        start = (page - 1) * per_page
        end = start + per_page
        equipment = equipment[start:end]
        
        # Create pagination object manually
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page < ((total + per_page - 1) // per_page),
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < ((total + per_page - 1) // per_page) else None
        }
    else:
        equipment_query = Equipment.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        equipment = equipment_query.items
        pagination = {
            'page': equipment_query.page,
            'per_page': equipment_query.per_page,
            'total': equipment_query.total,
            'pages': equipment_query.pages,
            'has_prev': equipment_query.has_prev,
            'has_next': equipment_query.has_next,
            'prev_num': equipment_query.prev_num,
            'next_num': equipment_query.next_num
        }
    
    return render_template('equipment_list.html', 
                         equipment=equipment, 
                         search_form=search_form,
                         pagination=pagination)

@app.route('/equipment/new', methods=['GET', 'POST'])
def equipment_new():
    """Create new equipment"""
    form = EquipmentForm()
    
    if form.validate_on_submit():
        # Check if patrimonio already exists
        existing = Equipment.query.filter_by(patrimonio=form.patrimonio.data).first()
        if existing:
            flash('Patrimônio já existe no sistema!', 'error')
            return render_template('equipment_form.html', form=form, title='Novo Equipamento')
        
        equipment = Equipment()
        equipment.responsavel = form.responsavel.data
        equipment.uf = form.uf.data
        equipment.cc = form.cc.data
        equipment.cnpj = form.cnpj.data
        equipment.fornecedor = form.fornecedor.data
        equipment.modelo = form.modelo.data
        equipment.status = form.status.data
        equipment.patrimonio = form.patrimonio.data
        equipment.valor = form.valor.data
        equipment.marca = form.marca.data
        equipment.processador = form.processador.data
        equipment.memoria_ram = form.memoria_ram.data
        equipment.hd_ssd = form.hd_ssd.data
        equipment.sistema_operacional = form.sistema_operacional.data
        equipment.antivirus = form.antivirus.data
        equipment.termo_assinado = form.termo_assinado.data
        equipment.milvus_funcionando = form.milvus_funcionando.data
        equipment.data_aquisicao = form.data_aquisicao.data
        equipment.data_baixa = form.data_baixa.data
        equipment.endereco = form.endereco.data
        equipment.telefone = form.telefone.data
        equipment.email = form.email.data
        equipment.link_termos = form.link_termos.data
        
        # Adicionar histórico de criação
        equipment.add_to_history(f"Equipamento criado por {form.responsavel.data}")
        
        db.session.add(equipment)
        db.session.commit()
        flash('Equipamento adicionado com sucesso!', 'success')
        return redirect(url_for('equipment_list'))
    
    return render_template('equipment_form.html', form=form, title='Novo Equipamento')

@app.route('/equipment/<int:id>')
def equipment_detail(id):
    """Equipment detail view"""
    equipment = Equipment.query.get_or_404(id)
    return render_template('equipment_detail.html', equipment=equipment)

@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
def equipment_edit(id):
    """Edit equipment"""
    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)
    
    if form.validate_on_submit():
        # Check if patrimonio already exists (excluding current equipment)
        existing = Equipment.query.filter(
            Equipment.patrimonio == form.patrimonio.data,
            Equipment.id != id
        ).first()
        if existing:
            flash('Patrimônio já existe no sistema!', 'error')
            return render_template('equipment_form.html', form=form, title='Editar Equipamento')
        
        # Track changes for history
        changes = []
        if equipment.responsavel != form.responsavel.data:
            changes.append(f"Responsável: {equipment.responsavel} → {form.responsavel.data}")
        if equipment.status != form.status.data:
            changes.append(f"Status: {equipment.status} → {form.status.data}")
        if equipment.valor != form.valor.data:
            changes.append(f"Valor: R$ {equipment.valor} → R$ {form.valor.data}")
        
        # Update equipment fields
        equipment.responsavel = form.responsavel.data
        equipment.uf = form.uf.data
        equipment.cc = form.cc.data
        equipment.cnpj = form.cnpj.data
        equipment.fornecedor = form.fornecedor.data
        equipment.modelo = form.modelo.data
        equipment.status = form.status.data
        equipment.patrimonio = form.patrimonio.data
        equipment.valor = form.valor.data
        equipment.marca = form.marca.data
        equipment.processador = form.processador.data
        equipment.memoria_ram = form.memoria_ram.data
        equipment.hd_ssd = form.hd_ssd.data
        equipment.sistema_operacional = form.sistema_operacional.data
        equipment.antivirus = form.antivirus.data
        equipment.termo_assinado = form.termo_assinado.data
        equipment.milvus_funcionando = form.milvus_funcionando.data
        equipment.data_aquisicao = form.data_aquisicao.data
        equipment.data_baixa = form.data_baixa.data
        equipment.endereco = form.endereco.data
        equipment.telefone = form.telefone.data
        equipment.email = form.email.data
        equipment.link_termos = form.link_termos.data
        
        # Add to history if there were changes
        if changes:
            equipment.add_to_history(f"Equipamento atualizado: {', '.join(changes)}")
        
        db.session.commit()
        flash('Equipamento atualizado com sucesso!', 'success')
        return redirect(url_for('equipment_detail', id=id))
    
    return render_template('equipment_form.html', form=form, title='Editar Equipamento', equipment=equipment)

@app.route('/equipment/<int:id>/delete', methods=['POST'])
def equipment_delete(id):
    """Delete equipment"""
    equipment = Equipment.query.get_or_404(id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipamento removido com sucesso!', 'success')
    return redirect(url_for('equipment_list'))

@app.route('/export/excel')
def export_excel():
    """Export equipment to Excel"""
    search_form = SearchForm(request.args)
    if search_form.validate():
        equipment = filter_equipment(search_form)
    else:
        equipment = Equipment.query.all()
    
    return export_to_excel(equipment)

@app.route('/export/pdf')
def export_pdf():
    """Export equipment to PDF"""
    search_form = SearchForm(request.args)
    if search_form.validate():
        equipment = filter_equipment(search_form)
    else:
        equipment = Equipment.query.all()
    
    return export_to_pdf(equipment)

@app.route('/import', methods=['GET', 'POST'])
def import_equipment():
    """Import equipment from Excel file"""
    form = ImportForm()
    
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        
        # Create uploads directory if it doesn't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        try:
            # Import data from Excel
            result = import_from_excel(file_path)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            if result['success']:
                flash(f'Importação concluída com sucesso! {result["imported_count"]} equipamentos importados.', 'success')
                if result['error_count'] > 0:
                    flash(f'{result["error_count"]} linhas tiveram erros e foram ignoradas.', 'warning')
                    # Show first few errors
                    for error in result['errors'][:5]:  # Show first 5 errors
                        flash(error, 'warning')
                    if len(result['errors']) > 5:
                        flash(f'... e mais {len(result["errors"]) - 5} erros.', 'warning')
            else:
                flash('Falha na importação. Verifique o formato do arquivo.', 'error')
                for error in result['errors']:
                    flash(error, 'error')
            
            return redirect(url_for('equipment_list'))
            
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
    
    return render_template('import_form.html', form=form)

@app.route('/download-template')
def download_template():
    """Download Excel template for import"""
    # Create a sample equipment list with proper headers for template
    sample_data = [{
        'ID': '',
        'Responsável': 'João Silva',
        'UF': 'SP',
        'Centro de Custo': 'TI001',
        'CNPJ': '12.345.678/0001-90',
        'Modelo': 'Dell OptiPlex 3090',
        'Status': 'Em uso',
        'Patrimônio': 'PAT001',
        'Valor': 2500.00,
        'Marca': 'Dell',
        'Processador': 'Intel Core i5',
        'Memória RAM': '8GB',
        'HD/SSD': 'SSD 256GB',
        'Sistema Operacional': 'Windows 11',
        'Antivírus': 'Sim',
        'Termo Assinado': 'Sim',
        'Milvus Funcionando': 'Não',
        'Data Aquisição': '15/01/2024',
        'Data Baixa': '',
        'Endereço': 'Av. Paulista, 1000',
        'Telefone': '(11) 9999-8888',
        'Email': 'joao.silva@empresa.com'
    }]
    
    return export_to_excel(sample_data)

@app.route('/history')
def history_log():
    """Display all equipment modification history"""
    # Get all equipment that have history
    equipment_list = Equipment.query.all()
    
    # Filter only equipment with history
    equipment_with_history = [eq for eq in equipment_list if eq.get_history()]
    
    # Count total history entries
    total_entries = sum(len(eq.get_history()) for eq in equipment_with_history)
    
    return render_template('history_log.html', 
                         equipment_list=equipment_with_history,
                         total_entries=total_entries)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
