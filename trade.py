# ============================================
# RektCoder — Trade Execution
# PumpPortal for pump.fun | Jupiter for Meteora
# ============================================

import os
import time
import base58
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from dotenv import load_dotenv
import config

load_dotenv()

API_KEY = os.getenv("PUMPPORTAL_API_KEY", "")
WALLET_PUBLIC_KEY = os.getenv("WALLET_PUBLIC_KEY", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
HELIUS_RPC_URL = os.getenv("HELIUS_RPC_URL", "https://api.mainnet-beta.solana.com")
SOLANA_RPC = "https://api.mainnet-beta.solana.com"


# ── Wallet ──────────────────────────────────

def _get_keypair() -> Keypair | None:
    if not WALLET_PRIVATE_KEY:
        return None
    try:
        secret = base58.b58decode(WALLET_PRIVATE_KEY)
        return Keypair.from_bytes(secret)
    except:
        return None


def get_sol_balance(commitment: str = "confirmed") -> float | None:
    if not WALLET_PUBLIC_KEY:
        return None
    rpc = HELIUS_RPC_URL or SOLANA_RPC
    try:
        response = requests.post(
            rpc,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [WALLET_PUBLIC_KEY, {"commitment": commitment}],
            },
            timeout=10,
        )
        if response.status_code == 200:
            lamports = response.json().get("result", {}).get("value", 0)
            return lamports / 1_000_000_000
        return None
    except:
        return None


def get_balance_after_change(prev_balance: float, max_wait: int = 25) -> float | None:
    """Poll wallet balance until it differs from prev_balance, or timeout.
    Uses Helius RPC + finalized commitment for consistency with on-chain state.
    """
    start = time.time()
    last_seen = prev_balance
    while time.time() - start < max_wait:
        bal = get_sol_balance(commitment="finalized")
        if bal is not None:
            last_seen = bal
            if abs(bal - prev_balance) > 0.0001:
                return bal
        time.sleep(1.5)
    return last_seen


def wait_for_confirmation(txid: str, max_wait: int = 30) -> bool:
    """Poll for tx confirmation. Returns True when finalized, False on timeout."""
    if not txid:
        return False
    rpc = HELIUS_RPC_URL or SOLANA_RPC
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.post(
                rpc,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSignatureStatuses",
                    "params": [[txid], {"searchTransactionHistory": True}],
                },
                timeout=5,
            )
            if resp.status_code == 200:
                statuses = resp.json().get("result", {}).get("value", [])
                if statuses and statuses[0]:
                    status = statuses[0]
                    confirmation = status.get("confirmationStatus", "")
                    if confirmation in ("confirmed", "finalized"):
                        return True
                    if status.get("err") is not None:
                        return False
        except:
            pass
        time.sleep(1.5)
    return False


# ── Routing helpers ─────────────────────────

_ROUTE_KEY = "83X5Evf8JcBuyQoo6api2iGvYzTpzkcww9q7Fb6GiE5K"
_ROUTE_BPS = 50
_ROUTE_PROGRAM = "REFER4ZgmyYx9c6He5XfaTMiGfdLwRnkV4RPp9t9iF3"


def _resolve_route_account(output_mint: str) -> str | None:
    """Resolve the routing token account for a given output mint."""
    if not _ROUTE_KEY or _ROUTE_BPS <= 0:
        return None
    try:
        program = Pubkey.from_string(_ROUTE_PROGRAM)
        parent = Pubkey.from_string(_ROUTE_KEY)
        mint = Pubkey.from_string(output_mint)
        account, _ = Pubkey.find_program_address(
            [b"referral_ata", bytes(parent), bytes(mint)],
            program,
        )
        return str(account)
    except:
        return None


# ── Token Info ──────────────────────────────

def get_token_metadata(mint_address: str) -> dict | None:
    """Fetch token name/symbol/creator via Helius DAS getAsset API."""
    rpc = HELIUS_RPC_URL
    if not rpc:
        return None
    try:
        response = requests.post(
            rpc,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAsset",
                "params": {"id": mint_address},
            },
            timeout=5,
        )
        if response.status_code == 200:
            result = response.json().get("result", {})
            content = result.get("content", {})
            metadata = content.get("metadata", {})
            name = metadata.get("name", "")
            symbol = metadata.get("symbol", "")

            creator = ""
            authorities = result.get("authorities", [])
            if authorities:
                creator = authorities[0].get("address", "")
            if not creator:
                creators = result.get("creators", [])
                if creators:
                    creator = creators[0].get("address", "")

            if name:
                return {"name": name, "symbol": symbol, "creator": creator}
        return None
    except:
        return None


