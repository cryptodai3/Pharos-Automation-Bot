from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from base64 import b64encode
from colorama import *
import asyncio, random, time, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

PUBLIC_KEY_PEM = b"""
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWPv2qP8+xLABhn3F/U/hp76HP
e8dD7kvPUh70TC14kfvwlLpCTHhYf2/6qulU1aLWpzCz3PJr69qonyqocx8QlThq
5Hik6H/5fmzHsjFvoPeGN5QRwYsVUH07MbP7MNbJH5M2zD5Z1WEp9AHJklITbS1z
h23cf2WfZ0vwDYzZ8QIDAQAB
-----END PUBLIC KEY-----
"""

class AutoStaking:
    def __init__(self) -> None:
        self.BASE_URL = "https://autostaking.pro/"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.MUSD_CONTRACT_ADDRESS = "0x7F5e05460F927Ee351005534423917976F92495e"
        self.mvMUSD_CONTRACT_ADDRESS = "0xF1CF5D79bE4682D50f7A60A047eACa9bD351fF8e"
        self.STAKING_ROUTER_ADDRESS = "0x11cD3700B310339003641Fdce57c1f9BD21aE015"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"claimFaucet","stateMutability":"nonpayable","inputs":[],"outputs":[{"name":"","type":"uint256"}]}
        ]''')
        self.AUTOSTAKING_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "getNextFaucetClaimTime",
                "stateMutability": "view",
                "inputs": [
                    { "name": "user", "type": "address" }
                ],
                "outputs": [
                    { "name": "", "type": "uint256" }
                ]
            }
        ]
        self.PROMPT = (
            "1. Mandatory Requirement: The product's TVL must be higher than one million USD.\n"
            "2. Balance Preference: Prioritize products that have a good balance of high current APY and high TVL.\n"
            "3. Portfolio Allocation: Select the 3 products with the best combined ranking in terms of current APY and TVL among those with TVL > 1,000,000 USD. "
            "To determine the combined ranking, rank all eligible products by current APY (highest to lowest) and by TVL (highest to lowest), "
            "then sum the two ranks for each product. Choose the 3 products with the smallest sum of ranks. Allocate the investment equally among these 3 products, "
            "with each receiving approximately 33.3% of the investment."
        )
        self.BASE_API = None
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.auth_tokens = {}
        self.used_nonce = {}
        self.staking_count = 0
        self.usdc_amount = 0
        self.usdt_amount = 0
        self.musd_amount = 0
        self.max_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self, project_name="AutoStaking"):
        border = "═" * 58  # Solid elite border
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + border)
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "    👑 YetiDAO PRIME Automation BOT 👑")
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "    ─────────────────────────────────────")
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"   🧠 Project    : AutoStaking - PRIME Bot")
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
        
    def generate_auth_token(self, address: str):
        try:
            public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)

            ciphertext = public_key.encrypt(
                address.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            token_base64 = b64encode(ciphertext).decode('utf-8')

            return token_base64
        except Exception as e:
            return None
        
    def generate_recommendation_payload(self, address: str):
        try:
            usdc_assets = int(self.usdc_amount * (10 ** 6))
            usdt_assets = int(self.usdt_amount * (10 ** 6))
            musd_assets = int(self.musd_amount * (10 ** 6))

            payload = {
                "user":address,
                "profile":self.PROMPT,
                "userPositions":[],
                "userAssets":[
                    {
                        "chain":{"id":688688},
                        "name":"USDC",
                        "symbol":"USDC",
                        "decimals":6,
                        "address":"0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
                        "assets":str(usdc_assets),
                        "price":1,
                        "assetsUsd":self.usdc_amount
                    },
                    {
                        "chain":{"id":688688},
                        "name":"USDT",
                        "symbol":"USDT",
                        "decimals":6,
                        "address":"0xD4071393f8716661958F766DF660033b3d35fD29",
                        "assets":str(usdt_assets),
                        "price":1,
                        "assetsUsd":self.usdt_amount
                    },
                    {
                        "chain":{"id":688688},
                        "name":"MockUSD",
                        "symbol":"MockUSD",
                        "decimals":6,
                        "address":"0x7F5e05460F927Ee351005534423917976F92495e",
                        "assets":str(musd_assets),
                        "price":1,
                        "assetsUsd":self.musd_amount
                    }
                ],
                "chainIds":[688688],
                "tokens":["USDC","USDT","MockUSD"],
                "protocols":["MockVault"],
                "env":"pharos"
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def generate_transactions_payload(self, address: str, change_tx: list):
        try:
            payload = {
                "user":address,
                "changes":change_tx,
                "prevTransactionResults":{}
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
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
            
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            balance = token_contract.functions.balanceOf(address).call()
            decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

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
    
    async def get_next_faucet_claim_time(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.mvMUSD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.AUTOSTAKING_CONTRACT_ABI)

            next_faucet_claim_time = token_contract.functions.getNextFaucetClaimTime(web3.to_checksum_address(address)).call()

            return next_faucet_claim_time
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.mvMUSD_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            claim_data = token_contract.functions.claimFaucet()
            estimated_gas = claim_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            claim_tx = claim_data.build_transaction({
                "from": web3.to_checksum_address(address),
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
        
    async def approving_token(self, account: str, address: str, ticker: str, router_address: str, asset_address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            
            amount_to_wei = int(amount * (10 ** decimals))

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

                block_number = receipt.blockNumber
                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} {ticker} Approved {Style.RESET_ALL}                                   "
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
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_staking(self, account: str, address: str, tickers: dict, change_tx: list, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, tickers['ticker0'], self.STAKING_ROUTER_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.usdc_amount, use_proxy)
            await self.approving_token(account, address, tickers['ticker1'], self.STAKING_ROUTER_ADDRESS, self.USDT_CONTRACT_ADDRESS, self.usdt_amount, use_proxy)
            await self.approving_token(account, address, tickers['ticker2'], self.STAKING_ROUTER_ADDRESS, self.MUSD_CONTRACT_ADDRESS, self.musd_amount, use_proxy)
            
            transactions = await self.generate_change_transactions(address, change_tx, use_proxy)
            if not transactions: 
                raise Exception("Fetch Transaction Calldata Failed")
                
            calldata = transactions["data"]["688688-0x11cD3700B310339003641Fdce57c1f9BD21aE015"]["data"]

            estimated_gas = web3.eth.estimate_gas({
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(self.STAKING_ROUTER_ADDRESS),
                "data": calldata,
            })

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            tx = {
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(self.STAKING_ROUTER_ADDRESS),
                "data": calldata,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
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
        for remaining in range(random.randint(self.max_delay, self.max_delay), 0, -1):
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
                staking_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Staking Count For Each Wallets -> {Style.RESET_ALL}").strip())
                if staking_count > 0:
                    self.staking_count = staking_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                usdc_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter USDC Amount -> {Style.RESET_ALL}").strip())
                if usdc_amount > 0:
                    self.usdc_amount = usdc_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                usdt_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter USDT Amount -> {Style.RESET_ALL}").strip())
                if usdt_amount > 0:
                    self.usdt_amount = usdt_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                musd_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter MockUSD Amount -> {Style.RESET_ALL}").strip())
                if musd_amount > 0:
                    self.musd_amount = musd_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay Each Tx -> {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay Each Tx -> {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
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
    
    async def fetch_base_api(self, retries=5):
        js_pattern = re.compile(r'src="([^"]+_next/static/chunks/[^"]+\.js)"')
        api_patterns = [
            re.compile(r'o\.Z\s*\?\s*"([^"]+)"'), 
            re.compile(r'r\.Z\s*\?\s*"([^"]+)"')
        ]

        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get(self.BASE_URL) as resp_index:
                        index_text = await resp_index.text()

                    js_files = js_pattern.findall(index_text)
                    if not js_files:
                        raise Exception("Js File Not Found")
                    
                    found_api = None

                    for js_file in js_files:
                        if not js_file.startswith("http"):
                            if js_file.startswith("/"):
                                js_url = self.BASE_URL.rstrip("/") + js_file
                            else:
                                js_url = self.BASE_URL.rstrip("/") + "/" + js_file
                        else:
                            js_url = js_file

                        async with session.get(js_url) as response:
                            response.raise_for_status()
                            resp_text = await response.text()

                            for pattern in api_patterns:
                                match = pattern.search(resp_text)
                                if match:
                                    found_api = match.group(1)
                                    break

                    if not found_api:
                        raise Exception("API URL Not Found")

                    return found_api
                    
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Base API Url   : {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Fetch API Url Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
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
            
    async def financial_portfolio_recommendation(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/investment/financial-portfolio-recommendation"
        data = json.dumps(self.generate_recommendation_payload(address))
        headers = {
            **self.HEADERS[address],
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def generate_change_transactions(self, address: str, change_tx: list, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/investment/generate-change-transactions"
        data = json.dumps(self.generate_transactions_payload(address, change_tx))
        headers = {
            **self.HEADERS[address],
            "Authorization": self.auth_tokens[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
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
                    continue

                return False
            
            return True
    
    async def process_perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        next_faucet_claim_time = await self.get_next_faucet_claim_time(address, use_proxy)
        if next_faucet_claim_time is not None:
            if int(time.time()) >= next_faucet_claim_time:
                tx_hash, block_number = await self.perform_claim_faucet(account, address, use_proxy)
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
            else:
                formatted_next_claim = datetime.fromtimestamp(next_faucet_claim_time).astimezone(wib).strftime("%x %X %Z")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Next Claim at {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{formatted_next_claim}{Style.RESET_ALL}"
                )

    async def process_perform_staking(self, account: str, address: str, tickers: dict, use_proxy: bool):
        portfolio = await self.financial_portfolio_recommendation(address, use_proxy)
        if portfolio:
            change_tx = portfolio["data"]["changes"]
            
            tx_hash, block_number = await self.perform_staking(account, address, tickers, change_tx, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}                                   "
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
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Fetch Financial Portfolio Recommendation Failed {Style.RESET_ALL}"
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

            self.log(f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}")

            await self.process_perform_claim_faucet(account, address, use_proxy)

            self.log(f"{Fore.CYAN+Style.BRIGHT}Staking :{Style.RESET_ALL}                                   ")

            for i in range(self.staking_count):
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Stake {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{self.staking_count}{Style.RESET_ALL}                                   "
                )

                tickers = {
                    "ticker0": "USDC",
                    "ticker1": "USDT",
                    "ticker2": "MockUSD",
                }

                self.log(f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}")

                usdc_balance = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS, use_proxy)
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      1.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {usdc_balance} {tickers['ticker0']} {Style.RESET_ALL}"
                )
                usdt_balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      2.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {usdt_balance} {tickers['ticker1']} {Style.RESET_ALL}"
                )
                musd_balance = await self.get_token_balance(address, self.MUSD_CONTRACT_ADDRESS, use_proxy)
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      3.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {musd_balance} {tickers['ticker2']} {Style.RESET_ALL}"
                )

                self.log(f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}")
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      1.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.usdc_amount} {tickers['ticker0']} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      2.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.usdt_amount} {tickers['ticker1']} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}      3.{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.musd_amount} {tickers['ticker2']} {Style.RESET_ALL}"
                )

                if usdc_balance is None:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch {tickers['ticker0']} Token Balance Failed {Style.RESET_ALL}"
                    )
                    continue

                if usdt_balance is None:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch {tickers['ticker1']} Token Balance Failed {Style.RESET_ALL}"
                    )
                    continue

                if musd_balance is None:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch {tickers['ticker2']} Token Balance Failed {Style.RESET_ALL}"
                    )
                    continue

                if usdc_balance < self.usdc_amount:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {tickers['ticker0']} Token Balance {Style.RESET_ALL}"
                    )
                    break

                if usdt_balance < self.usdt_amount:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {tickers['ticker1']} Token Balance {Style.RESET_ALL}"
                    )
                    break

                if musd_balance < self.musd_amount:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}    Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {tickers['ticker2']} Token Balance {Style.RESET_ALL}"
                    )
                    break

                await self.process_perform_staking(account, address, tickers, use_proxy)
                await self.print_timer()
            
    async def main(self):
        try:
            with open("accounts.txt", "r") as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    await self.load_proxies()

                base_api = await self.fetch_base_api()
                if not base_api: return
                
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Base API Url   : {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}{base_api}{Style.RESET_ALL}"
                )

                self.BASE_API = base_api
                
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

                        self.auth_tokens[address] = self.generate_auth_token(address)
                        if not self.auth_tokens[address]:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Cryptography Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        self.HEADERS[address] = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://autostaking.pro",
                            "Referer": "https://autostaking.pro/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": FakeUserAgent().random
                        }

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
        bot = AutoStaking()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] AutoStaking - BOT{Style.RESET_ALL}                                       "                              
        )
