import logging
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN
from auto_announce import auto_announce_signals
from handlers.signal_handler import send_signal_demo
from handlers.analyze_handler import analyze_token
from handlers.gas_handler import send_gas_alert

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ LUNERO DEGEN BOT — Forensic Intelligence Assistant\n\n"
        "Semua aktivitas terjadi di grup:\n"
        "👉 t.me/LuneroDegenHub\n\n"
        "Perintah yang tersedia:\n"
        "/signal — Kirim signal contoh ke #signal\n"
        "/analyze [alamat] — Analisis token ke #analyze\n"
        "/gas — Kirim alert gas ke #gas\n\n"
        "⚠️ DISCLAIMER: 95% memecoin rug pull dalam 24 jam."
    )
    await update.message.reply_text(welcome_text)

async def start_auto_announce(application: Application):
    while True:
        try:
            await auto_announce_signals(application.bot)
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Auto-announce error: {e}")
            await asyncio.sleep(30)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", send_signal_demo))
    application.add_handler(CommandHandler("analyze", analyze_token))
    application.add_handler(CommandHandler("gas", send_gas_alert))
    
    threading.Thread(target=lambda: asyncio.run(start_auto_announce(application)), daemon=True).start()
    application.run_polling()

if __name__ == "__main__":
    main()
