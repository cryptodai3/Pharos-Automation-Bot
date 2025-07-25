from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class OpenFi:
    def __init__(self) -> None:
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.PHRS_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.WPHRS_CONTRACT_ADDRESS = "0x3019B247381c850ab53Dc0EE53bCe7A07Ea9155f"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.WBTC_CONTRACT_ADDRESS = "0x8275c526d1bCEc59a31d673929d3cE8d108fF5c7"
        self.GOLD_CONTRACT_ADDRESS = "0xAaf03Cbb486201099EdD0a52E03Def18cd0c7354"
        self.TSLA_CONTRACT_ADDRESS = "0xA778b48339d3c6b4Bc5a75B37c6Ce210797076b1"
        self.NVIDIA_CONTRACT_ADDRESS = "0xAaF3A7F1676385883593d7Ea7ea4FcCc675EE5d6"
        self.FAUCET_ROUTER_ADDRESS = "0x0E29d74Af0489f4B08fBfc774e25C0D3b5f43285"
        self.WRAPPED_ROUTER_ADDRESS = "0xa7994d63Ec1DED6D1bE5163EE5e75658b3f2cbE4"
        self.POOL_ROUTER_ADDRESS = "0x11d1ca4012d94846962bca2FBD58e5A27ddcBfC5"
        self.LENDING_POOL_ADRESS = "0x0000000000000000000000000000000000000000"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        self.OPENFI_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "mint",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "_asset", "type": "address" },
                    { "internalType": "address", "name": "_account", "type": "address" },
                    { "internalType": "uint256", "name": "_amount", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "depositETH",
                "stateMutability": "payable",
                "inputs": [
                    { "name": "lendingPool", "type": "address" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "supply",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "borrow",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "interestRateMode", "type": "uint256" },
                    { "name": "referralCode", "type": "uint16" },
                    { "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "repay",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "address", "name": "asset", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" },
                    { "internalType": "uint256", "name": "interestRateMode", "type": "uint256" },
                    { "internalType": "address", "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ]
            },
            {
                "type": "function",
                "name": "withdraw",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "to", "type": "address" }
                ],
                "outputs": []
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.deposit_amount = 0
        self.supply_amount = 0
        self.borrow_amount = 0
        self.repay_amount = 0
        self.withdraw_amount = 0
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
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : OpenFi - Automation Bot")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Status     : Running & Monitoring...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by Cryptodai3 × YetiDAO | Buddy v1.5 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

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

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
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
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
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
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
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
                pass
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
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def mint_faucet(self, account: str, address: str, asset_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.FAUCET_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            asset_address = web3.to_checksum_address(asset_address)
            target_address = web3.to_checksum_address(address)

            asset_contract = web3.eth.contract(address=asset_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = asset_contract.functions.decimals().call()

            amount_to_wei = int(100 * (10 ** decimals))
            mint_data = router_contract.functions.mint(asset_address, target_address, amount_to_wei)
            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            mint_tx = mint_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, mint_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_deposit(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount_to_wei = web3.to_wei(amount, "ether")

            router_address = web3.to_checksum_address(self.WRAPPED_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            deposit_data = router_contract.functions.depositETH(self.LENDING_POOL_ADDRESS, address, 0)
            estimated_gas = deposit_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
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
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
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
                approve_data = token_contract.functions.approve(spender, amount_to_wei)
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
                    f"{Fore.CYAN+Style.BRIGHT}     Approve :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_supply(self, account: str, address: str, asset_address: str, supply_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, supply_amount, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(supply_amount * (10 ** decimals))
            supply_data = router_contract.functions.supply(token_address, amount_to_wei, address, 0)
            estimated_gas = supply_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            supply_tx = supply_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, supply_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_borrow(self, account: str, address: str, asset_address: str, borrow_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(borrow_amount * (10 ** decimals))
            borrow_data = router_contract.functions.borrow(token_address, amount_to_wei, 2, 0, address)
            estimated_gas = borrow_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            borrow_tx = borrow_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, borrow_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_repay(self, account: str, address: str, asset_address: str, repay_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, asset_address, repay_amount, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(repay_amount * (10 ** decimals))
            repay_data = router_contract.functions.repay(token_address, amount_to_wei, 2, address)
            estimated_gas = repay_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            repay_tx = repay_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, repay_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_withdraw(self, account: str, address: str, asset_address: str, withdraw_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.POOL_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.OPENFI_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(withdraw_amount * (10 ** decimals))
            withdraw_data = router_contract.functions.withdraw(token_address, amount_to_wei, address)
            estimated_gas = withdraw_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            withdraw_tx = withdraw_data.build_transaction({
                "from": address,
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
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
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
                deposit_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Amount ( PHRS to WPHRS ) -> {Style.RESET_ALL}").strip())
                if deposit_amount > 0:
                    self.deposit_amount = deposit_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_supply_question(self):
        while True:
            try:
                supply_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Supply Amount For Each Tokens -> {Style.RESET_ALL}").strip())
                if supply_amount > 0:
                    self.supply_amount = supply_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_borrow_question(self):
        while True:
            try:
                borrow_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Borrow Amount For Each Tokens -> {Style.RESET_ALL}").strip())
                if borrow_amount > 0:
                    self.borrow_amount = borrow_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_repay_question(self):
        while True:
            try:
                repay_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Repay Amount For Each Tokens -> {Style.RESET_ALL}").strip())
                if repay_amount > 0:
                    self.repay_amount = repay_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_withdraw_question(self):
        while True:
            try:
                withdraw_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount For Each Tokens -> {Style.RESET_ALL}").strip())
                if withdraw_amount > 0:
                    self.withdraw_amount = withdraw_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_delay_question(self):
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
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Mint Faucet{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Deposit{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Supply{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Borrow{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}5. Repay{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}6. Withdraw{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}7. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4/5/6/7] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4, 5, 6, 7]:
                    option_type = (
                        "Mint Faucet" if option == 1 else 
                        "Deposit" if option == 2 else 
                        "Supply" if option == 3 else
                        "Borrow" if option == 4 else
                        "Repay" if option == 5 else
                        "Withdraw" if option == 6 else
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, 4, 5, 6 or 7.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, 4, 5, 6 or 7).{Style.RESET_ALL}")

        if option == 1:
            self.print_delay_question()

        elif option == 2:
            self.print_deposit_question()
            self.print_delay_question()
            
        elif option == 3:
            self.print_supply_question()
            self.print_delay_question()

        elif option == 4:
            self.print_borrow_question()
            self.print_delay_question()
        
        elif option == 5:
            self.print_repay_question()
            self.print_delay_question()
        
        elif option == 6:
            self.print_withdraw_question()
            self.print_delay_question()
            
        elif option == 7:
            self.print_deposit_question()
            self.print_supply_question()
            self.print_borrow_question()
            self.print_repay_question()
            self.print_withdraw_question()
            self.print_delay_question()

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

        return option, choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True
    
    async def process_mint_faucet(self, account: str, address: str, asset_address: str, ticker: str, use_proxy: bool):
        tx_hash, block_number = await self.mint_faucet(account, address, asset_address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Mint 100 {ticker} Faucet Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_deposit(self, account: str, address: str, deposit_amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_deposit(account, address, deposit_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Deposit {deposit_amount} PHRS Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_supply(self, account: str, address: str, asset_address: str, supply_amount: float, ticker: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_supply(account, address, asset_address, supply_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Supply {supply_amount} {ticker} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_borrow(self, account: str, address: str, asset_address: str, borrow_amount: float, ticker: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_borrow(account, address, asset_address, borrow_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Borrow {borrow_amount} {ticker} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
            
    async def process_perform_repay(self, account: str, address: str, asset_address: str, repay_amount: float, ticker: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_repay(account, address, asset_address, repay_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Repay {repay_amount} {ticker} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_withdraw(self, account: str, address: str, asset_address: str, withdraw_amount: float, ticker: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_withdraw(account, address, asset_address, withdraw_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Withdraw {withdraw_amount} {ticker} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_option_1(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Mint Faucet{Style.RESET_ALL}                       "
        )

        for asset_address in [
                self.GOLD_CONTRACT_ADDRESS, self.TSLA_CONTRACT_ADDRESS, self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            await self.process_mint_faucet(account, address, asset_address, ticker, use_proxy)
            await self.print_timer()

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Deposit{Style.RESET_ALL}                       "
        )

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}PHRS to WPHRS{Style.RESET_ALL}                            "
        )

        balance = await self.get_token_balance(address, self.PHRS_CONTRACT_ADDRESS, use_proxy)

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {self.deposit_amount} PHRS {Style.RESET_ALL}"
        )

        if not balance or balance <= self.deposit_amount:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient PHRS Token Balance {Style.RESET_ALL}"
            )
            return

        await self.process_perform_deposit(account, address, self.deposit_amount, use_proxy)
        await self.print_timer()

    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Supply{Style.RESET_ALL}                       "
        )

        for asset_address in [
                self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.USDT_CONTRACT_ADDRESS, self.WBTC_CONTRACT_ADDRESS, 
                self.GOLD_CONTRACT_ADDRESS, self.TSLA_CONTRACT_ADDRESS, 
                self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "WBTC" if asset_address == self.WBTC_CONTRACT_ADDRESS else 
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            balance = await self.get_token_balance(address, asset_address, use_proxy)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {ticker} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.supply_amount} {ticker} {Style.RESET_ALL}"
            )

            if not balance or balance <= self.supply_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {ticker} Token Balance {Style.RESET_ALL}"
                )
                continue

            await self.process_perform_supply(account, address, asset_address, self.supply_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Borrow{Style.RESET_ALL}                       "
        )

        for asset_address in [
                self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.USDT_CONTRACT_ADDRESS, self.WBTC_CONTRACT_ADDRESS, 
                self.GOLD_CONTRACT_ADDRESS, self.TSLA_CONTRACT_ADDRESS, 
                self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "WBTC" if asset_address == self.WBTC_CONTRACT_ADDRESS else 
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            await self.process_perform_borrow(account, address, asset_address, self.borrow_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_5(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Repay{Style.RESET_ALL}                       "
        )

        for asset_address in [
                self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.USDT_CONTRACT_ADDRESS, self.WBTC_CONTRACT_ADDRESS, 
                self.GOLD_CONTRACT_ADDRESS, self.TSLA_CONTRACT_ADDRESS, 
                self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "WBTC" if asset_address == self.WBTC_CONTRACT_ADDRESS else 
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            await self.process_perform_repay(account, address, asset_address, self.repay_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_option_6(self, account: str, address: str, use_proxy: bool):
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT}Withdraw{Style.RESET_ALL}                       "
        )
        await asyncio.sleep(5)

        for asset_address in [
                self.WPHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.USDT_CONTRACT_ADDRESS, self.WBTC_CONTRACT_ADDRESS, 
                self.GOLD_CONTRACT_ADDRESS, self.TSLA_CONTRACT_ADDRESS, 
                self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "WBTC" if asset_address == self.WBTC_CONTRACT_ADDRESS else 
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            await self.process_perform_withdraw(account, address, asset_address, self.withdraw_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            if option == 1:
                await self.process_option_1(account, address, use_proxy)

            elif option == 2:
                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                await self.process_option_3(account, address, use_proxy)

            elif option == 4:
                await self.process_option_4(account, address, use_proxy)

            elif option == 5:
                await self.process_option_5(account, address, use_proxy)

            elif option == 6:
                await self.process_option_6(account, address, use_proxy)

            else:
                await self.process_option_1(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_2(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_3(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_4(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_5(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_6(account, address, use_proxy)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
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
                                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
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
        bot = OpenFi()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] OpenFi - BOT{Style.RESET_ALL}                                       "                              
        )
