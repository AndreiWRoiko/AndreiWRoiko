"""
Equipment Forms
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, FloatField, TextAreaField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from inventory_app.models.equipment import Equipment, CentroCusto


class EquipmentForm(FlaskForm):
    """Equipment creation/editing form"""
    # Básico
    patrimonio = StringField('Patrimônio', validators=[DataRequired(), Length(max=50)])
    tipo_equipamento = SelectField('Tipo', choices=[
        ('notebook', 'Notebook'),
        ('celular', 'Celular')
    ], default='notebook')
    responsavel = StringField('Responsável', validators=[DataRequired(), Length(max=100)])
    uf = SelectField('UF', choices=[
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
        ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
    ], validators=[DataRequired()])
    centro_custo_id = SelectField('Centro de Custo', coerce=int, validators=[DataRequired()])
    cnpj = SelectField('CNPJ', choices=[
        ('', 'Selecionar CNPJ'),
        ('24.329.959/0001-33', 'ATENAS SERVIÇO DE APOIO LTDA - 24.329.959/0001-33'),
        ('15.541.957/0001-12', 'TELOS CONSULTORIA EMPRESARIAL LTDA - 15.541.957/0001-12'),
        ('14.706.283/0001-04', 'OPUS CONSULTORIA LTDA - 14.706.283/0001-04'),
        ('14.706.283/0002-87', 'OPUS CONSULTORIA LTDA - 14.706.283/0002-87'),
        ('42.537.087/0001-80', 'OPUS SERVIÇOS ESPECIALIZADOS LTDA - 42.537.087/0001-80'),
        ('49.996.326/0001-00', 'OPUS MANUTENCAO LTDA - 49.996.326/0001-00'),
        ('50.016.866/0001-69', 'OPUS LOGISTICA LTDA - 50.016.866/0001-69'),
        ('42.537.087/0002-61', 'OPUS SERVICOS ESPECIALIZADOS LTDA - 42.537.087/0002-61')
    ], validators=[Optional()], validate_choice=False)
    
    # Equipamento
    fornecedor = StringField('Fornecedor', validators=[Length(max=100)])
    marca = StringField('Marca', validators=[Length(max=50)])
    modelo = StringField('Modelo', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Status', choices=[
        ('Em uso', 'Em uso'),
        ('Disponível', 'Disponível'),
        ('Em manutenção', 'Em manutenção'),
        ('Baixado', 'Baixado')
    ], default='Em uso')
    valor = FloatField('Valor', validators=[Optional(), NumberRange(min=0)])
    
    # Especificações técnicas
    processador = StringField('Processador', validators=[Length(max=100)])
    memoria_ram = StringField('Memória RAM', validators=[Length(max=20)])
    hd_ssd = StringField('HD/SSD', validators=[Length(max=50)])
    sistema_operacional = StringField('Sistema Operacional', validators=[Length(max=50)])
    licenca_microsoft = StringField('Licença Microsoft', validators=[Length(max=50)])
    
    # Campos específicos para celulares
    imei = StringField('IMEI', validators=[Length(max=20)])
    linha_telefonica = StringField('Linha Telefônica', validators=[Length(max=20)])
    sistema_operacional_celular = SelectField('Sistema Operacional', choices=[
        ('', 'Selecionar'),
        ('Android', 'Android'),
        ('iOS', 'iOS')
    ])
    
    # Controles
    antivirus = BooleanField('Antivírus Instalado')
    termo_assinado = BooleanField('Termo Assinado')
    milvus_funcionando = BooleanField('Milvus Funcionando')
    
    # Datas
    data_aquisicao = DateField('Data de Aquisição', validators=[Optional()])
    data_baixa = DateField('Data de Baixa', validators=[Optional()])
    
    # Contato
    endereco = TextAreaField('Endereço', validators=[Length(max=200)])
    telefone = StringField('Telefone', validators=[Length(max=20)])
    email = StringField('Email', validators=[Length(max=100)])
    link_termos = TextAreaField('Link dos Termos', validators=[Length(max=500)])
    
    submit = SubmitField('Salvar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate centro_custo choices
        centros = CentroCusto.get_all_active()
        if centros:
            self.centro_custo_id.choices = [
                (cc.id, f"{cc.codigo} - {cc.descricao}") 
                for cc in centros
            ]
        else:
            # If no cost centers exist, make it optional
            self.centro_custo_id.choices = [(0, 'Nenhum centro de custo cadastrado')]
            self.centro_custo_id.validators = [Optional()]
        
        # Handle legacy CNPJ values when editing existing equipment
        obj = kwargs.get('obj')
        if obj and hasattr(obj, 'cnpj') and obj.cnpj:
            # Get the list of predefined CNPJ values
            predefined_cnpjs = [choice[0] for choice in self.cnpj.choices]
            # If the equipment's CNPJ is not in the predefined list, add it
            if obj.cnpj not in predefined_cnpjs:
                self.cnpj.choices.append((obj.cnpj, f'{obj.cnpj} (Legado)'))

    
    def validate_patrimonio(self, patrimonio):
        """Validate patrimonio uniqueness"""
        equipment = Equipment.query.filter_by(patrimonio=patrimonio.data).first()
        if equipment and (not hasattr(self, 'equipment_id') or equipment.id != getattr(self, 'equipment_id', None)):
            raise ValidationError('Número de patrimônio já existe no sistema.')


class EquipmentSearchForm(FlaskForm):
    """Equipment search form"""
    query = StringField('Buscar', validators=[Length(max=100)])
    uf = SelectField('UF', choices=[('', 'Todos')] + [
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'),
        ('BA', 'BA'), ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'),
        ('GO', 'GO'), ('MA', 'MA'), ('MT', 'MT'), ('MS', 'MS'),
        ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'), ('PR', 'PR'),
        ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'),
        ('SP', 'SP'), ('SE', 'SE'), ('TO', 'TO')
    ])
    status = SelectField('Status', choices=[('', 'Todos')] + [
        ('Em uso', 'Em uso'),
        ('Disponível', 'Disponível'),
        ('Em manutenção', 'Em manutenção'),
        ('Baixado', 'Baixado')
    ])
    tipo_equipamento = SelectField('Tipo', choices=[('', 'Todos')] + [
        ('notebook', 'Notebook'),
        ('celular', 'Celular')
    ])
    centro_custo_id = SelectField('Centro de Custo', coerce=int)
    antivirus = SelectField('Antivírus', choices=[('', 'Todos'), ('1', 'Com Antivírus'), ('0', 'Sem Antivírus')])
    termo_assinado = SelectField('Termo', choices=[('', 'Todos'), ('1', 'Termo Assinado'), ('0', 'Termo Não Assinado')])
    submit = SubmitField('Buscar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate centro_custo choices
        self.centro_custo_id.choices = [(0, 'Todos')] + [
            (cc.id, f"{cc.codigo} - {cc.descricao}") 
            for cc in CentroCusto.get_all_active()
        ]


class ImportForm(FlaskForm):
    """Equipment import form"""
    file = FileField('Arquivo Excel', validators=[
        DataRequired('Selecione um arquivo Excel'),
        FileAllowed(['xlsx', 'xls'], 'Apenas arquivos Excel (.xlsx, .xls) são permitidos')
    ])
    submit = SubmitField('Importar')