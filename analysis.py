def generate_forensic_report(token_data, dex_data=None):
    """Buat laporan analisis dari Pump.fun + DexScreener"""
    token_name = token_data.get("name", "Unknown")
    token_symbol = token_data.get("symbol", "???")
    liquidity = token_data.get("liquidity", 0)
    price = token_data.get("price", 0)
    market_cap = token_data.get("market_cap", 0)
    created_at = token_data.get("created_timestamp", 0) / 1000
    age_minutes = (datetime.now(timezone.utc).timestamp() - created_at) / 60
    
    # Analisis dasar
    if liquidity >= 50000:
        liquidity_heatmap = "🟢 LOW SLIPPAGE (<15%)"
    elif liquidity >= 20000:
        liquidity_heatmap = "🟡 MODERATE SLIPPAGE (15-40%)"
    else:
        liquidity_heatmap = "🔴 HIGH SLIPPAGE (>40%)"
    
    # Hitung quality score
    quality_score = 85
    if liquidity >= 50000:
        quality_score += 10
    if age_minutes <= 3:
        quality_score += 5
    quality_score = min(quality_score, 100)
    
    return (
        f"🔍 FORENSIC ANALYSIS: ${token_symbol} ({token_name})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 PUMP CYCLE: SEEDING (menit ke-{age_minutes:.1f})\n"
        f"💧 LIQUIDITY: ${liquidity:,.0f}\n"
        f"💰 MARKET CAP: ${market_cap:,.0f}\n"
        f"📈 LIQUIDITY HEATMAP: {liquidity_heatmap}\n\n"
        f"✅ SETUP QUALITY: {quality_score}/100\n"
        f"⚡ [ TRADE WITH SETTINGS ] [ CUSTOMIZE RISK ]"
    )
