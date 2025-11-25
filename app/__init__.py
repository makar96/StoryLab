from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from secret_key_generator import secret_key_generator

from bs4 import BeautifulSoup

db = SQLAlchemy()

login_manager = LoginManager()

migrate = Migrate()

SECRET_KEY = secret_key_generator.generate()


# User loader должен быть объявлен глобально
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Импорт здесь чтобы избежать циклических зависимостей

    return User.query.get(int(user_id))


def create_app():
    # Создаем экземпляр приложения Flask
    app = Flask(__name__)

    # Настройка базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # Инициализируем db (СТРОГО ДО РОУТОВ)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'  # Добавляем страницу для логина

    # Определяем функцию для извлечения первого изображения
    def extract_first_image(content):
        soup = BeautifulSoup(content, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and 'src' in img_tag.attrs:
            return img_tag['src']
        return None

    # Экспортируем функцию в глобальное пространство Jinja
    app.jinja_env.globals.update(extract_first_image=extract_first_image)

    # Инициализация логин менеджер
    login_manager.init_app(app)

    # Импортируем модели
    from app import models

    # Импортируем роуты
    from .routes import index, articles, user, create_post, edit_post, delete_post, view_post, travel_post,\
        technologies_post, search, today_posts, login_page, register, logout, redirect_to_signin, user_edit, \
        comment_add, comment_delete, comment_edit, games_post, toggle_like


    # Регистрируем маршруты
    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/articles', view_func=articles)
    app.add_url_rule('/today', view_func=today_posts)

    app.add_url_rule('/user/<int:user_id>', view_func=user)
    app.add_url_rule('/user/<int:user_id>/edit', view_func=user_edit, methods=['GET', 'POST'])

    app.add_url_rule('/create_post', view_func=create_post, methods=['GET', 'POST'])
    app.add_url_rule('/post/<int:post_id>/edit', view_func=edit_post, methods=['GET', 'POST'])
    app.add_url_rule('/post/<int:post_id>/delete', view_func=delete_post, methods=['GET', 'POST'])
    app.add_url_rule('/post/<int:post_id>', view_func=view_post)

    app.add_url_rule('/post/<int:post_id>/comment/add', view_func=comment_add, methods=['GET', 'POST'])
    app.add_url_rule('/comment/<int:comment_id>/delete', view_func=comment_delete, methods=['POST'])
    app.add_url_rule('/comment/<int:comment_id>/edit', view_func=comment_edit, methods=['GET', 'POST'])

    app.add_url_rule('/toggle_like/<int:post_id>', view_func=toggle_like, methods=['GET', 'POST'])

    app.add_url_rule('/topic/travel', view_func=travel_post)
    app.add_url_rule('/topic/technologies', view_func=technologies_post)
    app.add_url_rule('/topic/games', view_func=games_post)


    app.add_url_rule('/search/', view_func=search, methods=['GET'])
    app.add_url_rule('/login', view_func=login_page, methods=['GET', 'POST'])
    app.add_url_rule('/logout/', view_func=logout, methods=['GET', 'POST'])
    app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])

    app.after_request(redirect_to_signin)
    login_manager.user_loader(load_user)

    return app



