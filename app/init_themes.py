# Скрипт для создания начальных тем
from app import db
from app.models import Theme


def init_themes():
    # """Функция для добавления тем в базу данных"""
    themes_data = [
        'путешествия', 'технологии', 'наука', 'развлечения',
        'искусство', 'спорт', 'гейминг', 'аниме',
        'образование', 'здоровье', 'авто', 'новости']

    # Добавляем темы
    for theme_name in themes_data:
        theme = Theme(name=theme_name)
        db.session.add(theme)

    try:
        db.session.commit()
        print("Темы успешно добавлены в базу данных")
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении тем: {e}")

