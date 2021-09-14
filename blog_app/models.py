from flask_sqlalchemy import SQLAlchemy
import uuid
import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask_marshmallow import Marshmallow


ma = Marshmallow()


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True, unique=True)
    user_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    book = db.relationship('Book', backref='owner', lazy=True)
    posts = db.relationship('BlogPost', backref='author', lazy=True)

    def __init__(self, user_name, email, password, token='', id=''):
        self.id = self.set_id()
        self.user_name = user_name
        self.email = email
        self.password = self.set_password(password)
        self.token = self.get_token(24)

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash
    
    def get_token(self, length):
        return secrets.token_hex(length)


class Book(db.Model):
    id = db.Column(db.String, primary_key=True, unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    release_year = db.Column(db.String(4))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500), nullable=False)
    user_token = db.Column(db.String, db.ForeignKey('user.token'), nullable=False)

    def __init__(self, title, author, release_year, description, user_token):
        self.id = self.set_id()
        self.title = title
        self.author = author
        self.release_year = release_year
        self.description = description
        self.user_token = user_token

    def set_id(self):
        return str(uuid.uuid4())


class BlogPost(db.Model):
    id = db.Column(db.String, primary_key=True)
    post_title = db.Column(db.String(100), nullable=False)
    sub_title = db.Column(db.String(200), nullable=True)
    body = db.Column(db.String(5000), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_token = db.Column(db.String, db.ForeignKey('user.token'), nullable=False)

    def __init__(self, post_title, sub_title, body, user_token):
        self.id = self.set_id()
        self.post_title = post_title
        self.sub_title = sub_title
        self.body = body
        self.user_token = user_token
    
    def set_id(self):
        return str(uuid.uuid4())


# looking at data fetched from db & serializes 
#     to be read as dict data type when served up
class BookSchema(ma.Schema):
    class Meta:
        fields = ['id', 'title', 'author', 'release_year', 'date_created', 'description']

book_schema = BookSchema()
books_schema = BookSchema(many = True)


class BlogPostSchema(ma.Schema):
    class Meta:
        fields = ['id', 'post_title', 'sub_title', 'book_reference', 'body', 'timestamp', 'user_token']

blog_post_schema = BlogPostSchema()
blog_posts_schema = BlogPostSchema(many = True)


class UserSchema(ma.Schema):
    class Meta:
        fields = ['user_name', 'token']

user_schema = UserSchema()