import os
from secret_key_generator import secret_key_generator
from dotenv import load_dotenv
from config import *

# Загружаем переменные окружения из .env файла
load_dotenv()

# Генерация ключа
SECRET_KEY = secret_key_generator.generate()

class BaseConfig:
    #Ключ
    SECRET_KEY = os.environ.get('SECRET_KEY') == SECRET_KEY

    # Настройка базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') == 'sqlite:///blog.db'
    DEBUG = True

    ##### настройка Flask-Mail #####
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'YOU_MAIL@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'password'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME


    # Загрузка файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


