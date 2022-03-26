from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from passlib.hash import sha256_crypt
from sqlalchemy.sql import func
from sqlalchemy import DateTime, select

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/myulibrary'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

CORS(app)

db = SQLAlchemy(app)


@cross_origin()
@app.route("/login", methods = ["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]

    stmt = select(User).where(User.email == email)
    users_obj = db.session.execute(stmt)

    users = []
    for user in users_obj.scalars():
        users.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "password_hash": user.password 
        })
    
    user = users[0]

    password_correct = sha256_crypt.verify(password, user["password_hash"])

    del user["password_hash"]
    response = {
        "success": False,
        "user": user
    }
    if (password_correct):
        response["success"] = True

    return jsonify(response)

@cross_origin()
@app.route("/get_users", methods = ["GET"])
def get_users():
    users = User.query.all()
    usersObj = []
    for user in users:
        obj = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role
        }
        usersObj.append(obj)
    
    return jsonify({
        "success": True,
        "users": usersObj
    })

@cross_origin()
@app.route("/add_user", methods = ["POST"])
def add_user():
    data = request.json

    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    role = data["role"]
    password = sha256_crypt.encrypt(data["password"])

    user = User(first_name = first_name, last_name = last_name, email = email, role = role, password = password)
    db.session.add(user)
    db.session.commit()
    
    return {
        "success": "true",
        "response": "User added"
    }

@cross_origin()
@app.route("/add_book", methods = ["POST"])
def add_book():
    data = request.json

    title = data["title"]
    author = data["author"]
    genre = data["genre"]
    stock = data["stock"]

    book = Book(title = title, author = author, genre = genre, stock = stock)
    db.session.add(book)
    db.session.commit()

    return jsonify({
        "success": True,
        "response": "Book added"
    })

@cross_origin()
@app.route("/get_genres", methods = ["GET"])
def get_genres():
    bookGenres = BookGenre.query.all()
    bookGenresObj = []
    for bookGenre in bookGenres:
        obj = {
            "id": bookGenre.id,
            "title": bookGenre.title
        }
        bookGenresObj.append(obj)
    
    return jsonify({
        "success": True,
        "genres": bookGenresObj
    })

@cross_origin()
@app.route("/get_books", methods = ["GET"])
def get_books():
    books = Book.query.all()
    booksObj = []
    for book in books:
        obj = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "stock": book.stock
        }
        booksObj.append(obj)
    
    return jsonify({
        "success": True,
        "books": booksObj
    })

#region models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(255), nullable = False)
    last_name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    role = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    def __repr__(self) -> str:
        return "<User %r>" % self.first_name

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)
    author = db.Column(db.String(255), nullable = False)
    genre = db.Column(db.String(255), nullable = False)
    stock = db.Column(db.Integer, default = 0, nullable = False)

    def __repr__(self) -> str:
        return "<Book %r>" % self.title

class BookGenre(db.Model):
    __tablename__ = 'book_genre'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)

    def __repr__(self) -> str:
        return "<BookGenre %r>" % self.title
#endregion