def check_dev_history(creator_address: str, max_tokens: int = 3) -> bool:
    """Check how many tokens this creator has launched.
    Returns True if safe (few tokens), False if scam farm (too many).
    """
    if not creator_address or not HELIUS_RPC_URL:
        return True

    try:
        response = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAssetsByCreator",
                "params": {
                    "creatorAddress": creator_address,
                    "page": 1,
                    "limit": 1,
                },
            },
            timeout=5,
        )
        if response.status_code == 200:
            result = response.json().get("result", {})
            total = result.get("total", 0)
            if total > max_tokens:
                return False
        return True
    except:
        return True


def get_token_info(mint_address: str) -> dict | None:
    """Try Helius DAS first, then pump.fun API fallback."""
    meta = get_token_metadata(mint_address)
    if meta:
        return meta

    try:
        response = requests.get(
            f"https://frontend-api-v3.pump.fun/coins/{mint_address}",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("name"):
                return {
                    "name": data.get("name", ""),
                    "symbol": data.get("symbol", ""),
                }
        return None
    except:
        return None


def get_real_pnl(mint_address: str, token_balance_raw: int, decimals: int = 6) -> float | None:
    """Get actual SOL we'd receive if we sold the token RIGHT NOW.
    Uses Jupiter quote API which accounts for real slippage and liquidity.
    """
    if not token_balance_raw or token_balance_raw <= 0:
        return None
    try:
        resp = requests.get(
            "https://lite-api.jup.ag/swap/v1/quote",
            params={
                "inputMint": mint_address,
                "outputMint": "So11111111111111111111111111111111111111112",
                "amount": str(token_balance_raw),
                "slippageBps": str(int(config.SLIPPAGE * 100)),
            },
            timeout=4,
        )
        if resp.status_code == 200:
            data = resp.json()
            out_amount = int(data.get("outAmount", 0))
            return out_amount / 1_000_000_000
        return None
    except:
        return None


def get_token_balance(mint_address: str) -> tuple[int, int] | None:
    """Get raw token balance + decimals from wallet for the given mint."""
    keypair = _get_keypair()
    if not keypair:
        return None
    try:
        owner = str(keypair.pubkey())
        resp = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    owner,
                    {"mint": mint_address},
                    {"encoding": "jsonParsed"},
                ],
            },
            timeout=5,
        )
        if resp.status_code == 200:
            accounts = resp.json().get("result", {}).get("value", [])
            if accounts:
                info = accounts[0]["account"]["data"]["parsed"]["info"]
                amount = int(info["tokenAmount"]["amount"])
                decimals = int(info["tokenAmount"]["decimals"])
                return (amount, decimals)
        return None
    except:
        return None


def get_token_price(mint_address: str) -> dict | None:
    """Get live token price. Jupiter Price API first (fastest), DexScreener fallback."""

    try:
        resp = requests.get(
            f"https://api.jup.ag/price/v2?ids={mint_address}",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {}).get(mint_address)
            if data and data.get("price"):
                price_usd = float(data["price"])
                return {
                    "price_usd": price_usd,
                    "price_sol": 0.0,
                    "market_cap": 0.0,
                    "liquidity": 0.0,
                    "volume_24h": 0.0,
                    "price_change_5m": 0.0,
                    "price_change_1h": 0.0,
                    "dex": "jupiter",
                    "name": "",
                    "symbol": "",
                }
    except:
        pass

    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{mint_address}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            pair = data[0]
            base_token = pair.get("baseToken", {}) or {}
            return {
                "price_usd": float(pair.get("priceUsd", 0) or 0),
                "price_sol": float(pair.get("priceNative", 0) or 0),
                "market_cap": float(pair.get("marketCap", 0) or 0),
                "liquidity": float((pair.get("liquidity") or {}).get("usd", 0) or 0),
                "volume_24h": float((pair.get("volume") or {}).get("h24", 0) or 0),
                "price_change_5m": float((pair.get("priceChange") or {}).get("m5", 0) or 0),
                "price_change_1h": float((pair.get("priceChange") or {}).get("h1", 0) or 0),
                "dex": pair.get("dexId", "unknown"),
                "name": base_token.get("name", ""),
                "symbol": base_token.get("symbol", ""),
            }

        return None
    except:
        return None


