from datetime import datetime, date

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import cast, Date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from datetime import timedelta
from sqlalchemy import func

from bs4 import BeautifulSoup # Для преобразования html в чистый текст

from app import db

from .models import Post, Theme, User, Comment, Like  # ★★★ ЯВНЫЙ ИМПОРТ НУЖНЫХ МОДЕЛЕЙ ★★★


today_start = datetime.combine(date.today(), datetime.min.time())

# Очистка html-тегов для отображения чистого текста
def strip_html_tags(html_text):
    soup = BeautifulSoup(html_text, features="html.parser")
    stripped_text = soup.get_text()
    return stripped_text.strip()

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

        # Подсчет сегодняшних постов
        posts_today = len([post for post in posts if post.created_at >= today_start])

        # Получаем 3 последних поста для sticky container
        latest_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()

        print(f"Найдено постов: {len(posts)}")
        print(f"Последние 3 поста: {len(latest_posts)}")

        # Передаем обе переменные в шаблон
        return render_template('home.html', posts=posts, latest_posts=latest_posts, all_posts=all_posts, posts_today=posts_today, Comment=Comment, Like=Like)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Маршрут со всеми постами
def articles():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())
        posts_today = len([post for post in posts if post.created_at >= today_start])
        # Подсчет сегодняшних постов
        posts_today = len([post for post in posts if post.created_at >= today_start])
        print(f"Найдено постов: {len(posts)}")
        return render_template('all_posts.html', posts=posts, all_posts=all_posts, posts_today=posts_today, Comment=Comment, Like=Like)
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

def user(user_id=None):

    # Вызывать по умолчанию текущего пользователя
    if user_id is None:
        user_id = current_user.id
    try:
        user = User.query.get_or_404(user_id)

        # Получение постов из бд
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.user_id == user_id).all()

        # Подсчет сегодняшних постов
        posts_today = len([post for post in posts if post.created_at >= today_start])

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        print(f"Найдено постов: {len(posts)}")  # Для отладки
        return render_template('user.html', posts=posts, all_posts=all_posts, user=user, user_name=user.name, user_surname=user.surname, user_blogname=user.blogname, user_description=user.description, posts_today=posts_today, Comment=Comment, Like=Like)
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
            user.blogname = request.form['blogname']
            user.description = request.form['description']

            # ДОБАВИТЬ ПРОВЕРКУ УНИКАЛЬНОСТИ EMAIL!!!

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
    user_id = Post.user_id

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

    if post.user_id != current_user.id:
        print(f"Post.user_id = {post.user_id}")
        print(f"current_user.id = {current_user.id}")
        abort(403)

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

        clean_content = strip_html_tags(post.content) #Чтобы выводить нормальный текст, а не html

        num_comments = Comment.query.filter_by(post_id=post_id).count()

        # comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        comments = Comment.query.filter_by(post_id=post_id).order_by(desc(Comment.created_at)).all()

        return render_template('post.html', post=post, clean_content=clean_content, all_posts=all_posts, comments=comments, num_comments=num_comments, Like=Like)
    except Exception as e:
        print(f"Ошибка при просмотре поста: {e}")
        return f"Ошибка: {e}"


# Путешествия
def travel_post():
    try:
        # Получаем все посты для основной страницы
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.theme_id == '1').all()

        # Подсчет всех постов (для хейдера)
        all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

        print(f"Найдено постов: {len(posts)}")

        # Передаем обе переменные в шаблон
        return render_template('travel.html', posts=posts, all_posts=all_posts, Comment=Comment)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Технологии
def technologies_post():
    try:
        # Получаем все посты для основной страницы
        # posts = Post.query.order_by(Post.created_at.desc()).all()
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.theme_id == '2').all()
        print(f"Найдено постов: {len(posts)}")

        # Передаем обе переменные в шаблон
        return render_template('technologies.html', posts=posts, Comment=Comment)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Игры
