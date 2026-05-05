# ============================================
# RektCoder — Wallet Balance Checker
# Usage: python balance.py <wallet_address>
# ============================================

import sys
import requests

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
D = "\033[90m"
B = "\033[1m"
X = "\033[0m"


def get_sol_balance(public_key):
    try:
        response = requests.post(SOLANA_RPC, json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getBalance",
            "params": [public_key],
        }, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", {}).get("value", 0) / 1_000_000_000
    except:
        pass
    return None


def get_usdc_balance(public_key):
    try:
        response = requests.post(SOLANA_RPC, json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [public_key, {"mint": USDC_MINT}, {"encoding": "jsonParsed"}],
        }, timeout=10)
        if response.status_code == 200:
            accounts = response.json().get("result", {}).get("value", [])
            if accounts:
                return float(accounts[0].get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("tokenAmount", {}).get("uiAmount", 0) or 0)
            return 0.0
    except:
        pass
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n  {Y}Usage: python balance.py <wallet_address>{X}\n")
        sys.exit(1)

    wallet = sys.argv[1]
    print()
    print(f"  {C}{B}Wallet Balance{X}")
    print(f"  {D}{'─' * 44}{X}")
    print(f"  {D}Address:{X}  {W}{wallet}{X}")
    print()

    sol = get_sol_balance(wallet)
    usdc = get_usdc_balance(wallet)

    if sol is not None:
        print(f"  {D}SOL:{X}      {G}{B}{sol:.6f} SOL{X}")
    else:
        print(f"  {D}SOL:{X}      {Y}Failed to fetch{X}")

    if usdc is not None:
        print(f"  {D}USDC:{X}     {G}{B}{usdc:.2f} USDC{X}")
    else:
        print(f"  {D}USDC:{X}     {Y}Failed to fetch{X}")

    print(f"  {D}{'─' * 44}{X}")
    print(f"  {D}🔗 https://solscan.io/account/{wallet}{X}")
    print()
