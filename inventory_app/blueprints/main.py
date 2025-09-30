"""
Main Blueprint - Dashboard and core routes
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from inventory_app.services.equipment_service import EquipmentService
from inventory_app.services.user_service import UserService
from inventory_app.extensions import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    """Landing page - redirects to login if not authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if not current_user.can_access_system():
        flash('Sua conta ainda não foi aprovada ou foi desativada.', 'warning')
        return redirect(url_for('auth.logout'))
    
    # Get dashboard data
    equipment_data = EquipmentService.get_dashboard_data()
    user_stats = UserService.get_user_stats()
    
    return render_template('dashboard.html', 
                         equipment_data=equipment_data,
                         user_stats=user_stats)


@main_bp.route('/dashboard/data')
@login_required
def dashboard_data():
    """API endpoint for dashboard data"""
    if not current_user.has_permission('view'):
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        data = EquipmentService.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Equipment Inventory System',
        'database': 'PostgreSQL connected' if db.engine else 'No database'
    })


@main_bp.route("/centro-custo/new", methods=["POST"])
@login_required
def create_centro_custo():
    """Create new cost center via AJAX"""
    from inventory_app.models.equipment import CentroCusto
    from flask import request
    
    if not current_user.has_permission("create"):
        return jsonify({"success": False, "message": "Sem permissão"}), 403
    
    try:
        codigo = request.form.get("codigo")
        descricao = request.form.get("descricao")
        
        if not codigo or not descricao:
            return jsonify({"success": False, "message": "Código e descrição são obrigatórios"}), 400
        
        # Check if codigo already exists
        existing = CentroCusto.query.filter_by(codigo=codigo).first()
        if existing:
            return jsonify({"success": False, "message": f"Código {codigo} já existe"}), 400
        
        # Create new centro custo
        centro_custo = CentroCusto(codigo=codigo, descricao=descricao, ativo=True)
        db.session.add(centro_custo)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Centro de custo {codigo} criado com sucesso!",
            "id": centro_custo.id,
            "codigo": centro_custo.codigo,
            "descricao": centro_custo.descricao
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
