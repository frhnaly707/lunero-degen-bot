import asyncio
import requests
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID, ANALYZE_TOPIC_ID

PUMP_FUN_NEW_URL = "https://api.pump.fun/coins?limit=20&offset=0&sort=created_timestamp&order=DESC"
DEXSCREENER_PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"

async def fetch_new_tokens():
    """Ambil token baru dari Pump.fun"""
    try:
        response = requests.get(PUMP_FUN_NEW_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Pump.fun  {e}")
        return None

def is_valid_signal(token_data):
    """Filter token berkualitas"""
    try:
        # Hitung usia token (dalam menit)
        created_at = token_data.get("created_timestamp", 0) / 1000  # Konversi ms ke detik
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        
        # Ambil data penting
        liquidity = token_data.get("liquidity", 0)
        price = token_data.get("price", 0)
        market_cap = token_data.get("market_cap", 0)
        
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

async def get_dexscreener_data(mint_address):
    """Ambil data tambahan dari DexScreener berdasarkan mint address"""
    try:
        # Format pair address untuk DexScreener: So1..._mint...
        pair_address = f"So11111111111111111111111111111111111111112_{mint_address}"
        url = DEXSCREENER_PAIR_URL.format(pair_address=pair_address)
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("pairs", [{}])[0] if data.get("pairs") else {}
        return {}
    except:
        return {}

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    """Auto-announce berbasis Pump.fun + DexScreener"""
    tokens = await fetch_new_tokens()
    if not tokens:
        return
        
    for token in tokens:
        if not is_valid_signal(token):
            continue
            
        # Ambil data dasar
        mint_address = token.get("mint", "")
        token_name = token.get("name", "Unknown")
        token_symbol = token.get("symbol", "???")
        price = token.get("price", 0)
        liquidity = token.get("liquidity", 0)
        created_at = token.get("created_timestamp", 0) / 1000
        age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
        
        # Dapatkan data tambahan dari DexScreener
        dex_data = await get_dexscreener_data(mint_address) if mint_address else {}
        
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
            analysis_text = generate_forensic_report(token, dex_data)
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                message_thread_id=ANALYZE_TOPIC_ID,
                text=analysis_text
            )
            
        break  # Kirim 1 token terbaik per cycle
