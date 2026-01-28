from telegram import Update
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID

async def send_signal_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SIGNAL_TOPIC_ID:
        await update.message.reply_text("❌ SIGNAL_TOPIC_ID belum dikonfigurasi!")
        return
        
    signal_text = (
        "🚨 DEGEN SIGNAL — $MOONSHOT\n"
        "✅ Setup Quality: 89/100\n"
        "⏰ Valid window: Next 60 seconds\n\n"
        "📊 Pump Phase: SEEDING (menit ke-2.1)\n"
        "💧 Liquidity: $58k (burned 97%)\n\n"
        "⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
    )
    
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=SIGNAL_TOPIC_ID,
        text=signal_text
    )
    await update.message.reply_text("✅ Signal demo dikirim ke #signal!")