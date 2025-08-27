from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Equipment, CentroCusto, Task, ChecklistItem
from forms import EquipmentForm, SearchForm, ImportForm, CentroCustoForm, TaskForm, get_centro_custo_choices, get_equipment_choices
from utils import export_to_excel, export_to_pdf, create_uf_chart, create_value_chart, filter_equipment, import_from_excel
import json
import os
from werkzeug.utils import secure_filename

@app.route('/')
def dashboard():
    """Main dashboard route"""
    stats = Equipment.get_dashboard_stats()
    
    # Convert SQLAlchemy Row objects to simple lists
    uf_data = [[item[0], item[1]] for item in Equipment.get_by_uf()]
    fornecedor_data = [[item[0], item[1]] for item in Equipment.get_by_fornecedor()]
    status_data = [[item[0], item[1]] for item in Equipment.get_by_status()]
    segmentos_data = [[item[0], item[1]] for item in Equipment.get_by_segmento()]
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         uf_data=uf_data,
                         fornecedor_data=fornecedor_data,
                         status_data=status_data,
                         segmentos_data=segmentos_data)

@app.route('/equipment')
def equipment_list():
    """Equipment list with search and filtering"""
    search_form = SearchForm(request.args)
    # Carregar choices para centro de custo
    search_form.cc.choices = [('', 'Todos')] + [(str(c.id), f"{c.codigo} - {c.descricao}") for c in CentroCusto.get_all_active()]
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Check if any search criteria is provided
    has_search_criteria = (
        request.args.get('search_term') or 
        request.args.get('uf') or 
        request.args.get('status') or 
        request.args.get('cnpj') or 
        request.args.get('marca') or 
        request.args.get('cc')
    )
    
    if has_search_criteria:
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

@app.route('/centro-custo/new', methods=['POST'])
def centro_custo_new():
    """Create new cost center via AJAX"""
    form = CentroCustoForm()
    
    if form.validate_on_submit():
        # Verificar se já existe
        existing = CentroCusto.query.filter_by(codigo=form.codigo.data).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Código já existe!'
            })
        
        centro_custo = CentroCusto(
            codigo=form.codigo.data,
            descricao=form.descricao.data
        )
        db.session.add(centro_custo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': centro_custo.id,
            'codigo': centro_custo.codigo,
            'descricao': centro_custo.descricao,
            'message': 'Centro de custo criado com sucesso!'
        })
    
    return jsonify({
        'success': False,
        'message': 'Dados inválidos!'
    })

@app.route('/centro-custo/list')
def centro_custo_list():
    """Get list of cost centers for AJAX"""
    centros = CentroCusto.get_all_active()
    return jsonify([{
        'id': c.id,
        'codigo': c.codigo,
        'descricao': c.descricao
    } for c in centros])

