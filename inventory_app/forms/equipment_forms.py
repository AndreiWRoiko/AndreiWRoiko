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
    cnpj = TextAreaField('CNPJ', validators=[DataRequired()])
    
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
        self.centro_custo_id.choices = [(0, 'Selecionar')] + [
            (cc.id, f"{cc.codigo} - {cc.descricao}") 
            for cc in CentroCusto.get_all_active()
        ]
    
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