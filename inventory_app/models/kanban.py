"""
Kanban Models - Task Management System
"""
from datetime import datetime
from inventory_app.extensions import db


class KanbanList(db.Model):
    """Kanban List Model"""
    __tablename__ = 'kanban_list'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0, index=True)
    color = db.Column(db.String(7), default='#6c757d')  # Cor hexadecimal
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamento com tarefas
    tasks = db.relationship('KanbanTask', 
                           backref='list', 
                           lazy='dynamic', 
                           cascade='all, delete-orphan', 
                           order_by='KanbanTask.position')
    
    def __repr__(self):
        return f'<KanbanList {self.name}>'
    
    @staticmethod
    def get_all_ordered():
        """Retorna todas as listas ordenadas por posição"""
        return KanbanList.query.order_by(KanbanList.position).all()


class KanbanTask(db.Model):
    """Kanban Task Model"""
    __tablename__ = 'kanban_task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0, index=True)
    priority = db.Column(db.String(20), default='medium', index=True)  # low, medium, high
    due_date = db.Column(db.Date, nullable=True, index=True)
    completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign key para a lista
    list_id = db.Column(db.Integer, db.ForeignKey('kanban_list.id'), nullable=False, index=True)
    
    # Relacionamento com checklist
    checklist_items = db.relationship('KanbanChecklist', 
                                     backref='task', 
                                     lazy='dynamic', 
                                     cascade='all, delete-orphan', 
                                     order_by='KanbanChecklist.position')
    
    def __repr__(self):
        return f'<KanbanTask {self.title}>'
    
    @property
    def priority_color(self):
        """Retorna a cor baseada na prioridade"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#dc3545'
        }
        return colors.get(self.priority, '#6c757d')
    
    @property
    def is_overdue(self):
        """Verifica se a tarefa está atrasada"""
        if self.due_date and not self.completed:
            return self.due_date < datetime.now().date()
        return False
    
    @property
    def checklist_progress(self):
        """Retorna o progresso do checklist (itens completados / total)"""
        checklist_items = self.checklist_items.all()
        if not checklist_items:
            return None
        total = len(checklist_items)
        completed = sum(1 for item in checklist_items if item.completed)
        return {'completed': completed, 'total': total, 'percentage': (completed / total) * 100 if total > 0 else 0}


class KanbanChecklist(db.Model):
    """Kanban Checklist Item Model"""
    __tablename__ = 'kanban_checklist'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    position = db.Column(db.Integer, nullable=False, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Foreign key para a tarefa
    task_id = db.Column(db.Integer, db.ForeignKey('kanban_task.id'), nullable=False, index=True)
    
    def __repr__(self):
        return f'<KanbanChecklist {self.text}>'