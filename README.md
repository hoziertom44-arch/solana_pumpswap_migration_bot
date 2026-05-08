<!-- ============================================ -->
<!--   SOLANA SNIPER BOT — README                 -->
<!--   github.com/hoziertom44-arch                -->
<!-- ============================================ -->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,30&height=220&section=header&text=SOLANA%20SNIPER%20BOT&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Pump.fun%20%2B%20Meteora%20%C2%B7%20Built%20in%20Python%20%C2%B7%20Free&descAlignY=58&descSize=18" width="100%" />

<br/>

<a href="https://youtu.be/0UsQ3zcf2SU"><img src="https://img.shields.io/badge/▶_Watch_The_Build-FF0000?style=for-the-badge&logoColor=white" /></a>
<a href="https://t.me/rektcodercommunity"><img src="https://img.shields.io/badge/Join_Community-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>
<a href="https://x.com/rektcoder_"><img src="https://img.shields.io/badge/Follow-000000?style=for-the-badge&logo=x&logoColor=white" /></a>

<br/><br/>

<img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/solana-9945FF?style=flat-square&logo=solana&logoColor=white" />
<img src="https://img.shields.io/badge/pump.fun-00D632?style=flat-square" />
<img src="https://img.shields.io/badge/meteora-FF6B35?style=flat-square" />
<img src="https://img.shields.io/badge/jupiter-FBA43A?style=flat-square" />
<img src="https://img.shields.io/badge/helius-7B3FF2?style=flat-square" />
<img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" />

<br/><br/>

<a href="https://readme-typing-svg.demolab.com">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&pause=1000&color=9945FF&center=true&vCenter=true&width=600&lines=Snipes+memecoins+the+second+they+migrate.;Dual+launchpad.+Filters+the+rugs.+Free+code." />
</a>

</div>

<br/>

> **It doesn't snipe launches. It snipes migrations.** The market filters the dead tokens for you. The bot just catches the survivors.

<br/>

## ⚡ quickstart

​```bash
git clone https://github.com/hoziertom44-arch/solana_pumpswap_migration_bot
cd solana_pumpswap_migration_bot
pip install -r requirements.txt
python main.py
​```

<br/>

## 🎯 how it works

<div align="center">

​```
   ┌───────────────────┐         ┌───────────────────┐
   │  pump.fun migrate │         │  meteora migrate  │
   │   (pump portal)   │         │     (helius)      │
   └─────────┬─────────┘         └─────────┬─────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
                   ╔════════════════╗
                   ║  scam filters  ║
                   ╚════════╤═══════╝
                            ▼
                   ╔════════════════╗
                   ║   auto buy     ║
                   ╚════════╤═══════╝
                            ▼
                   ╔════════════════╗
                   ║  live pnl 5s   ║
                   ╚════════╤═══════╝
                            ▼
                   ╔════════════════╗
                   ║  manual sell   ║
                   ╚════════════════╝
​```

</div>

<table>
<tr>
<td width="33%" valign="top">

#### 🎧 listeners
Pump Portal websocket for pump.fun. Helius websocket for Meteora DBC. Both fire the second a token graduates.

</td>
<td width="33%" valign="top">

#### 🛡️ filters
Blacklist words. Dev wallet history. Duplicate name skip. Freshness cutoff at 120s. Most rugs die here.

</td>
<td width="33%" valign="top">

#### 💸 execution
Pump Portal for pump.fun, Jupiter swap for Meteora. Real wallet balance diff for true PnL — no estimates.

</td>
</tr>
</table>

<br/>

## 🛠️ setup

You need three things. All free to start.

<table>
<tr>
<td width="33%" align="center">
  <a href="https://www.helius.dev">
    <img src="https://img.shields.io/badge/HELIUS-7B3FF2?style=for-the-badge&logoColor=white" /><br/>
    <sub>RPC + Websocket</sub>
  </a>
</td>
<td width="33%" align="center">
  <a href="https://pumpportal.fun">
    <img src="https://img.shields.io/badge/PUMP_PORTAL-00D632?style=for-the-badge&logoColor=white" /><br/>
    <sub>Pump.fun trades + wallet</sub>
  </a>
