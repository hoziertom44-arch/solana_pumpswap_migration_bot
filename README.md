<h1 align="center">SOLANA SNIPER BOT</h1>

<p align="center">
  <strong>Pump.fun + Meteora · Built in Python · Free</strong>
</p>

<p align="center">
  Snipes memecoins the second they migrate. Dual launchpad, scam filters baked in, live PnL tracking.
</p>

<p align="center">
  <a href="https://youtu.be/0UsQ3zcf2SU">Watch the build</a> ·
  <a href="https://t.me/rektcodercommunity">Join community</a> ·
  <a href="https://github.com/hoziertom44-arch/solana_pumpswap_migration_bot/issues">Report issue</a>
</p>

---

​```bash
git clone https://github.com/hoziertom44-arch/solana_pumpswap_migration_bot
cd solana_pumpswap_migration_bot
pip install -r requirements.txt
python main.py
​```

---

## the idea

Most sniper bots watch one launchpad and buy anything. This one watches two and filters out 90% of what crosses the wire.

It doesn't snipe launches. It snipes migrations — the moment a token graduates from a bonding curve to a real AMM pool. That's when liquidity is locked, the token survived initial selling pressure, and price discovery actually starts.

The market does the filtering for you. The bot just catches the survivors.

## what it does

​```
pump.fun migration ─┐
                    ├─→ filters ─→ buy ─→ live pnl ─→ sell
meteora migration ──┘
​```

Two websocket listeners, four filters, two buy paths, one terminal UI. Six Python files total.

**Filters**
- Word blacklist (partial + exact match)
- Dev wallet history (skip if creator launched > N tokens)
- Duplicate names within session
- Stale migration cutoff (120s)

**Buy paths**
- Pump Portal trade API for pump.fun tokens
- Jupiter swap for Meteora tokens

**Tracking**
- Live PnL every 5s via Jupiter quote
- Real wallet balance diff for actual profit

## setup

You'll need three things — none of them cost money to get started.

| | |
|---|---|
| [Helius](https://www.helius.dev) | RPC + websocket |
| [Pump Portal](https://pumpportal.fun) | Pump.fun trades + free wallet |
| [Phantom](https://phantom.app) | View your bot wallet |

Copy `.env.example` to `.env` and fill it in:

​```env
HELIUS_API_KEY=
HELIUS_RPC_URL=https://mainnet.helius-rpc.com/?api-key=
HELIUS_WS_URL=wss://mainnet.helius-rpc.com/?api-key=
PUMPPORTAL_API_KEY=
WALLET_PUBLIC_KEY=
WALLET_PRIVATE_KEY=
​```

Fund the Pump Portal wallet with some SOL. 0.1 to 0.5 is enough to test.

Pump Portal doesn't have a UI for the wallet it generates, so import the private key into Phantom if you want to see what's happening.

## tuning

Everything lives in `config.py`.

​```python
LAUNCHPAD = "both"          # pumpfun / meteora / both
AUTO_BUY = False            # start false, watch first
BUY_AMOUNT_SOL = 0.05
SLIPPAGE = 15
MAX_DEV_TOKENS = 5          # skip serial scammers
SKIP_DUPLICATE_NAMES = True
​```

Two presets I run depending on the day:

​```python
# aggressive — more catches, more rugs
MAX_DEV_TOKENS = 15
BUY_AMOUNT_SOL = 0.1

# conservative — fewer catches, cleaner picks
MAX_DEV_TOKENS = 2
BUY_AMOUNT_SOL = 0.01
ASCII_NAMES_ONLY = True
​```

## how the dev check works

When a migration hits, the bot calls Helius `getAssetsByCreator` and counts how many tokens this wallet has launched. If it's above `MAX_DEV_TOKENS`, skip.

Real builders launch one or two tokens. Scam farms launch fifty. This single filter kills more rugs than every other check combined.

## how the freshness check works

For Meteora migrations the bot pulls `pairCreatedAt` from DexScreener. Anything older than 120 seconds gets dropped — by then the snipe window is closed and you're just exit liquidity for whoever caught it first.

## from the demo

The video walks through a real run end to end:

​```
start          0.508 SOL
caught         pump.fun migration
bought         0.1 SOL
low            -71%
peak           +200%
sold           +0.044 SOL
​```

→ [youtu.be/0UsQ3zcf2SU](https://youtu.be/0UsQ3zcf2SU)

## stack

Python 3.10+, websockets, requests, rich, solders, solana-py, python-dotenv.

That's it. No frameworks, no SDK soup.

## files

​```
main.py            listeners + main loop
trade.py           buy/sell + dev history
display.py         terminal UI
balance.py         wallet helpers
config.py          all settings
requirements.txt
​```

## disclaimer

For education. Sniping memecoins is high risk and most tokens go to zero. Don't trade money you can't lose. Not financial advice.

## who

Built by Tom — [@rektcoder](https://www.youtube.com/@rektcoder). I drop a new bot every week, all open source, all on telegram.

[YouTube](https://www.youtube.com/@rektcoder) · [Channel](https://t.me/rektcoderchannel) · [Community](https://t.me/rektcodercommunity) · [Twitter](https://x.com/rektcoder_)

## license

MIT.
