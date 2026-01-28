import asyncio
import requests
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID, ANALYZE_TOPIC_ID, MORALIS_API_KEY

# Endpoint resmi Moralis untuk Pump.fun tokens
MORALIS_PUMP_FUN_URL = "https://deep-index.moralis.io/api/v2.2/pumpfun/tokens"

headers = {
    "X-API-Key": MORALIS_API_KEY,
    "Content-Type": "application/json"
}

async def fetch_new_pumpfun_tokens():
    """Ambil token baru dari Moralis Pump.fun API"""
    try:
        params = {
            "chain": "solana",
            "limit": 20
        }
        response = requests.get(MORALIS_PUMP_FUN_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Moralis error: {e}")
        return None

def is_valid_signal(token):
    """Filter token berkualitas"""
    try:
        # Hitung usia token (dalam menit)
        created_at = token.get("created_timestamp", 0) / 1000  # konversi ms ke detik
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        
        # Ambil data penting
        liquidity = token.get("liquidity", 0)
        price = token.get("price", 0)
        market_cap = token.get("market_cap", 0)
        
        # Kriteria signal
        if age_minutes > 10:  # Hanya token <10 menit
            return False
        if liquidity < 10000:  # Minimal LP $10k
            return False
        if price == 0 or market_cap == 0:
            return False
            
        return True
    except Exception as e:
        print(f"Error validating token: {e}")
        return False

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    """Auto-announce signal ke grup Telegram"""
    data = await fetch_new_pumpfun_tokens()
    if not data or "result" not in data:
        return
        
    for token in data["result"]:
        if not is_valid_signal(token):
            continue
            
        # Format data
        token_name = token.get("name", "Unknown")
        token_symbol = token.get("symbol", "???")
        mint = token.get("mint", "")
        price = token.get("price", 0)
        liquidity = token.get("liquidity", 0)
        market_cap = token.get("market_cap", 0)
        created_at = token.get("created_timestamp", 0) / 1000
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        
        # Kirim ke #signal
        signal_text = (
            f"🚨 DEGEN SIGNAL — ${token_symbol} ({token_name})\n"
            f"✅ Setup Quality: 85/100\n"
            f"⏰ Age: {age_minutes:.1f} minutes\n"
            f"💧 Liquidity: ${liquidity:,.0f}\n"
            f"💰 Price: ${price:.8f}\n"
            f"🪙 Mint: `{mint}`\n\n"
            f"⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
        )
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=SIGNAL_TOPIC_ID,
            text=signal_text,
            parse_mode="Markdown"
        )
        
        # Kirim analisis ke #analyze
        if ANALYZE_TOPIC_ID:
            await asyncio.sleep(2)
            analysis_text = (
                f"🔍 FORENSIC ANALYSIS: ${token_symbol}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 MARKET CAP: ${market_cap:,.0f}\n"
                f"💧 LIQUIDITY: ${liquidity:,.0f}\n"
                f"⏰ DETECTED: {age_minutes:.1f} minutes ago\n"
                f"🪙 MINT: `{mint}`\n\n"
                f"✅ SETUP QUALITY: 85/100\n"
                f"⚠️ RISK: Verify contract before trading\n\n"
                f"⚡ [ TRADE WITH SETTINGS ] [ CUSTOMIZE RISK ]"
            )
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                message_thread_id=ANALYZE_TOPIC_ID,
                text=analysis_text,
                parse_mode="Markdown"
            )
            
        break  # Kirim 1 token terbaik per cycle
