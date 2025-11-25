from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import insert

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

# ПРОВЕРКА ХЕШИРОВАНИЯ ПАРОЛЕЙ!!!!
hash = generate_password_hash("MakasiHattori_18m!")
print(hash)
print(check_password_hash(hash, "MakasiHattori_18m!"))


class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    posts = db.relationship("Post", backref="theme", lazy='dynamic')


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    blogname = db.Column(db.String(50), index=True, unique=True)
    description = db.Column(db.Text)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', backref='user', lazy='dynamic')

    comments = db.relationship('Comment', backref='user', lazy='dynamic')


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

