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

class Brokex:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://app.brokex.trade",
            "Referer": "https://app.brokex.trade/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://proof.brokex.trade"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.PHRS_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.USDT_CONTRACT_ADDRESS = "0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef"
        self.FAUCET_ROUTER_ADDRESS = "0xa7Bb3C282Ff1eFBc3F2D8fcd60AaAB3aeE3CBa49"
        self.TRADE_ROUTER_ADDRESS = "0x34f89ca5a1c6dc4eb67dfe0af5b621185df32854"
        self.POOL_ROUTER_ADDRESS = "0x9A88d07850723267DB386C681646217Af7e220d7"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"hasClaimed","stateMutability":"view","inputs":[{"internalType":"address","name":"","type":"address"}],"outputs":[{"internalType":"bool","name":"","type":"bool"}]},
            {"type":"function","name":"claim","stateMutability":"nonpayable","inputs":[],"outputs":[]}
        ]''')
        self.BROKEX_CONTRACT_ABI = [
            {
                "name": "openPosition",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "idx", "type": "uint256" },
                    { "internalType": "bytes",   "name": "proof", "type": "bytes" },
                    { "internalType": "bool",    "name": "isLong", "type": "bool" },
                    { "internalType": "uint256", "name": "lev", "type": "uint256" },
                    { "internalType": "uint256", "name": "size", "type": "uint256" },
                    { "internalType": "uint256", "name": "sl", "type": "uint256" },
                    { "internalType": "uint256", "name": "tp", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "name": "getUserOpenIds",
                "type": "function",
                "stateMutability": "view",
                "inputs": [
                    { "internalType": "address", "name": "user", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256[]", "name": "", "type": "uint256[]" }
                ]
            },
            {
                "inputs": [
                    { "internalType": "uint256", "name": "id", "type": "uint256" }
                ],
                "name": "getOpenById",
                "outputs": [
                    {
                        "internalType": "struct IBrokexStorage.Open",
                        "name": "",
                        "type": "tuple",
                        "components": [
                            { "internalType": "address", "name": "trader", "type": "address" },
                            { "internalType": "uint256", "name": "id", "type": "uint256" },
                            { "internalType": "uint256", "name": "assetIndex", "type": "uint256" },
                            { "internalType": "bool",    "name": "isLong",     "type": "bool"    },
                            { "internalType": "uint256", "name": "leverage",   "type": "uint256" },
                            { "internalType": "uint256", "name": "openPrice",  "type": "uint256" },
                            { "internalType": "uint256", "name": "sizeUsd",    "type": "uint256" },
                            { "internalType": "uint256", "name": "timestamp",  "type": "uint256" },
                            { "internalType": "uint256", "name": "stopLossPrice",   "type": "uint256" },
                            { "internalType": "uint256", "name": "takeProfitPrice", "type": "uint256" },
                            { "internalType": "uint256", "name": "liquidationPrice","type": "uint256" }
                        ]
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "name": "closePosition",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "openId", "type": "uint256" },
                    { "internalType": "bytes",   "name": "proof",  "type": "bytes"   }
                ],
                "outputs": []
            },
            {
                "name": "depositLiquidity",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "usdtAmount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "name": "balanceOf", 
                "type": "function",
                "stateMutability": "view", 
                "inputs": [
                    { "internalType": "address", "name": "account", "type": "address" }
                ], 
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ], 
            },
            {
                "name": "withdrawLiquidity",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "uint256", "name": "lpAmount", "type":"uint256" }
                ],
                "outputs": []
            }
        ]
        self.pairs = [
            { "name": "BTC_USDT", "desimal": 0 },
            { "name": "ETH_USDT", "desimal": 1 },
            { "name": "SOL_USDT", "desimal": 10 },
            { "name": "XRP_USDT", "desimal": 14 },
            { "name": "AVAX_USDT", "desimal": 5 },
            # { "name": "DOGE_USDT", "desimal": 3 },
            { "name": "TRX_USDT", "desimal": 15 },
            { "name": "ADA_USDT", "desimal": 16 },
            { "name": "SUI_USDT", "desimal": 90 },
            { "name": "LINK_USDT", "desimal": 2 },
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.open_ids = {}
        self.potition_option = 0
        self.potition_count = 0
        self.open_amount = 0
        self.deposit_lp_count = 0
        self.deposit_lp_amount = 0
        self.withdraw_lp_count = 0
        self.withdraw_lp_amount = 0
        self.lp_option = 0
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

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Pharos Testnet Automation BOT  ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Brokex - Automation Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v2.2 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

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
        
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            if contract_address == self.PHRS_CONTRACT_ADDRESS:
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
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
        
    async def get_lp_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)
            balance = token_contract.functions.balanceOf(address).call()

            lp_balance = balance / (10 ** 18)

            return lp_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def get_user_open_ids(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)
            open_ids = token_contract.functions.getUserOpenIds(address).call()

            return open_ids
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def get_open_data_by_id(self, address: str, open_id: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)
            open_data = token_contract.functions.getOpenById(open_id).call()

            return {
                "trader": open_data[0],
                "id": open_data[1],
                "assetIndex": open_data[2],
                "isLong": open_data[3],
                "leverage": open_data[4],
                "openPrice": open_data[5],
                "sizeUsd": open_data[6],
                "timestamp": open_data[7],
                "stopLossPrice": open_data[8],
                "takeProfitPrice": open_data[9],
                "liquidationPrice": open_data[10]
            }
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
        
    async def check_faucet_status(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            claim_data = token_contract.functions.hasClaimed(web3.to_checksum_address(address)).call()

            return claim_data
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_claim_faucet(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            claim_data = token_contract.functions.claim()
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
        
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount: float, use_proxy: bool):
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
                    f"{Fore.CYAN+Style.BRIGHT}   Approve :{Style.RESET_ALL}"
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
                await asyncio.sleep(5)

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")

    async def perform_open_potition(self, account: str, address: str, pair: int, is_long: bool, use_proxy: bool, lev=1, sl=0, tp=0):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(self.USDT_CONTRACT_ADDRESS)
            asset_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()
            
            open_amount = int(self.open_amount * (10 ** decimals))

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, self.open_amount, use_proxy)

            await self.approving_token(account, address, self.TRADE_ROUTER_ADDRESS, asset_address, self.open_amount, use_proxy)

            proof = await self.get_proof(address, pair, use_proxy)
            if not proof:
                raise Exception("Failed to Fetch Proof")

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            open_position_data = token_contract.functions.openPosition(pair, proof['proof'], is_long, lev, open_amount, sl, tp)
            estimated_gas = open_position_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            open_position_tx = open_position_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, open_position_tx)
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
        
    async def perform_close_potition(self, account: str, address: str, open_id: int, pair: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            proof = await self.get_proof(address, pair, use_proxy)
            if not proof:
                raise Exception("Failed to Fetch Proof")

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            close_position_data = token_contract.functions.closePosition(open_id, proof['proof'])
            estimated_gas = close_position_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            close_position_tx = close_position_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, close_position_tx)
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
        
    async def perform_deposit_lp(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(self.USDT_CONTRACT_ADDRESS)
            asset_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()
            
            deposit_lp_amount = int(self.deposit_lp_amount * (10 ** decimals))

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, self.deposit_lp_amount, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            lp_data = token_contract.functions.depositLiquidity(deposit_lp_amount)
            estimated_gas = lp_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, lp_tx)
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
        
    async def perform_withdraw_lp(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            withdraw_lp_amount = int(self.withdraw_lp_amount * (10 ** 18))

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POOL_ROUTER_ADDRESS), abi=self.BROKEX_CONTRACT_ABI)

            lp_data = token_contract.functions.withdrawLiquidity(withdraw_lp_amount)
            estimated_gas = lp_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, lp_tx)
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

    def print_potition_option_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Choose Potition Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Open Potition{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Close Potition{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Skipped{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Open Potition" if option == 1 else 
                        "Close Potition" if option == 2 else 
                        "Skipped"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")

                    if option == 1:
                        self.print_potition_question("Open")
                        self.print_open_question()

                    elif option == 2:
                        self.print_potition_question("Close")

                    self.potition_option = option
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

    def print_potition_question(self, type: str):
        while True:
            try:
                potition_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}{type} Potition Count For Each Wallet -> {Style.RESET_ALL}").strip())
                if potition_count > 0:
                    self.potition_count = potition_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}{type} Potition Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
    
    def print_open_question(self):
        while True:
            try:
                open_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Open Potition Amount [Min 10] -> {Style.RESET_ALL}").strip())
                if open_amount >= 10:
                    self.open_amount = open_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Open Potition Amount must be >= 10.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_lp_option_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Choose LP Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Deposit Liquidity{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Withdraw Liquidity{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Skipped{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Deposit Liquidity" if option == 1 else 
                        "Withdraw Liquidity" if option == 2 else 
                        "Skipped"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")

                    if option == 1:
                        self.print_deposit_lp_question()

                    elif option == 2:
                        self.print_withdraw_lp_question()

                    self.lp_option = option
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")
    
    def print_deposit_lp_question(self):
        while True:
            try:
                deposit_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Deposit Liquidity Count For Each Wallet -> {Style.RESET_ALL}").strip())
                if deposit_lp_count > 0:
                    self.deposit_lp_count = deposit_lp_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Deposit Liquidity Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                deposit_lp_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Liquidity Amount -> {Style.RESET_ALL}").strip())
                if deposit_lp_amount > 0:
                    self.deposit_lp_amount = deposit_lp_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Deposit Liquidity Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_withdraw_lp_question(self):
        while True:
            try:
                withdraw_lp_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Withdraw Liquidity Count For Each Wallet -> {Style.RESET_ALL}").strip())
                if withdraw_lp_count > 0:
                    self.withdraw_lp_count = withdraw_lp_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Withdraw Liquidity Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                withdraw_lp_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Liquidity Amount -> {Style.RESET_ALL}").strip())
                if withdraw_lp_amount > 0:
                    self.withdraw_lp_amount = withdraw_lp_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Withdraw Liquidity Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_delay_question(self):
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
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Claim Faucet{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Open Potition{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Close Potition{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Deposit Liquidity{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}5. Withdraw Liquidity{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}6. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4/5/6] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4, 5, 6]:
                    option_type = (
                        "Claim Faucet" if option == 1 else 
                        "Open Potition" if option == 2 else 
                        "Close Potition" if option == 3 else 
                        "Deposit Liquidity" if option == 4 else 
                        "Withdraw Liquidity" if option == 5 else 
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, 4, 5, or 6.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, 4, 5, or 6).{Style.RESET_ALL}")

        if option == 2:
            self.print_potition_question("Open")
            self.print_open_question()
            self.print_delay_question()

        if option == 3:
            self.print_potition_question("Close")
            self.print_delay_question()
            
        elif option == 4:
            self.print_deposit_lp_question()
            self.print_delay_question()

        elif option == 5:
            self.print_withdraw_lp_question()
            self.print_delay_question()
            
        elif option == 6:
            self.print_potition_option_question()
            self.print_lp_option_question()
            self.print_delay_question()

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

        return option, proxy_choice, rotate_proxy
    
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
        
    async def get_proof(self, address: str, pair: int, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/proof?pairs={pair}"
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.HEADERS, proxy=proxy, proxy_auth=proxy_auth) as response:
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
        has_claimed = await self.check_faucet_status(address, use_proxy)
        if not has_claimed:
            tx_hash, block_number = await self.perform_claim_faucet(account, address, use_proxy)
            if tx_hash and block_number:
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} USDT Faucet Claimed Successfully {Style.RESET_ALL}"
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
                f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
            )

    async def process_perform_open_potition(self, account: str, address: str, pair: int, is_long: bool, use_proxy: bool):
        tx_hash, block_number = await self.perform_open_potition(account, address, pair, is_long, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Open Potition Success {Style.RESET_ALL}"
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
            
    async def process_perform_close_potition(self, account: str, address: str, used_ids, open_id: int, pair: int, use_proxy: bool):
        tx_hash, block_number = await self.perform_close_potition(account, address, open_id, pair, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            used_ids.add(open_id)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Close Potition Success {Style.RESET_ALL}"
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

    async def process_perform_deposit_lp(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit_lp(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Deposit Liquidity Success {Style.RESET_ALL}"
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

    async def process_perform_withdraw_lp(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_withdraw_lp(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Withdraw Liquidity Success {Style.RESET_ALL}"
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

    async def process_option_1(self, account: str, address: str, use_proxy):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Claim Faucet{Style.RESET_ALL}"
        )

        await self.process_perform_claim_faucet(account, address, use_proxy)

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Potition{Style.RESET_ALL}"
        )

        for i in range(self.potition_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Trade {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.potition_count}{Style.RESET_ALL}                                   "
            )

            pairs = random.choice(self.pairs)
            is_long = random.choice([True, False])
            name = pairs["name"]
            pair = pairs["desimal"]
            action = "Long" if is_long == True else "Short"

            balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} USDT {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.open_amount} USDT {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Pair    :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {action} - {name} {Style.RESET_ALL}"
            )

            if not balance or balance <= self.open_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDT Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_open_potition(account, address, pair, is_long, use_proxy)
            await self.print_timer()

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Potition{Style.RESET_ALL}"
        )

        open_ids = await self.get_user_open_ids(address, use_proxy)
        if not open_ids:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} No Open Ids Found {Style.RESET_ALL}"
            )
            return

        self.open_ids[address] = open_ids

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Fetch {len(open_ids)} Open Ids Success {Style.RESET_ALL}"
        )

        used_ids = set()

        for i in range(self.potition_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Trade {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.potition_count}{Style.RESET_ALL}                                   "
            )

            available_ids = [oid for oid in self.open_ids[address] if oid not in used_ids]
            if not available_ids:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} No more unique Open Ids available. Stopping early. {Style.RESET_ALL}"
                )
                break

            open_id = random.choice(available_ids)

            open_data = await self.get_open_data_by_id(address, open_id, use_proxy)
            if not open_data:
                continue
            
            pair = open_data["assetIndex"]
            is_long = open_data["isLong"]
            size = open_data["sizeUsd"]

            name = (
                "BTC_USDT" if pair == 0 else "ETH_USDT" if pair == 1 else 
                "SOL_USDT" if pair == 10 else "XRP_USDT" if pair == 14 else 
                "AVAX_USDT" if pair == 5 else "DOGE_USDT" if pair == 3 else 
                "TRX_USDT" if pair == 15 else "ADA_USDT" if pair == 16 else 
                "SUI_USDT" if pair == 90 else "LINK_USDT" if pair == 2 else 
                "NaN_USDT"
            )
            formatted_size = size / 10**6
            action = "Long" if is_long == True else "Short"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Open Id :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {open_id} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Size    :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {formatted_size} USDT {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Pair    :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {action} - {name} {Style.RESET_ALL}"
            )
            
            await self.process_perform_close_potition(account, address, used_ids, open_id, pair, use_proxy)
            await self.print_timer()

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Liquidity Pool{Style.RESET_ALL}"
        )

        for i in range(self.deposit_lp_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Deposit LP {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.deposit_lp_count}{Style.RESET_ALL}                                   "
            )

            balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} USDT {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.deposit_lp_amount} USDT {Style.RESET_ALL}"
            )

            if not balance or balance <= self.deposit_lp_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDT Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_deposit_lp(account, address, use_proxy)
            await self.print_timer()

    async def process_option_5(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Liquidity Pool{Style.RESET_ALL}"
        )

        for i in range(self.withdraw_lp_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ●{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} Withdraw LP {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.withdraw_lp_count}{Style.RESET_ALL}                                   "
            )

            balance = await self.get_lp_balance(address, use_proxy)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   LP Held :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.withdraw_lp_amount} {Style.RESET_ALL}"
            )

            if not balance or balance <= self.withdraw_lp_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient LP Tokens Held {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_withdraw_lp(account, address, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
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
            
            if option == 1:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Claim Faucet {Style.RESET_ALL}"
                )
                
                await self.process_option_1(account, address, use_proxy)

            elif option == 2:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Open Potition {Style.RESET_ALL}"
                )

                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Close Potition {Style.RESET_ALL}"
                )

                await self.process_option_3(account, address, use_proxy)

            elif option == 4:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Deposit Liquidity {Style.RESET_ALL}"
                )

                await self.process_option_4(account, address, use_proxy)

            elif option == 5:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Withdraw Liquidity {Style.RESET_ALL}"
                )

                await self.process_option_5(account, address, use_proxy)

            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Run All Features {Style.RESET_ALL}"
                )

                await self.process_option_1(account, address, use_proxy)
                await asyncio.sleep(5)
                
                if self.potition_option == 1:
                    await self.process_option_2(account, address, use_proxy)
                elif self.potition_option == 2:
                    await self.process_option_3(account, address, use_proxy)

                await asyncio.sleep(5)

                if self.lp_option == 1:
                    await self.process_option_4(account, address, use_proxy)

                elif self.lp_option == 2:
                    await self.process_option_5(account, address, use_proxy)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            option, proxy_choice, rotate_proxy = self.print_question()

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

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
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
        bot = Brokex()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Brokex Protocol - BOT{Style.RESET_ALL}                                       "                              
        )
