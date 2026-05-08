

## ⚡ Quick Start

### 1️⃣ Clone the repo

```bash
git clone https://github.com/hoziertom44-arch/solana_pumpswap_migration_bot.git
cd solana_pumpswap_migration_bot
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Get your API keys

| Service | Link | Purpose |
|---|---|---|
| 🟣 **Helius** | [helius.dev](https://www.helius.dev) | RPC + Websocket (free tier works) |
| 🟢 **Pump Portal** | [pumpportal.fun](https://pumpportal.fun) | Pump.fun trade API + free wallet |
| 🔵 **Phantom** | [phantom.app](https://phantom.app) | View / manage your bot wallet |

### 4️⃣ Configure your `.env`

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

### 5️⃣ Fund the Pump Portal wallet

Send some SOL to the wallet Pump Portal generated. Start small.

> 💡 **Tip:** 0.1 to 0.5 SOL is plenty for testing.

### 6️⃣ Import the wallet into Phantom (recommended)

Pump Portal doesn't give you a UI to view balances or transactions. Import the private key into Phantom so you can actually see what your bot is doing.

### 7️⃣ Run the bot

```bash
python main.py
```

---

## ⚙️ Configuration

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

### 🎛️ Tuning Presets

<table>
<tr>
<td>

**🔥 Aggressive**
*More catches, more rugs*

```python
MAX_DEV_TOKENS = 15
BUY_AMOUNT_SOL = 0.1
```

</td>
<td>

**🛡️ Conservative**
*Fewer catches, cleaner picks*

```python
MAX_DEV_TOKENS = 2
BUY_AMOUNT_SOL = 0.01
ASCII_NAMES_ONLY = True
```

</td>
</tr>
</table>

---

## 🧠 How It Works

### Dev Wallet Check

Every time a new migration hits, the bot calls Helius's `getAssetsByCreator` and asks **how many other tokens this developer has launched**. If the answer is more than `MAX_DEV_TOKENS`, the bot skips the trade.

> Real builders don't launch 50 tokens. Scam farms do.
> This single filter alone kills a huge chunk of the rugs that even experienced traders fall for.

### Freshness Check

After detecting a Meteora migration, the bot calls DexScreener and checks `pairCreatedAt`. If the migration is older than **120 seconds**, the bot skips it.

> Old migrations are usually already pumped and dumped. Buying late means buying someone's exit liquidity.

---

## 🎬 Live Demo

[![Watch the demo](https://img.shields.io/badge/▶_Watch_the_Live_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/0UsQ3zcf2SU)

**Sample run from the video:**

| Metric | Value |
|---|---|
| Starting balance | `0.508 SOL` |
| Migration caught | ✅ Pump.fun |
| Bought | `0.1 SOL` worth |
| Lowest PnL | `-71%` |
| Peak PnL | `+200%` |
| Final profit | `+0.044 SOL` |

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Solana](https://img.shields.io/badge/Solana-9945FF?style=flat-square&logo=solana&logoColor=white)
![Websockets](https://img.shields.io/badge/Websockets-010101?style=flat-square&logo=socket.io&logoColor=white)
![Jupiter](https://img.shields.io/badge/Jupiter_Swap-FBA43A?style=flat-square)
![Helius](https://img.shields.io/badge/Helius_RPC-7B3FF2?style=flat-square)
![Pump.fun](https://img.shields.io/badge/Pump.fun-00D632?style=flat-square)
![Meteora](https://img.shields.io/badge/Meteora_DBC-FF6B35?style=flat-square)

</div>

| Library | Purpose |
|---|---|
| `websockets` | Pump Portal + Helius streams |
| `requests` | HTTP calls to Helius, Jupiter, DexScreener |
| `rich` | Terminal UI |
| `solders` + `solana-py` | Wallet signing for Meteora trades |
| `python-dotenv` | Environment variable loading |

---

## 🤝 Contributing

PRs are welcome. If you build something cool on top of this, tag me.

```bash
# Fork the repo, make your changes, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a PR
```

---

## ⚠️ Disclaimer

> **This bot is for educational purposes only.**
>
> Sniping memecoins is extremely high risk. Most tokens go to zero. Never invest more than you're willing to lose. This is not financial advice. Trade at your own risk.

---

## 👤 Author

<div align="center">

**Built by Tom @ RektCoder**

I build crypto bots from scratch, test them with real money on chain, and give you the full source code completely free. New bot every week.

[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@rektcoder)
[![Telegram](https://img.shields.io/badge/Telegram_Channel-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/rektcoderchannel)
[![Community](https://img.shields.io/badge/Community_Group-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/rektcodercommunity)
[![Twitter](https://img.shields.io/badge/Twitter-Follow-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/rektcoder_)

</div>

---

## 📜 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**MIT** — use it, fork it, ship it.

---

<div align="center">

### ⭐ If this bot helped you, drop a star

Made with ☕ and a lot of solana

</div>
