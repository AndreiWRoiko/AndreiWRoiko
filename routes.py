from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from urllib.parse import urlparse as url_parse
from app import app, db
from models import Equipment, CentroCusto, KanbanList, KanbanTask, KanbanChecklist, User
from forms import (EquipmentForm, SearchForm, ImportForm, CentroCustoForm, KanbanListForm, KanbanTaskForm, 
                   LoginForm, RegisterForm, get_centro_custo_choices,
                   UserApprovalForm, AdminUserCreationForm, UserEditForm, AdminFilterForm, BulkUserActionForm)
from utils import export_to_excel, export_to_pdf, create_uf_chart, create_value_chart, filter_equipment, import_from_excel
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from auth_decorators import (requires_permission, requires_role, admin_required, support_or_admin_required, 
                            approved_user_required, log_user_access, inject_user_permissions)
from functools import wraps
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make session permanent and perform automatic cleanup
@app.before_request
def make_session_permanent():
    session.permanent = True
    
    # Executar limpeza automática de usuários recusados uma vez por dia
    # (verificação baseada em cookie para evitar execução excessiva)
    last_cleanup = session.get('last_cleanup_check')
    today = datetime.now().strftime('%Y-%m-%d')
    
    if last_cleanup != today:
        try:
            # Limpeza automática de usuários recusados há mais de 30 dias
            users_to_delete = User.get_rejected_users_for_cleanup()
            if users_to_delete:
                count = len(users_to_delete)
                for user in users_to_delete:
                    db.session.delete(user)
                db.session.commit()
                print(f"[CLEANUP] {count} usuários recusados foram removidos automaticamente")
            
            session['last_cleanup_check'] = today
        except Exception as e:
            print(f"[CLEANUP ERROR] Erro durante limpeza automática: {e}")
            db.session.rollback()

