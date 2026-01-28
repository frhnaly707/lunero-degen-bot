from telegram import Update
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, GAS_TOPIC_ID

async def send_gas_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GAS_TOPIC_ID:
        await update.message.reply_text("❌ GAS_TOPIC_ID belum dikonfigurasi!")
        return
        
    gas_text = (
        "⛽ GAS ALERT — Solana Network\n"
        "🔴 HIGH CONGESTION\n\n"
        "💰 Gas Fee: $0.47 per tx\n"
        "📉 Failed Tx Rate: 32%\n"
        "⏱️ Avg Confirmation: 8.2 detik\n\n"
        "💡 SARAN: Tunggu 3-5 menit atau skip trade"
    )
    
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=GAS_TOPIC_ID,
        text=gas_text
    )
    await update.message.reply_text("✅ Gas alert dikirim ke #gas!")