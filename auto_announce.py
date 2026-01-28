import asyncio
import requests
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID, ANALYZE_TOPIC_ID

PUMP_FUN_NEW_URL = "https://api.pump.fun/coins?limit=20&offset=0&sort=created_timestamp&order=DESC"

async def fetch_new_tokens():
    try:
        response = requests.get(PUMP_FUN_NEW_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Pump.fun  {e}")
        return None

def is_valid_signal(token_data):
    try:
        created_at = token_data.get("created_timestamp", 0) / 1000
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        liquidity = token_data.get("liquidity", 0)
        price = token_data.get("price", 0)
        return (age_minutes <= 10 and liquidity >= 10000 and price > 0)
    except:
        return False

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    tokens = await fetch_new_tokens()
    if not tokens:
        return
        
    for token in tokens:
        if not is_valid_signal(token):
            continue
            
        mint_address = token.get("mint", "")
        token_name = token.get("name", "Unknown")
        token_symbol = token.get("symbol", "???")
        price = token.get("price", 0)
        liquidity = token.get("liquidity", 0)
        created_at = token.get("created_timestamp", 0) / 1000
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        
        # Kirim ke #signal
        signal_text = (
            f"🚨 DEGEN SIGNAL — ${token_symbol} ({token_name})\n"
            f"✅ Setup Quality: 85/100\n"
            f"⏰ Age: {age_minutes:.1f} minutes\n"
            f"💧 Liquidity: ${liquidity:,.0f}\n"
            f"💰 Price: ${price:.8f}\n\n"
            f"⚡ [ ANALYZE ] [ TRADE ] [ TRACK ]"
        )
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=SIGNAL_TOPIC_ID,
            text=signal_text
        )
        
        # Kirim analisis ke #analyze
        if ANALYZE_TOPIC_ID:
            await asyncio.sleep(2)
            analysis_text = (
                f"🔍 FORENSIC ANALYSIS: ${token_symbol} ({token_name})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 PUMP CYCLE: SEEDING (menit ke-{age_minutes:.1f})\n"
                f"💧 LIQUIDITY: ${liquidity:,.0f}\n"
                f"💰 MARKET CAP: ${token.get('market_cap', 0):,.0f}\n"
                f"📈 LIQUIDITY HEATMAP: {'🟢 LOW SLIPPAGE' if liquidity >= 50000 else '🟡 MODERATE' if liquidity >= 20000 else '🔴 HIGH SLIPPAGE'}\n\n"
                f"✅ SETUP QUALITY: {min(85 + (10 if liquidity >= 50000 else 0) + (5 if age_minutes <= 3 else 0), 100)}/100\n"
                f"⚡ [ TRADE WITH SETTINGS ] [ CUSTOMIZE RISK ]"
            )
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                message_thread_id=ANALYZE_TOPIC_ID,
                text=analysis_text
            )
            
        break
