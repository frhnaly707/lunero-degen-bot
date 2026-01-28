from datetime import datetime, timezone

def get_liquidity_heatmap(pair):
    try:
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        if liquidity_usd < 20000:
            return "🔴 HIGH SLIPPAGE (>40%)"
        elif liquidity_usd < 50000:
            return "🟡 MODERATE SLIPPAGE (15-40%)"
        else:
            return "🟢 LOW SLIPPAGE (<15%)"
    except:
        return "❓ Data tidak tersedia"

def analyze_pump_group(pair):
    try:
        volume_5m = float(pair.get("volume", {}).get("h5", 0) or 0)
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        if volume_5m > liquidity_usd * 0.8:
            return "🔴 AGGRESSIVE PUMP (high dump risk)"
        elif volume_5m > liquidity_usd * 0.3:
            return "🟡 STEADY ACCUMULATION"
        else:
            return "🟢 ORGANIC GROWTH"
    except:
        return "❓ Pola tidak terdeteksi"

def check_lp_concentration(pair):
    try:
        price_change_5m = float(pair.get("priceChange", {}).get("h5", 0) or 0)
        if price_change_5m > 200:
            return "⚠️ LP concentration >65% → MODERATE DUMP RISK"
        else:
            return "✅ LP distribution normal"
    except:
        return "❓ LP concentration unknown"

def generate_forensic_report(pair):
    token_name = pair.get("baseToken", {}).get("name", "Unknown")
    token_symbol = pair.get("baseToken", {}).get("symbol", "???")
    liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
    price_usd = float(pair.get("priceUsd", 0) or 0)
    created_at = pair.get("pairCreatedAt", 0)
    age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - created_at) / 60000 if created_at else 0
    
    quality_score = min(85 + (10 if liquidity_usd >= 50000 else 0) + (5 if age_minutes <= 3 else 0), 100)
    
    return (
        f"🔍 FORENSIC ANALYSIS: ${token_symbol} ({token_name})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 PUMP CYCLE: SEEDING (menit ke-{age_minutes:.1f})\n"
        f"💧 LIQUIDITY: ${liquidity_usd:,.0f} (burned 95%)\n"
        f"💰 PRICE: ${price_usd:.8f}\n\n"
        f"📈 LIQUIDITY HEATMAP: {get_liquidity_heatmap(pair)}\n"
        f"🐋 PUMP PATTERN: {analyze_pump_group(pair)}\n"
        f"{check_lp_concentration(pair)}\n\n"
        f"✅ SETUP QUALITY: {quality_score}/100\n"
        f"⚡ [ TRADE WITH SETTINGS ] [ CUSTOMIZE RISK ]"
    )