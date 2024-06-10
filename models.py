from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    senha = db.Column(db.String)

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)

class BookFacade:
    @staticmethod
    def get_all_books():
        return Book.query.all()

    @staticmethod
    def add_book(title, author, genre):
        new_book = Book(title=title, author=author, genre=genre)
        db.session.add(new_book)
        db.session.commit()

    @staticmethod
    def update_book(book_id, title, author, genre):
        book = Book.query.get(book_id)
        book.title = title
        book.author = author
        book.genre = genre
        db.session.commit()

    @staticmethod
    def delete_book(book_id):
        book = Book.query.get(book_id)
        db.session.delete(book)
        db.session.commit()

class BookNotifier:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()

class Observer:
    def update(self):
        print("New book added!")
