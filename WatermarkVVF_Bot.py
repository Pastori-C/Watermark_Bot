import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image
from datetime import datetime
import sys

from dotenv import load_dotenv
import os

load_dotenv()  # Carica le variabili dal file .env

TOKEN = os.getenv("TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID"))

# Debug: stampa tutte le variabili d'ambiente caricate
print("TOKEN:", os.getenv("TOKEN"))
print("AUTHORIZED_CHAT_ID:", os.getenv("AUTHORIZED_CHAT_ID"))

AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID"))

#sys.exit("Stop for maintenance")
sys.stdout.reconfigure(encoding='utf-8')  # Forza l'output in UTF-8

# 🔹 Configura logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Configurazione del bot (INSERISCI IL TUO TOKEN QUI)
TOKEN = os.getenv("TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID"))  # 🔹 Sostituisci con il tuo ID Telegram

# 🔹 Funzione di start
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Accesso negato.")
        return

    await update.message.reply_text("✅ Ciao! Inviami un'immagine e aggiungerò il watermark.")

# 🔹 Funzione per aggiungere watermark alle foto
async def foto(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Accesso negato.")
        return

    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive('Pictures.jpg')
    logger.info("Foto ricevuta da %s", user.first_name)

    # Apri immagine principale
    image = Image.open('Pictures.jpg')
    width, height = image.size

    # Apri il logo
    logo = Image.open('Original_Watermark.png')

    # Ridimensiona il logo in base alla proporzione minore (larghezza o altezza)
    proporzione = min(width, height)
    dimensionelogo = (30 * proporzione) / 100
    logo.thumbnail((dimensionelogo, dimensionelogo))
    logo.save('Watermark.png')

    # Aggiungi watermark
    logo_r = Image.open('Watermark.png')
    widthL, heightL = logo_r.size
    image_copy = image.copy()
    # Margini proporzionali (5% della larghezza dell'immagine)
    margin_x = int(width * 0.05)  # 5% della larghezza
    margin_y = int(height * 0.05)  # 5% dell'altezza

    # Calcola la posizione del watermark (alto a destra)
    posorizzontale = width - widthL - margin_x
    posverticale = margin_y

    image_copy.paste(logo_r, (posorizzontale, posverticale), logo_r)

    # Salva l'immagine con watermark
    image_copy.save('Photo_Watermark.jpg')

    await update.message.reply_text("🔄 Sto aggiungendo il logo, attendi un attimo...")
    await context.bot.send_photo(chat_id, photo=open('Photo_Watermark.jpg', 'rb'))

    # Rinomina l'immagine originale con timestamp
    i = datetime.now().strftime('%Y-%m-%d %H%M%S')
    os.rename('Pictures.jpg', f'Send_Pictures_{i}.jpg')

    await update.message.reply_text("✅ Fatto! Sono pronto per ricevere un'altra foto.")

# 🔹 Configura l'applicazione
def main():
    application = Application.builder().token(TOKEN).build()

    # 🔹 Aggiungi i gestori di comando
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, foto))

    # 🔹 Avvia il bot
    print("🤖 Bot in esecuzione...")
    application.run_polling()

if __name__ == '__main__':
    main()
