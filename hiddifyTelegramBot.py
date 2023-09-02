import AdminBot.bot
from threading import Thread
from config import CLIENT_TOKEN

if __name__ == '__main__':
    Thread(target=AdminBot.bot.start).start()
    if CLIENT_TOKEN:
        import UserBot.bot

        Thread(target=UserBot.bot.start).start()
