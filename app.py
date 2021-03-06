from datetime import datetime
from os import abort
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
    password = sha256_crypt.hash(data["password"])

    user = User(first_name = first_name, last_name = last_name, email = email, role = role, password = password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "response": "User added"
    })

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


@cross_origin()
@app.route("/lend_book", methods = ["POST"])
def add_request():
    data = request.json

    student_id = data["student_id"]
    book_id = data["book_id"]

    stmt = select(BookRequested).where(BookRequested.book_id == book_id).where(BookRequested.student_id == student_id)
    book_already_requested = db.session.execute(stmt)
    there_is_any_book = len([a for a in book_already_requested.scalars()])

    if there_is_any_book > 0:
        return jsonify({
            "success": False,
            "response": "You already have this book"
        })

    book_requested = BookRequested(student_id = student_id, book_id = book_id, state = "borrowed")
    db.session.add(book_requested)
    db.session.commit()

    book = Book.query.get(book_id)

    if book is None:
        abort(404)
        return
    else:
        book.stock = book.stock - 1
        db.session.add(book)
        db.session.commit()

        return jsonify({
            "success": True
        })

@cross_origin()
@app.route("/get_books_requested", methods = ["POST"])
def get_books_requested():
    data = request.json

    id_user = data["id_user"]
    user = User.query.get(id_user)

    if user is None:
        abort(404)
    else:
        stmt = select(BookRequested).where(BookRequested.student_id == id_user).where(BookRequested.state == "borrowed")
        books_obj = db.session.execute(stmt)

        books = []
        for book in books_obj.scalars():
            book_obj = Book.query.get(book.book_id)
            if book_obj is not None:
                books.append({
                    "id": book_obj.id,
                    "title": book_obj.title,
                    "author": book_obj.author,
                    "genre": book_obj.genre,
                })

    return jsonify({
        "success": True,
        "books": books
    })

@cross_origin()
@app.route("/get_all_requested", methods = ["GET"])
def get_all_requested():
    stmt = select(BookRequested).where(BookRequested.state == "borrowed")
    books_objs = db.session.execute(stmt)
    books = []
    for bookR in books_objs.scalars():
        user = User.query.get(bookR.student_id)
        book = Book.query.get(bookR.book_id)
        
        dt = bookR.requested_at
        d = datetime.strftime(dt, '%Y/%m/%d')
        books.append({
            "id": bookR.id,
            "student": user.first_name + " " + user.last_name,
            "book": book.title,
            "date": d
        })
    
    return jsonify({
        "success": True,
        "books": books
    })

@cross_origin()
@app.route("/return_book", methods = ["POST"])
def return_book():
    data = request.json

    id_request = data["id_request"]
    book = data["book"]

    stmt = select(Book).where(Book.title == book)
    books_obj = db.session.execute(stmt)
    books = [a for a in books_obj.scalars()]

    # increasing book stock
    book = books[0]
    book.stock = book.stock + 1
    db.session.add(book)
    db.session.commit()

    # Changin request state to returned
    requested = BookRequested.query.get(id_request)
    requested.state = "returned"
    db.session.add(requested)
    db.session.commit()

    return jsonify({
        "success": True
    })


@cross_origin()
@app.route("/get_book_stock", methods = ["POST"])
def get_book_stock():
    data = request.json

    id_book = data["id_book"]

    book = Book.query.get(id_book)
    if book is None:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "stock": book.stock
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

class BookRequested(db.Model):
    __tablename__ = 'books_requested'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, nullable = False)
    book_id = db.Column(db.Integer, nullable = False)
    state = db.Column(db.String(255), nullable = False)
    requested_at = db.Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return "<BooksRequested %r>" % self.id
#endregion