@app.route('/')
@approved_user_required
def index():
    """Main route - dashboard for approved users only"""
    log_user_access('dashboard')
    
    # User is approved and logged in, show the dashboard
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with access control verification"""
    if current_user.is_authenticated:
        if current_user.is_pending:
            return redirect(url_for('pending_approval'))
        elif current_user.is_rejected:
            return redirect(url_for('access_denied'))
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Verificar status do usuário antes de fazer login
            if user.is_pending:
                flash('Sua conta está pendente de aprovação. Aguarde a liberação de um administrador.', 'warning')
                return render_template('login.html', form=form)
            elif user.is_rejected:
                flash('Sua conta foi recusada. Entre em contato com o suporte para mais informações.', 'error')
                return render_template('login.html', form=form)
            elif not user.is_active:
                flash('Sua conta está desativada. Entre em contato com o suporte.', 'error')
                return render_template('login.html', form=form)
            
            # Atualizar último login
            user.update_last_login()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            log_user_access('login')
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        flash('Usuário ou senha inválidos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with pending approval system"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Criar usuário com status pendente
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='Controladoria',  # Role padrão
            status='Pendente'      # Status pendente para aprovação
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registro realizado com sucesso! Sua conta está pendente de aprovação por um administrador. '
              'Você receberá um email quando sua conta for liberada.', 'info')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/equipment')
@requires_permission('view')
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
        request.args.get('cc') or
        request.args.get('tipo_equipamento')
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
@login_required
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
@login_required
def centro_custo_list():
    """Get list of cost centers for AJAX"""
    centros = CentroCusto.get_all_active()
    return jsonify([{
        'id': c.id,
        'codigo': c.codigo,
        'descricao': c.descricao
    } for c in centros])

@app.route('/equipment/new', methods=['GET', 'POST'])
@requires_permission('create')
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
        equipment.tipo_equipamento = form.tipo_equipamento.data
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
        equipment.licenca_microsoft = form.licenca_microsoft.data
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
        
        # Campos específicos para celulares
        if form.tipo_equipamento.data == 'celular':
            equipment.imei = form.imei.data
            equipment.linha_telefonica = form.linha_telefonica.data
            equipment.sistema_operacional_celular = form.sistema_operacional_celular.data
        
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
@requires_permission('view')
def equipment_detail(id):
    """Equipment detail view"""
    equipment = Equipment.query.get_or_404(id)
    return render_template('equipment_detail.html', equipment=equipment)

@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
@requires_permission('edit')
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
        if equipment.licenca_microsoft != form.licenca_microsoft.data:
            changes.append(f"Licença Microsoft: {equipment.licenca_microsoft or 'N/A'} → {form.licenca_microsoft.data or 'N/A'}")
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
        
        # Verificar mudanças nos campos específicos de celulares
        if form.tipo_equipamento.data == 'celular':
            if equipment.imei != form.imei.data:
                changes.append(f"IMEI: {equipment.imei or 'N/A'} → {form.imei.data or 'N/A'}")
            if equipment.linha_telefonica != form.linha_telefonica.data:
                changes.append(f"Linha Telefônica: {equipment.linha_telefonica or 'N/A'} → {form.linha_telefonica.data or 'N/A'}")
            if equipment.sistema_operacional_celular != form.sistema_operacional_celular.data:
                changes.append(f"Sistema Operacional Celular: {equipment.sistema_operacional_celular or 'N/A'} → {form.sistema_operacional_celular.data or 'N/A'}")
        
        # Update equipment fields
        equipment.tipo_equipamento = form.tipo_equipamento.data
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
        equipment.licenca_microsoft = form.licenca_microsoft.data
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
        
        # Atualizar campos específicos para celulares
        if form.tipo_equipamento.data == 'celular':
            equipment.imei = form.imei.data
            equipment.linha_telefonica = form.linha_telefonica.data
            equipment.sistema_operacional_celular = form.sistema_operacional_celular.data
        else:
            # Limpar campos de celular se mudou para notebook
            equipment.imei = None
            equipment.linha_telefonica = None
            equipment.sistema_operacional_celular = None
        
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
@requires_permission('delete')
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
@login_required
def export_excel():
    """Export equipment to Excel"""
    search_form = SearchForm(request.args)
    if search_form.validate():
        equipment = filter_equipment(search_form)
    else:
        equipment = Equipment.query.all()
    
    return export_to_excel(equipment)

@app.route('/export/pdf')
@login_required
def export_pdf():
    """Export equipment to PDF"""
    search_form = SearchForm(request.args)
    if search_form.validate():
        equipment = filter_equipment(search_form)
    else:
        equipment = Equipment.query.all()
    
    return export_to_pdf(equipment)

@app.route('/import', methods=['GET', 'POST'])
@requires_permission('create')
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
@login_required
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
@login_required
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
@login_required
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Kanban/Planner Routes
@app.route('/planner')
@login_required
def planner():
    """Main planner/kanban board"""
    lists = KanbanList.get_all_ordered()
    return render_template('planner.html', lists=lists)

@app.route('/planner/list/new', methods=['POST'])
@login_required
def kanban_list_new():
    """Create new kanban list"""
    form = KanbanListForm()
    if form.validate_on_submit():
        # Get next position
        max_position = db.session.query(db.func.max(KanbanList.position)).scalar() or 0
        
        kanban_list = KanbanList(
            name=form.name.data,
            color=form.color.data,
            position=max_position + 1
        )
        db.session.add(kanban_list)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'list': {
                'id': kanban_list.id,
                'name': kanban_list.name,
                'color': kanban_list.color,
                'position': kanban_list.position
            }
        })
    
    return jsonify({'success': False, 'errors': form.errors})

@app.route('/planner/list/<int:list_id>/delete', methods=['DELETE'])
@login_required
def kanban_list_delete(list_id):
    """Delete kanban list"""
    kanban_list = KanbanList.query.get_or_404(list_id)
    db.session.delete(kanban_list)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/planner/task/new', methods=['POST'])
@login_required
def kanban_task_new():
    """Create new kanban task"""
    form = KanbanTaskForm()
    
    # Populate list choices
    form.list_id.choices = [(l.id, l.name) for l in KanbanList.query.all()]
    
    if form.validate_on_submit():
        # Get next position in the list
        max_position = db.session.query(db.func.max(KanbanTask.position)).filter_by(list_id=form.list_id.data).scalar() or 0
        
        task = KanbanTask(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            list_id=form.list_id.data,
            position=max_position + 1
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'priority_color': task.priority_color,
                'due_date': task.due_date.strftime('%d/%m/%Y') if task.due_date else None,
                'is_overdue': task.is_overdue,
                'list_id': task.list_id,
                'checklist_progress': task.checklist_progress
            }
        })
    
    return jsonify({'success': False, 'errors': form.errors})

@app.route('/planner/task/<int:task_id>/edit', methods=['PUT'])
@login_required
def kanban_task_edit(task_id):
    """Edit kanban task"""
    task = KanbanTask.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        if data['due_date']:
            from datetime import datetime
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        else:
            task.due_date = None
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'priority_color': task.priority_color,
            'due_date': task.due_date.strftime('%d/%m/%Y') if task.due_date else None,
            'is_overdue': task.is_overdue,
            'completed': task.completed
        }
    })

@app.route('/planner/task/<int:task_id>/delete', methods=['DELETE'])
@login_required
def kanban_task_delete(task_id):
    """Delete kanban task"""
    task = KanbanTask.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/planner/task/<int:task_id>/move', methods=['PUT'])
@login_required
def kanban_task_move(task_id):
    """Move task to different list and position"""
    task = KanbanTask.query.get_or_404(task_id)
    data = request.get_json()
    
    new_list_id = data.get('list_id')
    new_position = data.get('position', 0)
    
    if new_list_id:
        task.list_id = new_list_id
        task.position = new_position
        db.session.commit()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid data'})

@app.route('/planner/task/<int:task_id>/checklist', methods=['GET'])
@login_required
def get_task_checklist(task_id):
    """Get checklist items for a task"""
    task = KanbanTask.query.get_or_404(task_id)
    checklist_items = [
        {
            'id': item.id,
            'text': item.text,
            'completed': item.completed,
            'position': item.position
        }
        for item in task.checklist_items
    ]
    return jsonify({
        'success': True,
        'task_id': task_id,
        'checklist': checklist_items,
        'progress': task.checklist_progress
    })

@app.route('/planner/task/<int:task_id>/checklist/add', methods=['POST'])
@login_required
def add_checklist_item(task_id):
    """Add new checklist item to task"""
    task = KanbanTask.query.get_or_404(task_id)
    data = request.get_json()
    
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'Texto é obrigatório'})
    
    # Get next position
    max_position = db.session.query(db.func.max(KanbanChecklist.position)).filter_by(task_id=task_id).scalar() or 0
    
    checklist_item = KanbanChecklist(
        text=text,
        task_id=task_id,
        position=max_position + 1
    )
    
    db.session.add(checklist_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'item': {
            'id': checklist_item.id,
            'text': checklist_item.text,
            'completed': checklist_item.completed,
            'position': checklist_item.position
        },
        'progress': task.checklist_progress
    })

@app.route('/planner/checklist/<int:item_id>/toggle', methods=['PUT'])
def toggle_checklist_item(item_id):
    """Toggle completion status of checklist item"""
    item = KanbanChecklist.query.get_or_404(item_id)
    item.completed = not item.completed
    db.session.commit()
    
    return jsonify({
        'success': True,
        'item': {
            'id': item.id,
            'text': item.text,
            'completed': item.completed
        },
        'progress': item.task.checklist_progress
    })

@app.route('/planner/checklist/<int:item_id>/delete', methods=['DELETE'])
def delete_checklist_item(item_id):
    """Delete checklist item"""
    item = KanbanChecklist.query.get_or_404(item_id)
    task_id = item.task_id
    db.session.delete(item)
    db.session.commit()
    
    # Get updated progress
    task = KanbanTask.query.get(task_id)
    
    return jsonify({
        'success': True,
        'progress': task.checklist_progress
    })

# =============================================================================
# ROTAS ADMINISTRATIVAS - Sistema de Controle de Acesso
# =============================================================================

@app.route('/pending-approval')
@login_required
def pending_approval():
    """Página para usuários pendentes de aprovação"""
    if not current_user.is_pending:
        return redirect(url_for('index'))
    return render_template('pending_approval.html')

@app.route('/access-denied')
def access_denied():
    """Página de acesso negado"""
    return render_template('access_denied.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Painel administrativo principal"""
    log_user_access('admin_dashboard')
    
    # Estatísticas gerais
    stats = {
        'pending_users': User.query.filter_by(status='Pendente').count(),
        'total_users': User.query.count(),
        'approved_users': User.query.filter_by(status='Aprovado').count(),
        'rejected_users': User.query.filter_by(status='Recusado').count(),
        'admin_users': User.query.filter_by(role='ADM', status='Aprovado').count(),
        'support_users': User.query.filter_by(role='Suporte', status='Aprovado').count(),
        'controladoria_users': User.query.filter_by(role='Controladoria', status='Aprovado').count(),
    }
    
    # Usuários pendentes recentes (últimos 10)
    pending_users = User.query.filter_by(status='Pendente').order_by(User.created_at.desc()).limit(10).all()
    
    # Usuários recusados para limpeza (mais de 30 dias)
    users_for_cleanup = User.get_rejected_users_for_cleanup()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         pending_users=pending_users,
                         users_for_cleanup=users_for_cleanup)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Gestão de usuários"""
    log_user_access('admin_users')
    
    # Filtros
    filter_form = AdminFilterForm(request.args)
    
    # Query base
    query = User.query
    
    # Aplicar filtros
    if filter_form.status_filter.data:
        query = query.filter(User.status == filter_form.status_filter.data)
    
    if filter_form.role_filter.data:
        query = query.filter(User.role == filter_form.role_filter.data)
    
    if filter_form.search.data:
        search_term = f"%{filter_form.search.data}%"
        query = query.filter(
            db.or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, filter_form=filter_form)

@app.route('/admin/users/pending')
@admin_required
def admin_pending_users():
    """Usuários pendentes de aprovação"""
    log_user_access('admin_pending_users')
    
    pending_users = User.get_pending_users()
    return render_template('admin/pending_users.html', pending_users=pending_users)

@app.route('/admin/users/approve/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def approve_user(user_id):
    """Aprovar usuário"""
    user = User.query.get_or_404(user_id)
    if user.status != 'Pendente':
        flash('Este usuário não está pendente de aprovação.', 'error')
        return redirect(url_for('admin_pending_users'))
    
    form = UserApprovalForm()
    if form.validate_on_submit():
        user.approve(current_user)
        user.role = form.role.data
        db.session.commit()
        
        log_user_access('approve_user', f'User {user.username} approved with role {user.role}')
        flash(f'Usuário {user.username} aprovado com sucesso como {user.role}.', 'success')
        
        # TODO: Enviar email de aprovação
        
        return redirect(url_for('admin_pending_users'))
    
    # Pré-preencher formulário
    form.user_id.data = user.id
    form.action.data = 'approve'
    
    return render_template('admin/approve_user.html', user=user, form=form)

@app.route('/admin/users/reject/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def reject_user(user_id):
    """Recusar usuário"""
    user = User.query.get_or_404(user_id)
    if user.status != 'Pendente':
        flash('Este usuário não está pendente de aprovação.', 'error')
        return redirect(url_for('admin_pending_users'))
    
    form = UserApprovalForm()
    if form.validate_on_submit():
        reason = form.rejection_reason.data or 'Sem motivo especificado'
        user.reject(current_user, reason)
        db.session.commit()
        
        log_user_access('reject_user', f'User {user.username} rejected: {reason}')
        flash(f'Usuário {user.username} recusado.', 'info')
        
        # TODO: Enviar email de recusa
        
        return redirect(url_for('admin_pending_users'))
    
    # Pré-preencher formulário
    form.user_id.data = user.id
    form.action.data = 'reject'
    
    return render_template('admin/reject_user.html', user=user, form=form)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@support_or_admin_required
def admin_create_user():
    """Criar usuário através do painel administrativo"""
    log_user_access('admin_create_user')
    
    form = AdminUserCreationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        if form.auto_approve.data:
            user.status = 'Aprovado'
            user.approved_by = current_user.id
            user.approved_at = datetime.utcnow()
        else:
            user.status = 'Pendente'
        
        db.session.add(user)
        db.session.commit()
        
        log_user_access('create_user', f'User {user.username} created with role {user.role}')
        flash(f'Usuário {user.username} criado com sucesso.', 'success')
        
        return redirect(url_for('admin_users'))
    
    return render_template('admin/create_user.html', form=form)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@support_or_admin_required
def admin_edit_user(user_id):
    """Editar usuário"""
    user = User.query.get_or_404(user_id)
    
    # Suporte não pode editar administradores
    if current_user.role == 'Suporte' and user.role == 'ADM':
        flash('Você não tem permissão para editar administradores.', 'error')
        return redirect(url_for('admin_users'))
    
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_active = form.is_active.data
        
        # Suporte não pode alterar role para ADM
        if current_user.role == 'ADM' or form.role.data != 'ADM':
            user.role = form.role.data
        
        if form.change_password.data and form.new_password.data:
            user.set_password(form.new_password.data)
        
        db.session.commit()
        
        log_user_access('edit_user', f'User {user.username} edited')
        flash(f'Usuário {user.username} atualizado com sucesso.', 'success')
        
        return redirect(url_for('admin_users'))
    
    # Pré-preencher formulário
    form.user_id.data = user.id
    
    return render_template('admin/edit_user.html', user=user, form=form)

@app.route('/admin/users/cleanup')
@admin_required
def cleanup_rejected_users():
    """Limpeza automática de usuários recusados há mais de 30 dias"""
    log_user_access('cleanup_rejected_users')
    
    users_to_delete = User.get_rejected_users_for_cleanup()
    count = len(users_to_delete)
    
    for user in users_to_delete:
        db.session.delete(user)
    
    db.session.commit()
    
    flash(f'{count} usuários recusados foram removidos do sistema.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/bulk-action', methods=['POST'])
@admin_required
def bulk_user_action():
    """Ações em lote para usuários"""
    form = BulkUserActionForm()
    
    if form.validate_on_submit():
        selected_user_ids = request.form.getlist('selected_users')
        action = form.bulk_action.data
        
        if not selected_user_ids:
            flash('Selecione pelo menos um usuário.', 'error')
            return redirect(url_for('admin_users'))
        
        users = User.query.filter(User.id.in_(selected_user_ids)).all()
        count = len(users)
        
        if action == 'approve':
            for user in users:
                if user.status == 'Pendente':
                    user.approve(current_user)
            flash(f'{count} usuários aprovados.', 'success')
            
        elif action == 'reject':
            reason = form.bulk_rejection_reason.data or 'Recusa em lote'
            for user in users:
                if user.status == 'Pendente':
                    user.reject(current_user, reason)
            flash(f'{count} usuários recusados.', 'info')
            
        elif action == 'activate':
            for user in users:
                user.is_active = True
            flash(f'{count} usuários ativados.', 'success')
            
        elif action == 'deactivate':
            for user in users:
                user.is_active = False
            flash(f'{count} usuários desativados.', 'info')
            
        elif action == 'delete_rejected':
            users_to_delete = [u for u in users if u.status == 'Recusado']
            for user in users_to_delete:
                db.session.delete(user)
            flash(f'{len(users_to_delete)} usuários recusados removidos.', 'info')
        
        db.session.commit()
        log_user_access('bulk_action', f'Action {action} on {count} users')
    
    return redirect(url_for('admin_users'))

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'logo.png', mimetype='image/png')
