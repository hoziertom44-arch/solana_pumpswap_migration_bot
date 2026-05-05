# ============================================
# RektCoder — Memecoin Sniper Bot
# Dual launchpad: PumpFun + Meteora DBC
# ============================================

import asyncio
import json
import time
import sys
import os
import re
import select
import websockets
import requests
from dotenv import load_dotenv

import config
import trade
import display
from display import (
    print_header,
    print_config,
    print_wallet_balance,
    print_listening_status,
    print_new_token,
    print_buying,
    print_buy_result,
    print_skip,
    print_pnl_update,
    print_monitoring_start,
    print_selling,
    print_sell_result,
    print_continue_prompt,
    print_status,
    print_info,
    print_error,
    print_final_stats,
)

load_dotenv()

HELIUS_WS_URL = os.getenv("HELIUS_WS_URL", "")
HELIUS_RPC_URL = os.getenv("HELIUS_RPC_URL", "")

total_migrations = 0
total_bought = 0
last_buy_time = 0
current_position = None
seen_signatures = set()
bought_mints = set()
seen_names = set()


# ── Position monitoring ─────────────────────

async def monitor_position():
    global current_position

    from display import monitoring
    import display
    display.monitoring = True

    print_monitoring_start()

    last_real_pnl_check = 0
    last_pnl_update_time = 0

    while current_position is not None:
        now = time.time()

        # Update PnL display every ~5 seconds
        if now - last_pnl_update_time >= 5:
            # Quick price fetch (Jupiter Price API is fast ~200ms)
            try:
                price_data = await asyncio.wait_for(
                    asyncio.to_thread(trade.get_token_price, current_position["mint"]),
                    timeout=3,
                )
            except:
                price_data = None

            # Cache token balance once
            if not current_position.get("token_balance_raw"):
                try:
                    tb = await asyncio.wait_for(
                        asyncio.to_thread(trade.get_token_balance, current_position["mint"]),
                        timeout=3,
                    )
                    if tb:
                        current_position["token_balance_raw"] = tb[0]
                        current_position["token_decimals"] = tb[1]
                except:
                    pass

            # Real PnL via Jupiter quote — only every 15s (slower call)
            real_sol_out = current_position.get("last_real_sol_out")
            if current_position.get("token_balance_raw") and (now - last_real_pnl_check >= 15):
                try:
                    real_sol_out = await asyncio.wait_for(
                        asyncio.to_thread(
                            trade.get_real_pnl,
                            current_position["mint"],
                            current_position["token_balance_raw"],
                        ),
                        timeout=3,
                    )
                    if real_sol_out:
                        current_position["last_real_sol_out"] = real_sol_out
                    last_real_pnl_check = now
                except:
                    pass

            print_pnl_update(current_position, price_data, real_sol_out)
            last_pnl_update_time = now

        # Check stdin for "sell" — non-blocking
        if sys.stdin in select.select([sys.stdin], [], [], 0.3)[0]:
            user_input = sys.stdin.readline().strip().lower()
            if user_input == "sell":
                bal_before_buy = current_position.get("bal_before_buy", None)
                bal_after_buy = current_position.get("bal_after_buy", None)
                source = current_position.get("source", "pumpfun")

                print_selling(current_position["name"])
                display.monitoring = False
                success, result = trade.sell_token(current_position["mint"], source)

                bal_after = None
                if success:
                    trade.wait_for_confirmation(result, max_wait=30)
                    bal_after = trade.get_balance_after_change(
                        prev_balance=bal_after_buy,
                        max_wait=30,
                    )

                print_sell_result(
                    success,
                    name=current_position["name"],
                    bal_before=bal_before_buy,
                    bal_after=bal_after,
                    txid=result if success else None,
                    error=result if not success else None,
                )
                if success:
                    current_position = None
                    return True
                else:
                    display.monitoring = True
                    print_info("Still holding. Type 'sell' to try again.")
                    await asyncio.sleep(2)

        await asyncio.sleep(0.3)

    display.monitoring = False
    return False


async def ask_continue() -> bool:
    # Flush any leftover stdin input (prevents double-type issue)
    import termios
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

    print_continue_prompt()

    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0.5)[0]:
            user_input = sys.stdin.readline().strip().lower()
            if user_input in ("yes", "y"):
                return True
            elif user_input in ("no", "n"):
                return False
        await asyncio.sleep(0)


# ── Handle migration event ──────────────────

