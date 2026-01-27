import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # ID grup Lunero Degen Hub

# Topic IDs (dari @RawDataBot)
SIGNAL_TOPIC_ID = int(os.getenv("SIGNAL_TOPIC_ID", 0))
ANALYZE_TOPIC_ID = int(os.getenv("ANALYZE_TOPIC_ID", 0))
TRADE_TOPIC_ID = int(os.getenv("TRADE_TOPIC_ID", 0))
PORTFOLIO_TOPIC_ID = int(os.getenv("PORTFOLIO_TOPIC_ID", 0))
AUTOPSY_TOPIC_ID = int(os.getenv("AUTOPSY_TOPIC_ID", 0))
GAS_TOPIC_ID = int(os.getenv("GAS_TOPIC_ID", 0))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ LUNERO DEGEN BOT — Forensic Intelligence Assistant\n\n"
        "Semua aktivitas terjadi di grup:\n"
        "👉 t.me/LuneroDegenHub\n\n"
        "Topik tersedia:\n"
        "• 📡 #signal — Auto-announce peluang\n"
        "• 🔍 #analyze — Analisis token spesifik\n"
        "• ⚡ #trade — Eksekusi semi-auto\n"
        "• 📊 #portfolio — Tracking PnL\n"
        "• 🔬 #autopsy — Post-trade lessons\n"
        "• ⛽ #gas — Gas optimizer alerts\n\n"
        "⚠️ DISCLAIMER: 95% memecoin rug pull dalam 24 jam."
    )
    await update.message.reply_text(welcome_text)

async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contoh: kirim signal ke topik #signal"""
    if not GROUP_CHAT_ID or not SIGNAL_TOPIC_ID:
        await update.message.reply_text("❌ Topic ID belum dikonfigurasi!")
        return
        
    signal_text = (
        "🚨 DEGEN SIGNAL — $MOONSHOT\n"
        "✅ Setup Quality: 89/100\n"
        "⏰ Valid window: Next 60 seconds\n\n"
        "⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
    )
    
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=SIGNAL_TOPIC_ID,
        text=signal_text
    )
    await update.message.reply_text("✅ Signal dikirim ke #signal!")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", send_signal))
    
    application.run_polling()

if __name__ == "__main__":
    main()
