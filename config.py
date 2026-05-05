# ============================================
# RektCoder — Memecoin Sniper Bot
# Configuration — trade settings
# ============================================

# ── Launchpad ────────────────────────────────
# "pumpfun"   → PumpPortal websocket + PumpPortal trade
# "meteora"   → Helius websocket watching DBC + Jupiter swap
# "both"      → Watch both simultaneously
LAUNCHPAD = "pumpfun"

# ── Trade settings ───────────────────────────
AUTO_BUY = True
BUY_AMOUNT_SOL = 0.1
SLIPPAGE = 15
PRIORITY_FEE = 0.0005

# ── Pool for pump.fun tokens ────────────────
BUY_POOLS = ["pump-amm", "auto"]

# ── Cooldown ─────────────────────────────────
COOLDOWN_SECONDS = 5

# ── PumpPortal (pump.fun buy/sell) ───────────
WS_URL = "wss://pumpportal.fun/api/data"
TRADE_URL = "https://pumpportal.fun/api/trade"

# ── Meteora DBC program ─────────────────────
METEORA_DBC_PROGRAM = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"

# ── Jupiter swap API ────────────────────────
JUPITER_QUOTE_URL = "https://lite-api.jup.ag/swap/v1/quote"
JUPITER_SWAP_URL = "https://lite-api.jup.ag/swap/v1/swap"

# ── SOL mint ────────────────────────────────
SOL_MINT = "So11111111111111111111111111111111111111112"

# ── Scam filters ───────────────────────────
# Skip tokens containing these words in the name (case-insensitive partial match)
BLACKLISTED_WORDS = {
    "spacex", "tesla", "apple inc", "google", "microsoft", "amazon",
    "nvidia", "openai", "chatgpt", "claude ai",
    "biden", "obama", "putin",
    "meteora lp", "lp token", "raydium",
    "binance", "coinbase", "robinhood",
}

# Exact name matches to skip (case-insensitive)
BLACKLISTED_EXACT = {
    "sol", "btc", "eth", "bnb", "xrp", "usdt", "usdc",
    "lp", "test", "token", "airdrop",
}

# Skip tokens with names shorter than this
MIN_NAME_LENGTH = 2

# Skip duplicate token names in same session
SKIP_DUPLICATE_NAMES = True

# Only allow ASCII names (skip Chinese/Arabic/emoji-only names)
ASCII_NAMES_ONLY = False

# Max tokens a dev can have created before we flag as scam farm
# Set to 0 to disable dev history check
MAX_DEV_TOKENS = 5