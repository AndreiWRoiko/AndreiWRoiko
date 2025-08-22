from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, FloatField, SelectField, BooleanField, DateField, TextAreaField, FieldList, FormField, HiddenField
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
        ('TI001', 'TI001 - Tecnologia da Informação'),
        ('ADM001', 'ADM001 - Administrativo'),
        ('FIN001', 'FIN001 - Financeiro'),
        ('RH001', 'RH001 - Recursos Humanos'),
        ('COM001', 'COM001 - Comercial')
    ], validators=[DataRequired()])
    
    # CNPJ com opções fixas
    cnpj = SelectField('CNPJ', choices=[
        ('', 'Selecione um CNPJ...'),
        ('12.345.678/0001-90', '12.345.678/0001-90 - Matriz'),
        ('12.345.678/0002-71', '12.345.678/0002-71 - Filial São Paulo'),
        ('12.345.678/0003-52', '12.345.678/0003-52 - Filial Rio de Janeiro'),
        ('98.765.432/0001-10', '98.765.432/0001-10 - Filial Brasília'),
        ('87.654.321/0001-20', '87.654.321/0001-20 - Filial Belo Horizonte')
    ], validators=[DataRequired()])
    
    # Campo fornecedor com opções fixas
    fornecedor = SelectField('Fornecedor', choices=[
        ('', 'Selecione um fornecedor...'),
        ('Fornecedor A', 'Fornecedor A'),
        ('Fornecedor B', 'Fornecedor B'), 
        ('Fornecedor C', 'Fornecedor C'),
        ('Fornecedor D', 'Fornecedor D'),
        ('Fornecedor E', 'Fornecedor E')
    ], validators=[Optional()])
    
    modelo = StringField('Modelo', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Em uso', 'Em uso'),
        ('Disponível', 'Disponível'),
        ('Manutenção', 'Manutenção'),
        ('Baixado', 'Baixado'),
        ('Emprestado', 'Emprestado')
    ], validators=[DataRequired()])
    patrimonio = StringField('Patrimônio', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0)])
    
    # Additional fields
    marca = StringField('Marca', validators=[Optional()])
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
        ('Emprestado', 'Emprestado')
    ])
    cnpj = SelectField('CNPJ', choices=[('', 'Todos')] + [
        ('12.345.678/0001-90', '12.345.678/0001-90 - Matriz'),
        ('12.345.678/0002-71', '12.345.678/0002-71 - Filial São Paulo'),
        ('12.345.678/0003-52', '12.345.678/0003-52 - Filial Rio de Janeiro'),
        ('98.765.432/0001-10', '98.765.432/0001-10 - Filial Brasília'),
        ('87.654.321/0001-20', '87.654.321/0001-20 - Filial Belo Horizonte')
    ])
    cc = SelectField('Centro de Custo', choices=[('', 'Todos')] + [
        ('TI001', 'TI001 - Tecnologia da Informação'),
        ('ADM001', 'ADM001 - Administrativo'),
        ('FIN001', 'FIN001 - Financeiro'),
        ('RH001', 'RH001 - Recursos Humanos'),
        ('COM001', 'COM001 - Comercial')
    ])

class ImportForm(FlaskForm):
    file = FileField('Arquivo Excel', validators=[
        FileRequired(message='Por favor, selecione um arquivo'),
        FileAllowed(['xlsx', 'xls'], message='Apenas arquivos Excel (.xlsx, .xls) são permitidos')
    ])