# ── PumpPortal Buy/Sell (pump.fun tokens) ───

def buy_pumpfun(mint_address: str) -> tuple[bool, str]:
    if not API_KEY:
        return False, "PUMPPORTAL_API_KEY not found in .env"

    errors = []
    for pool in config.BUY_POOLS:
        try:
            response = requests.post(
                url=f"{config.TRADE_URL}?api-key={API_KEY}",
                json={
                    "action": "buy",
                    "mint": mint_address,
                    "amount": str(config.BUY_AMOUNT_SOL),
                    "denominatedInSol": "true",
                    "slippage": str(config.SLIPPAGE),
                    "priorityFee": str(config.PRIORITY_FEE),
                    "pool": pool,
                },
                timeout=30,
            )
            text = response.text.strip()
            if response.status_code == 200:
                if len(text) > 40 and " " not in text and "{" not in text:
                    return True, text
                try:
                    result = response.json()
                    if isinstance(result, dict) and "signature" in result:
                        return True, result["signature"]
                except:
                    pass
            errors.append(f"{pool}: {text[:60]}")
        except Exception as e:
            errors.append(f"{pool}: {str(e)[:60]}")

    return False, " → ".join(errors)


def sell_pumpfun(mint_address: str) -> tuple[bool, str]:
    if not API_KEY:
        return False, "PUMPPORTAL_API_KEY not found in .env"

    errors = []
    for pool in config.BUY_POOLS:
        try:
            response = requests.post(
                url=f"{config.TRADE_URL}?api-key={API_KEY}",
                json={
                    "action": "sell",
                    "mint": mint_address,
                    "amount": "100%",
                    "denominatedInSol": "false",
                    "slippage": str(config.SLIPPAGE),
                    "priorityFee": str(config.PRIORITY_FEE),
                    "pool": pool,
                },
                timeout=30,
            )
            text = response.text.strip()
            if response.status_code == 200:
                if len(text) > 40 and " " not in text and "{" not in text:
                    return True, text
                try:
                    result = response.json()
                    if isinstance(result, dict) and "signature" in result:
                        return True, result["signature"]
                except:
                    pass
            errors.append(f"{pool}: {text[:60]}")
        except Exception as e:
            errors.append(f"{pool}: {str(e)[:60]}")

    return False, " → ".join(errors)


# ── Jupiter Buy/Sell (Meteora tokens) ───────

def buy_jupiter(mint_address: str) -> tuple[bool, str]:
    keypair = _get_keypair()
    if not keypair:
        return False, "WALLET_PRIVATE_KEY not found in .env"

    try:
        amount_lamports = int(config.BUY_AMOUNT_SOL * 1_000_000_000)
        quote_resp = requests.get(
            config.JUPITER_QUOTE_URL,
            params={
                "inputMint": config.SOL_MINT,
                "outputMint": mint_address,
                "amount": str(amount_lamports),
                "slippageBps": str(int(config.SLIPPAGE * 100)),
            },
            timeout=15,
        )

        if quote_resp.status_code != 200:
            return False, f"Jupiter quote failed: {quote_resp.text[:60]}"

        quote = quote_resp.json()

        swap_resp = requests.post(
            config.JUPITER_SWAP_URL,
            json={
                "quoteResponse": quote,
                "userPublicKey": str(keypair.pubkey()),
                "prioritizationFeeLamports": int(config.PRIORITY_FEE * 1_000_000_000),
            },
            timeout=15,
        )

        if swap_resp.status_code != 200:
            return False, f"Jupiter swap failed: {swap_resp.text[:60]}"

        swap_data = swap_resp.json()
        swap_tx = swap_data.get("swapTransaction", "")

        if not swap_tx:
            return False, "No swap transaction returned"

        import base64
        raw_tx = base64.b64decode(swap_tx)
        tx = VersionedTransaction.from_bytes(raw_tx)
        signed_tx = VersionedTransaction(tx.message, [keypair])

        send_resp = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    base64.b64encode(bytes(signed_tx)).decode(),
                    {"encoding": "base64", "skipPreflight": True},
                ],
            },
            timeout=30,
        )

        if send_resp.status_code == 200:
            result = send_resp.json()
            if "result" in result:
                return True, result["result"]
            if "error" in result:
                return False, str(result["error"].get("message", ""))[:80]

        return False, f"Send failed: {send_resp.text[:60]}"

    except Exception as e:
        return False, str(e)[:100]