@app.route('/equipment/new', methods=['GET', 'POST'])
def equipment_new():
    """Create new equipment"""
    form = EquipmentForm()
    # Carregar choices dinamicamente
    form.centro_custo_id.choices = get_centro_custo_choices()
    
    if form.validate_on_submit():
        # Check if patrimonio already exists
        existing = Equipment.query.filter_by(patrimonio=form.patrimonio.data).first()
        if existing:
            flash('Patrimônio já existe no sistema!', 'error')
            return render_template('equipment_form.html', form=form, title='Novo Equipamento')
        
        equipment = Equipment()
        equipment.responsavel = form.responsavel.data
        equipment.uf = form.uf.data
        equipment.centro_custo_id = form.centro_custo_id.data
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
        equipment.senha = form.senha.data
        
        # Adicionar histórico de criação
        equipment.add_to_history(f"Equipamento criado por {form.responsavel.data}")
        
        # Populate cc field from centro_custo relationship
        if equipment.centro_custo_id:
            centro_custo = CentroCusto.query.get(equipment.centro_custo_id)
            if centro_custo:
                equipment.cc = f"{centro_custo.codigo} - {centro_custo.descricao}"
        
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
    # Carregar choices dinamicamente
    form.centro_custo_id.choices = get_centro_custo_choices()
    
    if form.validate_on_submit():
        # Check if patrimonio already exists (excluding current equipment)
        existing = Equipment.query.filter(
            Equipment.patrimonio == form.patrimonio.data,
            Equipment.id != id
        ).first()
        if existing:
            flash('Patrimônio já existe no sistema!', 'error')
            return render_template('equipment_form.html', form=form, title='Editar Equipamento')
        
        # Track changes for history - comprehensive tracking
        changes = []
        if equipment.responsavel != form.responsavel.data:
            changes.append(f"Responsável: {equipment.responsavel} → {form.responsavel.data}")
        if equipment.uf != form.uf.data:
            changes.append(f"UF: {equipment.uf} → {form.uf.data}")
        if equipment.centro_custo_id != form.centro_custo_id.data:
            old_cc = f"{equipment.centro_custo.codigo} - {equipment.centro_custo.descricao}" if equipment.centro_custo else "N/A"
            new_cc_obj = CentroCusto.query.get(form.centro_custo_id.data)
            new_cc = f"{new_cc_obj.codigo} - {new_cc_obj.descricao}" if new_cc_obj else "N/A"
            changes.append(f"Centro de Custo: {old_cc} → {new_cc}")
        if equipment.cnpj != form.cnpj.data:
            changes.append(f"CNPJ: {equipment.cnpj} → {form.cnpj.data}")
        if equipment.fornecedor != form.fornecedor.data:
            changes.append(f"Fornecedor: {equipment.fornecedor or 'N/A'} → {form.fornecedor.data or 'N/A'}")
        if equipment.modelo != form.modelo.data:
            changes.append(f"Modelo: {equipment.modelo} → {form.modelo.data}")
        if equipment.status != form.status.data:
            changes.append(f"Status: {equipment.status} → {form.status.data}")
        if equipment.patrimonio != form.patrimonio.data:
            changes.append(f"Patrimônio: {equipment.patrimonio} → {form.patrimonio.data}")
        if equipment.valor != form.valor.data:
            changes.append(f"Valor: R$ {equipment.valor} → R$ {form.valor.data}")
        if equipment.marca != form.marca.data:
            changes.append(f"Marca: {equipment.marca or 'N/A'} → {form.marca.data or 'N/A'}")
        if equipment.processador != form.processador.data:
            changes.append(f"Processador: {equipment.processador or 'N/A'} → {form.processador.data or 'N/A'}")
        if equipment.memoria_ram != form.memoria_ram.data:
            changes.append(f"Memória RAM: {equipment.memoria_ram or 'N/A'} → {form.memoria_ram.data or 'N/A'}")
        if equipment.hd_ssd != form.hd_ssd.data:
            changes.append(f"HD/SSD: {equipment.hd_ssd or 'N/A'} → {form.hd_ssd.data or 'N/A'}")
        if equipment.sistema_operacional != form.sistema_operacional.data:
            changes.append(f"Sistema Operacional: {equipment.sistema_operacional or 'N/A'} → {form.sistema_operacional.data or 'N/A'}")
        if equipment.antivirus != form.antivirus.data:
            changes.append(f"Antivírus: {'Sim' if equipment.antivirus else 'Não'} → {'Sim' if form.antivirus.data else 'Não'}")
        if equipment.termo_assinado != form.termo_assinado.data:
            changes.append(f"Termo Assinado: {'Sim' if equipment.termo_assinado else 'Não'} → {'Sim' if form.termo_assinado.data else 'Não'}")
        if equipment.milvus_funcionando != form.milvus_funcionando.data:
            changes.append(f"Milvus Funcionando: {'Sim' if equipment.milvus_funcionando else 'Não'} → {'Sim' if form.milvus_funcionando.data else 'Não'}")
        if equipment.data_aquisicao != form.data_aquisicao.data:
            old_date = equipment.data_aquisicao.strftime('%d/%m/%Y') if equipment.data_aquisicao else 'N/A'
            new_date = form.data_aquisicao.data.strftime('%d/%m/%Y') if form.data_aquisicao.data else 'N/A'
            changes.append(f"Data Aquisição: {old_date} → {new_date}")
        if equipment.data_baixa != form.data_baixa.data:
            old_date = equipment.data_baixa.strftime('%d/%m/%Y') if equipment.data_baixa else 'N/A'
            new_date = form.data_baixa.data.strftime('%d/%m/%Y') if form.data_baixa.data else 'N/A'
            changes.append(f"Data Baixa: {old_date} → {new_date}")
        if equipment.endereco != form.endereco.data:
            changes.append(f"Endereço: {equipment.endereco or 'N/A'} → {form.endereco.data or 'N/A'}")
        if equipment.telefone != form.telefone.data:
            changes.append(f"Telefone: {equipment.telefone or 'N/A'} → {form.telefone.data or 'N/A'}")
        if equipment.email != form.email.data:
            changes.append(f"Email: {equipment.email or 'N/A'} → {form.email.data or 'N/A'}")
        if equipment.link_termos != form.link_termos.data:
            changes.append(f"Link Termos: {equipment.link_termos or 'N/A'} → {form.link_termos.data or 'N/A'}")
        if equipment.senha != form.senha.data:
            changes.append(f"Senha: {'***' if equipment.senha else 'N/A'} → {'***' if form.senha.data else 'N/A'}")
        
        # Update equipment fields
        equipment.responsavel = form.responsavel.data
        equipment.uf = form.uf.data
        equipment.centro_custo_id = form.centro_custo_id.data
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
        equipment.senha = form.senha.data
        
        # Update cc field when centro_custo_id changes
        if equipment.centro_custo_id:
            centro_custo = CentroCusto.query.get(equipment.centro_custo_id)
            if centro_custo:
                equipment.cc = f"{centro_custo.codigo} - {centro_custo.descricao}"
        
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
    
    # Add to history before deleting
    equipment.add_to_history(f"Equipamento removido do sistema (Patrimônio: {equipment.patrimonio})")
    db.session.commit()  # Commit history before deletion
    
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
    """Display user selection for history by profile"""
    # Get all equipment that have history
    all_equipment = Equipment.query.all()
    equipment_with_history = [eq for eq in all_equipment if eq.get_history()]
    
    # Get unique profiles (responsáveis)
    profiles = list(set([eq.responsavel for eq in equipment_with_history]))
    profiles.sort()
    
    # If only one profile, redirect directly to it
    if len(profiles) == 1:
        return redirect(url_for('history_by_profile', profile_name=profiles[0]))
    
    return render_template('history_log.html', 
                         profiles=profiles,
                         show_profile_selection=True)

