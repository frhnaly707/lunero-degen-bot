# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", 0))
BITQUERY_API_KEY = os.getenv("BITQUERY_API_KEY")  # ← Ini harus ada

SIGNAL_TOPIC_ID = int(os.getenv("SIGNAL_TOPIC_ID", 0))
ANALYZE_TOPIC_ID = int(os.getenv("ANALYZE_TOPIC_ID", 0))
# ... (topic lainnya)
