from datetime import datetime, date

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import cast, Date
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from .models import Post, Theme, User  # ★★★ ЯВНЫЙ ИМПОРТ НУЖНЫХ МОДЕЛЕЙ ★★★


today_start = datetime.combine(date.today(), datetime.min.time())

# Маршруты приложения


# Маршрут логина
def login_page():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):  #Первый парол из бд, а второй который получили снаружи \
                # user and check... нужен чтобы проверка была только если пользователь действительно найден
                login_user(user)

            # # После авторизации юзера нужно перенаправить
            #     next_page = request.args.get('next')
            #     if next_page:
            #         return redirect(next_page)

                return redirect(url_for('user', user_id=current_user.id))
            else:
                flash("Данные введены не верно")
        else:
            flash("Пожалуйста, заполните эту форму, чтобы войти в учетную запись.")

    return render_template("login.html", title="Авторизация")


# Маршрут для логаута
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for('login_page'))


# Перенаправление на страницу регистрации, если юзер стучится туда, куда нет доступа
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


# Маршрут регистрации
def register():

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        # Проверка на существующего пользователя
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Пользователь с таким email уже существует")
            return render_template("register.html", title="Регистрация")

        # Добавление пользователя в бд и проверка полей
        if not all([name, surname, email, password, password2]):
            flash("Пожалуйста, заполните все поля")
        elif password != password2:
            flash("Пароли не совпадают")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(name=name, surname=surname, email=email, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            # Перенаправление на страницу авторизации (ну а хули он?)
            return redirect(url_for('login_page'))

    return render_template("register.html", title="Регистрация")


def index():
    try:

        # Получаем все посты для основной страницы
        posts = Post.query.order_by(Post.created_at.desc()).all()

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        # Подсчет сегодняшних постов (НЕ РАБОТАЕТ, НАЙТИ РЕШЕНИЕ!!!)
        posts_today = len([post for post in posts if post.created_at >= today_start])

        # Получаем 3 последних поста для sticky container
        latest_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()

        print(f"Найдено постов: {len(posts)}")
        print(f"Последние 3 поста: {len(latest_posts)}")

        # Передаем обе переменные в шаблон
        return render_template('home.html', posts=posts, latest_posts=latest_posts, all_posts=all_posts, posts_today=posts_today)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Маршрут со всеми постами
def articles():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())
        posts_today = len([post for post in posts if post.created_at >= today_start])
        print(f"Найдено постов: {len(posts)}")
        return render_template('all_posts.html', posts=posts, all_posts=all_posts)
    except Exception as e:
        print(f"Ошибка при запросе на все посты: {e}")
        return f"Ошибка: {e}"


# Посты за текущий день
def today_posts():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())
        posts_today_len = len([post for post in posts if post.created_at >= today_start])
        today = date.today()
        posts_today = Post.query.filter(
            cast(Post.created_at, Date) == today
        ).count()
        print(f"Найдено постов: {len(posts)}")
        return render_template('today_posts.html', posts=posts, all_posts=all_posts, posts_today=posts_today)
    except Exception as e:
        print(f"Ошибка при запросе на все посты: {e}")
        return f"Ошибка: {e}"


# Страница юзера
# login_required нужен, чтобы на эту страницу мог попасть только авторизованный юзер
@login_required
def user(user_id=None):
    # Вызывать по умолчанию текущего пользователя
    if user_id is None:
        user_id = current_user.id
    try:
        user = User.query.get_or_404(user_id)
        # Получение постов из бд
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.user_id == user_id).all()

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        print(f"Найдено постов: {len(posts)}")  # Для отладки
        return render_template('user.html', posts=posts, all_posts=all_posts)
    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"



