import asyncio
import requests
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID, ANALYZE_TOPIC_ID
from analysis import generate_forensic_report

DEXSCREENER_SOLANA_URL = "https://api.dexscreener.com/latest/dex/chains/solana"

async def fetch_new_pairs():
    try:
        response = requests.get(DEXSCREENER_SOLANA_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching DexScreener data: {e}")
        return None

def is_valid_signal(pair):
    try:
        created_at = pair.get("pairCreatedAt", 0)
        if created_at == 0:
            return False
            
        age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - created_at) / 60000
        price_usd = float(pair.get("priceUsd", 0) or 0)
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        price_change_5m = float(pair.get("priceChange", {}).get("h5", 0) or 0)
        
        return (age_minutes <= 10 and 
                liquidity_usd >= 10000 and 
                price_usd > 0 and 
                price_change_5m <= 300)
    except:
        return False

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    data = await fetch_new_pairs()
    if not data or "pairs" not in 
        return
        
    for pair in data["pairs"]:
        if not is_valid_signal(pair):
            continue
            
        token_name = pair.get("baseToken", {}).get("name", "Unknown")
        token_symbol = pair.get("baseToken", {}).get("symbol", "???")
        price_usd = float(pair.get("priceUsd", 0) or 0)
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - pair.get("pairCreatedAt", 0)) / 60000
        
        # Kirim ke #signal
        signal_text = (
            f"🚨 DEGEN SIGNAL — ${token_symbol} ({token_name})\n"
            f"✅ Setup Quality: 85/100\n"
            f"⏰ Age: {age_minutes:.1f} minutes\n"
            f"💧 Liquidity: ${liquidity_usd:,.0f}\n"
            f"💰 Price: ${price_usd:.8f}\n\n"
            f"⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
        )
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=SIGNAL_TOPIC_ID,
            text=signal_text
        )
        
        # Kirim ke #analyze
        if ANALYZE_TOPIC_ID:
            await asyncio.sleep(2)
            forensic_report = generate_forensic_report(pair)
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                message_thread_id=ANALYZE_TOPIC_ID,
                text=forensic_report
            )
            
        break