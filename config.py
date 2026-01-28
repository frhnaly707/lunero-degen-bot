# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", 0))
BITQUERY_API_KEY = os.getenv("BITQUERY_API_KEY")  # ← Baris ini HARUS ada

SIGNAL_TOPIC_ID = int(os.getenv("SIGNAL_TOPIC_ID", 0))
ANALYZE_TOPIC_ID = int(os.getenv("ANALYZE_TOPIC_ID", 0))
TRADE_TOPIC_ID = int(os.getenv("TRADE_TOPIC_ID", 0))
PORTFOLIO_TOPIC_ID = int(os.getenv("PORTFOLIO_TOPIC_ID", 0))
AUTOPSY_TOPIC_ID = int(os.getenv("AUTOPSY_TOPIC_ID", 0))
GAS_TOPIC_ID = int(os.getenv("GAS_TOPIC_ID", 0))
