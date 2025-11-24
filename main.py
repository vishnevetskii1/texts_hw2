import asyncio
from classic_bot import start_bot as start_classic_bot, stop_bot as stop_classic_bot
from user_bot import user_bot

async def main():
    print("🚀 Запускаю полную систему...")
    
    try:
        # Запускаем оба бота
        await asyncio.gather(
            start_classic_bot(),
            user_bot.start()
        )
    except KeyboardInterrupt:
        print("\n🛑 Остановка системы...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await stop_classic_bot()
        await user_bot.stop()

if __name__ == "__main__":
    asyncio.run(main())