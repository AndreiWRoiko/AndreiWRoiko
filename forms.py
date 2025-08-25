from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, FloatField, SelectField, BooleanField, DateField, TextAreaField, FieldList, FormField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, URL
from datetime import date

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
    # Centro de Custo com opções fixas
    cc = SelectField('Centro de Custo', choices=[
        ('', 'Selecione um centro de custo...'),
        ('830000', '830000 - VALLOUREC JECEABA - 1'),
        ('420101', '420101 -  OPUS - PR - PIC'),
        ('620021', '620021 -  TELOS CONSULTORIA -PR- MERCADO LIVRE LONDRINA TEMPORARIOS'),
        ('98', '98 - ACELERA IT'),
        ('980001', '980001 - ACELERA IT - ADMINISTRATIVO'),
        ('980003', '980003 - ACELERA IT - AGITA AI'),
        ('980002', '980002 - ACELERA IT - COMERCIAL'),
        ('300001', '300001 - ADMINISTRACAO COMERCIAL'),
        ('20', '20 - ADMINISTRATIVO'),
        ('500000', '500000 - ADMINISTRATIVO ENGENHARIA'),
        ('89', '89 - ATENAS'),
        ('890012', '890012 - ATENAS -  SUP FED AGRICULTURA ESTADO RS'),
        ('890001', '890001 - ATENAS - ADMINISTRATIVO'),
        ('98', '98 - ACELERA IT')
    ], validators=[DataRequired()])
    
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

    cc = SelectField('Centro de Custo', choices=[('', 'Todos')] + [
        ('830000', '830000 - VALLOUREC JECEABA - 1'),
        ('420101', '420101 -  OPUS - PR - PIC'),
        ('620021', '620021 -  TELOS CONSULTORIA -PR- MERCADO LIVRE LONDRINA TEMPORARIOS'),
        ('98', '98 - ACELERA IT'),
        ('980001', '980001 - ACELERA IT - ADMINISTRATIVO'),
        ('980003', '980003 - ACELERA IT - AGITA AI'),
        ('980002', '980002 - ACELERA IT - COMERCIAL'),
        ('300001', '300001 - ADMINISTRACAO COMERCIAL'),
        ('20', '20 - ADMINISTRATIVO'),
        ('500000', '500000 - ADMINISTRATIVO ENGENHARIA'),
        ('89', '89 - ATENAS'),
        ('890012', '890012 - ATENAS -  SUP FED AGRICULTURA ESTADO RS'),
        ('890001', '890001 - ATENAS - ADMINISTRATIVO'),
        ('98', '98 - ACELERA IT')
    ])

class ImportForm(FlaskForm):
    file = FileField('Arquivo Excel', validators=[
        FileRequired(message='Por favor, selecione um arquivo'),
        FileAllowed(['xlsx', 'xls'], message='Apenas arquivos Excel (.xlsx, .xls) são permitidos')
    ])
