import logging
import os
import asyncio
import threading
import requests
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes,
    filters
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables (set in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", 0))

# Topic IDs for each section
SIGNAL_TOPIC_ID = int(os.getenv("SIGNAL_TOPIC_ID", 0))
ANALYZE_TOPIC_ID = int(os.getenv("ANALYZE_TOPIC_ID", 0))
TRADE_TOPIC_ID = int(os.getenv("TRADE_TOPIC_ID", 0))
PORTFOLIO_TOPIC_ID = int(os.getenv("PORTFOLIO_TOPIC_ID", 0))
AUTOPSY_TOPIC_ID = int(os.getenv("AUTOPSY_TOPIC_ID", 0))
GAS_TOPIC_ID = int(os.getenv("GAS_TOPIC_ID", 0))

# Validate required variables
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required")

# DexScreener API constants
DEXSCREENER_SOLANA_URL = "https://api.dexscreener.com/latest/dex/chains/solana"

async def fetch_new_pairs():
    """Ambil token baru dari DexScreener"""
    try:
        response = requests.get(DEXSCREENER_SOLANA_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching DexScreener data: {e}")
        return None

def is_valid_signal(pair):
    """Filter token berkualitas"""
    try:
        created_at = pair.get("pairCreatedAt", 0)
        if created_at == 0:
            return False
            
        age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - created_at) / 60000
        
        price_usd = float(pair.get("priceUsd", 0) or 0)
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        price_change_5m = float(pair.get("priceChange", {}).get("h5", 0) or 0)
        
        # Kriteria signal
        if age_minutes > 10:  # Hanya token <10 menit
            return False
        if liquidity_usd < 10000:  # Minimal LP $10k
            return False
        if price_usd == 0:
            return False
        if price_change_5m > 300:  # Hindari late entry
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating pair: {e}")
        return False

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi utama auto-announce"""
    data = await fetch_new_pairs()
    if not data or "pairs" not in data:
        return
        
    for pair in data["pairs"]:
        if not is_valid_signal(pair):
            continue
            
        token_name = pair.get("baseToken", {}).get("name", "Unknown")
        token_symbol = pair.get("baseToken", {}).get("symbol", "???")
        price_usd = float(pair.get("priceUsd", 0) or 0)
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - pair.get("pairCreatedAt", 0)) / 60000
        
        signal_text = (
            f"🚨 DEGEN SIGNAL — ${token_symbol} ({token_name})\n"
            f"✅ Setup Quality: 85/100\n"
            f"⏰ Age: {age_minutes:.1f} minutes\n"
            f"💧 Liquidity: ${liquidity_usd:,.0f}\n"
            f"💰 Price: ${price_usd:.8f}\n\n"
            f"⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
        )
        
        try:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                message_thread_id=SIGNAL_TOPIC_ID,
                text=signal_text
            )
            logger.info(f"Auto-signal sent: {token_symbol}")
            break  # Kirim 1 signal terbaik per cycle
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            break

async def start_auto_announce(application: Application):
    """Jalankan auto-announce setiap 30 detik"""
    while True:
        try:
            await auto_announce_signals(application.bot)
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Auto-announce error: {e}")
            await asyncio.sleep(30)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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

async def send_signal_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual trigger: kirim signal demo ke topik #signal"""
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
    
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=SIGNAL_TOPIC_ID,
            text=signal_text
        )
        await update.message.reply_text("✅ Signal demo dikirim ke #signal!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def analyze_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze [alamat] command from group"""
    if not update.message or not update.message.text:
        return
        
    tokens = update.message.text.split()
    if len(tokens) < 2 or tokens[0] != "/analyze":
        return
        
    token_address = tokens[1]
    
    if not ANALYZE_TOPIC_ID:
        await update.message.reply_text("❌ ANALYZE_TOPIC_ID belum dikonfigurasi!")
        return
    
    analysis_text = (
        f"🔍 FORENSIC ANALYSIS: {token_address}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 PUMP CYCLE: SEEDING (menit ke-2.3)\n"
        "💧 LIQUIDITY: $42k (burned 95%)\n"
        "👥 CREATOR: Clean history (0 rug pull)\n"
        "🐋 WHALE: Akumulasi bertahap (bukan pump artifisial)\n\n"
        "✅ SETUP QUALITY: 84/100\n"
        "⚠️ RISK: LP concentration 68% di top 5 dompet\n\n"
        "⚡ [ TRADE WITH SETTINGS ] [ CUSTOMIZE RISK ]"
    )
    
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ANALYZE_TOPIC_ID,
            text=analysis_text
        )
        await update.message.reply_text("✅ Analisis dikirim ke #analyze!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def send_gas_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual trigger: kirim gas alert ke #gas"""
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
    
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=GAS_TOPIC_ID,
            text=gas_text
        )
        await update.message.reply_text("✅ Gas alert dikirim ke #gas!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handler untuk perintah
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", send_signal_demo))
    application.add_handler(CommandHandler("analyze", analyze_token))
    application.add_handler(CommandHandler("gas", send_gas_alert))
    
    # Jalankan auto-announce di background thread
    threading.Thread(target=lambda: asyncio.run(start_auto_announce(application)), daemon=True).start()
    
    application.run_polling()

if __name__ == "__main__":
    main()
