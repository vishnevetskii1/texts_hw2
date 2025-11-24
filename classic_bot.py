import asyncio
from pyrogram import Client
from pyrogram.types import Message
from database import init_db, get_db
from models import User, Filter, Channel
from config import Config

# Глобальные переменные
app = None

async def handle_start(message: Message):
    try:
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                target_chat_id=message.chat.id
            )
            db.add(user)
            db.commit()
            print(f"👤 Новый пользователь: {user.first_name}")
        
        response = """
🎉 **News Aggregator Bot**

✅ Система агрегации новостей работает!

**Основные команды:**
📋 `/filters` - Ваши фильтры
➕ `/addfilter` - Добавить фильтр
📰 `/channels` - Список каналов
💬 `/setchat` - Установить чат
🔔 `/subscribe` - Подписаться на канал
🔕 `/unsubscribe` - Отписаться от канала
❓ `/help` - Помощь
🧪 `/test` - Проверка связи

**Пример использования:**
`/addfilter Технологии python,ai,программирование`
`/channels` - посмотреть доступные каналы
"""
        await message.reply(response)
        print("✅ Ответил на /start")
        
    except Exception as e:
        print(f"❌ Ошибка в handle_start: {e}")
        await message.reply("❌ Ошибка сервера")

async def handle_filters(message: Message):
    try:
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user or not user.filters:
            await message.reply("📭 У вас пока нет фильтров\n\nДобавьте первый фильтр:\n`/addfilter Название ключевые_слова`")
            return
        
        text = "📋 **Ваши фильтры:**\n\n"
        for i, f in enumerate(user.filters, 1):
            status = "✅" if f.is_active else "❌"
            text += f"{i}. {status} **{f.name}**\n"
            text += f"   Ключевые слова: `{f.keywords}`\n\n"
        
        await message.reply(text)
        print("✅ Показал фильтры")
        
    except Exception as e:
        await message.reply("❌ Ошибка при получении фильтров")
        print(f"❌ Ошибка в handle_filters: {e}")

