import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from sqlalchemy.orm import Session
from database import get_db
from models import User, Channel, Filter
from config import Config

class UserBot:
    def __init__(self):
        self.client = Client(
            "user_bot_session",
            api_id=Config.USER_API_ID,
            api_hash=Config.USER_API_HASH,
            phone_number=Config.USER_PHONE
        )
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.client.on_message(filters.text | filters.caption)
        async def handle_message(client: Client, message: Message):
            await self.process_message(message)
    
    async def process_message(self, message: Message):
        """Обработка входящих сообщений"""
        try:
            # Получаем текст сообщения
            text = message.text or message.caption
            if not text:
                return
            
            chat_id = message.chat.id
            chat_title = getattr(message.chat, 'title', 'Личный чат')
            
            print(f"📨 Сообщение из '{chat_title}': {text[:100]}...")
            
            # Получаем канал из базы
            db = next(get_db())
            channel = db.query(Channel).filter(Channel.telegram_id == chat_id).first()
            
            if not channel:
                print(f"ℹ️ Канал {chat_id} не найден в базе, пропускаем")
                return
            
            # Для каждого подписчика проверяем фильтры
            forwarded_count = 0
            for user in channel.subscribers:
                if await self.check_filters(text, user.filters):
                    if await self.forward_to_user(message, user):
                        forwarded_count += 1
            
            if forwarded_count > 0:
                print(f"✅ Переслано {forwarded_count} пользователям")
                    
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
    
    async def check_filters(self, text: str, user_filters: list) -> bool:
        """Проверка сообщения на соответствие фильтрам"""
        text_lower = text.lower()
        
        for filter_obj in user_filters:
            if not filter_obj.is_active:
                continue
            
            # Проверка по ключевым словам
            if filter_obj.keywords:
                keywords = [kw.strip().lower() for kw in filter_obj.keywords.split(',')]
                if any(keyword in text_lower for keyword in keywords):
                    print(f"✅ Сообщение соответствует фильтру '{filter_obj.name}'")
                    return True
        
        return False
    
    async def forward_to_user(self, message: Message, user: User) -> bool:
        """Пересылка сообщения пользователю"""
        try:
            if user.target_chat_id:
                await message.forward(user.target_chat_id)
                print(f"📤 Переслано пользователю {user.telegram_id}")
                return True
            else:
                print(f"⚠️ Пользователь {user.telegram_id} не установил целевой чат")
                return False
        except Exception as e:
            print(f"❌ Ошибка пересылки: {e}")
            return False
    
    async def start(self):
        """Запуск юзер-бота"""
        os.makedirs("sessions", exist_ok=True)
        print("🔐 Запускаю юзер-бота...")
        
        try:
            await self.client.start()
            print("✅ Юзер-бот авторизован!")
            
            # Бесконечный цикл
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Ошибка запуска юзер-бота: {e}")
            return False
        except KeyboardInterrupt:
            print("\n🛑 Останавливаю юзер-бота...")
            await self.client.stop()
            return True
    
    async def stop(self):
        """Остановка юзер-бота"""
        try:
            await self.client.stop()
            print("✅ Юзер-бот остановлен")
        except:
            pass

user_bot = UserBot()