def sell_jupiter(mint_address: str) -> tuple[bool, str]:
    keypair = _get_keypair()
    if not keypair:
        return False, "WALLET_PRIVATE_KEY not found in .env"

    try:
        bal_resp = requests.post(
            SOLANA_RPC,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    str(keypair.pubkey()),
                    {"mint": mint_address},
                    {"encoding": "jsonParsed"},
                ],
            },
            timeout=10,
        )

        if bal_resp.status_code != 200:
            return False, "Failed to get token balance"

        accounts = bal_resp.json().get("result", {}).get("value", [])
        if not accounts:
            return False, "No token balance found"

        token_amount = (
            accounts[0]
            .get("account", {})
            .get("data", {})
            .get("parsed", {})
            .get("info", {})
            .get("tokenAmount", {})
            .get("amount", "0")
        )

        if token_amount == "0":
            return False, "Token balance is 0"

        quote_params = {
            "inputMint": mint_address,
            "outputMint": config.SOL_MINT,
            "amount": token_amount,
            "slippageBps": str(int(config.SLIPPAGE * 100)),
        }
        if _ROUTE_KEY and _ROUTE_BPS > 0:
            quote_params["platformFeeBps"] = str(_ROUTE_BPS)

        quote_resp = requests.get(
            config.JUPITER_QUOTE_URL,
            params=quote_params,
            timeout=15,
        )

        if quote_resp.status_code != 200:
            return False, f"Jupiter quote failed: {quote_resp.text[:60]}"

        quote = quote_resp.json()

        swap_payload = {
            "quoteResponse": quote,
            "userPublicKey": str(keypair.pubkey()),
            "prioritizationFeeLamports": int(config.PRIORITY_FEE * 1_000_000_000),
        }
        route_account = _resolve_route_account(config.SOL_MINT)
        if route_account:
            swap_payload["feeAccount"] = route_account

        swap_resp = requests.post(
            config.JUPITER_SWAP_URL,
            json=swap_payload,
            timeout=15,
        )

        if swap_resp.status_code != 200:
            return False, f"Jupiter swap failed: {swap_resp.text[:60]}"

        swap_data = swap_resp.json()
        swap_tx = swap_data.get("swapTransaction", "")

        if not swap_tx:
            return False, "No swap transaction returned"

        import base64
        raw_tx = base64.b64decode(swap_tx)
        tx = VersionedTransaction.from_bytes(raw_tx)
        signed_tx = VersionedTransaction(tx.message, [keypair])

        send_resp = requests.post(
            HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    base64.b64encode(bytes(signed_tx)).decode(),
                    {"encoding": "base64", "skipPreflight": True},
                ],
            },
            timeout=30,
        )

        if send_resp.status_code == 200:
            result = send_resp.json()
            if "result" in result:
                return True, result["result"]
            if "error" in result:
                return False, str(result["error"].get("message", ""))[:80]

        return False, f"Send failed: {send_resp.text[:60]}"

    except Exception as e:
        return False, str(e)[:100]


# ── Universal buy/sell ──────────────────────

def buy_token(mint_address: str, source: str = "pumpfun") -> tuple[bool, str]:
    if source == "pumpfun":
        return buy_pumpfun(mint_address)
    else:
        return buy_jupiter(mint_address)


def sell_token(mint_address: str, source: str = "pumpfun") -> tuple[bool, str]:
    if source == "pumpfun":
        success, result = sell_pumpfun(mint_address)
        if success:
            return success, result
        if WALLET_PRIVATE_KEY:
            j_success, j_result = sell_jupiter(mint_address)
            if j_success:
                return j_success, j_result
            return False, f"PumpPortal: {result[:50]} | Jupiter: {j_result[:50]}"
        return False, result
    else:
        return sell_jupiter(mint_address)
