import asyncio
from pyrogram import Client
from database import init_db, get_db
from models import Channel
from config import Config

async def add_real_channels_to_db():
    """Утилита для добавления РЕАЛЬНЫХ каналов в базу данных"""
    init_db()
    
    client = Client(
        "channel_adder",
        api_id=Config.USER_API_ID,
        api_hash=Config.USER_API_HASH,
        phone_number=Config.USER_PHONE
    )
    
    await client.start()
    
    try:
        print("🔍 Ищу каналы и группы...")
        added_count = 0
        
        # Получаем диалоги (чаты, группы, каналы)
        async for dialog in client.get_dialogs():
            chat = dialog.chat
            
            # Фильтруем только каналы и группы
            if chat.type in ["channel", "group", "supergroup"]:
                db = next(get_db())
                
                # Проверяем, есть ли уже такой канал в базе
                existing_channel = db.query(Channel).filter(
                    (Channel.telegram_id == chat.id)
                ).first()
                
                if not existing_channel:
                    new_channel = Channel(
                        telegram_id=chat.id,
                        username=chat.username,
                        title=chat.title,
                        is_public=True
                    )
                    db.add(new_channel)
                    db.commit()
                    print(f"✅ Добавлен канал: {chat.title}")
                    if chat.username:
                        print(f"   📍 @{chat.username}")
                    print(f"   🆔 ID: {chat.id}")
                    added_count += 1
                else:
                    print(f"ℹ️ Уже в базе: {chat.title}")
        
        print(f"\n🎉 Добавлено {added_count} новых каналов!")
        
        # Покажем итоговый список каналов в базе
        db = next(get_db())
        all_channels = db.query(Channel).all()
        print(f"\n📋 Всего каналов в базе: {len(all_channels)}")
        for channel in all_channels:
            print(f"   • {channel.title} (@{channel.username})")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(add_real_channels_to_db())