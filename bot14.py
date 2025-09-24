from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Primuslabs:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.SEND_ROUTER_ADDRESS = "0xD17512B7EC12880Bd94Eca9d774089fF89805F02"
        self.PRIMUSLABS_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "tip",
                "stateMutability": "payable",
                "inputs": [
                    {
                        "name": "token",
                        "type": "tuple",
                        "internalType": "struct TipToken",
                        "components": [
                            { "name": "tokenType", "type": "uint32", "internalType": "uint32" }, 
                            { "name": "tokenAddress", "type": "address", "internalType": "address" }
                        ]
                    }, 
                    {
                        "name": "recipient",
                        "type": "tuple",
                        "internalType": "struct TipRecipientInfo",
                        "components": [
                            { "name": "idSource", "type": "string", "internalType": "string" }, 
                            { "name": "id", "type": "string", "internalType": "string" }, 
                            { "name": "amount", "type": "uint256", "internalType": "uint256" }, 
                            { "name": "nftIds", "type": "uint256[]", "internalType": "uint256[]" }
                        ]
                    }
                ],
                "outputs": []
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.tip_count = 0
        self.tip_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self, project_name="Primuslabs"):
        border = "═" * 58  # Solid elite border
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    👑 YetiDAO PRIME Automation BOT 👑")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"   🧠 Project    : Primuslabs - PRIME Bot")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    💻 Author     : YetiDAO")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    🌐 Status     : Active & Privately Monitored 🔒")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "    🚀 Mode       : PRIME Access (VIP Only)")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    💎 Powered by Cryptodai3 × YetiDAO | Prime Engine v1.0 ⚙️")
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/http.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def generate_username(self):
        first_parts = [
            "reza", "andi", "rama", "dika", "nino", "alfa", "bima", "zaki", "yoga", "galih",
            "dewa", "luki", "fajar", "bagas", "taufik", "ilham", "riko", "arif", "dian", "ivan",
            "fikri", "adit", "udin", "eko", "kiki", "naufal", "faiz", "farhan", "syam", "rizky",
            "david", "ryan", "tommy", "kevin", "aldi", "joko", "yusuf", "hadi", "andre", "deni",
            "bayu", "rafi", "ghani", "irfan", "ari", "fauzi", "fikar", "tio", "ali", "ilmi",
            "sandy", "brian", "nanda", "randi", "wahyu", "salman", "rudi", "agus", "firman",
            "azhar", "lukman", "daniel", "mario", "jeffry", "nasrul", "dion", "amar"
        ]

        second_parts = [
            "dev", "bot", "jr", "x", "kun", "chan", "gamer", "tv", "yt", "zz", "id", "ku", "io",
            "tech", "ops", "hub", "net", "app", "xyz", "vr", "cloud", "main", "lab", "studio",
            "prod", "zone", "world", "offcl", "web", "site", "desk", "data", "sys", "byte", "bit",
            "online", "master", "pro", "beta", "night", "dark", "light", "zero", "sky", "nova",
            "droid", "sense", "blast", "next", "prodigy", "prime", "origin", "logic", "script",
            "mind", "pulse", "gen", "spark", "core", "flux", "shift", "sage", "nova", "root",
            "drop", "code"
        ]

        numbers = [str(random.randint(10, 99)) for _ in range(50)]
        separators = ["", "_", ".", ""]

        first = random.choice(first_parts)
        second = random.choice(second_parts + numbers)
        separator = random.choice(separators)

        username = first + separator + second

        if not (8 <= len(username) <= 15):
            return self.generate_username()

        def has_adjacent_vowels(s):
            vowels = "aeiou"
            return any(s[i] in vowels and s[i+1] in vowels for i in range(len(s)-1))

        if has_adjacent_vowels(username):
            return self.generate_username()

        return username
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            balance = web3.eth.get_balance(address)
            token_balance = web3.from_wei(balance, "ether")

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Send TX Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def perform_send_tip(self, account: str, address: str, handler: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = web3.to_wei(self.tip_amount, "ether")

            token = (1, web3.to_checksum_address("0x0000000000000000000000000000000000000000"))
            recipient = ("x", handler, amount_to_wei, [])

            contract_address = web3.to_checksum_address(self.SEND_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.PRIMUSLABS_CONTRACT_ABI)

            tip_data = token_contract.functions.tip(token, recipient)
            estimated_gas = tip_data.estimate_gas({"from":address, "value":amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            tip_tx = tip_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tip_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
       
    def print_question(self):
        while True:
            try:
                tip_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Send Tip Count For Each Wallet -> {Style.RESET_ALL}").strip())
                if tip_count > 0:
                    self.tip_count = tip_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Send Tip Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                tip_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Send Tip Amount -> {Style.RESET_ALL}").strip())
                if tip_amount > 0:
                    self.tip_amount = tip_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Send Tip Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Max Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def process_check_connection(self, address: int, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True
    
    async def process_perform_send_tip(self, account: str, address: str, handler: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_send_tip(account, address, handler, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Send Tip Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Send Tip:{Style.RESET_ALL}")

            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            for i in range(self.tip_count):
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Tip {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.tip_count}{Style.RESET_ALL}                                   "
                )

                balance = await self.get_token_balance(address, use_proxy)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.tip_amount} PHRS {Style.RESET_ALL}"
                )

                handler = self.generate_username()

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Handler :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} {handler} {Style.RESET_ALL}"
                )

                if not balance or balance <= self.tip_amount:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
                    )
                    return
                
                await self.process_perform_send_tip(account, address, handler, use_proxy)
                await self.print_timer()

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Primuslabs()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Primuslabs Send - BOT{Style.RESET_ALL}                                       "                              
        )
