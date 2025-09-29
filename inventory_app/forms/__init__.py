"""
Forms package - WTForms for the application
"""
from inventory_app.forms.auth_forms import LoginForm, RegistrationForm
from inventory_app.forms.equipment_forms import EquipmentForm, EquipmentSearchForm
from inventory_app.forms.user_forms import UserApprovalForm, UserRoleForm

__all__ = [
    'LoginForm', 'RegistrationForm', 
    'EquipmentForm', 'EquipmentSearchForm',
    'UserApprovalForm', 'UserRoleForm'
]