def games_post():
    try:
        # Получаем все посты для основной страницы
        # posts = Post.query.order_by(Post.created_at.desc()).all()
        posts = Post.query.order_by(Post.created_at.desc()).filter(Post.theme_id == '7').all()
        print(f"Найдено постов: {len(posts)}")

        # Передаем обе переменные в шаблон
        return render_template('games.html', posts=posts, Comment=Comment)

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        return f"Ошибка: {e}"


# Модель поиска
def search():

    query = request.args.get("query")
    if query:
        try:
            #Получение всех постов по post.content
            # ВАЖНО!!! ПРИ ПЕРЕХОДЕ НА POSTGRESQL ВЕРНУТЬ ОБРАТНО ИСПОЛЬЗОВАНИЕ ILIKE!!!
            # results = Post.query.filter(
            #     db.or_(
            #         Post.title.ilike(f"%{query}%"),
            #         Post.content.ilike(f"%{query}%")
            #     )
            # ).order_by(Post.created_at.desc()).all()

            # Регистронезависимый поиск с преобразованием строки в нижний регистр
            results = Post.query.filter(
                db.or_(
                    func.lower(Post.title).contains(func.lower(query)),
                    func.lower(Post.content).contains(func.lower(query))
                )
            ).order_by(Post.created_at.desc()).all()

            # Подсчет всех постов (для хейдера)
            all_posts = len(Post.query.order_by(Post.created_at.desc()).all())

            print(f"Найдено постов по поиску: {len(results)}")

        except Exception as e:
            print(f"Ошибка при поиске постов: {e}")
            return f"Ошибка: {e}"
    return render_template('search.html', results=results,  all_posts=all_posts, Comment=Comment)

@login_required
def comment_add(post_id):

    post = Post.query.get_or_404(post_id)

    print(f"Received POST request for post_id: {post_id}")
    print(f"User authenticated: {current_user.is_authenticated}")

    # Проверка аутентификации
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Получение текста из формы
            text = request.form['text'].strip()

            # Проверяем заполненность комментария
            if not text:
                flash('Комментарий не может быть пустым', 'error')
                return render_template('post.html', post=post)

            # Создаем комментарий
            new_comment = Comment(text=text, post_id=post_id, author_id=current_user.id)

            # Добавление в базу данных
            db.session.add(new_comment)
            db.session.commit()

            return redirect(url_for('view_post', post_id=post.id))

        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании комментария: {e}")
            flash('Возникла ошибка при сохранении комментария.', category='danger')
    else:
        return render_template('post.html', post_id=post_id)


# Удаление комментария
@login_required
def comment_delete(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    # Проверяем, является ли текущий пользователь автором комментария
    if current_user.id != comment.author_id:
        return redirect(url_for('view_post', post_id=comment.post_id))

    post_id = comment.post_id

    try:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))

    except Exception as e:
        print(f"При удалении записи произошла ошибка: {e}")
        db.session.rollback()
        return redirect(url_for('view_post', post_id=post_id))


# Редактирование комментария
@login_required
def comment_edit(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    post_id = comment.post_id

    if comment.author_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        new_text = request.form.get('text', '').strip()
        print(f"Получен текст: '{new_text}'")

        # Обновление комментария
        comment.text = new_text

        try:
            db.session.commit()
            print('Комментарий обновлен', 'success')
        except Exception as e:
            db.session.rollback()
            print(f'Ошибка при обновлении: {e}', 'error')

        except Exception as e:
            db.session.rollback()
            return f"Ошибка {e}"

        return redirect(url_for('view_post', post_id=comment.post_id))

    return redirect(url_for('view_post', post_id=comment.post_id))

# Добавление и удаление лайка
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)

    # Проверка, не поставил ли пользователь уже лайк
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing_like:
        # Удаляем лайк
        db.session.delete(existing_like)
        db.session.commit()

    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
    # return redirect(request.referrer or url_for('home'))
    return redirect(f"{request.referrer}#post-{post_id}")