async def handle_migration(mint: str, source: str = "pumpfun", migration_queue_ref=None) -> bool:
    global total_migrations, total_bought, last_buy_time, current_position

    total_migrations += 1

    if not mint:
        return True

    if current_position is not None:
        return True

    if mint in bought_mints:
        return True

    data = {"mint": mint}

    # Fetch name from on-chain Metaplex metadata (works for ALL tokens)
    token_info = trade.get_token_info(mint)
    if token_info and token_info.get("name"):
        data["name"] = token_info["name"]
        data["symbol"] = token_info.get("symbol", "???")
        data["creator"] = token_info.get("creator", "")

    # ── Scam filters ──
    name = (data.get("name", "") or "").strip()
    name_lower = name.lower()

    # Too short
    if len(name) < config.MIN_NAME_LENGTH:
        return True

    # Exact blacklist
    if name_lower in config.BLACKLISTED_EXACT:
        print_info(f"  ⛔ Blacklisted: {name}")
        return True

    # Partial word blacklist
    for word in config.BLACKLISTED_WORDS:
        if word in name_lower:
            print_info(f"  ⛔ Blacklisted word '{word}' in: {name}")
            return True

    # Duplicate name in session
    if config.SKIP_DUPLICATE_NAMES and name_lower and name_lower in seen_names:
        print_info(f"  ⛔ Duplicate name: {name}")
        return True

    # ASCII-only filter
    if config.ASCII_NAMES_ONLY and name and not name.isascii():
        print_info(f"  ⛔ Non-ASCII: {name}")
        return True

    # Dev history check — is this creator a scam farm?
    creator = data.get("creator", "")
    if config.MAX_DEV_TOKENS > 0 and creator:
        is_safe = trade.check_dev_history(creator, config.MAX_DEV_TOKENS)
        if not is_safe:
            print_info(f"  ⛔ Scam farm dev (>{config.MAX_DEV_TOKENS} tokens): {name}")
            return True

    # Track name
    if name_lower:
        seen_names.add(name_lower)

    print_new_token(data, source)

    # Cooldown
    now = time.time()
    if now - last_buy_time < config.COOLDOWN_SECONDS:
        remaining = config.COOLDOWN_SECONDS - (now - last_buy_time)
        print_skip(f"Cooldown — {remaining:.0f}s remaining")
        print_status(total_migrations, total_bought)
        return True

    if not config.AUTO_BUY:
        print_skip("AUTO_BUY is OFF — not buying")
        print_status(total_migrations, total_bought)
        return True

    # Balance before
    bal_before = trade.get_sol_balance()

    # Pool settle delay
    print_info("  ┃ ⏳ Waiting for pool to settle...")
    await asyncio.sleep(3)

    # Buy
    print_buying(config.BUY_AMOUNT_SOL)
    success, result = trade.buy_token(mint, source)
    print_buy_result(
        success,
        txid=result if success else None,
        error=result if not success else None,
    )

    if success:
        total_bought += 1
        last_buy_time = time.time()
        bought_mints.add(mint)

        # Wait for buy tx to settle, then capture the post-buy balance
        # This is what we'll compare against to detect sell completion
        await asyncio.sleep(8)
        bal_after_buy = trade.get_sol_balance() or bal_before

        current_position = {
            "mint": mint,
            "name": data.get("name", "Unknown") or "Unknown",
            "symbol": data.get("symbol", "???") or "???",
            "entry_sol": config.BUY_AMOUNT_SOL,
            "bought_at": time.time(),
            "txid": result,
            "entry_price": 0.0,
            "bal_before_buy": bal_before,
            "bal_after_buy": bal_after_buy,
            "source": source,
        }

        # Fetch entry price
        entry_data = trade.get_token_price(mint)
        if entry_data:
            current_position["entry_price"] = entry_data["price_usd"]
            if entry_data.get("name") and current_position["name"] == "Unknown":
                current_position["name"] = entry_data["name"]
                current_position["symbol"] = entry_data.get("symbol", "???")

        await monitor_position()

        should_continue = await ask_continue()
        if not should_continue:
            return False

        # Drain stale events that piled up while we were in position
        drained = 0
        while not migration_queue_ref.empty():
            try:
                migration_queue_ref.get_nowait()
                drained += 1
            except:
                break
        if drained:
            print_info(f"  Skipped {drained} stale migrations from queue")

        print()
        print_header()
        print_status(total_migrations, total_bought)
        print()

    else:
        print_status(total_migrations, total_bought)

    return True


# ── PumpFun listener ────────────────────────

