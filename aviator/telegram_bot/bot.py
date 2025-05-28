import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from handlers import (
    start, bet, place_bet, withdraw, cancel, leaderboard, BET, PLAYING
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# États de conversation
BET, PLAYING = range(2)

# Simulateur simple de base de données en mémoire (à remplacer par accès DB Django)
users = {}  # user_id : {'balance': int, 'current_bet': int, 'game_active': bool, 'multiplier': float}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {'balance': 10000, 'current_bet': 0, 'game_active': False, 'multiplier': 1.0}
    await update.message.reply_text(
        f"Bienvenue à AviatorBot! Votre solde: {users[user_id]['balance']} F.\n"
        "Envoyez /bet pour placer votre mise."
    )

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {'balance': 10000, 'current_bet': 0, 'game_active': False, 'multiplier': 1.0}
    await update.message.reply_text("Entrez la somme que vous souhaitez parier (exemple: 1000):")
    return BET

async def place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        amount = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Veuillez entrer un nombre valide.")
        return BET

    if amount <= 0:
        await update.message.reply_text("La mise doit être supérieure à 0.")
        return BET
    if amount > users[user_id]['balance']:
        await update.message.reply_text("Solde insuffisant. Veuillez entrer une somme plus petite.")
        return BET

    users[user_id]['current_bet'] = amount
    users[user_id]['balance'] -= amount
    users[user_id]['game_active'] = True

    keyboard = [
        [InlineKeyboardButton("Retirer maintenant", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Jeu lancé! Le multiplicateur commence à grimper... Appuyez sur 'Retirer maintenant' avant le crash!",
        reply_markup=reply_markup
    )
    # Démarrer le multiplicateur aléatoire en tâche de fond (simulé ici)
    context.job_queue.run_once(crash_game, 5, chat_id=update.effective_chat.id, name=str(user_id))
    context.user_data['multiplier'] = 1.0
    context.job = context.job_queue.run_repeating(increment_multiplier, 1, chat_id=update.effective_chat.id, name=str(user_id))
    return PLAYING

async def increment_multiplier(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = int(job.name)
    context.user_data['multiplier'] += 0.5  # monte de 0.5 par seconde
    multiplier = context.user_data['multiplier']
    await context.bot.send_message(job.chat_id, f"Multiplicateur actuel: x{multiplier:.1f}")

async def crash_game(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = int(job.name)
    if users[user_id]['game_active']:
        users[user_id]['game_active'] = False
        multiplier = context.user_data.get('multiplier', 1.0)
        # Le multiplicateur de crash est entre 2 et 10, aléatoire
        crash_value = random.uniform(2, 10)
        if multiplier >= crash_value:
            gain = 0
            result_msg = f"Crash à x{crash_value:.2f} ! Vous avez perdu votre mise."
        else:
            gain = int(users[user_id]['current_bet'] * multiplier)
            users[user_id]['balance'] += gain
            result_msg = f"Bravo ! Vous avez retiré à x{multiplier:.1f} et gagné {gain} F."
        users[user_id]['current_bet'] = 0
        await context.bot.send_message(job.chat_id, result_msg)
        context.job.schedule_removal()

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not users[user_id]['game_active']:
        await query.edit_message_text("Le jeu n'est pas actif.")
        return ConversationHandler.END
    multiplier = context.user_data.get('multiplier', 1.0)
    gain = int(users[user_id]['current_bet'] * multiplier)
    users[user_id]['balance'] += gain
    users[user_id]['current_bet'] = 0
    users[user_id]['game_active'] = False
    await query.edit_message_text(f"Vous avez retiré à x{multiplier:.1f} ! Gain: {gain} F. Solde: {users[user_id]['balance']} F")
    # Supprimer le job de crash si possible
    current_jobs = context.job_queue.get_jobs_by_name(str(user_id))
    for job in current_jobs:
        job.schedule_removal()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jeu annulé.")
    return ConversationHandler.END


if __name__ == '__main__':
    import os
    from telegram.ext import Application

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('bet', bet)],
        states={
            BET: [MessageHandler(filters.TEXT & ~filters.COMMAND, place_bet)],
            PLAYING: [CallbackQueryHandler(withdraw, pattern='^withdraw$')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)

    print("Bot démarré...")
    app.run_polling()
