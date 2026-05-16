# ============================================
# RektCoder — Terminal Display
# ============================================

import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
monitoring = False

# Layout constants
WIDTH = 70

# Colors
PRIMARY = "bright_magenta"
ACCENT = "cyan"
SUCCESS = "bright_green"
DANGER = "bright_red"
WARNING = "yellow"
DIM = "grey50"
MUTED = "grey42"


def print_header():
    console.print()
    text = Text()
    text.append("⚡ ", style=WARNING)
    text.append("REKT", style=f"bold {DANGER}")
    text.append("CODER", style=f"bold {PRIMARY}")
    text.append("  ·  Memecoin Sniper Bot  ·  ", style=DIM)
    text.append("v2.0", style=MUTED)

    panel = Panel(
        text,
        box=box.DOUBLE,
        border_style=PRIMARY,
        padding=(0, 2),
        width=WIDTH,
    )
    console.print(panel)


def print_config(config):
    auto = f"[bold {SUCCESS}]ON[/]" if config.AUTO_BUY else f"[bold {DANGER}]OFF[/]"

    table = Table(
        box=box.ROUNDED,
        border_style=DIM,
        show_header=False,
        padding=(0, 2),
        width=WIDTH,
    )
    table.add_column(style=MUTED, width=14, no_wrap=True)
    table.add_column(no_wrap=True)

    table.add_row("Auto Buy", auto)
    table.add_row("Buy Amount", f"[bold {WARNING}]{config.BUY_AMOUNT_SOL} SOL[/]")
    table.add_row("Slippage", f"{config.SLIPPAGE}%")
    table.add_row("Priority Fee", f"{config.PRIORITY_FEE} SOL")
    table.add_row("Mode", f"[{ACCENT}]{config.LAUNCHPAD.upper()}[/]")

    console.print(table)


def print_wallet_balance(balance):
    if balance is None:
        console.print(f"[{DANGER}]⚠  Could not fetch wallet balance[/]")
        return

    bal_color = SUCCESS if balance > 0.05 else WARNING
    text = Text()
    text.append("💰 Wallet  ", style=DIM)
    text.append(f"{balance:.4f} SOL", style=f"bold {bal_color}")

    panel = Panel(
        text,
        box=box.ROUNDED,
        border_style=DIM,
        padding=(0, 2),
        width=WIDTH,
    )
    console.print(panel)


def print_listening_status(total_migrations=0, total_bought=0):
    text = Text()
    text.append("● ", style=f"bold {SUCCESS}")
    text.append("LIVE", style=f"bold {SUCCESS}")
    text.append("  │  ", style=DIM)
    text.append("Migrations ", style=DIM)
    text.append(f"{total_migrations}", style="bold white")
    text.append("   Bought ", style=DIM)
    text.append(f"{total_bought}", style=f"bold {WARNING}")
    text.append("   ", style=DIM)
    text.append("● Listening", style=f"italic {DIM}")
    console.print(text)
    console.print()


def print_status(total_migrations, total_bought):
    print_listening_status(total_migrations, total_bought)


def print_new_token(data, source="pumpfun"):
    name = data.get("name", "") or "Unknown"
    symbol = data.get("symbol", "") or "???"
    mint = data.get("mint", "")

    if source == "pumpfun":
        src_color = SUCCESS
        src_icon = "🟢"
        src_label = "PUMP.FUN"
    else:
        src_color = WARNING
        src_icon = "🟠"
        src_label = "METEORA"

    title = Text()
    title.append("🎯 MIGRATION ", style=f"bold {ACCENT}")
    title.append("•  ", style=DIM)
    title.append(f"{src_icon} {src_label}", style=f"bold {src_color}")

    table = Table(
        box=None,
        show_header=False,
        padding=(0, 1),
        expand=False,
    )
    table.add_column(style=MUTED, width=8, no_wrap=True)
    table.add_column(no_wrap=False)

    table.add_row("Name", f"[bold white]{name}[/] [{DIM}]({symbol})[/]")
    table.add_row("Chart", f"[{ACCENT}]https://dexscreener.com/solana?q={mint}[/]")
    table.add_row("Chart", f"[{ACCENT}]https://dexscreener.com/solana/{mint}[/]")

    panel = Panel(
        table,
        title=title,
        title_align="left",
        box=box.ROUNDED,
        border_style=src_color,
        padding=(0, 1),
        width=WIDTH,
    )
    console.print()
    console.print(panel)