async def listen_pumpfun(migration_queue: asyncio.Queue):
    """Listen to PumpPortal for pump.fun migrations."""

    backoff = 5
    consecutive_failures = 0

    while True:
        try:
            print_info("  [PumpFun] Connecting...")

            async with websockets.connect(config.WS_URL) as ws:
                print_info("  [PumpFun] ✅ Connected")
                backoff = 5  # reset on successful connect
                consecutive_failures = 0

                await ws.send(json.dumps({
                    "method": "subscribeMigration",
                }))

                print_info("  [PumpFun] Subscribed to migrations")

                async for message in ws:
                    try:
                        data = json.loads(message)
                        if isinstance(data, dict) and "mint" in data:
                            mint = data.get("mint", "")
                            if mint:
                                await migration_queue.put(("pumpfun", mint))
                    except:
                        continue

        except Exception as e:
            consecutive_failures += 1
            # Only print the first error, then go quiet (avoids spamming screen)
            if not display.monitoring and consecutive_failures == 1:
                print_error(f"[PumpFun] {str(e)[:70]}")
                print_info("  [PumpFun] Will retry quietly in background...")
            elif not display.monitoring and consecutive_failures % 10 == 0:
                # Status update every 10 retries
                print_info(f"  [PumpFun] Still down — retried {consecutive_failures} times")

            # Exponential backoff capped at 60s
            await asyncio.sleep(backoff)
            backoff = min(backoff * 1.5, 60)


# ── Meteora DBC listener ───────────────────

# Meteora DAMM programs — when DBC migrates, it CPI-calls one of these
DAMM_V1_PROGRAM = "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"
DAMM_V2_PROGRAM = "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG"


async def _resolve_meteora_mint(signature: str, migration_queue: asyncio.Queue):
    """Background task: fetch tx details, extract token mint, verify freshness."""

    api_key = ""
    for url in [HELIUS_RPC_URL, HELIUS_WS_URL]:
        if "api-key=" in url:
            api_key = url.split("api-key=")[-1].split("&")[0]
            break

    rpc_url = HELIUS_RPC_URL or HELIUS_WS_URL.replace("wss://", "https://")
    found_mint = None

    for attempt in range(5):
        await asyncio.sleep(1.5 if attempt == 0 else 2.5)

        # ── Try 1: Helius Enhanced Transactions API ──
        if api_key and not found_mint:
            try:
                enhanced_url = f"https://api-mainnet.helius-rpc.com/v0/transactions?api-key={api_key}"
                resp = requests.post(
                    enhanced_url,
                    json={"transactions": [signature]},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        tx = data[0]
                        # From tokenTransfers: pick the one with the largest amount
                        # Real tokens have massive supplies, LP tokens have tiny amounts
                        best_mint = None
                        best_amount = 0
                        for transfer in tx.get("tokenTransfers", []):
                            mint = transfer.get("mint", "")
                            amount = transfer.get("tokenAmount", 0) or 0
                            if mint and mint != config.SOL_MINT and amount > best_amount:
                                best_amount = amount
                                best_mint = mint
                        if best_mint:
                            found_mint = best_mint
                        else:
                            # Fallback to accountData
                            for account in tx.get("accountData", []):
                                for change in account.get("tokenBalanceChanges", []):
                                    mint = change.get("mint", "")
                                    if mint and mint != config.SOL_MINT:
                                        found_mint = mint
                                        break
                                if found_mint:
                                    break
            except:
                pass

        # ── Try 2: Standard getTransaction RPC ──
        if not found_mint:
            try:
                tx_resp = requests.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {
                                "encoding": "jsonParsed",
                                "maxSupportedTransactionVersion": 0,
                                "commitment": "confirmed",
                            }
                        ]
                    },
                    timeout=10,
                )
                if tx_resp.status_code == 200:
                    tx_data = tx_resp.json().get("result")
                    if tx_data:
                        meta = tx_data.get("meta", {})
                        # Collect all mints from pre and post balances
                        pre_mints = set()
                        for bal in meta.get("preTokenBalances", []):
                            m = bal.get("mint", "")
                            if m and m != config.SOL_MINT:
                                pre_mints.add(m)

                        post_mints = set()
                        for bal in meta.get("postTokenBalances", []):
                            m = bal.get("mint", "")
                            if m and m != config.SOL_MINT:
                                post_mints.add(m)

                        # The real token exists in BOTH pre and post balances
                        # LP tokens only appear in post (created during migration)
                        real_tokens = pre_mints & post_mints
                        if real_tokens:
                            found_mint = real_tokens.pop()
                        elif post_mints:
                            # Fallback: if no pre balances, take highest-supply token
                            # Skip mints that look like LP tokens (name contains "LP")
                            for bal in meta.get("postTokenBalances", []):
                                m = bal.get("mint", "")
                                if m and m != config.SOL_MINT:
                                    amount = bal.get("uiTokenAmount", {}).get("uiAmount", 0) or 0
                                    if amount > 1000:  # Real tokens have large supplies
                                        found_mint = m
                                        break
            except:
                pass

        if found_mint:
            break

    if not found_mint:
        print_info(f"  [Meteora] ⚠️ Could not resolve {signature[:12]}...")
        return

    # ── Freshness check ──
    # Skip tokens whose pool was created more than 2 minutes ago (stale replays)
    try:
        ds_resp = requests.get(
            f"https://api.dexscreener.com/tokens/v1/solana/{found_mint}",
            timeout=5,
        )
        if ds_resp.status_code == 200:
            pairs = ds_resp.json()
            if isinstance(pairs, list) and len(pairs) > 0:
                created_at = pairs[0].get("pairCreatedAt", 0)
                if created_at:
                    age_seconds = (time.time() * 1000 - created_at) / 1000
                    if age_seconds > 120:
                        print_info(f"  [Meteora] ⏭️ Stale ({age_seconds:.0f}s old): {found_mint[:16]}...")
                        return
    except:
        pass

    print_info(f"  [Meteora] ✅ Fresh token: {found_mint[:16]}...")

    # Skip if we already queued this mint
    if found_mint in seen_signatures:
        return
    seen_signatures.add(found_mint)

    await migration_queue.put(("meteora", found_mint))


