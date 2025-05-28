import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

# États de conversation
BET, PLAYING = range(2)

# Base de données temporaire (remplace par DB Django)
users = {}  # { user_id: {balance, bet, active, multiplier} }

### COMMANDES DE BASE ###

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {'balance': 10000, 'current_bet': 0, 'game_active': False, 'multiplier': 1.0}

    await update.message.reply_text(
        f"👋 Bienvenue à AviatorBot !\n💰 Solde actuel : {users[user_id]['balance']} F.\n"
        "🎮 Envoyez /bet pour commencer une partie."
    )


async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {'balance': 10000, 'current_bet': 0, 'game_active': False, 'multiplier': 1.0}

    await update.message.reply_text("💸 Entrez la mise que vous souhaitez parier (ex: 1000) :")
    return BET


async def place_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        amount = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Entrez un nombre valide.")
        return BET

    if amount <= 0:
        await update.message.reply_text("❌ Mise invalide. Essayez encore.")
        return BET
    if amount > users[user_id]['balance']:
        await update.message.reply_text("⚠️ Solde insuffisant.")
        return BET

    users[user_id]['current_bet'] = amount
    users[user_id]['balance'] -= amount
    users[user_id]['game_active'] = True
    context.user_data['multiplier'] = 1.0

    keyboard = [
        [InlineKeyboardButton("🏃‍♂️ Retirer maintenant", callback_data='withdraw')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 Le multiplicateur démarre… Appuyez sur 'Retirer maintenant' avant le crash !",
        reply_markup=reply_markup
    )

    # Lancer les jobs de jeu
    context.job_queue.run_once(crash_game, 6, chat_id=update.effective_chat.id, name=str(user_id))
    context.job_queue.run_repeating(increment_multiplier, 1, chat_id=update.effective_chat.id, name=f"multi_{user_id}")
    return PLAYING


async def increment_multiplier(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = int(job.name.split("_")[1])
    if users[user_id]['game_active']:
        context.user_data['multiplier'] += 0.5
        await context.bot.send_message(job.chat_id, f"📈 x{context.user_data['multiplier']:.1f}")


async def crash_game(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = int(job.name)

    if users[user_id]['game_active']:
        crash_point = random.uniform(2.0, 10.0)
        multiplier = context.user_data.get('multiplier', 1.0)
        users[user_id]['game_active'] = False

        if multiplier < crash_point:
            await context.bot.send_message(job.chat_id, f"💥 Crash à x{crash_point:.2f} ! Vous avez PERDU votre mise.")
        else:
            gain = int(users[user_id]['current_bet'] * multiplier)
            users[user_id]['balance'] += gain
            await context.bot.send_message(job.chat_id, f"✅ Vous avez gagné {gain} F à x{multiplier:.2f} !")

        users[user_id]['current_bet'] = 0

        # Arrêter les autres jobs
        for j in context.job_queue.get_jobs_by_name(f"multi_{user_id}"):
            j.schedule_removal()


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not users[user_id]['game_active']:
        await query.edit_message_text("⚠️ Trop tard. Le jeu est terminé.")
        return ConversationHandler.END

    multiplier = context.user_data.get('multiplier', 1.0)
    gain = int(users[user_id]['current_bet'] * multiplier)
    users[user_id]['balance'] += gain
    users[user_id]['current_bet'] = 0
    users[user_id]['game_active'] = False

    await query.edit_message_text(
        f"🏁 Retiré à x{multiplier:.2f} ! Vous gagnez {gain} F.\n💼 Nouveau solde : {users[user_id]['balance']} F"
    )

    # Arrêter les jobs
    for j in context.job_queue.get_jobs_by_name(f"multi_{user_id}"):
        j.schedule_removal()
    for j in context.job_queue.get_jobs_by_name(str(user_id)):
        j.schedule_removal()

    return ConversationHandler.END


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
    msg = "🏆 *Classement des meilleurs joueurs :*\n\n"
    for i, (uid, data) in enumerate(top, 1):
        username = f"User {uid}"
        balance = data['balance']
        msg += f"{i}. {username} - {balance} F\n"
    await update.message.reply_text(msg, parse_mode='Markdown')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Opération annulée.")
    return ConversationHandler.END
