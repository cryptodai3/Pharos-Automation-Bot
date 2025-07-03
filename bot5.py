import time
import requests
import random
import datetime
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound
import colorama
from colorama import Fore, Style

# Initialize Colorama
colorama.init(autoreset=True)

# === FORMAT SECONDS FUNCTION ===
def format_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# === WELCOME BANNER ===
def welcome_banner():
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
    print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos Automation BOT ⚡")
    print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
    print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Forswap - Automation Bot")
    print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
    print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
    print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
    print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.0 🚀")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

# === CONFIGURATION ===
PHAROS_RPC = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
PRIVATE_KEY_FILE = "accounts.txt"
PROXY_FILE = "proxy.txt"
PHRS_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
USDC_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
USDT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"

# Display banner
welcome_banner()

# === READ MULTI-WALLET PRIVATE KEYS ===
with open(PRIVATE_KEY_FILE, "r") as f:
    private_keys = [line.strip() for line in f if line.strip().startswith("0x") and len(line.strip()) == 66]

if not private_keys:
    raise ValueError("❌ No valid private keys found in accounts.txt")

# === READ PROXIES ===
def load_proxies(filename=PROXY_FILE):
    try:
        with open(filename, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            return proxies if proxies else None
    except FileNotFoundError:
        return None

proxies = load_proxies()

# === CONVERT AMOUNT FROM FLOAT TO WEI BASED ON DECIMALS ===
def to_token_wei(amount_float, decimals):
    return int(amount_float * (10 ** decimals))

# === FETCH DODO ROUTE FUNCTION ===
def fetch_dodo_route(from_addr, to_addr, user_addr, amount_wei, proxy_dict):
    deadline = int(time.time()) + 1200

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
    ]

    for attempt in range(1, 31):
        print(f"\n🌐 Finding quote (Attempt {attempt}/30)")

        headers = {
            "User-Agent": random.choice(user_agents)
        }

        if proxies:
            proxy = random.choice(proxies)
            proxy_dict = {"http": proxy, "https": proxy}
            print(f"🔁 Using proxy: {proxy}")
        else:
            proxy_dict = None

        url = (
            f"https://api.dodoex.io/route-service/v2/widget/getdodoroute"
            f"?chainId={CHAIN_ID}&deadLine={deadline}"
            f"&apikey=a37546505892e1a952"
            f"&slippage=4.225&source=dodoV2AndMixWasm"
            f"&toTokenAddress={to_addr}&fromTokenAddress={from_addr}"
            f"&userAddr={user_addr}&estimateGas=true&fromAmount={amount_wei}"
        )

        try:
            response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
            data = response.json()

            if data["status"] != -1:
                print("✅ Quote found.")
                return data["data"]
            else:
                print("⚠️ No quote available. Retrying...")

        except Exception as e:
            print(f"❌ Fetch failed: {e}")

        time.sleep(3)

    print("❌ Failed to get route after 30 attempts.")
    return None

