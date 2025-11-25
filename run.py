from app import create_app, db
import os
from app.init_themes import *



# Создаем экземпляр приложения
app = create_app()
with app.app_context():
    init_themes()

with app.app_context():
    db.create_all()
    print("Таблицы созданы!")

if __name__ == '__main__':
    # ★★★ ВСЯ КОНФИГУРАЦИЯ ЗАПУСКА В ОДНОМ МЕСТЕ ★★★
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host='0.0.0.0', port=port, debug=True)