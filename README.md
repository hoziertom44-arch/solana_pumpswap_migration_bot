

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/hoziertom44-arch/solana_pumpswap_migration_bot.git
cd solana_pumpswap_migration_bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your API keys

| Service | Link | Purpose |
|---|---|---|
| Helius | https://www.helius.dev | RPC + Websocket (free tier works) |
| Pump Portal | https://pumpportal.fun | Pump.fun trade API + free wallet |
| Phantom | https://phantom.app | View / manage your bot wallet |

### 4. Configure your .env

Copy the template and fill it in:

```bash
cp .env.example .env
```

Then paste your keys:

```env
HELIUS_API_KEY=your_helius_api_key
HELIUS_RPC_URL=https://mainnet.helius-rpc.com/?api-key=your_helius_api_key
HELIUS_WS_URL=wss://mainnet.helius-rpc.com/?api-key=your_helius_api_key
PUMPPORTAL_API_KEY=your_pumpportal_api_key
WALLET_PUBLIC_KEY=your_wallet_public_address
WALLET_PRIVATE_KEY=your_wallet_private_key
```

### 5. Fund the Pump Portal wallet

Send some SOL to the wallet address Pump Portal generated. Start small. 0.1 to 0.5 SOL is plenty for testing.

### 6. (Recommended) Import the wallet into Phantom

Pump Portal doesn't give you a UI to view balances or transactions. Import the private key into Phantom so you can actually see what your bot is doing.

### 7. Run the bot

```bash
python main.py
```

---

## Configuration

Open `config.py` and tune the bot to your risk tolerance.

### Trade settings

```python
LAUNCHPAD = "both"          # "pumpfun" / "meteora" / "both"
AUTO_BUY = False            # Start False to watch, flip to True to go live
BUY_AMOUNT_SOL = 0.05       # SOL to spend per snipe
SLIPPAGE = 15               # 15% — needed for fresh migrations
PRIORITY_FEE = 0.0005       # Validator tip for faster execution
COOLDOWN_SECONDS = 5        # Wait time between buys
```

### Scam filters

```python
BLACKLISTED_WORDS = {        # Partial match — blocks "ultra mega tesla coin"
    "spacex", "tesla", "apple inc", "google", "microsoft", "amazon",
    "nvidia", "openai", "chatgpt", "claude ai",
    "biden", "obama", "putin",
    "meteora lp", "lp token", "raydium",
    "binance", "coinbase", "robinhood",
}

BLACKLISTED_EXACT = {        # Exact match — for short keywords
    "sol", "btc", "eth", "bnb", "xrp", "usdt", "usdc",
    "lp", "test", "token", "airdrop",
}

MIN_NAME_LENGTH = 2          # Skip empty / single-char names
SKIP_DUPLICATE_NAMES = True  # Skip repeat token names in same session
ASCII_NAMES_ONLY = False     # Skip non-ASCII names if True
MAX_DEV_TOKENS = 5           # Skip if dev launched more than 5 tokens
```

### Tuning presets

**Aggressive (more catches, more rugs):**
- `MAX_DEV_TOKENS = 15`
- `BUY_AMOUNT_SOL = 0.1`

**Conservative (fewer catches, cleaner picks):**
- `MAX_DEV_TOKENS = 2`
- `BUY_AMOUNT_SOL = 0.01`
- `ASCII_NAMES_ONLY = True`

---

## How the dev wallet check works

Every time a new migration hits, the bot calls Helius's `getAssetsByCreator` and asks how many other tokens this developer has launched. If the answer is more than `MAX_DEV_TOKENS`, the bot skips the trade. Real builders don't launch 50 tokens. Scam farms do.

This single filter alone kills a huge chunk of the rugs that even experienced traders fall for.

---

## How the freshness check works

After detecting a Meteora migration, the bot calls DexScreener and checks `pairCreatedAt`. If the migration is older than 120 seconds, the bot skips it. Old migrations are usually already pumped and dumped. Buying late means buying someone's exit liquidity.

---

## Live demo

Watch the full live demo in the YouTube video:

▶️ https://youtu.be/0UsQ3zcf2SU

Sample run from the video:
- Started with 0.508 SOL
- Bot caught a Pump.fun migration on its own
- Bought 0.1 SOL worth
- Trade dipped to -71% then recovered to +200%
- Manually sold for +0.044 SOL profit

---

## Tech stack

- **Python 3.10+**
- **websockets** — Pump Portal + Helius streams
- **requests** — HTTP calls to Helius, Jupiter, DexScreener
- **rich** — Terminal UI
- **solders** + **solana-py** — Wallet signing for Meteora trades
- **python-dotenv** — Environment variable loading

---

## Disclaimer

This bot is for educational purposes only.

Sniping memecoins is extremely high risk. Most tokens go to zero. Never invest more than you're willing to lose. This is not financial advice. Trade at your own risk.

---

## Author

Built by Tom from RektCoder.

- 📺 **YouTube:** https://www.youtube.com/@rektcoder
- 💬 **Telegram:** https://t.me/rektcoderchannel
- 👥 **Community:** https://t.me/rektcodercommunity
- 🐦 **Twitter / X:** https://x.com/rektcoder_

---

## License

MIT — use it, fork it, ship it. If you build something cool with it, tag me.
