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

class Bitverse:
    def __init__(self) -> None:
        self.BASE_API = "https://api.bitverse.zone/bitverse"
        self.RPC_URL = "https://testnet.dplabs-internal.com/"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.POSITION_ROUTER_ADDRESS = "0xA307cE75Bc6eF22794410D783e5D4265dEd1A24f"
        self.TRADE_ROUTER_ADDRESS = "0xbf428011d76eFbfaEE35a20dD6a0cA589B539c54"
        self.TRADE_PROVIDER_ADDRESS = "bvx17w0adeg64ky0daxwd2ugyuneellmjgnx53lm9l"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"nonpayable","inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[]}
        ]''')
        self.BITVERSE_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "placeOrder",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "string", "name": "pairId", "type": "string" }, 
                    { "internalType": "uint256", "name": "price", "type": "uint256" }, 
                    { "internalType": "uint8", "name": "orderType", "type": "uint8" }, 
                    { "internalType": "uint64", "name": "leverageE2", "type": "uint64" }, 
                    { "internalType": "uint8", "name": "side", "type": "uint8" }, 
                    { "internalType": "uint64", "name": "slippageE6", "type": "uint64" }, 
                    {
                        "type": "tuple[]" ,
                        "name": "margins",
                        "internalType": "struct Margin[]",
                        "components": [
                            { "internalType": "address", "name": "token", "type": "address" }, 
                            { "internalType": "uint256", "name": "amount", "type": "uint256" }
                        ]
                    }, 
                    { "internalType": "uint256", "name": "takeProfitPrice", "type": "uint256" }, 
                    { "internalType": "uint256", "name": "stopLossPrice", "type": "uint256" }, 
                    { "internalType": "uint256", "name": "positionLongOI", "type": "uint256" }, 
                    { "internalType": "uint256", "name": "positionShortOI", "type": "uint256" }, 
                    { "internalType": "uint256", "name": "timestamp", "type": "uint256" }, 
                    { "internalType": "bytes", "name": "signature", "type": "bytes" }, 
                    { "internalType": "bool", "name": "isExecuteImmediately", "type": "bool" }
                ],
                "outputs": []
            }
        ]
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.action_option = 0
        self.deposit_amount = 0
        self.withdraw_amount = 0
        self.trade_count = 0
        self.trade_amount = 0
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

    def welcome(self, project_name="AutoStaking"):
        border = "═╬═" * 20  # Dynamic border pattern
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + border)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "    ⚡ YetiDAO Public Automation BOT ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + f"   🧠 Project    : Bitverse - Public Bot")
        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "    💻 Author     : YetiDAO")
        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "    🌐 Status     : Running & Open for Community 🌱")
        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "    🛰️ Mode       : Public (Free to Use)")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.0 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + border)

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
        
    def generate_trade_option(self):
        trade_pair = random.choice(["BTC-USD", "ETH-USD"])
        # trade_side = random.choice([1, 2])
        return trade_pair, 1
    
    def generate_order_payload(self, trade_pair: str, acceptable_price: int, trade_side: int):
        payload = {
            "address":self.TRADE_PROVIDER_ADDRESS,
            "pair":trade_pair,
            "price":str(acceptable_price),
            "orderType":2,
            "leverageE2":500,
            "side":trade_side,
            "margin":[
                {"denom":"USDT","amount":str(int(self.trade_amount))}
            ],
            "allowedSlippage":"10",
            "isV2":"0"
        }

        return payload
        
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
    
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount:
                approve_data = token_contract.functions.approve(spender, amount)
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
        
    async def perform_deposit(self, account: str, address: str, asset: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(asset)
            asset_contract = web3.eth.contract(address=asset_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            amount_to_wei = int(amount * (10 ** decimals))

            await self.approving_token(account, address, self.POSITION_ROUTER_ADDRESS, asset_address, amount_to_wei, use_proxy)

            contract_address = web3.to_checksum_address(self.POSITION_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            deposit_data = token_contract.functions.deposit(asset_address, amount_to_wei)
            estimated_gas = deposit_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, deposit_tx)
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
        
    async def perform_withdraw(self, account: str, address: str, asset: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(asset)
            asset_contract = web3.eth.contract(address=asset_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            amount_to_wei = int(amount * (10 ** decimals))

            contract_address = web3.to_checksum_address(self.POSITION_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            withdraw_data = token_contract.functions.withdraw(asset_address, amount_to_wei)
            estimated_gas = withdraw_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            withdraw_tx = withdraw_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, withdraw_tx)
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
        
    async def perform_trade(self, account: str, address: str, orders: dict, acceptable_price: int, asset: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            asset_address = web3.to_checksum_address(asset)
            asset_contract = web3.eth.contract(address=asset_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            amount_to_wei = int(amount * (10 ** decimals))

            pair_id = orders["result"]["pair"]
            order_type = 2
            leverage_e2 = int(orders["result"]["leverageE2"])
            side = int(orders["result"]["side"])
            slippage_e6 = int(orders["result"]["allowedSlippage"])
            margins = [(asset_address, amount_to_wei)]
            take_profit_price = 0
            stop_loss_price = 0
            position_long_oi = int(orders["result"]["longOI"])
            position_short_oi = int(orders["result"]["shortOI"])
            timestamp = int(orders["result"]["signTimestamp"])
            signature = bytes.fromhex(orders["result"]["sign"][2:])
            is_execute_immediately = bool(orders["result"]["marketOpening"])

            contract_address = web3.to_checksum_address(self.TRADE_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.BITVERSE_CONTRACT_ABI)

            trade_data = token_contract.functions.placeOrder(
                pair_id, acceptable_price, order_type, leverage_e2, side, slippage_e6, margins, take_profit_price, 
                stop_loss_price, position_long_oi, position_short_oi, timestamp, signature, is_execute_immediately
            )

            estimated_gas = trade_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            trade_tx = trade_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, trade_tx)
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

    def print_deposit_question(self):
        while True:
            try:
                deposit_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Amount [USDT] -> {Style.RESET_ALL}").strip())
                if deposit_amount > 0:
                    self.deposit_amount = deposit_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Deposit Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_withdraw_question(self):
        while True:
            try:
                withdraw_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount [USDT] -> {Style.RESET_ALL}").strip())
                if withdraw_amount > 0:
                    self.withdraw_amount = withdraw_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Withdraw Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_trade_question(self):
        while True:
            try:
                trade_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Trade Count -> {Style.RESET_ALL}").strip())
                if trade_count > 0:
                    self.trade_count = trade_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Trade Count must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
        
        while True:
            try:
                trade_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Trade Amount [Min. 2 USDT] -> {Style.RESET_ALL}").strip())
                if trade_amount >= 2:
                    self.trade_amount = trade_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Trade Amount must be >= 2.{Style.RESET_ALL}")
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
        
    def print_action_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Deposit USDT{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Withdraw USDT{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if option in [1, 2]:
                    option_type = (
                        "Deposit USDT" if option == 1 else 
                        "Withdraw USDT"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    self.action_option = option
                    if self.action_option == 1:
                        self.print_deposit_question()
                    elif self.action_option == 2:
                        self.print_withdraw_question()
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")
    
    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Deposit USDT{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Withdraw USDT{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Random Trade{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4]:
                    option_type = (
                        "Deposit USDT" if option == 1 else 
                        "Withdraw USDT" if option == 2 else 
                        "Random Trade" if option == 3 else 
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, or 4.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, or 4).{Style.RESET_ALL}")

        if option == 1:
            self.print_deposit_question()

        elif option == 2:
            self.print_withdraw_question()

        elif option == 3:
            self.print_trade_question()
            self.print_delay_question()

        elif option == 4:
            self.print_action_question()
            self.print_trade_question()
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
        
    async def get_all_balance(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/trade-data/v1/account/balance/allCoinBalance"
        data = json.dumps({"address":address})
        headers = {
            **self.HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Deposited USDT Token Balance Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
        
    async def get_market_price(self, address: str, trade_pair: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/quote-all-in-one/v1/public/market/ticker?symbol={trade_pair}"
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.HEADERS[address], proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch {trade_pair} Market Price Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
        
    async def order_simulation(self, address: str, trade_pair: str, acceptable_price: int, trade_side: int, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/trade-data/v1//order/simulation/pendingOrder"
        data = json.dumps(self.generate_order_payload(trade_pair, acceptable_price, trade_side))
        headers = {
            **self.HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Built Order Simulation Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
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
    
    async def process_perform_deposit(self, account: str, address: str, asset: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit(account, address, asset, amount, use_proxy)
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
    
    async def process_perform_withdraw(self, account: str, address: str, asset: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_withdraw(account, address, asset, amount, use_proxy)
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
    
    async def process_perform_trade(self, account: str, address: str, orders: dict, acceptable_price: int, asset: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_trade(account, address, orders, acceptable_price, asset, amount, use_proxy)
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

    async def process_option_1(self, account: str, address: str, use_proxy):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Deposit :{Style.RESET_ALL}")

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.deposit_amount} USDT {Style.RESET_ALL}"
        )

        balance = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)
        if balance is None:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Fetch USDT Token Balance Failed {Style.RESET_ALL}"
            )
            return
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} USDT {Style.RESET_ALL}"
        )
        
        if balance < self.deposit_amount:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDT Token Balance {Style.RESET_ALL}"
            )
            return

        await self.process_perform_deposit(account, address, self.USDT_CONTRACT_ADDRESS, self.deposit_amount, use_proxy)

    async def process_option_2(self, account: str, address: str, use_proxy):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Withdraw:{Style.RESET_ALL}")

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.withdraw_amount} USDT {Style.RESET_ALL}"
        )

        all_balance = await self.get_all_balance(address, use_proxy)
        if all_balance is None: return
        
        if all_balance and all_balance.get("retCode") != 0:
            msg = all_balance.get("retMsg", "Unknown Error")
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Fetch Deposited USDT Token Balance Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
            )
            return
        
        coin_balance = all_balance.get("result", {}).get("coinBalance", [])
        if not coin_balance:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} No Tokens Have Been Deposited Yet {Style.RESET_ALL}"
            )
            return
        
        usdt_data = next(
            (coin for coin in coin_balance if coin.get("coinName") == "USDT"),
            None
        )

        balance = float(usdt_data.get("balanceSize", 0) if usdt_data else 0)

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} USDT {Style.RESET_ALL}"
        )
        
        if balance < self.withdraw_amount:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient Deposited USDT Token Balance {Style.RESET_ALL}"
            )
            return

        await self.process_perform_withdraw(account, address, self.USDT_CONTRACT_ADDRESS, self.withdraw_amount, use_proxy)

    async def process_option_3(self, account: str, address: str, use_proxy):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Trading :{Style.RESET_ALL}")

        for i in range(self.trade_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Trade{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}Of{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.trade_count} {Style.RESET_ALL}                                   "
            )

            trade_pair, trade_side = self.generate_trade_option()
            trade_option, color = (
                ("[Long]", Fore.GREEN) if trade_side == 1 else ("[Short]", Fore.RED)
            )

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Pair    :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {trade_pair} {Style.RESET_ALL}"
                f"{color+Style.BRIGHT}{trade_option}{Style.RESET_ALL}"
            )

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.trade_amount} USDT {Style.RESET_ALL}"
            )

            all_balance = await self.get_all_balance(address, use_proxy)
            if all_balance is None: continue
            
            if all_balance and all_balance.get("retCode") != 0:
                msg = all_balance.get("retMsg", "Unknown Error")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Deposited USDT Token Balance Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
                continue
            
            coin_balance = all_balance.get("result", {}).get("coinBalance", [])
            if not coin_balance:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} No Tokens Have Been Deposited Yet {Style.RESET_ALL}"
                )
                return
            
            usdt_data = next(
                (coin for coin in coin_balance if coin.get("coinName") == "USDT"),
                None
            )

            balance = float(usdt_data.get("balanceSize", 0) if usdt_data else 0)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} USDT {Style.RESET_ALL}"
            )
            
            if balance < self.trade_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient Deposited USDT Token Balance {Style.RESET_ALL}"
                )
                return
            
            markets = await self.get_market_price(address, trade_pair, use_proxy)
            if not markets: continue

            if markets and markets.get("retCode") != 0:
                msg = markets.get("retMsg", "Unknown Error")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch {trade_pair} Market Price Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
                continue

            market_price = float(markets.get("result", {}).get("lastPrice"))
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Price   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {market_price} USDT {Style.RESET_ALL}"
            )

            if trade_side == 1:
                acceptable_price = market_price * (1 + 0.01)
            elif trade_side == 2:
                acceptable_price = market_price * (1 - 0.01)

            acceptable_price_to_wei = int(acceptable_price * (10**6))

            orders = await self.order_simulation(address, trade_pair, acceptable_price_to_wei, trade_side, use_proxy)
            if not orders: continue

            if orders and orders.get("retCode") != 0:
                msg = orders.get("retMsg", "Unknown Error")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Built Simulation Order Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
                continue

            await self.process_perform_trade(account, address, orders, acceptable_price_to_wei, self.USDT_CONTRACT_ADDRESS, self.trade_amount, use_proxy)
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
                    f"{Fore.BLUE+Style.BRIGHT} Deposit USDT {Style.RESET_ALL}"
                )
                
                await self.process_option_1(account, address, use_proxy)
            
            elif option == 2:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Withdraw USDT {Style.RESET_ALL}"
                )
                
                await self.process_option_2(account, address, use_proxy)
            
            elif option == 3:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Random Trade {Style.RESET_ALL}"
                )
                
                await self.process_option_3(account, address, use_proxy)
            
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Run All Features {Style.RESET_ALL}"
                )
                
                if self.action_option == 1:
                    await self.process_option_1(account, address, use_proxy)
                else:
                    await self.process_option_2(account, address, use_proxy)

                await asyncio.sleep(5)

                await self.process_option_3(account, address, use_proxy)

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

                        self.HEADERS[address] = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Chain-Id": "688688",
                            "Origin": "https://testnet.bitverse.zone",
                            "Referer": "https://testnet.bitverse.zone/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "Tenant-Id": "PHAROS",
                            "User-Agent": FakeUserAgent().random
                        }

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
        bot = Bitverse()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Bitverse - BOT{Style.RESET_ALL}                                       "                              
        )
