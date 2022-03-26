from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/myulibrary'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

CORS(app)

db = SQLAlchemy(app)

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