async def handle_add_filter(message: Message):
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            await message.reply("❌ Используйте: `/addfilter Название ключевые_слова`")
            return
        
        name = parts[1]
        keywords = parts[2]
        
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            await message.reply("❌ Сначала используйте /start")
            return
        
        filter_obj = Filter(
            user_id=user.id,
            name=name,
            keywords=keywords
        )
        db.add(filter_obj)
        db.commit()
        
        await message.reply(f"✅ **Фильтр добавлен!**\n\n**Название:** {name}\n**Ключевые слова:** `{keywords}`")
        print(f"✅ Добавил фильтр: {name}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
        print(f"❌ Ошибка в handle_add_filter: {e}")

async def handle_channels(message: Message):
    try:
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        channels = db.query(Channel).filter(Channel.is_public == True).all()
        
        if not channels:
            await message.reply("📭 Нет доступных каналов\n\nДобавьте каналы через утилиту:\n`python3 add_channel.py`")
            return
        
        text = "📰 **Доступные каналы:**\n\n"
        for i, channel in enumerate(channels, 1):
            is_subscribed = user and channel in user.subscribed_channels
            status = "✅ ПОДПИСАН" if is_subscribed else "❌ НЕ ПОДПИСАН"
            text += f"{i}. **{channel.title}**\n"
            if channel.username:
                text += f"   @{channel.username}\n"
            text += f"   {status}\n\n"
        
        text += "**Команды для управления:**\n"
        text += "`/subscribe @username` - подписаться на канал\n"
        text += "`/unsubscribe @username` - отписаться от канала\n\n"
        text += "**💡 Для работы необходимо:**\n"
        text += "• Юзер-бот должен быть участником канала\n"
        text += "• Канал должен быть добавлен в базу данных"
        
        await message.reply(text)
        print("✅ Показал каналы со статусами подписки")
        
    except Exception as e:
        await message.reply("❌ Ошибка при получении каналов")
        print(f"❌ Ошибка в handle_channels: {e}")

async def handle_all_messages(client: Client, message: Message):
    if not message.text:
        return
        
    print(f"🎯 ПОЛУЧЕНО: '{message.text}' от {message.from_user.id}")
    
    # Простая обработка команд
    if message.text == "/start":
        await handle_start(message)
    elif message.text == "/test":
        await message.reply("✅ ClassicBot работает!")
    elif message.text == "/filters":
        await handle_filters(message)
    elif message.text.startswith("/addfilter"):
        await handle_add_filter(message)
    elif message.text == "/channels":
        await handle_channels(message)
    elif message.text == "/setchat":
        await handle_set_chat(message)
    elif message.text.startswith("/subscribe"):
        await handle_subscribe(message)
    elif message.text.startswith("/unsubscribe"):
        await handle_unsubscribe(message)
    elif message.text == "/help":
        await handle_help(message)
    elif message.text.startswith("/"):
        await message.reply("❌ Неизвестная команда. Используйте /help")

async def handle_set_chat(message: Message):
    try:
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if user:
            user.target_chat_id = message.chat.id
            db.commit()
            await message.reply("✅ **Этот чат установлен для получения новостей!**")
            print(f"✅ Установил чат для {user.first_name}")
        else:
            await message.reply("❌ Сначала используйте /start")
            
    except Exception as e:
        print(f"❌ Ошибка в handle_set_chat: {e}")

async def handle_subscribe(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Укажите username канала\nПример: `/subscribe @username`")
            return
        
        username = parts[1].lstrip('@')
        
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        channel = db.query(Channel).filter(Channel.username == username).first()
        
        if not user:
            await message.reply("❌ Сначала используйте /start")
            return
        
        if not channel:
            await message.reply(f"❌ Канал @{username} не найден в базе данных\n\nИспользуйте `/channels` чтобы посмотреть доступные каналы")
            return
        
        # Проверяем, подписан ли уже пользователь
        if channel in user.subscribed_channels:
            await message.reply(f"ℹ️ Вы уже подписаны на канал **{channel.title}**")
            return
        
        # Добавляем подписку
        user.subscribed_channels.append(channel)
        db.commit()
        
        await message.reply(f"✅ **Подписка оформлена!**\n\n📰 Канал: **{channel.title}**\n📍 @{channel.username}\n\nТеперь я буду присылать вам сообщения из этого канала, соответствующие вашим фильтрам!")
        print(f"✅ Пользователь {user.first_name} подписался на {channel.title}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка при подписке: {e}")
        print(f"❌ Ошибка в handle_subscribe: {e}")

async def handle_unsubscribe(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Укажите username канала\nПример: `/unsubscribe @username`")
            return
        
        username = parts[1].lstrip('@')
        
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        channel = db.query(Channel).filter(Channel.username == username).first()
        
        if not user:
            await message.reply("❌ Сначала используйте /start")
            return
        
        if not channel:
            await message.reply(f"❌ Канал @{username} не найден в базе данных")
            return
        
        # Проверяем, подписан ли пользователь
        if channel not in user.subscribed_channels:
            await message.reply(f"ℹ️ Вы не подписаны на канал **{channel.title}**")
            return
        
        # Удаляем подписку
        user.subscribed_channels.remove(channel)
        db.commit()
        
        await message.reply(f"✅ **Отписка выполнена!**\n\nВы отписались от канала **{channel.title}**")
        print(f"✅ Пользователь {user.first_name} отписался от {channel.title}")
        
    except Exception as e:
        await message.reply(f"❌ Ошибка при отписке: {e}")
        print(f"❌ Ошибка в handle_unsubscribe: {e}")

async def handle_help(message: Message):
    help_text = """
🤖 **News Aggregator Bot - Помощь**

**Основные команды:**
`/start` - Начать работу
`/filters` - Ваши фильтры  
`/addfilter` - Добавить фильтр
`/channels` - Список каналов
`/setchat` - Установить чат
`/subscribe` - Подписаться
`/unsubscribe` - Отписаться
`/help` - Эта справка
`/test` - Проверка связи
"""
    await message.reply(help_text)
    print("✅ Показал справку")

async def start_bot():
    """Запуск бота"""
    global app
    init_db()
    
    app = Client(
        "classic_bot",
        api_id=Config.USER_API_ID,
        api_hash=Config.USER_API_HASH,
        bot_token=Config.BOT_TOKEN
    )
    
    # Регистрируем обработчик
    app.on_message()(handle_all_messages)
    
    await app.start()
    me = await app.get_me()
    print(f"✅ ClassicBot @{me.username} запущен и готов к командам!")
    
    # Бесконечный цикл
    while True:
        await asyncio.sleep(1)

async def stop_bot():
    """Остановка бота"""
    global app
    if app:
        await app.stop()
        print("✅ ClassicBot остановлен")

# Для обратной совместимости
class ClassicBot:
    async def start(self):
        await start_bot()
    
    async def stop(self):
        await stop_bot()

classic_bot = ClassicBot()