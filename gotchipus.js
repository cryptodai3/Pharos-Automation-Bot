require('dotenv').config();
const { ethers } = require('ethers');
const prompt = require('prompt-sync')();

const colors = {
  reset: "\x1b[0m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  white: "\x1b[37m",
  bold: "\x1b[1m"
};

const logger = {
  info: (msg) => console.log(`${colors.green}[✓] ${msg}${colors.reset}`),
  warn: (msg) => console.log(`${colors.yellow}[⚠] ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}[✗] ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}[✅] ${msg}${colors.reset}`),
  loading: (msg) => console.log(`${colors.cyan}[⟳] ${msg}${colors.reset}`),
  step: (msg) => console.log(`${colors.white}[➤] ${msg}${colors.reset}`),
  banner: () => {
    console.log(`${colors.cyan}${colors.bold}`);
    console.log(`---------------------------------------------`);
    console.log(`  Gotchipus Mint Auto Bot - YetiDAO  `);
    console.log(`---------------------------------------------${colors.reset}`);
    console.log();
  }
};

const RPC_URL = 'https://testnet.dplabs-internal.com';
const CHAIN_ID = 688688;
const CONTRACT_ADDRESS = '0x0000000038f050528452d6da1e7aacfa7b3ec0a8';
const MINT_METHOD_ID = '0x5b70ea9f';
const GAS_PRICE = ethers.parseUnits('1.3', 'gwei'); 
const GAS_LIMIT = 286314;

function getPrivateKeys() {
  const privateKeys = [];
  let i = 1;
  while (process.env[`PRIVATE_KEY_${i}`]) {
    privateKeys.push(process.env[`PRIVATE_KEY_${i}`]);
    i++;
  }
  return privateKeys;
}

async function mintNFTs() {
  logger.banner();

  const privateKeys = getPrivateKeys();
  if (privateKeys.length === 0) {
    logger.error('No private keys found in .env file. Please set PRIVATE_KEY_1, PRIVATE_KEY_2, etc.');
    return;
  }
  logger.info(`Found ${privateKeys.length} wallet(s) in .env file`);

  const mintCount = parseInt(prompt('Enter the number of NFTs to mint per wallet: '));
  if (isNaN(mintCount) || mintCount <= 0) {
    logger.error('Invalid number of NFTs. Please enter a positive number.');
    return;
  }

  try {
    const provider = new ethers.JsonRpcProvider(RPC_URL);

    const network = await provider.getNetwork();
    if (network.chainId !== BigInt(CHAIN_ID)) {
      logger.error(`Incorrect chain ID. Expected: ${CHAIN_ID}, Got: ${network.chainId}`);
      return;
    }
    logger.step('Connected to Pharos Testnet');

    for (let walletIndex = 0; walletIndex < privateKeys.length; walletIndex++) {
      const privateKey = privateKeys[walletIndex];
      const wallet = new ethers.Wallet(privateKey, provider);
      logger.info(`Processing wallet ${walletIndex + 1}: ${wallet.address}`);

      for (let i = 1; i <= mintCount; i++) {
        logger.loading(`Minting NFT ${i} of ${mintCount} for wallet ${walletIndex + 1}...`);

        const tx = {
          to: CONTRACT_ADDRESS,
          data: MINT_METHOD_ID,
          gasPrice: GAS_PRICE,
          gasLimit: GAS_LIMIT,
          chainId: CHAIN_ID,
          nonce: await provider.getTransactionCount(wallet.address, 'pending'),
          value: 0 
        };

        const txResponse = await wallet.sendTransaction(tx);

        logger.step(`Transaction sent for wallet ${walletIndex + 1}: ${txResponse.hash}`);
        logger.loading(`Waiting for transaction confirmation for wallet ${walletIndex + 1}...`);

        const receipt = await txResponse.wait();

        if (receipt.status === 1) {
          logger.success(`NFT ${i} minted successfully for wallet ${walletIndex + 1}! Tx Hash: ${txResponse.hash}`);
        } else {
          logger.error(`Minting failed for NFT ${i} in wallet ${walletIndex + 1}. Transaction reverted.`);
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      logger.success(`Completed minting ${mintCount} NFTs for wallet ${walletIndex + 1}!`);
    }

    logger.success(`Completed minting for all ${privateKeys.length} wallets!`);
  } catch (error) {
    logger.error(`Error during minting: ${error.message}`);
  }
}

mintNFTs();
