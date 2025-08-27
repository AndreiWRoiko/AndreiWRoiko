from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, FloatField, SelectField, BooleanField, DateField, TextAreaField, FieldList, FormField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, URL, Length
from datetime import date

def get_centro_custo_choices():
    """Função para carregar dinamicamente os centros de custo"""
    try:
        from models import CentroCusto
        centros = CentroCusto.get_all_active()
        choices = [('', 'Selecione um centro de custo...')]
        choices.extend([(str(c.id), f"{c.codigo} - {c.descricao}") for c in centros])
        return choices
    except:
        return [('', 'Selecione um centro de custo...')]

def coerce_int_or_none(value):
    """Coerce to int or None for required fields"""
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def coerce_int_or_empty(value):
    """Coerce to int or empty string for optional fields"""
    if value == '' or value is None:
        return ''
    try:
        return int(value)
    except (ValueError, TypeError):
        return ''

class EquipmentForm(FlaskForm):
    responsavel = StringField('Responsável', validators=[DataRequired()])
    uf = SelectField('UF', choices=[
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
        ('SE', 'SE'), ('TO', 'TO')
    ], validators=[DataRequired()])
    # Centro de Custo dinâmico
    centro_custo_id = SelectField('Centro de Custo', coerce=coerce_int_or_none, validators=[DataRequired()])
    
    # CNPJ com opções fixas
    cnpj = SelectField('CNPJ', choices=[
        ('', 'Selecione um CNPJ...'),
        ('24.329.959/0001-33', '24.329.959/0001-33 ATENAS SERVIÇO DE APOIO LTDA - CNPJ'),
        ('15.541.957/0001-12', '15.541.957/0001-12 TELOS CONSULTORIA EMPRESARIAL LTDA - CNPJ'),
        ('14.706.283/0001-04', '14.706.283/0001-04 - OPUS CONSULTORIA LTDA - CNPJ'),
        ('14.706.283/0002-87', '14.706.283/0002-87 - OPUS CONSULTORIA LTDA - CNPJ'),
        ('49.996.326/0001-00', '49.996.326/0001-00 - OPUS MANUTENCAO LTDA - CNPJ'),
        ('50.016.866/0001-69', '50.016.866/0001-69 - OPUS LOGISTICA LTDA - CNPJ'),
        ('42.537.087/0002-61', ' 42.537.087/0002-61 - OPUS SERVICOS ESPECIALIZADOS LTDA - CNPJ'),
        ('42.537.087/0001-80', '42.537.087/0001-80 - OPUS SERVIÇOS ESPECIALIZADOS LTDA - CNPJ')
    ], validators=[DataRequired()])
    
    # Campo fornecedor com opções fixas
    fornecedor = SelectField('Fornecedor', choices=[
        ('', 'Selecione um fornecedor...'),
        ('MAGNA', 'MAGNA'),
        ('OPUS', 'OPUS'), 
        ('STELANISS', 'STELANISS'),
        ('ALLU', 'ALLU'),
        ('ONLY', 'ONLY')
    ], validators=[Optional()])
    
    modelo = StringField('Modelo', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Em uso', 'Em uso'),
        ('Disponível', 'Disponível'),
        ('Manutenção', 'Manutenção'),
        ('Baixado', 'Baixado'),
        ('Roubado', 'Roubado'),
        ('Emprestado', 'Emprestado')
    ], validators=[DataRequired()])
    patrimonio = StringField('Patrimônio', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0)])
    
    # Additional fields
    marca = SelectField('Segmento', choices=[
        ('Acelera', 'Acelera'),
        ('Adm', 'Adm'),
        ('Atenas', 'Atenas'),
        ('Engenharia', 'Engenharia'),
        ('Facilities', 'Facilities'),
        ('Industrial', 'Industrial'),
        ('Mobilidade', 'Mobilidade'),
        ('Telos', 'Telos')
    ],validators=[Optional()])
    
    processador = StringField('Processador', validators=[Optional()])
    memoria_ram = StringField('Memória RAM', validators=[Optional()])
    hd_ssd = StringField('HD/SSD', validators=[Optional()])
    sistema_operacional = SelectField('Sistema Operacional', choices=[
        ('', 'Selecione...'),
        ('Windows 10', 'Windows 10'),
        ('Windows 11', 'Windows 11'),
        ('Ubuntu', 'Ubuntu'),
        ('macOS', 'macOS'),
        ('Outro', 'Outro')
    ], validators=[Optional()])
    licenca_microsoft = SelectField('Licença Microsoft', choices=[
        ('', 'Selecione...'),
        ('Microsoft 365 Basic', 'Microsoft 365 Basic'),
        ('Microsoft 365 Standard', 'Microsoft 365 Standard')
    ], validators=[Optional()])
    
    antivirus = BooleanField('Antivírus Instalado')
    termo_assinado = BooleanField('Termo de Responsabilidade Assinado')
    milvus_funcionando = BooleanField('Milvus Funcionando')
    
    data_aquisicao = DateField('Data de Aquisição', validators=[Optional()])
    data_baixa = DateField('Data de Baixa', validators=[Optional()])
    
    endereco = TextAreaField('Endereço', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    
    # Novo campo para link dos termos
    link_termos = StringField('Link dos Termos Assinados', validators=[Optional(), URL()], 
                             render_kw={'placeholder': 'https://exemplo.com/termo-assinado'})
    
    # Campo senha
    senha = StringField('Senha', validators=[Optional()], 
                       render_kw={'placeholder': 'Digite a senha'})

class SearchForm(FlaskForm):
    search_term = StringField('Buscar')
    uf = SelectField('UF', choices=[('', 'Todos')] + [
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
        ('SE', 'SE'), ('TO', 'TO')
    ])
    status = SelectField('Status', choices=[
        ('', 'Todos'),
        ('Em uso', 'Em uso'),
        ('Disponível', 'Disponível'),
        ('Manutenção', 'Manutenção'),
        ('Baixado', 'Baixado'),
        ('Roubado', 'Roubado'),
        ('Emprestado', 'Emprestado')
    ])
    cnpj = SelectField('CNPJ', choices=[('', 'Todos')] + [
        ('24.329.959/0001-33', '24.329.959/0001-33 ATENAS SERVIÇO DE APOIO LTDA - CNPJ'),
        ('15.541.957/0001-12', '15.541.957/0001-12 TELOS CONSULTORIA EMPRESARIAL LTDA - CNPJ'),
        ('14.706.283/0001-04', '14.706.283/0001-04 - OPUS CONSULTORIA LTDA - CNPJ'),
        ('14.706.283/0002-87', '14.706.283/0002-87 - OPUS CONSULTORIA LTDA - CNPJ'),
        ('49.996.326/0001-00', '49.996.326/0001-00 - OPUS MANUTENCAO LTDA - CNPJ'),
        ('50.016.866/0001-69', '50.016.866/0001-69 - OPUS LOGISTICA LTDA - CNPJ'),
        ('42.537.087/0002-61', ' 42.537.087/0002-61 - OPUS SERVICOS ESPECIALIZADOS LTDA - CNPJ'),
        ('42.537.087/0001-80', '42.537.087/0001-80 - OPUS SERVIÇOS ESPECIALIZADOS LTDA - CNPJ')
    ])

    marca = SelectField('Segmento', choices=[('','Todos')] + [
        ('Acelera', 'Acelera'),
        ('Adm', 'Adm'),
        ('Atenas', 'Atenas'),
        ('Engenharia', 'Engenharia'),
        ('Facilities', 'Facilities'),
        ('Industrial', 'Industrial'),
        ('Mobilidade', 'Mobilidade'),
        ('Telos', 'Telos')
    ])

    cc = SelectField('Centro de Custo', coerce=coerce_int_or_empty)

class CentroCustoForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Ex: TI001"})
    descricao = StringField('Descrição', validators=[DataRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Ex: Tecnologia da Informação"})

class ImportForm(FlaskForm):
    file = FileField('Arquivo Excel', validators=[
        FileRequired(message='Por favor, selecione um arquivo'),
        FileAllowed(['xlsx', 'xls'], message='Apenas arquivos Excel (.xlsx, .xls) são permitidos')
    ])

class KanbanListForm(FlaskForm):
    name = StringField('Nome da Lista', validators=[DataRequired(), Length(min=1, max=100)])
    color = StringField('Cor', validators=[Optional()], render_kw={'type': 'color', 'value': '#6c757d'})

class KanbanTaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Descrição', validators=[Optional()])
    priority = SelectField('Prioridade', choices=[
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta')
    ], default='medium')
    due_date = DateField('Data de Vencimento', validators=[Optional()])
    list_id = SelectField('Lista', coerce=int)
