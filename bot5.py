from web3 import Web3
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientSession, ClientTimeout
from fake_useragent import FakeUserAgent
from colorama import init, Fore, Style
import asyncio, json, os, random, time, sys

# Initialize colorama for colored output
init(autoreset=True)

class PharosTestnet:
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/ef2693fcb98646c694885bc318c00126"
        self.TOKENS = {
            "PHRS": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "WBTC": "0x8275c526d1bCEc59a31d673929d3cE8d108fF5c7",
            "WETH": "0x4E28826d32F1C398DED160DC16Ac6873357d048f",
            "USDC": "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED",
            "USDT": "0xD4071393f8716661958F766DF660033b3d35fD29",
            "WPHRS": "0x3019B247381c850ab53Dc0EE53bCe7A07Ea9155f"
        }
        self.POSITION_MANAGER_ADDRESS = "0x4b177aded3b8bd1d5d747f91b9e853513838cd49"
        self.SWAP_ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        self.EXPLORER_URL = "https://pharos-testnet.socialscan.io/tx"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {
                "type": "function",
                "name": "balanceOf",
                "stateMutability": "view",
                "inputs": [{"name": "address", "type": "address"}],
                "outputs": [{"name": "", "type": "uint256"}]
            },
            {
                "type": "function",
                "name": "allowance",
                "stateMutability": "view",
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"}
                ],
                "outputs": [{"name": "", "type": "uint256"}]
            },
            {
                "type": "function",
                "name": "approve",
                "stateMutability": "nonpayable",
                "inputs": [
                    {"name": "spender", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "outputs": [{"name": "", "type": "bool"}]
            },
            {
                "type": "function",
                "name": "decimals",
                "stateMutability": "view",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint8"}]
            },
            {
                "type": "function",
                "name": "deposit",
                "stateMutability": "payable",
                "inputs": [],
                "outputs": []
            },
            {
                "type": "function",
                "name": "withdraw",
                "stateMutability": "nonpayable",
                "inputs": [{"name": "wad", "type": "uint256"}],
                "outputs": []
            }
        ]''')
        self.ADD_LP_CONTRACT_ABI = json.loads('''[
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "address", "name": "token0", "type": "address"},
                            {"internalType": "address", "name": "token1", "type": "address"},
                            {"internalType": "uint24", "name": "fee", "type": "uint24"},
                            {"internalType": "int24", "name": "tickLower", "type": "int24"},
                            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                            {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "mint",
                "outputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
                    {"internalType": "uint256", "name": "amount0", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1", "type": "uint256"}
                ],
                "stateMutability": "payable",
                "type": "function"
            }
        ]''')
        self.SWAP_ROUTER_ABI = json.loads('''[
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "address", "name": "tokenIn", "type": "address"},
                            {"internalType": "address", "name": "tokenOut", "type": "address"},
                            {"internalType": "uint24", "name": "fee", "type": "uint24"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                            {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                        ],
                        "internalType": "struct ISwapRouter.ExactInputSingleParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInputSingle",
                "outputs": [
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
                ],
                "stateMutability": "payable",
                "type": "function"
            }
        ]''')
        self.ref_code = "8G8MJ3zGE5B7tJgP"
        self.signatures = {}
        self.access_tokens = {}
        self.wrap_option = None
        self.wrap_amount = 0
        self.swap_amount = 0
        self.auto_all_count = 0
        self.swap_count = 0

    def log(self, message, indent=0, color=Fore.WHITE):
        print(f"{'  ' * indent}{color}{message}{Style.RESET_ALL}")

    def loading_animation(self):
        animation = "|/-\\"
        for i in range(10):
            sys.stdout.write(f"\r{Fore.YELLOW}Initializing{animation[i % len(animation)]}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 20 + "\r")
        sys.stdout.flush()

    def display_menu(self):
        banner = """
███████╗ █████╗ ██████╗  ██████╗ ███████╗██╗    ██╗ █████╗ ██████╗ 
██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔════╝██║    ██║██╔══██╗██╔══██╗
█████╗  ███████║██████╔╝██║   ██║███████╗██║ █╗ ██║███████║██████╔╝
██╔══╝  ██╔══██║██╔══██╗██║   ██║╚════██║██║███╗██║██╔══██║██╔═══╝ 
██║     ██║  ██║██║  ██║╚██████╔╝███████║╚███╔███╔╝██║  ██║██║     
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝     
"""
        print(f"{Style.BRIGHT + Fore.CYAN}{banner}")
        print(f"{Style.BRIGHT + Fore.MAGENTA}{'=' * 50}")
        print(f"{Fore.CYAN}     PHAROS X Faroswap Auto Tx Bot          ")
        print(f"{Fore.CYAN}           LETS FUCK THIS TESTNET           ")
        print(f"{Style.BRIGHT + Fore.MAGENTA}{'=' * 50}")
        print(f"{Fore.GREEN}1. Wrap PHRS to WPHRS")
        print(f"{Fore.YELLOW}2. Unwrap WPHRS to PHRS")
        print(f"{Fore.CYAN}3. Auto All (Wrap, Unwrap, Swap, Liquidity)")
        print(f"{Fore.WHITE}4. Swap Tokens")
        print(f"{Fore.RED}5. Exit")
        print(f"{Style.BRIGHT + Fore.MAGENTA}{'=' * 50}")

    def generate_address(self, account):
        try:
            account = Account.from_key(account)
            return account.address
        except Exception as e:
            self.log(f"Generate Address Failed: {e}", indent=1, color=Fore.RED)
            return None

    def generate_signature(self, account):
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=account)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return to_hex(signed_message.signature)
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.log(f"Signature attempt {attempt + 1} failed: {e}, retrying...", indent=1, color=Fore.YELLOW)
                        time.sleep(2)
                    else:
                        self.log(f"Generate Signature Failed after {max_retries} attempts: {e}", indent=1, color=Fore.RED)
                        return None
        except Exception as e:
            self.log(f"Generate Signature Failed: {e}", indent=1, color=Fore.RED)
            return None

    def mask_account(self, account):
        try:
            return account[:4] + '*' * 4 + account[-4:]
        except:
            return None

    async def get_web3(self, retries=3, timeout=60):
        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs={"timeout": timeout}))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                self.log(f"Failed to Connect to RPC: {e}", indent=1, color=Fore.RED)
                return None

    async def get_token_balance(self, address, token_symbol):
        try:
            web3 = await self.get_web3()
            if not web3:
                return None
            contract_address = self.TOKENS.get(token_symbol)
            if not contract_address:
                self.log(f"Invalid token symbol: {token_symbol}", indent=1, color=Fore.RED)
                return None
            if token_symbol == "PHRS":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()
            return balance / (10 ** decimals)
        except Exception as e:
            self.log(f"Get Token Balance Failed for {token_symbol}: {e}", indent=1, color=Fore.RED)
            return None

    async def perform_wrapped(self, account, address):
        try:
            web3 = await self.get_web3()
            if not web3:
                return None, None
            contract_address = web3.to_checksum_address(self.TOKENS["WPHRS"])
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})
            max_priority_fee = web3.to_wei(1, "gwei")
            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_priority_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id
            })
            signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            return tx_hash, receipt.blockNumber
        except Exception as e:
            self.log(f"Wrap Failed: {e}", indent=2, color=Fore.RED)
            return None, None

    async def perform_unwrapped(self, account, address):
        try:
            web3 = await self.get_web3()
            if not web3:
                return None, None
            contract_address = web3.to_checksum_address(self.TOKENS["WPHRS"])
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_priority_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id
            })
            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            return tx_hash, receipt.blockNumber
        except Exception as e:
            self.log(f"Unwrap Failed: {e}", indent=2, color=Fore.RED)
            return None, None

    async def approving_token(self, account, address, spender_address, contract_address, amount):
        try:
            web3 = await self.get_web3()
            if not web3:
                return False
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(amount * (10 ** decimals))
            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})
                max_priority_fee = web3.to_wei(1, "gwei")
                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_priority_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id
                })
                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                self.log(f"Approve Success: Block {receipt.blockNumber}", indent=2, color=Fore.GREEN)
                self.log(f"Tx: {tx_hash}", indent=2, color=Fore.CYAN)
                self.log(f"Explorer: {self.EXPLORER_URL}/{tx_hash}", indent=2, color=Fore.CYAN)
                await asyncio.sleep(10)
            return True
        except Exception as e:
            self.log(f"Approve Failed: {e}", indent=2, color=Fore.RED)
            return False

    async def perform_add_liquidity(self, account, address, add_lp_option, token0, token1, amount0, amount1):
        try:
            web3 = await self.get_web3()
            if not web3:
                return None, None
            if add_lp_option in ["USDCnWPHRS", "WPHRSnUSDT", "USDCnUSDT", "WETHnUSDC", "WBTCnUSDT"]:
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token0, amount0)
                await self.approving_token(account, address, self.POSITION_MANAGER_ADDRESS, token1, amount1)
            token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
            token0_decimals = token0_contract.functions.decimals().call()
            amount0_desired = int(amount0 * (10 ** token0_decimals))
            token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
            token1_decimals = token1_contract.functions.decimals().call()
            amount1_desired = int(amount1 * (10 ** token1_decimals))
            mint_params = {
                "token0": web3.to_checksum_address(token0),
                "token1": web3.to_checksum_address(token1),
                "fee": 500,
                "tickLower": -887270,
                "tickUpper": 887270,
                "amount0Desired": amount0_desired,
                "amount1Desired": amount1_desired,
                "amount0Min": 0,
                "amount1Min": 0,
                "recipient": web3.to_checksum_address(address),
                "deadline": int(time.time()) + 600
            }
            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)
            lp_data = token_contract.functions.mint(mint_params)
            estimated_gas = lp_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_priority_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id
            })
            signed_tx = web3.eth.account.sign_transaction(lp_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            return tx_hash, receipt.blockNumber
        except Exception as e:
            self.log(f"Add Liquidity Failed: {e}", indent=2, color=Fore.RED)
            return None, None

    async def perform_swap(self, account, address, token_in_symbol, token_out_symbol, amount_in):
        try:
            web3 = await self.get_web3()
            if not web3:
                return None, None
            token_in = self.TOKENS.get(token_in_symbol)
            token_out = self.TOKENS.get(token_out_symbol)
            if not token_in or not token_out:
                self.log(f"Invalid token pair: {token_in_symbol}/{token_out_symbol}", indent=2, color=Fore.RED)
                return None, None
            if token_in_symbol != "PHRS":
                await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, token_in, amount_in)
            token_in_contract = web3.eth.contract(address=web3.to_checksum_address(token_in), abi=self.ERC20_CONTRACT_ABI) if token_in_symbol != "PHRS" else None
            decimals = 18 if token_in_symbol == "PHRS" else token_in_contract.functions.decimals().call()
            amount_in_wei = int(amount_in * (10 ** decimals))
            swap_params = {
                "tokenIn": web3.to_checksum_address(token_in),
                "tokenOut": web3.to_checksum_address(token_out),
                "fee": 500,
                "recipient": web3.to_checksum_address(address),
                "deadline": int(time.time()) + 600,
                "amountIn": amount_in_wei,
                "amountOutMinimum": 0,
                "sqrtPriceLimitX96": 0
            }
            swap_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_ROUTER_ABI)
            swap_data = swap_contract.functions.exactInputSingle(swap_params)
            estimated_gas = swap_data.estimate_gas({"from": address, "value": amount_in_wei if token_in_symbol == "PHRS" else 0})
            max_priority_fee = web3.to_wei(1, "gwei")
            swap_tx = swap_data.build_transaction({
                "from": address,
                "value": amount_in_wei if token_in_symbol == "PHRS" else 0,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_priority_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id
            })
            signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            return tx_hash, receipt.blockNumber
        except Exception as e:
            self.log(f"Swap Failed: {e}", indent=2, color=Fore.RED)
            return None, None

    async def process_perform_wrapped(self, account, address, iteration=None, total_iterations=None):
        self.log(f"{'Wrap' if iteration is None else f'Wrap {iteration}/{total_iterations}'}", indent=2, color=Fore.YELLOW)
        balance = await self.get_token_balance(address, "PHRS")
        self.log(f"Balance: {balance} PHRS", indent=2, color=Fore.CYAN)
        self.log(f"Amount: {self.wrap_amount} PHRS", indent=2, color=Fore.CYAN)
        if not balance or balance <= self.wrap_amount:
            self.log("Insufficient PHRS Balance", indent=2, color=Fore.RED)
            return False
        tx_hash, block_number = await self.perform_wrapped(account, address)
        if tx_hash and block_number:
            self.log(f"Wrapped {self.wrap_amount} PHRS to WPHRS Success", indent=2, color=Fore.GREEN)
            self.log(f"Block: {block_number}", indent=2, color=Fore.CYAN)
            self.log(f"Tx: {tx_hash}", indent=2, color=Fore.CYAN)
            self.log(f"Explorer: {self.EXPLORER_URL}/{tx_hash}", indent=2, color=Fore.CYAN)
            return True
        else:
            self.log("Wrap Failed", indent=2, color=Fore.RED)
            return False

    async def process_perform_unwrapped(self, account, address, iteration=None, total_iterations=None):
        self.log(f"{'Unwrap' if iteration is None else f'Unwrap {iteration}/{total_iterations}'}", indent=2, color=Fore.YELLOW)
        balance = await self.get_token_balance(address, "WPHRS")
        self.log(f"Balance: {balance} WPHRS", indent=2, color=Fore.CYAN)
        self.log(f"Amount: {self.wrap_amount} WPHRS", indent=2, color=Fore.CYAN)
        if not balance or balance <= self.wrap_amount:
            self.log("Insufficient WPHRS Balance", indent=2, color=Fore.RED)
            return False
        tx_hash, block_number = await self.perform_unwrapped(account, address)
        if tx_hash and block_number:
            self.log(f"Unwrapped {self.wrap_amount} WPHRS to PHRS Success", indent=2, color=Fore.GREEN)
            self.log(f"Block: {block_number}", indent=2, color=Fore.CYAN)
            self.log(f"Tx: {tx_hash}", indent=2, color=Fore.CYAN)
            self.log(f"Explorer: {self.EXPLORER_URL}/{tx_hash}", indent=2, color=Fore.CYAN)
            return True
        else:
            self.log("Unwrap Failed", indent=2, color=Fore.RED)
            return False

    async def process_perform_add_liquidity(self, account, address, add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1, iteration, total_iterations):
        self.log(f"Add Liquidity {iteration}/{total_iterations}: {ticker0}/{ticker1}", indent=2, color=Fore.YELLOW)
        token0_balance = await self.get_token_balance(address, ticker0)
        token1_balance = await self.get_token_balance(address, ticker1)
        self.log(f"Balance: {token0_balance} {ticker0}, {token1_balance} {ticker1}", indent=2, color=Fore.CYAN)
        self.log(f"Amount: {amount0} {ticker0}, {amount1} {ticker1}", indent=2, color=Fore.CYAN)
        if not token0_balance or token0_balance <= amount0:
            self.log(f"Insufficient {ticker0} Balance", indent=2, color=Fore.RED)
            return False
        if not token1_balance or token1_balance <= amount1:
            self.log(f"Insufficient {ticker1} Balance", indent=2, color=Fore.RED)
            return False
        tx_hash, block_number = await self.perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1)
        if tx_hash and block_number:
            self.log(f"Add LP {amount0} {ticker0}/{amount1} {ticker1} Success", indent=2, color=Fore.GREEN)
            self.log(f"Block: {block_number}", indent=2, color=Fore.CYAN)
            self.log(f"Tx: {tx_hash}", indent=2, color=Fore.CYAN)
            self.log(f"Explorer: {self.EXPLORER_URL}/{tx_hash}", indent=2, color=Fore.CYAN)
            return True
        else:
            self.log("Add Liquidity Failed", indent=2, color=Fore.RED)
            return False

    async def process_perform_swap(self, account, address, token_in_symbol, token_out_symbol, amount_in, iteration, total_iterations):
        self.log(f"Swap {iteration}/{total_iterations}: {token_in_symbol}/{token_out_symbol}", indent=2, color=Fore.YELLOW)
        balance = await self.get_token_balance(address, token_in_symbol)
        self.log(f"Balance: {balance} {token_in_symbol}", indent=2, color=Fore.CYAN)
        self.log(f"Amount: {amount_in} {token_in_symbol}", indent=2, color=Fore.CYAN)
        if not balance or balance <= amount_in:
            self.log(f"Insufficient {token_in_symbol} Balance", indent=2, color=Fore.RED)
            return False
        tx_hash, block_number = await self.perform_swap(account, address, token_in_symbol, token_out_symbol, amount_in)
        if tx_hash and block_number:
            self.log(f"Swap {amount_in} {token_in_symbol} to {token_out_symbol} Success", indent=2, color=Fore.GREEN)
            self.log(f"Block: {block_number}", indent=2, color=Fore.CYAN)
            self.log(f"Tx: {tx_hash}", indent=2, color=Fore.CYAN)
            self.log(f"Explorer: {self.EXPLORER_URL}/{tx_hash}", indent=2, color=Fore.CYAN)
            return True
        else:
            self.log("Swap Failed", indent=2, color=Fore.RED)
            return False

    def generate_add_lp_option(self):
        add_lp_option = random.choice(["USDCnWPHRS", "USDCnUSDT", "WPHRSnUSDT", "WETHnUSDC", "WBTCnUSDT"])
        if add_lp_option == "USDCnWPHRS":
            token0, token1 = self.TOKENS["USDC"], self.TOKENS["WPHRS"]
            amount0, amount1 = 0.45, 0.001
            ticker0, ticker1 = "USDC", "WPHRS"
        elif add_lp_option == "USDCnUSDT":
            token0, token1 = self.TOKENS["USDC"], self.TOKENS["USDT"]
            amount0, amount1 = 1, 1
            ticker0, ticker1 = "USDC", "USDT"
        elif add_lp_option == "WPHRSnUSDT":
            token0, token1 = self.TOKENS["WPHRS"], self.TOKENS["USDT"]
            amount0, amount1 = 0.001, 0.45
            ticker0, ticker1 = "WPHRS", "USDT"
        elif add_lp_option == "WETHnUSDC":
            token0, token1 = self.TOKENS["WETH"], self.TOKENS["USDC"]
            amount0, amount1 = 0.0001, 0.45
            ticker0, ticker1 = "WETH", "USDC"
        else:  # WBTCnUSDT
            token0, token1 = self.TOKENS["WBTC"], self.TOKENS["USDT"]
            amount0, amount1 = 0.00001, 0.45
            ticker0, ticker1 = "WBTC", "USDT"
        return add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1

    def generate_swap_option(self):
        swap_pairs = [
            ("PHRS", "WPHRS", 0.001),
            ("USDC", "USDT", 1),
            ("WETH", "USDC", 0.0001),
            ("WBTC", "USDT", 0.00001),
            ("USDT", "USDC", 1),
        ]
        token_in_symbol, token_out_symbol, amount_in = random.choice(swap_pairs)
        return token_in_symbol, token_out_symbol, amount_in

    async def user_login(self, address, retries=5):
        url = f"{self.BASE_API}/user/login?address={address}&signature={self.signatures[address]}&invite_code={self.ref_code}"
        headers = {**self.headers, "Authorization": "Bearer null", "Content-Length": "0"}
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(f"Login Failed: {e}", indent=1, color=Fore.RED)
                return None

    async def process_user_login(self, address):
        self.log("Logging in...", indent=1, color=Fore.YELLOW)
        login = await self.user_login(address)
        if login and login.get("code") == 0:
            self.access_tokens[address] = login["data"]["jwt"]
            self.log("Login Success", indent=1, color=Fore.GREEN)
            return True
        self.log("Login Failed", indent=1, color=Fore.RED)
        return False

    async def process_option_3(self, account, address):
        self.log(f"Starting Auto All: Wrap, Unwrap, Swap, Liquidity ({self.auto_all_count} cycles)", indent=1, color=Fore.YELLOW)
        for i in range(self.auto_all_count):
            self.log(f"Cycle {i+1}/{self.auto_all_count}", indent=1, color=Fore.YELLOW)
            # Wrap
            wrap_success = await self.process_perform_wrapped(account, address, i+1, self.auto_all_count)
            if wrap_success:
                self.log("Waiting before unwrap...", indent=2, color=Fore.YELLOW)
                await asyncio.sleep(5)
                # Unwrap
                unwrap_success = await self.process_perform_unwrapped(account, address, i+1, self.auto_all_count)
                if unwrap_success:
                    self.log("Waiting before swap...", indent=2, color=Fore.YELLOW)
                    await asyncio.sleep(5)
                    # Swap
                    token_in_symbol, token_out_symbol, amount_in = self.generate_swap_option()
                    swap_success = await self.process_perform_swap(account, address, token_in_symbol, token_out_symbol, amount_in, i+1, self.auto_all_count)
                    if swap_success:
                        self.log("Waiting before liquidity...", indent=2, color=Fore.YELLOW)
                        await asyncio.sleep(5)
                        # Add Liquidity
                        add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1 = self.generate_add_lp_option()
                        await self.process_perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1, i+1, self.auto_all_count)
                    else:
                        self.log("Skipping liquidity due to swap failure", indent=2, color=Fore.RED)
                else:
                    self.log("Skipping swap and liquidity due to unwrap failure", indent=2, color=Fore.RED)
            else:
                self.log("Skipping unwrap, swap, and liquidity due to wrap failure", indent=2, color=Fore.RED)
            if i < self.auto_all_count - 1:
                await asyncio.sleep(5)

    async def process_option_4(self, account, address):
        self.log(f"Starting Swap Tokens ({self.swap_count} cycles)", indent=1, color=Fore.YELLOW)
        for i in range(self.swap_count):
            token_in_symbol, token_out_symbol, amount_in = self.generate_swap_option()
            await self.process_perform_swap(account, address, token_in_symbol, token_out_symbol, amount_in, i+1, self.swap_count)
            if i < self.swap_count - 1:
                await asyncio.sleep(5)

    def print_question(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_menu()
        while True:
            try:
                option = int(input(f"{Style.BRIGHT + Fore.CYAN}Enter your choice (1-5): ").strip())
                if option in [1, 2, 3, 4, 5]:
                    if option == 5:
                        print(f"{Style.BRIGHT + Fore.RED}Exiting...")
                        sys.exit(0)
                    self.log(f"Option {option} Selected.", indent=0, color=Fore.GREEN)
                    break
                print(f"{Style.BRIGHT + Fore.RED}Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            except ValueError:
                print(f"{Style.BRIGHT + Fore.RED}Invalid input. Enter a number (1-5).")

        if option in [1, 2, 3]:
            while True:
                try:
                    wrap_amount = float(input(f"{Style.BRIGHT + Fore.CYAN}Enter Amount for Wrap/Unwrap [e.g., 1, 0.01, 0.001]: ").strip())
                    if wrap_amount > 0:
                        self.wrap_amount = wrap_amount
                        break
                    print(f"{Style.BRIGHT + Fore.RED}Amount must be greater than 0.")
                except ValueError:
                    print(f"{Style.BRIGHT + Fore.RED}Invalid input. Enter a float or decimal number.")
            if option == 3:
                while True:
                    try:
                        self.auto_all_count = int(input(f"{Style.BRIGHT + Fore.CYAN}How Many Times for Auto All (Wrap, Unwrap, Swap, Liquidity)?: ").strip())
                        if self.auto_all_count > 0:
                            break
                        print(f"{Style.BRIGHT + Fore.RED}Please enter a positive number.")
                    except ValueError:
                        print(f"{Style.BRIGHT + Fore.RED}Invalid input. Enter a number.")
        if option == 4:
            while True:
                try:
                    self.swap_count = int(input(f"{Style.BRIGHT + Fore.CYAN}How Many Times to Swap Tokens?: ").strip())
                    if self.swap_count > 0:
                        break
                    print(f"{Style.BRIGHT + Fore.RED}Please enter a positive number.")
                except ValueError:
                    print(f"{Style.BRIGHT + Fore.RED}Invalid input. Enter a number.")

        self.wrap_option = option
        return option

    async def process_accounts(self, account, address):
        if await self.process_user_login(address):
            if self.wrap_option == 1:
                self.log("Option: Wrap PHRS to WPHRS", indent=0, color=Fore.BLUE)
                await self.process_perform_wrapped(account, address)
            elif self.wrap_option == 2:
                self.log("Option: Unwrap WPHRS to PHRS", indent=0, color=Fore.BLUE)
                await self.process_perform_unwrapped(account, address)
            elif self.wrap_option == 3:
                self.log("Option: Auto All (Wrap, Unwrap, Swap, Liquidity)", indent=0, color=Fore.BLUE)
                await self.process_option_3(account, address)
            elif self.wrap_option == 4:
                self.log("Option: Swap Tokens", indent=0, color=Fore.BLUE)
                await self.process_option_4(account, address)

    async def main(self):
        self.loading_animation()
        try:
            with open('pkey.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            self.log(f"Total Accounts: {len(accounts)}", indent=0, color=Fore.BLUE)
            while True:
                option = self.print_question()
                for i, account in enumerate(accounts, 1):
                    self.log(f"\nProcessing Account {i}/{len(accounts)}: {self.mask_account(self.generate_address(account))}", indent=0, color=Fore.BLUE)
                    address = self.generate_address(account)
                    signature = self.generate_signature(account)
                    if not address or not signature:
                        self.log("Invalid Private Key or Library Not Supported", indent=1, color=Fore.RED)
                        continue
                    self.signatures[address] = signature
                    await self.process_accounts(account, address)
                    if i < len(accounts):
                        self.log("Waiting before next account...", indent=1, color=Fore.YELLOW)
                        await asyncio.sleep(5)
                print(f"\n{Style.BRIGHT + Fore.CYAN}Run again? (y/n): ", end='')
                if input().strip().lower() != 'y':
                    print(f"{Style.BRIGHT + Fore.RED}Exiting...")
                    break
        except FileNotFoundError:
            self.log("File 'pkey.txt' Not Found.", indent=0, color=Fore.RED)
        except Exception as e:
            self.log(f"Error: {e}", indent=0, color=Fore.RED)

if __name__ == "__main__":
    try:
        bot = PharosTestnet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Style.BRIGHT + Fore.RED}Pharos Testnet - BOT Exited")