# === WAIT FOR TX RECEIPT ===
def wait_for_tx(w3, tx_hash, timeout=180):
    print("⏳ Waiting for transaction confirmation...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            print("✅ TX confirmed!\n")
            return receipt
        except TransactionNotFound:
            time.sleep(5)
    print("❌ Transaction not confirmed within timeout period.")
    return None

# === SEND TRANSACTION ===
def send_swap_tx(w3, private_key, route_data, nonce):
    gas_price = w3.to_wei("10", "gwei")
    tx = {
        "to": Web3.to_checksum_address(route_data["to"]),
        "data": route_data["data"],
        "value": int(route_data["value"]),
        "gas": int(route_data.get("gasLimit", 300000)),
        "gasPrice": gas_price,
        "nonce": nonce,
        "chainId": CHAIN_ID,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"🚀 TX sent: {tx_hash.hex()}")
    return wait_for_tx(w3, tx_hash)

# === MAIN EXECUTION ===
try:
    # Get user input once
    amount_input = float(input("💸 Amount of PHRS to swap (PHRS → USDC & USDT): "))
    delay = int(input("⏱ Delay between swaps (seconds): "))
    repeat = int(input("🔁 Number of swap repetitions: "))
    usdt_to_phrs = float(input("↩️ Amount USDT → PHRS: "))
    usdc_to_phrs = float(input("↩️ Amount USDC → PHRS: "))

    # Convert to wei once
    amount_phrs_wei = Web3.to_wei(amount_input, "ether")
    usdt_wei = to_token_wei(usdt_to_phrs, 6)
    usdc_wei = to_token_wei(usdc_to_phrs, 6)

    while True:
        print("\n🚀 Starting execution for all wallets...\n")

        # Process all wallets
        for accounts in private_keys:
            print("\n" + "=" * 40)
            print(f"🔐 Wallet: {accounts[:10]}...{accounts[-6:]}")
            try:
                w3 = Web3(Web3.HTTPProvider(PHAROS_RPC))
                account = w3.eth.account.from_key(accounts)
                print(f"📬 Address: {account.address}")
                print(f"💰 Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} PHRS")

                # Process all loops for this wallet
                for i in range(repeat):
                    print(f"\n🔄 Loop {i+1}/{repeat}")
                    try:
                        nonce = w3.eth.get_transaction_count(account.address, "pending")

                        print("🔁 Swap PHRS → USDC")
                        route1 = fetch_dodo_route(PHRS_ADDRESS, USDC_ADDRESS, account.address, amount_phrs_wei, None)
                        if route1: 
                            send_swap_tx(w3, accounts, route1, nonce)
                            nonce += 1
                        else: 
                            print("⚠️ Failed PHRS → USDC swap")

                        time.sleep(delay)

                        print("🔁 Swap PHRS → USDT")
                        route2 = fetch_dodo_route(PHRS_ADDRESS, USDT_ADDRESS, account.address, amount_phrs_wei, None)
                        if route2: 
                            send_swap_tx(w3, accounts, route2, nonce)
                            nonce += 1
                        else: 
                            print("⚠️ Failed PHRS → USDT swap")

                        time.sleep(delay)

                        print("🔁 Swap USDT → PHRS")
                        route3 = fetch_dodo_route(USDT_ADDRESS, PHRS_ADDRESS, account.address, usdt_wei, None)
                        if route3: 
                            send_swap_tx(w3, accounts, route3, nonce)
                            nonce += 1
                        else: 
                            print("⚠️ Failed USDT → PHRS swap")

                        time.sleep(delay)

                        print("🔁 Swap USDC → PHRS")
                        route4 = fetch_dodo_route(USDC_ADDRESS, PHRS_ADDRESS, account.address, usdc_wei, None)
                        if route4: 
                            send_swap_tx(w3, accounts, route4, nonce)
                            nonce += 1
                        else: 
                            print("⚠️ Failed USDC → PHRS swap")

                        if i < repeat - 1:
                            print(f"🕒 Delaying {delay}s before next loop...")
                            time.sleep(delay)

                    except Exception as inner_loop_error:
                        print(f"❌ Error in loop {i+1}: {inner_loop_error}")
                        continue

            except Exception as wallet_error:
                print(f"❌ Wallet error {accounts[:10]}...: {wallet_error}")
                continue

        # Start 24-hour countdown with real-time updates
        print(Fore.CYAN + Style.BRIGHT + "=" * 72)
        print(f"{Fore.BLUE+Style.BRIGHT}All wallets & loops completed. Cooling down for 24 hours before next execution...{Style.RESET_ALL}")
        
        seconds = 24 * 60 * 60  # 24 hours in seconds
        while seconds > 0:
            formatted_time = format_seconds(seconds)
            message = (
                f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}"
            )
            print(message, end='\r')
            time.sleep(1)
            seconds -= 1
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 72)
        print(f"{Fore.GREEN+Style.BRIGHT}Restarting automation cycle...{Style.RESET_ALL}")

except KeyboardInterrupt:
    current_time = datetime.datetime.now().strftime('%x %X')
    print(
        f"\n{Fore.CYAN + Style.BRIGHT}[ {current_time} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{Fore.RED + Style.BRIGHT}[ EXIT ] Faroswap - BOT{Style.RESET_ALL}"
    )
    exit()

except Exception as main_error:
    print("❌ Main error:", main_error)