async def listen_meteora(migration_queue: asyncio.Queue):
    """Listen to Helius for Meteora DBC migrations."""

    if not HELIUS_WS_URL:
        print_error("  [Meteora] HELIUS_WS_URL not set — skipping")
        return

    while True:
        try:
            print_info("  [Meteora] Connecting to Helius...")

            async with websockets.connect(HELIUS_WS_URL) as ws:
                print_info("  [Meteora] ✅ Connected")

                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [config.METEORA_DBC_PROGRAM]},
                        {"commitment": "confirmed"}
                    ]
                }))

                response = await ws.recv()
                result = json.loads(response)
                if "result" in result:
                    print_info("  [Meteora] Subscribed to DBC program")

                async for message in ws:
                    try:
                        data = json.loads(message)

                        params = data.get("params", {})
                        result = params.get("result", {})
                        value = result.get("value", {})

                        signature = value.get("signature", "")
                        logs = value.get("logs", [])
                        err = value.get("err")

                        if not signature or not logs:
                            continue

                        if signature in seen_signatures:
                            continue

                        seen_signatures.add(signature)

                        if len(seen_signatures) > 5000:
                            seen_signatures.clear()

                        # Skip failed transactions
                        if err is not None:
                            continue

                        # ── Migration detection ──
                        # DBC migration: DBC CPI-calls DAMM at invoke depth [2]+
                        # Direct pool creation or swap: DAMM at invoke [1]
                        is_migration = False
                        for log in logs:
                            if (DAMM_V1_PROGRAM in log or DAMM_V2_PROGRAM in log):
                                if "invoke [2]" in log or "invoke [3]" in log or "invoke [4]" in log:
                                    is_migration = True
                                    break

                        if not is_migration:
                            continue

                        print_info(f"  [Meteora] 🔍 Migration tx: {signature[:16]}...")

                        # Spawn background task to resolve mint
                        # This way the listener keeps catching new migrations
                        asyncio.create_task(
                            _resolve_meteora_mint(signature, migration_queue)
                        )

                    except:
                        continue

        except Exception as e:
            if not display.monitoring:
                print_error(f"[Meteora] Connection error: {str(e)[:60]}")
            await asyncio.sleep(5)


# ── Main ────────────────────────────────────

async def main():
    print_header()
    print_config(config)

    # Show wallet balance
    bal = trade.get_sol_balance()
    print_wallet_balance(bal)

    print_listening_status(total_migrations, total_bought)

    # Create a shared queue for migration events
    migration_queue = asyncio.Queue()

    # Start listeners based on config
    tasks = []

    if config.LAUNCHPAD in ("pumpfun", "both"):
        tasks.append(asyncio.create_task(listen_pumpfun(migration_queue)))

    if config.LAUNCHPAD in ("meteora", "both"):
        tasks.append(asyncio.create_task(listen_meteora(migration_queue)))

    if not tasks:
        print_error("No launchpad selected in config")
        return

    print_info("Waiting for tokens to graduate...")
    print()

    # Process migration events from the queue
    while True:
        try:
            source, mint = await migration_queue.get()

            should_continue = await handle_migration(mint, source, migration_queue)
            if not should_continue:
                print_final_stats(total_migrations, total_bought)

                for task in tasks:
                    task.cancel()
                return

        except asyncio.CancelledError:
            break
        except Exception as e:
            print_error(f"Error: {str(e)[:80]}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        if current_position:
            print_info(f"Still holding: {current_position['name']} ({current_position['mint']})")
            print_info(f"Sell manually: https://dexscreener.com/solana/{current_position['mint']}")
        print_info("Bot stopped by user")