@app.route('/history/profile/<profile_name>')
def history_by_profile(profile_name):
    """Display equipment modification history filtered by profile/responsável"""
    # Get all equipment for this profile that have history
    equipment_list = Equipment.query.filter_by(responsavel=profile_name).all()
    
    # Filter only equipment with history
    equipment_with_history = [eq for eq in equipment_list if eq.get_history()]
    
    # Count total history entries for this profile
    total_entries = sum(len(eq.get_history()) for eq in equipment_with_history)
    
    # Get unique profiles for navigation
    all_equipment = Equipment.query.all()
    equipment_with_any_history = [eq for eq in all_equipment if eq.get_history()]
    profiles = list(set([eq.responsavel for eq in equipment_with_any_history]))
    profiles.sort()
    
    return render_template('history_log.html', 
                         equipment_list=equipment_with_history,
                         total_entries=total_entries,
                         profiles=profiles,
                         current_profile=profile_name)

# Planner Routes
@app.route('/planner')
def planner():
    """Kanban planner view"""
    tasks = Task.get_by_status()
    return render_template('planner.html', tasks=tasks)

@app.route('/planner/task/new', methods=['GET', 'POST'])
def task_new():
    """Create new task"""
    form = TaskForm()
    
    if form.validate_on_submit():
        # Validate equipment ID if provided
        if form.equipment_id.data:
            equipment = Equipment.query.get(form.equipment_id.data)
            if not equipment:
                flash('Equipamento com ID especificado não foi encontrado!', 'error')
                return render_template('task_form.html', form=form, title='Nova Tarefa')
        
        task = Task()
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.equipment_id = form.equipment_id.data if form.equipment_id.data else None
        task.assigned_to = form.assigned_to.data
        task.due_date = form.due_date.data
        
        db.session.add(task)
        db.session.flush()  # Get the task ID
        
        # Process checklist items
        if form.checklist_items.data:
            checklist_text = form.checklist_items.data.strip()
            if checklist_text:
                items = [item.strip() for item in checklist_text.split('\n') if item.strip()]
                for index, item_title in enumerate(items):
                    checklist_item = ChecklistItem()
                    checklist_item.task_id = task.id
                    checklist_item.title = item_title
                    checklist_item.order_index = index
                    db.session.add(checklist_item)
        
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('planner'))
    
    return render_template('task_form.html', form=form, title='Nova Tarefa')

