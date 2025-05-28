from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import random, asyncio
from django.contrib.auth.models import User
from aviator.models import Joueur, Partie

# Commande /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue sur ✈️ *AviatorBot* !\n\n"
        "Tapez /aviator pour jouer et tenter de multiplier vos gains 💰",
        parse_mode='Markdown'
    )

# Commande /aviator
async def aviator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or user.first_name

    # Vérifier que l'utilisateur existe en base
    django_user, _ = User.objects.get_or_create(username=username)
    joueur, _ = Joueur.objects.get_or_create(user=django_user)

    mise = 1000  # Mise fixe pour la démo
    if joueur.solde < mise:
        await update.message.reply_text("❌ Solde insuffisant pour miser 1000 F.")
        return

    joueur.solde -= mise
    joueur.save()

    # Stocker les infos dans context.user_data
    context.user_data['jeu'] = {
        'mise': mise,
        'multiplicateur': 1.0,
        'crash': round(random.uniform(1.5, 5.0), 2),
        'retire': False,
        'joueur': joueur
    }

    # Afficher bouton "Retirer maintenant"
    bouton = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Retirer maintenant", callback_data="retirer")]
    ])

    message = await update.message.reply_text(
        f"🎮 Jeu lancé avec une mise de *{mise} F* !\nMultiplicateur : x1.00",
        reply_markup=bouton,
        parse_mode='Markdown'
    )

    # Faire grimper le multiplicateur jusqu'au crash
    while context.user_data['jeu']['multiplicateur'] < context.user_data['jeu']['crash']:
        await asyncio.sleep(1)
        context.user_data['jeu']['multiplicateur'] += round(random.uniform(0.1, 0.5), 2)
        multiplicateur = context.user_data['jeu']['multiplicateur']

        try:
            await message.edit_text(
                f"🎮 Jeu lancé avec une mise de *{mise} F* !\nMultiplicateur : x{multiplicateur:.2f}",
                reply_markup=bouton,
                parse_mode='Markdown'
            )
        except:
            pass

        if context.user_data['jeu'].get('retire'):
            gain = int(mise * multiplicateur)
            joueur.solde += gain
            joueur.save()
            Partie.objects.create(
                joueur=joueur,
                mise=mise,
                multiplicateur=multiplicateur,
                gain=gain,
                retire_avant_crash=True
            )
            await message.edit_text(f"✅ Retiré à x{multiplicateur:.2f} ! Gain : *{gain} F*", parse_mode='Markdown')
            return

    # Si crash
    Partie.objects.create(
        joueur=joueur,
        mise=mise,
        multiplicateur=context.user_data['jeu']['crash'],
        gain=0,
        retire_avant_crash=False
    )
    await message.edit_text(f"💥 Crash à x{context.user_data['jeu']['crash']} ! Tu as tout perdu 😢")

# Bouton "retirer"
async def retirer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['jeu']['retire'] = True
    await update.callback_query.answer("💸 Retrait demandé...")

# Enregistrement du handler pour callback
def register_handlers(app):
    app.add_handler(CallbackQueryHandler(retirer_callback, pattern="^retirer$"))
