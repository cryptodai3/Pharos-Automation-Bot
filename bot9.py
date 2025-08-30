from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://app.grandline.world",
    "Referer": "https://app.grandline.world/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": FakeUserAgent().random
}

class Grandline:
    def __init__(self) -> None:
        self.HOST_API = "https://app.grandline.world"
        self.BASE_API = "https://api.grandline.world"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.NATIVE_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}
        ]''')
        self.GRANDLINE_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "balanceOf",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "owner", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "type": "function",
                "name": "claim",
                "stateMutability": "payable",
                "inputs": [
                    { "internalType": "address", "name": "_receiver", "type": "address" },
                    { "internalType": "uint256", "name": "_quantity", "type": "uint256" },
                    { "internalType": "address", "name": "_currency", "type": "address" },
                    { "internalType": "uint256", "name": "_pricePerToken", "type": "uint256" },
                    {
                        "components": [
                            { "internalType": "bytes32[]", "name": "proof", "type": "bytes32[]" },
                            { "internalType": "uint256", "name": "quantityLimitPerWallet", "type": "uint256" },
                            { "internalType": "uint256", "name": "pricePerToken", "type": "uint256" },
                            { "internalType": "address", "name": "currency", "type": "address" }
                        ],
                        "internalType": "struct IClaimCondition.AllowlistProof",
                        "name": "_allowlistProof",
                        "type": "tuple"
                    },
                    { "internalType": "bytes", "name": "_data", "type": "bytes" }
                ],
                "outputs": []
            }
        ]
        self.NFT_LISTS = []
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self, project_name="Grandline"):
        border = "═" * 58  # Solid elite border
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    👑 YetiDAO PRIME Automation BOT 👑")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"   🧠 Project    : Grandline - PRIME Bot")
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

            token_balance = balance / (10 ** 18)

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
    
    async def check_nft_status(self, address: str, nft_contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(nft_contract_address), abi=self.GRANDLINE_CONTRACT_ABI)
            amount = token_contract.functions.balanceOf(address).call()

            return True if amount > 0 else False
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_claim_nft(self, account: str, address: str, nft_contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            nft_price = web3.to_wei(1, "ether")

            proof = {
                "proof": [],
                "quantityLimitPerWallet": 0,
                "pricePerToken": 2**256 - 1,
                "currency": self.ZERO_ADDRESS
            }

            contract_address = web3.to_checksum_address(nft_contract_address)
            token_contract = web3.eth.contract(address=contract_address, abi=self.GRANDLINE_CONTRACT_ABI)

            claim_data = token_contract.functions.claim(address, 1, self.NATIVE_ADDRESS, nft_price, proof, b'')
            estimated_gas = claim_data.estimate_gas({"from": address, "value": nft_price})

            max_priority_fee = web3.to_wei(10, "gwei")
            max_fee = max_priority_fee

            claim_tx = claim_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "value": nft_price,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, claim_tx)
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
        for remaining in range(random.randint(5, 10), 0, -1):
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
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                use_proxy = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if use_proxy in [1, 2]:
                    type = "With" if use_proxy == 1 else "Without"
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if use_proxy == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return use_proxy, rotate_proxy
    
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
        
    async def fetch_nft_addresses(self, retries=5):
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=self.HOST_API) as response:
                        response.raise_for_status()
                        html = await response.text()

                    js_files = re.findall(r'/_next/static/chunks/[0-9a-zA-Z\-]+\.js', html)
                    if not js_files:
                        return None

                    target_files = [f for f in js_files if f.startswith("/_next/static/chunks/78163")]

                    if not target_files:
                        target_files = js_files

                    for js_file in target_files:
                        js_url = f"{self.HOST_API}{js_file}"

                        async with session.get(js_url) as response:
                            response.raise_for_status()
                            resp_text = await response.text()

                            match = re.search(r'getAllCollectionAddress\(\)\s*{\s*return\s*(\[[^\]]+\])', resp_text)
                            if match:
                                addresses = re.findall(r'0x[a-fA-F0-9]{40}', match.group(1))
                                if addresses:
                                    return addresses
                                
            except Exception:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def fetch_nft_data(self, nft_contract_address: str, retries=5):
        url = f"{self.BASE_API}/items/collections/{nft_contract_address}"
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=HEADERS) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
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
                    await asyncio.sleep(1)
                    continue

                return False
            
            return True
        
    async def process_fetch_nft_addresses(self):
        addresses = await self.fetch_nft_addresses()
        if not addresses:
            print(f"{Fore.RED+Style.BRIGHT}Fetch NFT Contract Addresses Failed{Style.RESET_ALL}")
            return False

        for nft_contract_address in addresses:
            nft_data = await self.fetch_nft_data(nft_contract_address)
            if nft_data:
                nft_name = nft_data["data"]["name"]

                print(
                    f"{Fore.MAGENTA+Style.BRIGHT}[=]{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Fetch NFT With Address: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{nft_contract_address}{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                )

                self.NFT_LISTS.append({"name": nft_name, "address": nft_contract_address})

            else:
                print(
                    f"{Fore.MAGENTA+Style.BRIGHT}[=]{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Fetch NFT With Address: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{nft_contract_address}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                )

            await asyncio.sleep(1)

        return True

    async def process_perform_claim_nft(self, account: str, address: str, nft_contract_address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_claim_nft(account, address, nft_contract_address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
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

            self.log(f"{Fore.CYAN+Style.BRIGHT}Claim   :{Style.RESET_ALL}")
            
            for nft in self.NFT_LISTS:
                nft_name = nft["name"]
                nft_contract_address = nft["address"]

                balance = await self.get_token_balance(address, use_proxy)

                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{nft_name}{Style.RESET_ALL}                                   "
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Address :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} {nft_contract_address} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Price   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} 1 PHRS {Style.RESET_ALL}"
                )

                has_claimed = await self.check_nft_status(address, nft_contract_address, use_proxy)
                if has_claimed:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
                    )
                    continue

                balance = await self.get_token_balance(address, use_proxy)
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
                )

                if not balance or balance <= 1:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
                    )
                    return
                
                await self.process_perform_claim_nft(account, address, nft_contract_address, use_proxy)
                await self.print_timer()

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            proxy_choice, rotate_proxy = self.print_question()

            print(f"\n{Fore.BLUE+Style.BRIGHT}Fetch NFT Contract Addresses...{Style.RESET_ALL}\n")
            await asyncio.sleep(1)

            fetched = await self.process_fetch_nft_addresses()
            if not fetched: return

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
        bot = Grandline()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Grandline - BOT{Style.RESET_ALL}                                       "                              
        )
