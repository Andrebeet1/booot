import os
import django
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

# ▶️ Initialiser Django pour utiliser les modèles
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aviatorbot.settings')
django.setup()

# 🔽 Importer les handlers depuis handlers.py
from handlers import (
    start_handler,
    aviator_handler,
    register_handlers
)

# 🔐 Ton token Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# 🛠️ Logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Créer l'application Telegram
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commandes Telegram
    app.add_handler(CommandHandler('start', start_handler))
    app.add_handler(CommandHandler('aviator', aviator_handler))

    # Gestion des boutons (callback data)
    register_handlers(app)

    # Lancer le bot
    print("✅ AviatorBot est en ligne et prêt à jouer !")
    app.run_polling()

if __name__ == '__main__':
    main()
