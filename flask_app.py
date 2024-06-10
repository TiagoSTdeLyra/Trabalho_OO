from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Usuario, BookFacade, BookNotifier, Observer
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minhabase.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.app_context().push()

UPLOAD_FOLDER = '/home/TiagoLyra/mysite/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Observer setup
notifier = BookNotifier()
observer = Observer()
notifier.attach(observer)

def verificar_credenciais(nome, senha):
    usuario = Usuario.query.filter_by(nome=nome).first()
    if usuario and usuario.senha == senha:
        return True
    return False

@app.route('/area_vip', methods=['GET', 'POST'])
def area_vip():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'add_book' in request.form:
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            BookFacade.add_book(title, author, genre)
            notifier.notify()
        elif 'edit_book' in request.form:
            book_id = request.form['book_id']
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            BookFacade.update_book(book_id, title, author, genre)
        elif 'delete_book' in request.form:
            book_id = request.form['book_id']
            BookFacade.delete_book(book_id)
    
    books = BookFacade.get_all_books()
    return render_template('area_vip.html', username=session['username'], books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['username']
        senha = request.form['password']
        if verificar_credenciais(nome, senha):
            session['username'] = request.form['username']
            logging.info("Login bem-sucedido, redirecionando para a área vip...")
            return redirect(url_for('area_vip'))
        logging.info("Credenciais inválidas, voltando para o login.")
        return 'Usuário ou senha errados, tente novamente'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['username']
        senha = request.form['password']
        if Usuario.query.filter_by(nome=nome).first():
            logging.info("Usuário já existe")
            return 'Usuário já existe'
        try:
            user = Usuario(nome, senha)
            db.session.add(user)
            db.session.commit()
            logging.info("Usuário registrado com sucesso, redirecionando para o login...")
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Erro ao registrar usuário: {e}")
            return 'Erro ao registrar usuário'
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    logging.info("Usuário desconectado, redirecionando para a página inicial.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    books = BookFacade.get_all_books()
    return render_template('index.html', books=books)

if __name__ == "__main__":
    with app.app_context():
        logging.info("Creating all database tables.")
        db.create_all()
        logging.info("All database tables created successfully.")
    app.run(debug=True)
