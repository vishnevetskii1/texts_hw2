from database import init_db, get_db
from models import Channel

def add_test_data():
    """Добавление тестовых данных"""
    init_db()
    db = next(get_db())
    
    # Тестовые каналы (замените на реальные)
    test_channels = [
        {
            "telegram_id": -1001234567890, 
            "username": "test_news_channel", 
            "title": "Тестовый новостной канал", 
            "is_public": True
        },
        {
            "telegram_id": -1001234567891, 
            "username": "tech_updates", 
            "title": "Технологические обновления", 
            "is_public": True
        },
    ]
    
    added = 0
    for data in test_channels:
        # Проверяем, существует ли уже канал
        existing = db.query(Channel).filter(
            (Channel.telegram_id == data["telegram_id"]) | 
            (Channel.username == data["username"])
        ).first()
        
        if not existing:
            channel = Channel(**data)
            db.add(channel)
            print(f"✅ Добавлен канал: {data['title']} (@{data['username']})")
            added += 1
        else:
            print(f"ℹ️ Канал уже существует: {data['title']}")
    
    db.commit()
    print(f"\n🎉 Добавлено {added} новых каналов")
    print("💡 Не забудьте добавить юзер-бота в эти каналы!")

if __name__ == "__main__":
    add_test_data()