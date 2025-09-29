"""
Inventory Blueprint - Equipment management routes
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import tempfile

from inventory_app.services.equipment_service import EquipmentService
from inventory_app.forms.equipment_forms import EquipmentForm, EquipmentSearchForm, ImportForm
from inventory_app.models.equipment import Equipment

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/equipment')
@login_required
def equipment_list():
    """Equipment list with search and filters"""
    if not current_user.has_permission('view'):
        flash('Sem permissão para visualizar equipamentos.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = EquipmentSearchForm()
    page = request.args.get('page', 1, type=int)
    
    # Get search parameters
    query = request.args.get('query', '')
    filters = {
        'uf': request.args.get('uf', ''),
        'status': request.args.get('status', ''),
        'tipo_equipamento': request.args.get('tipo_equipamento', ''),
        'centro_custo_id': request.args.get('centro_custo_id', 0, type=int),
        'antivirus': request.args.get('antivirus', ''),
        'termo_assinado': request.args.get('termo_assinado', '')
    }
    
    # Convert string filters to boolean where needed
    if filters['antivirus']:
        filters['antivirus'] = filters['antivirus'] == '1'
    if filters['termo_assinado']:
        filters['termo_assinado'] = filters['termo_assinado'] == '1'
    
    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v != '' and v != 0}
    
    # Search equipment
    equipment_pagination = EquipmentService.search_equipment(query, filters, page)
    
    return render_template('equipment_list.html', 
                         equipment=equipment_pagination,
                         form=form,
                         query=query,
                         filters=request.args)


@inventory_bp.route('/equipment/new', methods=['GET', 'POST'])
@login_required
def equipment_create():
    """Create new equipment"""
    if not current_user.has_permission('create'):
        flash('Sem permissão para criar equipamentos.', 'error')
        return redirect(url_for('inventory.equipment_list'))
    
    form = EquipmentForm()
    if form.validate_on_submit():
        try:
            equipment_data = {
                'patrimonio': form.patrimonio.data,
                'tipo_equipamento': form.tipo_equipamento.data,
                'responsavel': form.responsavel.data,
                'uf': form.uf.data,
                'centro_custo_id': form.centro_custo_id.data,
                'cnpj': form.cnpj.data,
                'fornecedor': form.fornecedor.data,
                'marca': form.marca.data,
                'modelo': form.modelo.data,
                'status': form.status.data,
                'valor': form.valor.data or 0.0,
                'processador': form.processador.data,
                'memoria_ram': form.memoria_ram.data,
                'hd_ssd': form.hd_ssd.data,
                'sistema_operacional': form.sistema_operacional.data,
                'licenca_microsoft': form.licenca_microsoft.data,
                'imei': form.imei.data,
                'linha_telefonica': form.linha_telefonica.data,
                'sistema_operacional_celular': form.sistema_operacional_celular.data,
                'antivirus': form.antivirus.data,
                'termo_assinado': form.termo_assinado.data,
                'milvus_funcionando': form.milvus_funcionando.data,
                'data_aquisicao': form.data_aquisicao.data,
                'data_baixa': form.data_baixa.data,
                'endereco': form.endereco.data,
                'telefone': form.telefone.data,
                'email': form.email.data,
                'link_termos': form.link_termos.data
            }
            
            equipment = EquipmentService.create_equipment(equipment_data, current_user)
            flash(f'Equipamento {equipment.patrimonio} criado com sucesso!', 'success')
            return redirect(url_for('inventory.equipment_detail', id=equipment.id))
        except Exception as e:
            flash(f'Erro ao criar equipamento: {str(e)}', 'error')
    
    return render_template('equipment_form.html', form=form, title='Novo Equipamento')


@inventory_bp.route('/equipment/<int:id>')
@login_required
def equipment_detail(id):
    """Equipment detail view"""
    if not current_user.has_permission('view'):
        flash('Sem permissão para visualizar equipamentos.', 'error')
        return redirect(url_for('main.dashboard'))
    
    equipment = Equipment.query.get_or_404(id)
    return render_template('equipment_detail.html', equipment=equipment)


@inventory_bp.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def equipment_edit(id):
    """Edit equipment"""
    if not current_user.has_permission('edit'):
        flash('Sem permissão para editar equipamentos.', 'error')
        return redirect(url_for('inventory.equipment_detail', id=id))
    
    equipment = Equipment.query.get_or_404(id)
    form = EquipmentForm(obj=equipment)
    form.equipment_id = equipment.id  # For validation
    
    if form.validate_on_submit():
        try:
            equipment_data = {
                'patrimonio': form.patrimonio.data,
                'tipo_equipamento': form.tipo_equipamento.data,
                'responsavel': form.responsavel.data,
                'uf': form.uf.data,
                'centro_custo_id': form.centro_custo_id.data,
                'cnpj': form.cnpj.data,
                'fornecedor': form.fornecedor.data,
                'marca': form.marca.data,
                'modelo': form.modelo.data,
                'status': form.status.data,
                'valor': form.valor.data or 0.0,
                'processador': form.processador.data,
                'memoria_ram': form.memoria_ram.data,
                'hd_ssd': form.hd_ssd.data,
                'sistema_operacional': form.sistema_operacional.data,
                'licenca_microsoft': form.licenca_microsoft.data,
                'imei': form.imei.data,
                'linha_telefonica': form.linha_telefonica.data,
                'sistema_operacional_celular': form.sistema_operacional_celular.data,
                'antivirus': form.antivirus.data,
                'termo_assinado': form.termo_assinado.data,
                'milvus_funcionando': form.milvus_funcionando.data,
                'data_aquisicao': form.data_aquisicao.data,
                'data_baixa': form.data_baixa.data,
                'endereco': form.endereco.data,
                'telefone': form.telefone.data,
                'email': form.email.data,
                'link_termos': form.link_termos.data
            }
            
            EquipmentService.update_equipment(id, equipment_data, current_user)
            flash(f'Equipamento {equipment.patrimonio} atualizado com sucesso!', 'success')
            return redirect(url_for('inventory.equipment_detail', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar equipamento: {str(e)}', 'error')
    
    return render_template('equipment_form.html', form=form, equipment=equipment, title='Editar Equipamento')


@inventory_bp.route('/equipment/<int:id>/delete', methods=['POST'])
@login_required
def equipment_delete(id):
    """Delete equipment"""
    if not current_user.has_permission('delete'):
        flash('Sem permissão para excluir equipamentos.', 'error')
        return redirect(url_for('inventory.equipment_detail', id=id))
    
    try:
        equipment = Equipment.query.get_or_404(id)
        patrimonio = equipment.patrimonio
        EquipmentService.delete_equipment(id, current_user)
        flash(f'Equipamento {patrimonio} excluído com sucesso!', 'success')
        return redirect(url_for('inventory.equipment_list'))
    except Exception as e:
        flash(f'Erro ao excluir equipamento: {str(e)}', 'error')
        return redirect(url_for('inventory.equipment_detail', id=id))


@inventory_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_equipment():
    """Import equipment from Excel"""
    if not current_user.has_permission('create'):
        flash('Sem permissão para importar equipamentos.', 'error')
        return redirect(url_for('inventory.equipment_list'))
    
    form = ImportForm()
    if form.validate_on_submit():
        try:
            file = form.file.data
            filename = secure_filename(file.filename)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                file.save(temp_file.name)
                
                # Import data
                result = EquipmentService.import_from_excel(temp_file.name, current_user)
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                if result['success']:
                    flash(f'Importação concluída! {result["imported_count"]} equipamentos importados.', 'success')
                    if result['errors']:
                        flash(f'{len(result["errors"])} erros encontrados. Verifique o log.', 'warning')
                else:
                    flash(f'Erro na importação: {result["error"]}', 'error')
                
                return redirect(url_for('inventory.equipment_list'))
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'error')
    
    return render_template('import_form.html', form=form)