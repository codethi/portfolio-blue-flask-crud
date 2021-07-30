# Dica, crie um gmail especifico para essa atividade, para não compromoter a integridade do seu gmail pessoal.

#Após a criação configure os acesso em seu gmail:
   # Permitir aplicativos menos seguros (Ativar): https://myaccount.google.com/lesssecureapps
   # Desbloquear acesso os gmail: https://accounts.google.com/b/2/DisplayUnlockCaptcha
   # Ativar o acesso via IMAP: https://mail.google.com/mail/#settings/fwdandpop
# A verificação de duas etapas deve estar desativada, caso o contrário, você precisará configurar uma senha de app e colocar essa senha aqui.

# Instalar o flask_mail no terminal com o seguinte código: pip install Flask-Mail

# Instalar o flask_sqlalchemy no terminal com o seguinte código: pip install SQLAlchemy

from flask import Flask, render_template, redirect, request, session, flash
from flask_mail import Mail, Message #Importa o Mail e o Message do flask_mail para facilitar o envio de emails
from flask_sqlalchemy import SQLAlchemy # ORM responsável por realizar as operações do banco de dados via Python
#from mail_config import email, mail_senha # Módulo para esconder meu user e senha do email.

app = Flask(__name__)
app.secret_key = 'bluedtech' # Chave de criptografia para guardar sessão de login

# Configuração do envio de email.
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
   #  "MAIL_USERNAME": email,
   #  "MAIL_PASSWORD": mail_senha
}

app.config.update(mail_settings) #atualizar as configurações do app com o dicionário mail_settings
mail = Mail(app) # atribuir a class Mail o app atual.

# Conexão com o banco de dados, o nome entre os colchetes é padrão, o endereço do banco nós achamos nos Datails da instancia do nosso banco no ElephantSQL, no campo URL
# ATENÇÃO! A URL do ElephantSQL vem como postegres://(o resto da URL). 
# Modifique essa parte antes do // para postegresql://(o resto da URL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ylselsuy:NuSVipuZG7j7MolAE3CKQLgX4wqKGBGe@kesavan.db.elephantsql.com/ylselsuy'
db = SQLAlchemy(app) # Instancia o objeto db na classe SQLAlchemy e adiciona essa aplicação nela.

#--------------------------------

# Classes:

class Contato:
   def __init__ (self, nome, email, mensagem):
      self.nome = nome
      self.email = email
      self.mensagem = mensagem

class Projeto(db.Model): # Projetos herda metodos de db.Model
   # Ciração das colunas na tabela projetos:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    imagem = db.Column(db.String(500), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(300), nullable=False)
   # Construção dos atributos da classe Projeto, que receberão os dados a serem inseridos nas colunas criadas acima
    def __init__(self, nome, imagem, descricao, link):
        self.nome = nome
        self.imagem = imagem
        self.descricao = descricao
        self.link = link

#ATENÇÃO os nomes das colunas tem que ser os mesmos nomes dos atributos da classe Projeto.
#--------------------------------

# Rota principal apenas para renderizar a página principal.
@app.route('/')
def index():
   session['usuario_logado'] = None
   projetos = Projeto.query.all()  # Busca todos os projetos no banco e coloca na veriável projetos, que se transforma em uma lista.
   return render_template('index.html', projetos=projetos) # Renderiza a página index.html mandando a lista de projetos

#--------------------------------

# Rota de envio de email.
@app.route('/send', methods=['GET', 'POST'])
def send():
   if request.method == 'POST':
      # Capiturando as informações do formulário com o request do Flask e criando o objeto formContato
      formContato = Contato(
         request.form['nome'],
         request.form['email'],
         request.form['mensagem']
      )

      # Criando o objeto msg, que é uma instancia da Class Message do Flask_Mail
      msg = Message(
         subject= 'Contato do seu Portfólio', #Assunto do email
         sender=app.config.get("MAIL_USERNAME"), # Quem vai enviar o email, pega o email configurado no app (mail_settings)
         recipients=[app.config.get("MAIL_USERNAME")], # Quem vai receber o email, mando pra mim mesmo, posso mandar pra mais de um email.
         # Corpo do email.
         body=f'''O {formContato.nome} com o email {formContato.email}, te mandou a seguinte mensagem: 
         
               {formContato.mensagem}''' 
         )
      mail.send(msg) #envio efetivo do objeto msg através do método send() que vem do Flask_Mail
   return render_template('send.html', formContato=formContato) # Renderiza a página de confirmação de envio.

