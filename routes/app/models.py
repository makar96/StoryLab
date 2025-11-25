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

    posts = db.relationship("Post", back_populates="theme", lazy='dynamic')

    def __repr__(self):
        return f'<Theme {self.name}>'


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    blogname = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', back_populates='user', lazy='dynamic')  # Связь "один ко многим"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_full_name(self):
        return f"{self.name} {self.surname}"


# Модель данных для поста
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с таблицей User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates='posts')

    # Связь с таблицей Theme
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))  # Пост ссылается на тему
    theme = db.relationship("Theme", back_populates="posts")

    def __repr__(self):
        # Техническое представление (для разработчиков)
        return f'<Post id={self.id} title="{self.title}">'

    def __str__(self):
        # Пользовательское представление
        return f'Пост: {self.title}'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