def print_buying(amount):
    console.print(f"[{WARNING}]⚡ Sniping[/] [white]→[/] Buying [bold {WARNING}]{amount} SOL[/]...")


def print_buy_result(success, txid=None, error=None):
    if success:
        console.print(f"[bold {SUCCESS}]✓ SNIPED[/]")
        if txid:
            console.print(
                f"[{DIM}]  ↳ [/][{ACCENT}]https://solscan.io/tx/{txid}[/]",
                soft_wrap=True, overflow="ignore", crop=False,
            )
    else:
        console.print(f"[bold {DANGER}]✗ Buy failed:[/] [{DANGER}]{error}[/]")
    console.print()


def print_skip(reason):
    console.print(f"[{WARNING}]⊘ {reason}[/]")
    console.print()


def print_pnl_update(position, price_data, real_sol_out=None):
    name = position["name"]
    entry_sol = position["entry_sol"]
    entry_price = position.get("entry_price", 0)
    now = time.strftime("%H:%M:%S")

    # Truncate name to fit
    name_disp = name[:14].ljust(14)

    if not price_data:
        line = f"[{DIM}][{now}][/] [bold white]{name_disp}[/] [{WARNING}]⏳ Waiting for price...[/]"
        print("\r\033[K", end="")
        console.print(line, end="\r", soft_wrap=True, overflow="ignore", crop=False)
        return

    price_usd = price_data["price_usd"]
    market_cap = price_data["market_cap"]

    if entry_price == 0 and price_usd > 0:
        position["entry_price"] = price_usd
        entry_price = price_usd

    if position["name"] == "Unknown" and price_data.get("name"):
        position["name"] = price_data["name"]
        name = position["name"]
        name_disp = name[:14].ljust(14)

    if entry_price <= 0:
        line = f"[{DIM}][{now}][/] [bold white]{name_disp}[/] [{WARNING}]⏳ Setting entry...[/]"
        print("\r\033[K", end="")
        console.print(line, end="\r", soft_wrap=True, overflow="ignore", crop=False)
        return

    # PnL
    if real_sol_out is not None and real_sol_out > 0:
        pnl_sol = real_sol_out - entry_sol
        pnl_pct = (pnl_sol / entry_sol) * 100
        label = "REAL"
    else:
        pnl_pct = ((price_usd - entry_price) / entry_price) * 100
        pnl_sol = entry_sol * (pnl_pct / 100)
        label = "EST "

    pnl_color = SUCCESS if pnl_pct >= 0 else DANGER
    arrow = "▲" if pnl_pct >= 0 else "▼"
    sign = "+" if pnl_pct >= 0 else ""

    if market_cap >= 1_000_000:
        mcap = f"${market_cap / 1_000_000:.1f}M"
    elif market_cap >= 1000:
        mcap = f"${market_cap / 1000:.1f}K"
    else:
        mcap = f"${market_cap:,.0f}"
    mcap = mcap.ljust(7)

    label_color = SUCCESS if (label == "REAL" and pnl_pct >= 0) else (DANGER if label == "REAL" else MUTED)

    line = (
        f"[{DIM}][{now}][/] "
        f"[bold white]{name_disp}[/] "
        f"[{DIM}]│[/] [white]${price_usd:.8f}[/] "
        f"[{DIM}]│[/] [white]{mcap}[/] "
        f"[{DIM}]│[/] [{label_color}]{label}[/] "
        f"[bold {pnl_color}]{arrow}{sign}{pnl_pct:>6.2f}%[/] "
        f"[{DIM}]│[/] [{pnl_color}]{sign}{pnl_sol:.4f} SOL[/]"
    )
    print("\r\033[K", end="")
    console.print(line, end="\r", soft_wrap=True, overflow="ignore", crop=False)