#--------------------------------

# Rotas do Login e ADM

@app.route('/login')
def login():
   session['usuario_logado'] = None # Desloga o usuario
   return render_template('login.html')

@app.route('/auth', methods=['GET', 'POST']) # Rota de autenticação
def auth():
   if request.form['senha'] == 'admin': # Se a senha for 'admin' faça:
      session['usuario_logado'] = 'admin' # Adiciona um usuario na sessão
      flash('Login feito com sucesso!') # Envia mensagem de sucesso
      return redirect('/adm') # Redireciona para a rota adm
   else: # Se a senha estiver errada, faça:
      flash('Erro no login, tente novamente!')  # Envia mensagem de erro
      return redirect('/login') # Redireciona para a rota login

@app.route('/logout') # Rota para deslogar
def logout():
   session['usuario_logado'] = None # Deixa o usuario_logado vazio
   return redirect('/login') # Redireciona para a rota principal (index.html)

@app.route('/adm') # Rota da administração
def adm():
   # Protegendo a rota:
   # Verifica se existe algum 'usuario_logado' na sessão ou se esse user está vazio
   if 'usuario_logado' not in session or session['usuario_logado'] == None:
      flash('Faça o login antes de entrar nessa rota!') # Mensagem de erro
      return redirect('/login') # Redireciona para o login
   projetos = Projeto.query.all() # Busca todos os projetos no banco e coloca na veriável projetos, que se transforma em uma lista.
   return render_template('adm.html', projetos=projetos) # Caso esteja logado, renderiza a página adm.html passando a lista de projetos.

#--------------------------------

# Rotas do CRUD

# CREATE
@app.route('/new', methods=['GET', 'POST'])
def new():
   if request.method == 'POST': # Verifica se o metodo recebido na requisição é POST
      # cria o objeto projeto, adiconando os campos do form nele.
      projeto = Projeto(
         request.form['nome'],
         request.form['imagem'],
         request.form['descricao'],
         request.form['link']
      )
      db.session.add(projeto) # Adiciona o objeto projeto no banco de dados.
      db.session.commit() # Confirma a operação
      flash('Projeto criado com sucesso!') # Mensagem de sucesso.
      return redirect('/adm') # Redireciona para a rota adm

# Busca por id

# Rota para buscar um id recebendo um paremetro
@app.route('/<id>')
def musica_pelo_id(id):
   projeto = Projeto.query.get(id) # Busca um projeto por id no banco e coloca em projeto.
   return render_template('adm.html', projeto=projeto) # Renderiza a página adm.html passando o projeto encontrado na query.

# UPDATE

# Rota edit que recebe um paremetro
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
   projetoEdit = Projeto.query.get(id) # Busca um projeto no banco através do id
   if request.method == "POST": # Se a requisição for um POST, faça:
      # Alteração de todos os campos de projetoEdit selecionado no get id
      projetoEdit.nome = request.form['nome']
      projetoEdit.descricao = request.form['descricao']
      projetoEdit.imagem = request.form['imagem']
      projetoEdit.link = request.form['link']
      db.session.commit() # Confirma a operação
      return redirect('/adm') #Redireciona para a rota adm
   # Renderiza a página adm.html passando o projetoEdit (projeto a ser editado)
   return render_template('adm.html', projetoEdit=projetoEdit) 

# DELETE

# Rota delete que recebe um paremetro
@app.route('/delete/<id>') 
def delete(id):
   projeto = Projeto.query.get(id) # Busca um projeto no banco através do id
   db.session.delete(projeto) # Apaga o projeto no banco de dados
   db.session.commit() # Confirma a operação
   return redirect('/adm') #Redireciona para a rota adm

if __name__ == '__main__':
   db.create_all() # Cria o banco assim que a aplicação é ligada.
   app.run(debug=True)
