import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found. Set it in .env file")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ LUNERO DEGEN BOT — Forensic Intelligence Assistant\n\n"
        "Saya bukan sinyal trading ajaib. Saya adalah forensic investigator "
        "yang membantu Anda menghindari rug pull & late entry.\n\n"
        "✅ Fitur Utama:\n"
        "• Deteksi rug pull 60 detik sebelum terjadi\n"
        "• Analisis pump group behavioral patterns\n"
        "• Prediksi dump window berdasarkan data historis\n"
        "• FOMO Coach untuk lawan bias emosional Anda\n\n"
        "⚠️ DISCLAIMER:\n"
        "95% memecoin rug pull dalam 24 jam. Gunakan HANYA modal yang siap hilang 100%.\n\n"
        "Mulai dengan:\n"
        "/signal — Lihat channel signal utama\n"
        "/help — Panduan lengkap"
    )
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 LUNERO DEGEN BOT — Panduan Penggunaan\n\n"
        "🤖 CARA KERJA:\n"
        "1. @LuneroSignal: Terima auto-announce peluang berkualitas\n"
        "2. @LuneroAnalyze: Dapatkan deep forensic report + reasoning\n"
        "3. @LuneroTrade: Eksekusi semi-auto aman via Wallet Connect\n"
        "4. @LuneroPort: Monitor portfolio real-time (read-only)\n"
        "5. @LuneroAutopsy: Pelajari dari setiap trade yang selesai\n"
        "6. @LuneroGas: Dapatkan alert gas fee optimal\n\n"
        "⚠️ ATURAN WAJIB:\n"
        "• Max position size: 5% modal per trade\n"
        "• Selalu verifikasi reasoning di @LuneroAnalyze sebelum entry\n"
        "• Bot TIDAK pegang private key Anda — Anda selalu approve manual\n"
        "• 95% memecoin rug pull dalam 24 jam — siap kehilangan 100%"
    )
    await update.message.reply_text(help_text)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📡 CHANNEL SIGNAL UTAMA:\n"
        "https://t.me/lunerosignal\n\n"
        "Di sini Anda akan menerima auto-announce peluang berkualitas "
        "dengan Setup Quality Score ≥82/100."
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("signal", signal))
    
    application.run_polling()

if __name__ == "__main__":
    main()