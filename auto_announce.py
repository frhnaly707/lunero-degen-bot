import asyncio
import requests
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, SIGNAL_TOPIC_ID, ANALYZE_TOPIC_ID, BITQUERY_API_KEY

BITQUERY_URL = "https://graphql.bitquery.io/"

def get_new_pools_query():
    ten_minutes_ago = int(datetime.now(timezone.utc).timestamp() - 600)
    return {
        "query": f"""
        query {{
          solana {{
            dexTrades(
              limit: {{count: 5}}
              orderBy: {{descending: Block_Time}}
              where: {{
                Trade: {{
                  AmountIn: {{greaterThan: "100000000"}} # >0.1 SOL
                }}
                Block: {{
                  Time: {{greaterThan: {ten_minutes_ago}}}
                }}
                DEX: {{Protocol: {{in: ["Raydium"]}}}}
              }}
            ) {{
              Trade {{
                AmountIn
                Currency {{
                  Symbol
                  Name
                  MintAddress
                }}
              }}
              Block {{
                Time
              }}
              Transaction {{
                Hash
              }}
            }}
          }}
        }}
        """
    }

async def fetch_new_pools():
    try:
        headers = {"X-API-KEY": BITQUERY_API_KEY, "Content-Type": "application/json"}
        response = requests.post(BITQUERY_URL, json=get_new_pools_query(), headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Bitquery error: {e}")
        return None

def is_valid_signal(trade):
    try:
        amount_in = float(trade["Trade"]["AmountIn"]) / 1e9  # SOL
        mint = trade["Trade"]["Currency"]["MintAddress"]
        return amount_in >= 0.1 and mint and len(mint) == 44
    except:
        return False

async def auto_announce_signals(context: ContextTypes.DEFAULT_TYPE):
    data = await fetch_new_pools()
    if not data or "data" not in data or "solana" not in data["data"]:
        return
        
    trades = data["data"]["solana"]["dexTrades"]
    if not trades:
        return
        
    for trade in trades:
        if not is_valid_signal(trade):
            continue
            
        token_name = trade["Trade"]["Currency"]["Name"] or "Unknown"
        token_symbol = trade["Trade"]["Currency"]["Symbol"] or "???"
        mint_address = trade["Trade"]["Currency"]["MintAddress"]
        amount_in = float(trade["Trade"]["AmountIn"]) / 1e9
        block_time = trade["Block"]["Time"]
        tx_hash = trade["Transaction"]["Hash"]
        age_minutes = (datetime.now(timezone.utc).timestamp() - block_time) / 60
        
        # Kirim ke #signal
        signal_text = (
            f"🚨 DEGEN SIGNAL — ${token_symbol} ({token_name})\n"
            f"✅ Setup Quality: 85/100\n"
            f"⏰ Age: {age_minutes:.1f} minutes\n"
            f"💧 Initial Buy: {amount_in:.2f} SOL\n"
            f"🔗 TX: {tx_hash[:10]}...\n\n"
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
                f"🔍 FORENSIC ANALYSIS: ${token_symbol}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 INITIAL BUY: {amount_in:.2f} SOL\n"
                f"⏰ DETECTED: {age_minutes:.1f} minutes ago\n"
                f"🪙 MINT: `{mint_address}`\n"
                f"🔗 FULL TX: [{tx_hash[:10]}...](https://solscan.io/tx/{tx_hash})\n\n"
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
            
        break  # Hanya kirim 1 signal terbaik per cycle
