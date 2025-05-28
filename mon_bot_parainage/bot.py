import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# === Configuration ===
TOKEN = "7593835824:AAHgogA4tGQ6_SjaIAX8LgsaYG0gZ3keAKw"
BOT_USERNAME = "ApplesmobileBot"
CHANNELS = ["@NomDuCanal1", "@NomDuCanal2"]  # Remplace avec tes vrais canaux
DATA_FILE = "data.json"

# === Fonctions de gestion des données ===
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            f.write("{}")
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# === Commande /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start reçu")
    data = load_data()
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in data:
        data[user_id] = {"parrain": None, "filleuls": [], "solde": 0}

        if context.args:
            parrain_id = context.args[0]
            if parrain_id != user_id and parrain_id in data:
                data[user_id]["parrain"] = parrain_id
                data[parrain_id]["filleuls"].append(user_id)
                data[parrain_id]["solde"] += 1
                print(f"Nouveau parrainage : {parrain_id} → {user_id}")

    save_data(data)

    await update.message.reply_text(
        "Bienvenue 👋\nClique sur le bouton ci-dessous pour confirmer ton abonnement aux canaux.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Rejoindre les canaux", callback_data="check_join")]
        ])
    )

# === Vérification d’abonnement ===
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot
    joined_all = True

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                joined_all = False
                break
        except:
            joined_all = False
            break

    if joined_all:
        await update.callback_query.message.reply_text("Merci d’avoir rejoint les canaux ! ✅\nTu peux maintenant obtenir ton lien avec /monlien.")
    else:
        await update.callback_query.message.reply_text("Tu dois d’abord rejoindre tous les canaux pour continuer.")

# === Commande /monlien ===
async def monlien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"Voici ton lien de parrainage 👇\n{link}")

# === Commande /solde ===
async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    solde = data.get(user_id, {}).get("solde", 0)
    await update.message.reply_text(f"Tu as actuellement {solde} filleul(s).")

# === Commande /menu ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🎯 Mon lien", callback_data="monlien")],
        [InlineKeyboardButton("💰 Mon solde", callback_data="solde")],
        [InlineKeyboardButton("ℹ️ Aide", callback_data="aide")]
    ]
    await update.message.reply_text("Menu principal 👇", reply_markup=InlineKeyboardMarkup(buttons))

# === Gestion des boutons du menu ===
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "monlien":
        await monlien(update, context)
    elif data == "solde":
        await solde(update, context)
    elif data == "aide":
        await query.message.reply_text("🔹 Invite tes amis avec ton lien personnalisé pour gagner des récompenses !\n🔹 Plus tu parraines, plus tu gagnes 💰.")

# === Fonction principale ===
def main():
    print("Démarrage du bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("monlien", monlien))
    app.add_handler(CommandHandler("solde", solde))
    app.add_handler(CommandHandler("menu", menu))

    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(handle_menu_buttons, pattern="^(monlien|solde|aide)$"))

    print("Bot prêt à tourner.")
    app.run_polling()
    print("Polling terminé.")

if __name__ == "__main__":
    main()
