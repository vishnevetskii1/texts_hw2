import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Юзер-бот
    USER_API_ID = 38407531 #int(os.getenv("USER_API_ID"))
    USER_API_HASH = '59d394b774ced3801e46bf1e61ba41bc' #os.getenv("USER_API_HASH")
    USER_PHONE = '+79936173023' #os.getenv("USER_PHONE")
    
    # Классический бот
    BOT_TOKEN = '8278617692:AAHCHjsoEK-QvWfvO__fu-N-IcVe4b-pRIY' #os.getenv("BOT_TOKEN")
    
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///news_bot.db")