def print_monitoring_start():
    print()  # newline after buy link
    text = Text()
    text.append("💎 ", style="")
    text.append("MONITORING", style=f"bold {ACCENT}")
    text.append("  ·  type ", style=DIM)
    text.append("sell", style=f"bold {WARNING}")
    text.append(" + Enter to exit", style=DIM)
    console.print(text)
    console.rule(style=DIM, characters="─")


def print_selling(name):
    print()  # newline after PnL
    print()
    console.print(f"[bold {WARNING}]🔄 Selling 100% of[/] [bold white]{name}[/][bold {WARNING}]...[/]")


def print_sell_result(success, name=None, bal_before=None, bal_after=None, txid=None, error=None):
    if not success:
        console.print(f"[bold {DANGER}]✗ Sell failed:[/] [{DANGER}]{error}[/]")
        console.print(f"[{WARNING}]Try again or sell manually on Phantom[/]")
        console.print()
        return

    pnl = bal_after - bal_before if (bal_before and bal_after) else None
    pnl_color = SUCCESS if (pnl is None or pnl >= 0) else DANGER
    pnl_icon = "🚀" if (pnl and pnl > 0) else ("💀" if (pnl and pnl < 0) else "✓")

    title = Text()
    title.append(f"{pnl_icon}  CLOSED  ", style=f"bold {pnl_color}")
    title.append("·  ", style=DIM)
    title.append(name or "Token", style="bold white")

    table = Table(
        box=None,
        show_header=False,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style=MUTED, width=20, no_wrap=True)
    table.add_column(justify="right", width=22, no_wrap=True)

    if bal_before is not None and bal_after is not None:
        sign = "+" if pnl >= 0 else ""
        pct = (pnl / bal_before * 100) if bal_before > 0 else 0

        table.add_row("Wallet (pre-buy)", f"[white]{bal_before:.6f} SOL[/]")
        table.add_row("Wallet (post-sell)", f"[white]{bal_after:.6f} SOL[/]")
        table.add_row(f"[{DIM}]{'─' * 20}[/]", f"[{DIM}]{'─' * 22}[/]")
        table.add_row("Round-trip P&L", f"[bold {pnl_color}]{sign}{pnl:.6f} SOL[/]")
        table.add_row("P&L %", f"[bold {pnl_color}]{sign}{pct:.2f}%[/]")

    panel = Panel(
        table,
        title=title,
        title_align="left",
        box=box.HEAVY,
        border_style=pnl_color,
        padding=(0, 1),
        width=WIDTH,
    )
    console.print(panel)
    if txid:
        console.print(
            f"[{DIM}]  🔗 [/][{ACCENT}]https://solscan.io/tx/{txid}[/]",
            soft_wrap=True, overflow="ignore", crop=False,
        )
    console.print()


def print_continue_prompt():
    console.print(f"[bold {ACCENT}]▶ [/] [bold white]Continue sniping?[/] [{DIM}](yes/no): [/]", end="")


def print_info(msg):
    if not monitoring:
        console.print(f"[{DIM}]{msg}[/]", soft_wrap=True, overflow="ignore", crop=False)


def print_error(msg):
    console.print(f"[bold {DANGER}]✗ {msg}[/]")


def print_final_stats(total_migrations, total_bought):
    console.print()

    table = Table(
        box=None,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column(style=MUTED, width=22, no_wrap=True)
    table.add_column(justify="right", width=12, no_wrap=True)
    table.add_row("Migrations Detected", f"[bold white]{total_migrations}[/]")
    table.add_row("Tokens Bought", f"[bold {WARNING}]{total_bought}[/]")

    panel = Panel(
        table,
        title=f"[bold {ACCENT}]📊 Session Stats[/]",
        title_align="left",
        box=box.ROUNDED,
        border_style=PRIMARY,
        padding=(0, 1),
        width=WIDTH,
    )
    console.print(panel)
    console.print()
    console.print(f"[{DIM}]Thanks for using[/] [bold {PRIMARY}]RektCoder[/] [{DIM}]·[/] [{ACCENT}]youtube.com/@RektCoder[/]")
    console.print()