</td>
<td width="33%" align="center">
  <a href="https://phantom.app">
    <img src="https://img.shields.io/badge/PHANTOM-AB9FF2?style=for-the-badge&logoColor=white" /><br/>
    <sub>View your bot wallet</sub>
  </a>
</td>
</tr>
</table>

Copy `.env.example` to `.env` and fill it in:

​```env
HELIUS_API_KEY=
HELIUS_RPC_URL=https://mainnet.helius-rpc.com/?api-key=
HELIUS_WS_URL=wss://mainnet.helius-rpc.com/?api-key=
PUMPPORTAL_API_KEY=
WALLET_PUBLIC_KEY=
WALLET_PRIVATE_KEY=
​```

Fund the Pump Portal wallet with 0.1–0.5 SOL to test. Import the private key into Phantom so you can actually see what your bot is doing.

<br/>

## 🎛️ tuning

Everything lives in `config.py`.

​```python
LAUNCHPAD = "both"          # pumpfun / meteora / both
AUTO_BUY = False            # start false, watch first
BUY_AMOUNT_SOL = 0.05
SLIPPAGE = 15
MAX_DEV_TOKENS = 5          # skip serial scammers
SKIP_DUPLICATE_NAMES = True
​```

<table>
<tr>
<td width="50%" valign="top">

#### 🔥 aggressive
More catches, more rugs.

​```python
MAX_DEV_TOKENS = 15
BUY_AMOUNT_SOL = 0.1
​```

</td>
<td width="50%" valign="top">

#### 🛡️ conservative
Fewer catches, cleaner picks.

​```python
MAX_DEV_TOKENS = 2
BUY_AMOUNT_SOL = 0.01
ASCII_NAMES_ONLY = True
​```

</td>
</tr>
</table>

<br/>

## 🧠 the filters

#### dev wallet check
Bot calls Helius `getAssetsByCreator` and counts how many tokens this wallet has launched. Above `MAX_DEV_TOKENS` → skip. Real builders launch one or two. Scam farms launch fifty.

#### freshness check
Pulls `pairCreatedAt` from DexScreener for Meteora migrations. Older than 120s → skip. Late entry just means buying someone else's exit liquidity.

<br/>

## 📊 from the demo

<div align="center">

| | |
|---|---|
| **start** | 0.508 SOL |
| **caught** | pump.fun migration |
| **bought** | 0.1 SOL |
| **low** | <kbd>-71%</kbd> |
| **peak** | <kbd>+200%</kbd> |
| **sold** | <kbd>+0.044 SOL</kbd> |

<br/>

<a href="https://youtu.be/0UsQ3zcf2SU">
  <img src="https://img.shields.io/badge/▶_Watch_Full_Demo-FF0000?style=for-the-badge&logoColor=white" />
</a>

</div>

<br/>

## 📁 files

​```
main.py            listeners + main loop
trade.py           buy / sell + dev history
display.py         terminal UI
balance.py         wallet helpers
config.py          all settings
requirements.txt   dependencies
​```

<br/>

## 📦 stack

<p align="center">
<img src="https://skillicons.dev/icons?i=python,vscode,github" />
</p>

Python 3.10+, websockets, requests, rich, solders, solana-py, python-dotenv. No frameworks, no SDK soup.

<br/>

## ⚠️ disclaimer

For education. Sniping memecoins is extremely high risk and most tokens go to zero. Don't trade money you can't afford to lose. Not financial advice.

<br/>

## 👤 who

<div align="center">

Built by **Tom** — I drop a new bot every week, all open source, all free.

<a href="https://www.youtube.com/@rektcoder"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" /></a>
<a href="https://t.me/rektcoderchannel"><img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>
<a href="https://t.me/rektcodercommunity"><img src="https://img.shields.io/badge/Community-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" /></a>
<a href="https://x.com/rektcoder_"><img src="https://img.shields.io/badge/Twitter-000000?style=for-the-badge&logo=x&logoColor=white" /></a>

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,30&height=120&section=footer" width="100%" />

</div>