# Редактирование юзера
@login_required
def user_edit(user_id):

    user = User.query.get_or_404(user_id)
    print(f'===={request.headers}====')
    # Проверяем, что пользователь редактирует свой профиль
    if user.id != current_user.id:
        abort(403)

    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.surname = request.form['surname']
            user.email = request.form['email']

             # Валидация обязательных полей
            # if not name or not email:
            #     return render_template('user_edit.html', user=user, 
            #                          error="Имя и email обязательны для заполнения")
            
            # ДОБАВИТЬ ПРОВЕРКУ УНИКАЛЬНОСТИ EMAIL!!!

        # Добавить после миграции
        # user.description = request.form['description']
        # user.blogname = int(request.form['blogname'])

            db.session.commit()
            # flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('user', user_id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'error')

    return render_template('user_edit.html', user=user)


# Создание поста
@login_required
def create_post():
    # Получение всех тем для выпадающего списка
    themes = Theme.query.all()

    if request.method == 'POST':
        try:
            # Получение данных из формы
            title = request.form['title']
            content = request.form['content']
            theme_id = request.form['theme'] # Получение ID темы


            # Валидация данных
            if not title or not content or not theme_id:
                return "Все поля обязательны для заполнения", 400

            # Проверка существования темы
            theme = Theme.query.get(theme_id)
            if not theme:
                return "Выбранная тема не существует", 400

            # Создание нового поста
            # current_user нужен, чтобы создавать посты от текущего пользователя
            new_post = Post(title=title, content=content, theme_id=theme_id, user_id=current_user.id)

            # Добавление в базу данных
            db.session.add(new_post)
            db.session.commit()

            print(f"Создан новый пост: {title}")  # Отладка

            return redirect(url_for('user', user_id=current_user.id))
        except Exception as e:
            print(f"Ошибка при создании поста: {e}")
            return f"Ошибка: {e}"

    return render_template('create.html', themes=themes)


# Редактирование записи
@login_required
def edit_post(post_id):


    post = Post.query.get_or_404(post_id)
    themes = Theme.query.all()
    # if Post.user.id != current_user.id:
    #     abort(403)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.theme_id = int(request.form['theme'])

        try:
            db.session.commit()
            return redirect(url_for('user', user_id=current_user.id))

        except Exception as e:
            return f"Ошибка {e}"
    else:

        post = Post.query.get(post_id)
        return render_template('edit_post.html', post=post, themes=themes)


# Удаление записи
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('user', user_id=current_user.id))

    except Exception as e:
        print(f"При удалении записи произошла ошибка: {e}")


# Просмотр конкретного поста
def view_post(post_id):
    try:
        post = Post.query.options(db.joinedload(Post.theme)).get_or_404(post_id)

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        return render_template('post.html', post=post, all_posts=all_posts)
    except Exception as e:
        print(f"Ошибка при просмотре поста: {e}")
        return f"Ошибка: {e}"


# Путешествия
def travel_post():
    try:
        # Получаем все посты для основной страницы
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.theme_id == '5').all()

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        print(f"Найдено постов: {len(posts)}")

        # Передаем обе переменные в шаблон
        return render_template('travel.html', posts=posts, all_posts=all_posts)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Технологии
def technologies_post():
    try:
        # Получаем все посты для основной страницы
        # posts = Post.query.order_by(Post.created_at.desc()).all()
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.theme_id == '1').all()
        print(f"Найдено постов: {len(posts)}")

        # Передаем обе переменные в шаблон
        return render_template('technologies.html', posts=posts)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Модель поиска
def search():

    query = request.args.get("query")
    if query:
        try:
            #Получение всех постов по post.content
            results = Post.query.filter(
                db.or_(
                    Post.title.ilike(f"%{query}%"),
                    Post.content.ilike(f"%{query}%")
                )
            ).order_by(Post.created_at.desc()).all()

            # Подсчет всех постов (для хейдера)
            all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

            print(f"Найдено постов по поиску: {len(results)}")

        except Exception as e:
            print(f"Ошибка при поиске постов: {e}")
            return f"Ошибка: {e}"
    return render_template('search.html', results=results,  all_posts=all_posts)
