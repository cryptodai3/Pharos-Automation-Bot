from web3 import Web3
from eth_account import Account
from aiohttp import ClientSession, ClientTimeout
from datetime import datetime
from colorama import *
import asyncio, random, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class OpenFi:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.USDT_CONTRACT_ADDRESS = "0x0B00Fb1F513E02399667FBA50772B21f34c1b5D9"
        self.USDC_CONTRACT_ADDRESS = "0x48249feEb47a8453023f702f15CF00206eeBdF08"
        self.WPHRS_CONTRACT_ADDRESS = "0x253F3534e1e36B9E4a1b9A6F7b6dE47AC3e7AaD3"
        self.GOLD_CONTRACT_ADDRESS = "0x77f532df5f46DdFf1c97CDae3115271A523fa0f4"
        self.TSLA_CONTRACT_ADDRESS = "0xCDA3DF4AAB8a571688fE493EB1BdC1Ad210C09E4"
        self.BTC_CONTRACT_ADDRESS = "0xA4a967FC7cF0E9815bF5c2700A055813628b65BE"
        self.NVIDIA_CONTRACT_ADDRESS = "0x3299cc551B2a39926Bf14144e65630e533dF6944"
        self.MINT_ROUTER_ADDRESS = "0x2E9D89D372837F71Cb529e5BA85bFbC1785C69Cd"
        self.DEPOSIT_ROUTER_ADDRESS = "0xa8E550710Bf113DB6A1B38472118b8d6d5176D12"
        self.SUPPLY_ROUTER_ADDRESS = "0xAd3B4E20412A097F87CD8e8d84FbBe17ac7C89e9"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        self.MINT_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "mint",
                "inputs": [
                    { "internalType": "address", "name": "_asset", "type": "address" },
                    { "internalType": "address", "name": "_account", "type": "address" },
                    { "internalType": "uint256", "name": "_amount", "type": "uint256" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            }
        ]
        self.LENDING_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "depositETH",
                "inputs": [
                    { "name": "lendingPool", "type": "address" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": [],
                "stateMutability": "payable"
            },
            {
                "type": "function",
                "name": "supply",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "onBehalfOf", "type": "address" },
                    { "name": "referralCode", "type": "uint16" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "borrow",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "interestRateMode", "type": "uint256" },
                    { "name": "referralCode", "type": "uint16" },
                    { "name": "onBehalfOf", "type": "address" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            },
            {
                "type": "function",
                "name": "withdraw",
                "inputs": [
                    { "name": "asset", "type": "address" },
                    { "name": "amount", "type": "uint256" },
                    { "name": "to", "type": "address" }
                ],
                "outputs": [],
                "stateMutability": "nonpayable"
            }
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.deposit_amount = 0
        self.supply_amount = 0
        self.borrow_amount = 0
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
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
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

            if contract_address == "PHRS":
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
        
    async def mint_faucet(self, account: str, address: str, asset_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            router_address = web3.to_checksum_address(self.MINT_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.MINT_CONTRACT_ABI)

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
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(mint_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

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

            lending_pool = web3.to_checksum_address("0x0000000000000000000000000000000000000000")
            on_behalf_of = web3.to_checksum_address(address)
            amount_to_wei = web3.to_wei(amount, 'ether')

            router_address = web3.to_checksum_address(self.DEPOSIT_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.LENDING_CONTRACT_ABI)

            deposit_data = router_contract.functions.depositETH(lending_pool, on_behalf_of, 0)
            estimated_gas = deposit_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(deposit_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

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
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                block_number = receipt.blockNumber

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Approve :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                )

                await asyncio.sleep(random.randint(self.min_delay, self.max_delay))

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_supply(self, account: str, address: str, asset_address: str, supply_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.SUPPLY_ROUTER_ADDRESS, asset_address, supply_amount, use_proxy)

            router_address = web3.to_checksum_address(self.SUPPLY_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.LENDING_CONTRACT_ABI)

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
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(supply_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

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

            router_address = web3.to_checksum_address(self.SUPPLY_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.LENDING_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(borrow_amount * (10 ** decimals))
            deposit_data = router_contract.functions.borrow(token_address, amount_to_wei, 2, 0, address)
            estimated_gas = deposit_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(deposit_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

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

            router_address = web3.to_checksum_address(self.SUPPLY_ROUTER_ADDRESS)
            router_contract = web3.eth.contract(address=router_address, abi=self.LENDING_CONTRACT_ABI)

            token_address = web3.to_checksum_address(asset_address)
            token_contract = web3.eth.contract(address=token_address, abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(withdraw_amount * (10 ** decimals))
            deposit_data = router_contract.functions.withdraw(token_address, amount_to_wei, address)
            estimated_gas = deposit_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            deposit_tx = deposit_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(deposit_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

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
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Mint Faucet{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Deposit{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Supply{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}4. Borrow{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}5. Withdraw{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}6. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3/4/5/6] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4, 5, 6]:
                    option_type = (
                        "Mint Faucet" if option == 1 else 
                        "Deposit" if option == 2 else 
                        "Supply" if option == 3 else
                        "Borrow" if option == 4 else
                        "Withdraw" if option == 5 else
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, 3, 4, 5 or 6.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, 4, 5 or 6).{Style.RESET_ALL}")

        if option == 1:
            while True:
                try:
                    min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Mint Faucet Tx -> {Style.RESET_ALL}").strip())
                    if min_delay >= 0:
                        self.min_delay = min_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Mint Faucet Tx -> {Style.RESET_ALL}").strip())
                    if max_delay >= min_delay:
                        self.max_delay = max_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 2:
            while True:
                try:
                    deposit_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Amount ( PHRS ) [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if deposit_amount > 0:
                        self.deposit_amount = deposit_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
        
        elif option == 3:
            while True:
                try:
                    supply_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Supply Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if supply_amount > 0:
                        self.supply_amount = supply_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Supply Tx -> {Style.RESET_ALL}").strip())
                    if min_delay >= 0:
                        self.min_delay = min_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Supply Tx -> {Style.RESET_ALL}").strip())
                    if max_delay >= min_delay:
                        self.max_delay = max_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 4:
            while True:
                try:
                    borrow_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Borrow Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if borrow_amount > 0:
                        self.borrow_amount = borrow_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Borrow Tx -> {Style.RESET_ALL}").strip())
                    if min_delay >= 0:
                        self.min_delay = min_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Borrow Tx -> {Style.RESET_ALL}").strip())
                    if max_delay >= min_delay:
                        self.max_delay = max_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
        
        elif option == 5:
            while True:
                try:
                    withdraw_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if withdraw_amount > 0:
                        self.withdraw_amount = withdraw_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Withdraw Tx -> {Style.RESET_ALL}").strip())
                    if min_delay >= 0:
                        self.min_delay = min_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Withdraw Tx -> {Style.RESET_ALL}").strip())
                    if max_delay >= min_delay:
                        self.max_delay = max_delay
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 6:
            while True:
                try:
                    deposit_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Deposit Amount ( PHRS ) [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if deposit_amount > 0:
                        self.deposit_amount = deposit_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    supply_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Supply Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if supply_amount > 0:
                        self.supply_amount = supply_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    borrow_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Borrow Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if borrow_amount > 0:
                        self.borrow_amount = borrow_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

            while True:
                try:
                    withdraw_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Withdraw Amount For Each Tokens [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if withdraw_amount > 0:
                        self.withdraw_amount = withdraw_amount
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
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
                        print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
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

        return option, choose
    
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
        await asyncio.sleep(5)

        for asset_address in [
                self.USDT_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.GOLD_CONTRACT_ADDRESS,
                self.TSLA_CONTRACT_ADDRESS, self.BTC_CONTRACT_ADDRESS, self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "BTC" if asset_address == self.BTC_CONTRACT_ADDRESS else 
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
        await asyncio.sleep(5)

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}PHRS{Style.RESET_ALL}                            "
        )

        balance = await self.get_token_balance(address, "PHRS", use_proxy)

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
        await asyncio.sleep(5)

        for asset_address in [
                self.USDT_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.WPHRS_CONTRACT_ADDRESS, self.GOLD_CONTRACT_ADDRESS,
                self.TSLA_CONTRACT_ADDRESS, self.BTC_CONTRACT_ADDRESS, self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "BTC" if asset_address == self.BTC_CONTRACT_ADDRESS else 
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
        await asyncio.sleep(5)

        for asset_address in [
                self.USDT_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.WPHRS_CONTRACT_ADDRESS, self.GOLD_CONTRACT_ADDRESS,
                self.TSLA_CONTRACT_ADDRESS, self.BTC_CONTRACT_ADDRESS, self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "BTC" if asset_address == self.BTC_CONTRACT_ADDRESS else 
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
            f"{Fore.GREEN+Style.BRIGHT}Withdraw{Style.RESET_ALL}                       "
        )
        await asyncio.sleep(5)

        for asset_address in [
                self.USDT_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, 
                self.WPHRS_CONTRACT_ADDRESS, self.GOLD_CONTRACT_ADDRESS,
                self.TSLA_CONTRACT_ADDRESS, self.BTC_CONTRACT_ADDRESS, self.NVIDIA_CONTRACT_ADDRESS
            ]:
            
            ticker = ( 
                "USDT" if asset_address == self.USDT_CONTRACT_ADDRESS else 
                "USDC" if asset_address == self.USDC_CONTRACT_ADDRESS else
                "WPHRS" if asset_address == self.WPHRS_CONTRACT_ADDRESS else
                "GOLD" if asset_address == self.GOLD_CONTRACT_ADDRESS else
                "TSLA" if asset_address == self.TSLA_CONTRACT_ADDRESS else
                "BTC" if asset_address == self.BTC_CONTRACT_ADDRESS else 
                "NVIDA"
            )

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}{ticker}{Style.RESET_ALL}                            "
            )

            await self.process_perform_withdraw(account, address, asset_address, self.withdraw_amount, ticker, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool):
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

        else:
            await self.process_option_1(account, address, use_proxy)

            await self.process_option_2(account, address, use_proxy)

            await self.process_option_3(account, address, use_proxy)

            await self.process_option_4(account, address, use_proxy)

            await self.process_option_5(account, address, use_proxy)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, use_proxy_choice = self.print_question()

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

                        await self.process_accounts(account, address, option, use_proxy)
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
