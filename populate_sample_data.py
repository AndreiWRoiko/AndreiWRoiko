#!/usr/bin/env python3

from app import app, db
from models import Equipment
from datetime import datetime, date

def add_sample_data():
    """Add sample data to demonstrate the dashboard"""
    with app.app_context():
        # Check if data already exists
        if Equipment.query.count() > 0:
            print("Database already has data. Skipping sample data creation.")
            return
        
        # Sample data
        sample_equipment = [
            {
                'responsavel': 'João Silva',
                'uf': 'SP',
                'cc': 'TI001',
                'cnpj': '12.345.678/0001-90',
                'fornecedor': 'Dell',
                'modelo': 'OptiPlex 3090',
                'status': 'Em uso',
                'patrimonio': 'PAT001',
                'valor': 2500.00,
                'marca': 'Dell',
                'processador': 'Intel Core i5',
                'memoria_ram': '8GB',
                'hd_ssd': 'SSD 256GB',
                'sistema_operacional': 'Windows 11',
                'antivirus': True,
                'termo_assinado': True,
                'milvus_funcionando': True
            },
            {
                'responsavel': 'Maria Santos',
                'uf': 'RJ',
                'cc': 'ADM002',
                'cnpj': '98.765.432/0001-10',
                'fornecedor': 'HP',
                'modelo': 'ProDesk 400',
                'status': 'Em uso',
                'patrimonio': 'PAT002',
                'valor': 2200.00,
                'marca': 'HP',
                'processador': 'Intel Core i3',
                'memoria_ram': '4GB',
                'hd_ssd': 'HDD 500GB',
                'sistema_operacional': 'Windows 10',
                'antivirus': True,
                'termo_assinado': False,
                'milvus_funcionando': False
            },
            {
                'responsavel': 'Carlos Oliveira',
                'uf': 'MG',
                'cc': 'VEN003',
                'cnpj': '11.222.333/0001-44',
                'fornecedor': 'Lenovo',
                'modelo': 'ThinkCentre M70q',
                'status': 'Disponível',
                'patrimonio': 'PAT003',
                'valor': 2800.00,
                'marca': 'Lenovo',
                'processador': 'Intel Core i7',
                'memoria_ram': '16GB',
                'hd_ssd': 'SSD 512GB',
                'sistema_operacional': 'Windows 11',
                'antivirus': False,
                'termo_assinado': True,
                'milvus_funcionando': True
            },
            {
                'responsavel': 'Ana Costa',
                'uf': 'SP',
                'cc': 'FIN004',
                'cnpj': '12.345.678/0001-90',
                'fornecedor': 'Dell',
                'modelo': 'Inspiron 3471',
                'status': 'Em uso',
                'patrimonio': 'PAT004',
                'valor': 1800.00,
                'marca': 'Dell',
                'processador': 'Intel Core i3',
                'memoria_ram': '4GB',
                'hd_ssd': 'HDD 1TB',
                'sistema_operacional': 'Windows 10',
                'antivirus': True,
                'termo_assinado': True,
                'milvus_funcionando': False
            },
            {
                'responsavel': 'Pedro Lima',
                'uf': 'RS',
                'cc': 'LOG005',
                'cnpj': '55.666.777/0001-88',
                'fornecedor': 'HP',
                'modelo': 'Elite 8300',
                'status': 'Manutenção',
                'patrimonio': 'PAT005',
                'valor': 3200.00,
                'marca': 'HP',
                'processador': 'Intel Core i7',
                'memoria_ram': '16GB',
                'hd_ssd': 'SSD 256GB',
                'sistema_operacional': 'Windows 11',
                'antivirus': True,
                'termo_assinado': False,
                'milvus_funcionando': True
            },
            {
                'responsavel': 'João Silva',
                'uf': 'SP',
                'cc': 'TI001',
                'cnpj': '12.345.678/0001-90',
                'fornecedor': 'Acer',
                'modelo': 'Veriton X2665G',
                'status': 'Em uso',
                'patrimonio': 'PAT006',
                'valor': 2100.00,
                'marca': 'Acer',
                'processador': 'Intel Core i5',
                'memoria_ram': '8GB',
                'hd_ssd': 'SSD 256GB',
                'sistema_operacional': 'Windows 10',
                'antivirus': False,
                'termo_assinado': True,
                'milvus_funcionando': False
            },
            {
                'responsavel': 'Maria Santos',
                'uf': 'RJ',
                'cc': 'ADM002',
                'cnpj': '98.765.432/0001-10',
                'fornecedor': 'Lenovo',
                'modelo': 'IdeaCentre 3',
                'status': 'Baixado',
                'patrimonio': 'PAT007',
                'valor': 1900.00,
                'marca': 'Lenovo',
                'processador': 'AMD Ryzen 5',
                'memoria_ram': '8GB',
                'hd_ssd': 'HDD 500GB',
                'sistema_operacional': 'Windows 10',
                'antivirus': True,
                'termo_assinado': False,
                'milvus_funcionando': False
            }
        ]
        
        try:
            for equipment_data in sample_equipment:
                equipment = Equipment(**equipment_data)
                equipment.add_to_history(f"Equipamento criado por {equipment_data['responsavel']}")
                db.session.add(equipment)
            
            db.session.commit()
            print(f"✓ Successfully added {len(sample_equipment)} sample equipment records")
            
            # Show dashboard stats
            stats = Equipment.get_dashboard_stats()
            print(f"Dashboard Stats:")
            print(f"  - Total equipments: {stats['total']}")
            print(f"  - In use: {stats['em_uso']}")
            print(f"  - Without antivirus: {stats['sem_antivirus']}")
            print(f"  - Without signed term: {stats['sem_termo']}")
            print(f"  - Total value: R$ {stats['valor_total']:,.2f}")
            
        except Exception as e:
            print(f"✗ Error adding sample data: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_sample_data()