@app.route('/planner/task/<int:id>/edit', methods=['GET', 'POST'])
def task_edit(id):
    """Edit task"""
    task = Task.query.get_or_404(id)
    form = TaskForm(obj=task)
    
    # Populate checklist items in the form
    if request.method == 'GET':
        existing_items = [item.title for item in sorted(task.checklist_items, key=lambda x: x.order_index)]
        form.checklist_items.data = '\n'.join(existing_items)
    
    if form.validate_on_submit():
        # Validate equipment ID if provided
        if form.equipment_id.data:
            equipment = Equipment.query.get(form.equipment_id.data)
            if not equipment:
                flash('Equipamento com ID especificado não foi encontrado!', 'error')
                return render_template('task_form.html', form=form, title='Editar Tarefa', task=task)
        
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.equipment_id = form.equipment_id.data if form.equipment_id.data else None
        task.assigned_to = form.assigned_to.data
        task.due_date = form.due_date.data
        
        # Update checklist items - remove all existing and add new ones
        ChecklistItem.query.filter_by(task_id=task.id).delete()
        
        if form.checklist_items.data:
            checklist_text = form.checklist_items.data.strip()
            if checklist_text:
                items = [item.strip() for item in checklist_text.split('\n') if item.strip()]
                for index, item_title in enumerate(items):
                    checklist_item = ChecklistItem()
                    checklist_item.task_id = task.id
                    checklist_item.title = item_title
                    checklist_item.order_index = index
                    db.session.add(checklist_item)
        
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('planner'))
    
    return render_template('task_form.html', form=form, title='Editar Tarefa', task=task)

@app.route('/planner/task/<int:id>/update-status', methods=['POST'])
def task_update_status(id):
    """Update task status via AJAX"""
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' in data:
        task.status = data['status']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status atualizado!'})
    
    return jsonify({'success': False, 'message': 'Status inválido!'})

@app.route('/planner/task/<int:id>/delete', methods=['POST'])
def task_delete(id):
    """Delete task"""
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa removida com sucesso!', 'success')
    return redirect(url_for('planner'))

@app.route('/planner/task/<int:task_id>/checklist/<int:item_id>/toggle', methods=['POST'])
def toggle_checklist_item(task_id, item_id):
    """Toggle checklist item completion status"""
    task = Task.query.get_or_404(task_id)
    item = ChecklistItem.query.filter_by(id=item_id, task_id=task_id).first_or_404()
    
    item.completed = not item.completed
    db.session.commit()
    
    # Calculate updated progress
    progress = task.checklist_progress
    
    return jsonify({
        'success': True,
        'completed': item.completed,
        'progress': progress
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
