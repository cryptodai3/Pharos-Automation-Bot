from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class PNS:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.ENS_CONTROLLER_ADDRESS = "0x51bE1EF20a1fD5179419738FC71D95A8b6f8A175"
        self.ENS_RESOLVER_ADDRESS = "0x9a43dcA1C3BB268546b98eb2AB1401bFc5b58505"
        self.ENS_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "makeCommitment", 
                "stateMutability": "pure", 
                "inputs": [
                    { "name": "name", "type": "string" }, 
                    { "name": "owner", "type": "address" }, 
                    { "name": "duration", "type": "uint256" }, 
                    { "name": "secret", "type": "bytes32" }, 
                    { "name": "resolver", "type": "address" }, 
                    { "name": "data", "type": "bytes[]" }, 
                    { "name": "reverseRecord", "type": "bool" }, 
                    { "name": "ownerControlledFuses", "type": "uint16" }
                ],
                "outputs": [
                    { "name": "", "type": "bytes32" }
                ]
            },
            {
                "type": "function",
                "name": "commit", 
                "stateMutability": "nonpayable", 
                "inputs": [
                    { "name": "commitment", "type": "bytes32" }
                ], 
                "outputs": []
            },
            {
                "type": "function",
                "name": "rentPrice", 
                "stateMutability": "view", 
                "inputs": [
                    { "name": "name", "type": "string" }, 
                    { "name": "duration", "type": "uint256" }
                ],
                "outputs": [
                    {
                        "components": [
                            { "name": "base", "type": "uint256" }, 
                            { "name": "premium", "type": "uint256" }
                        ], 
                        "name": "price", 
                        "type": "tuple"
                    }
                ]
            },
            {
                "type": "function",
                "name": "register", 
                "stateMutability": "payable", 
                "inputs": [
                    { "name": "name", "type": "string" }, 
                    { "name": "owner", "type": "address" }, 
                    { "name": "duration", "type": "uint256" }, 
                    { "name": "secret", "type": "bytes32" }, 
                    { "name": "resolver", "type": "address" }, 
                    { "name": "data", "type": "bytes[]" }, 
                    { "name": "reverseRecord", "type": "bool" }, 
                    { "name": "ownerControlledFuses", "type": "uint16" }
                ],
                "outputs": []
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.mint_count = 0
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

    def welcome(self, project_name="Pharos Name Service"):
        border = "═" * 58  # Solid elite border
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    👑 YetiDAO PRIME Automation BOT 👑")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"   🧠 Project    : Pharos Name Service - PRIME Bot")
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
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
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

    def generate_secret_bytes(self):
        secret = os.urandom(32)
        return secret

    def generate_domains(self):
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"

        length = random.randint(8, 12)
        word = ""
        while len(word) < length:
            
            if len(word) < length:
                word += random.choice(consonants)
            
            if len(word) < length:
                word += random.choice(vowels)
        
        return word[:length]
        
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
        
    async def make_commitment(self, address: str, domain: str, secret: bytes, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.ENS_CONTROLLER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ENS_CONTRACT_ABI)

            commitment = token_contract.functions.makeCommitment(
                domain, address, 31536000, secret, self.ENS_RESOLVER_ADDRESS, [], True, 0
            ).call()

            return commitment
        except Exception as e:
            raise Exception(f"Make Commitment Failed: {str(e)}")
        
    async def get_mint_price(self, address: str, domain: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.ENS_CONTROLLER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ENS_CONTRACT_ABI)
            price = token_contract.functions.rentPrice(domain, 31536000).call()

            mint_price = price[0] + price[1]

            return mint_price
        except Exception as e:
            raise Exception(f"Fetch Mint Price Failed: {str(e)}")
    
    async def perform_commit_domain(self, account: str, address: str, domain: str, secret: bytes, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            commitment = await self.make_commitment(address, domain, secret, use_proxy)

            contract_address = web3.to_checksum_address(self.ENS_CONTROLLER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ENS_CONTRACT_ABI)

            commit_data = token_contract.functions.commit(commitment)

            estimated_gas = commit_data.estimate_gas({"from":address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            commit_tx = commit_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, commit_tx)
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
        
    async def perform_register_domain(self, account: str, address: str, domain: str, secret: bytes, mint_price: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.ENS_CONTROLLER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ENS_CONTRACT_ABI)

            register_data = token_contract.functions.register(
                domain, address, 31536000, (secret), self.ENS_RESOLVER_ADDRESS, [], True, 0
            )

            estimated_gas = register_data.estimate_gas({"from":address, "value":mint_price})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            register_tx = register_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "value": mint_price,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, register_tx)
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
        
    async def print_timer(self, min_delay: int, max_delay: int, message: str):
        for remaining in range(random.randint(min_delay, max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For {message}...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
       
    def print_question(self):
        while True:
            try:
                mint_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Mint Domain Count For Each Wallet -> {Style.RESET_ALL}").strip())
                if mint_count > 0:
                    self.mint_count = mint_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Mint Domain Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

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
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
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
    
    async def process_perform_commit_domain(self, account: str, address: str, domain: str, secret: bytes, use_proxy: bool):
        tx_hash, block_number = await self.perform_commit_domain(account, address, domain, secret, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Commit Success {Style.RESET_ALL}"
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
            return True
        
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
            return False

    async def process_perform_register_domain(self, account: str, address: str, domain: str, secret: bytes, mint_price: int, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Commit{Style.RESET_ALL}                                   "
        )

        commited = await self.process_perform_commit_domain(account, address, domain, secret, use_proxy)
        if not commited: return

        await self.print_timer(60, 65, "Registering Domain")

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Register{Style.RESET_ALL}                                   "
        )

        tx_hash, block_number = await self.perform_register_domain(account, address, domain, secret, mint_price, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Register Success {Style.RESET_ALL}"
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
            return True
        
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
            return False

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Domain  :{Style.RESET_ALL}")

            try:
                web3 = await self.get_web3_with_check(address, use_proxy)
            except Exception as e:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            for i in range(self.mint_count):
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Mint {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.mint_count}{Style.RESET_ALL}                                   "
                )

                domain = self.generate_domains()

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Domain  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} {domain}.phrs {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Duration:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} 1 Years {Style.RESET_ALL}"
                )

                secret = self.generate_secret_bytes()

                try:
                    mint_price = await self.get_mint_price(address, domain, use_proxy)
                except Exception as e:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                    )
                    continue

                formatted_price = mint_price / (10**18)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Price   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {formatted_price} PHRS {Style.RESET_ALL}"
                )

                balance = await self.get_token_balance(address, use_proxy)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
                )

                if not balance or balance <= formatted_price:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
                    )
                    return
                
                await self.process_perform_register_domain(account, address, domain, secret, mint_price, use_proxy)
                await self.print_timer(self.min_delay, self.max_delay, "Next Minting")

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = True if proxy_choice == 1 else False

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies()
                
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
        bot = PNS()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Pharos Name Service - BOT{Style.RESET_ALL}                                       "                              
        )
