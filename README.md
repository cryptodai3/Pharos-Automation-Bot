# 🌌 Pharos Testnet Multi-Bot

An automated multi-wallet bot built for the **Pharos Testnet**, designed to help you consistently interact with the network and potentially qualify for airdrops through regular activity.

---

# ✨ Features

- 🔁 **Automated Swaps** – Swaps between `WPHRS` and `USDC` tokens  
- 🔄 **PHRS Transfers** – Sends small PHRS to random addresses  
- 🚿 **Faucet Claims** – Automatically claims free testnet tokens  
- 📅 **Daily Check-ins** – Completes check-in tasks for airdrop eligibility  
- 🧩 **Proxy Support** – Supports rotating proxies for each account  
- 👥 **Multi-Wallet Support** – Runs through all your wallets one-by-one  
- 🖼️ **Auto NFT Mint** – Automatically mints available NFTs for each wallet  

---

# 📋 Prerequisites

- Node.js v18+  
- npm or yarn  
- One or more Pharos **testnet private keys**  
- (Optional) A list of proxies in `proxies.txt`  

---

# 🛠 Installation

```bash
git clone https://github.com/cryptodai3/Pharos-Testnet-Multi-Bot.git
````
```bash
cd Pharos-Testnet-Multi-Bot
````
```bash
npm install
````

---

# ⚙️ Setup Instructions

## 1. Create a `.env` file:

```env
PRIVATE_KEY_1=your_first_private_key_here
PRIVATE_KEY_2=your_second_private_key_here
# Add more if needed
```

## 2. (Optional) Create `proxies.txt`:

Each proxy must be on a new line:

```
http://user:pass@ip:port
socks5://user:pass@ip:port
```

---

# 🔧 Configuration

The bot comes with default settings for the Pharos Testnet, but you can customize:

* RPC endpoint
* Token contract addresses
* Swap amounts
* Transfer behavior

Edit values inside `index.js` or `config.js` (if available).

---

# 🚀 Usage

To run the main bot:

```bash
node index.js
```

The bot will:

1. Show a welcome banner
2. Load all wallets and proxies
3. For each wallet:

   * Claim faucet (if available)
   * Perform daily check-in
   * Transfer PHRS (10x)
   * Perform token swaps (10x)
4. Repeat all tasks every 30 minutes

---

# 🖼️ PHAROS NFT MINT

Use this to auto mint NFTs using all wallets:
One-time setup (first run only):
```bash
git pull
npm install ethers@latest dotenv prompt-sync@latest
```

Daily mint:
```bash
node gotchipus.js
```

Make sure your `.env` file has all your private keys ready!

---

# 📝 Logging

You’ll see:

* ✅ Success logs in green
* ⚠️ Warnings in yellow
* ❌ Errors in red
* 🔄 Process info in cyan
* ➤ Step logs in white

---

# ⚠️ Important Notes

* ONLY use testnet wallets
* NEVER paste mainnet private keys
* This bot runs indefinitely (`Ctrl + C` to stop)
* Randomized delays = safer and more human-like behavior
* Testnet = zero gas cost (free to experiment!)

---

# 💬 Support

Need help? Open an issue in the [GitHub repo](https://github.com/cryptodai3/Pharos-Testnet-Multi-Bot/issues)

---

# 🧑‍💻 Contributors

* Developed by [cryptodai3](https://t.me/cryptodai3)
* Supported by the Web3 farming community 💚

---

# 🙌 Support the Project

If this helps you, show love by:

* Using our referral links 💰
* Sharing the repo with your frens 🙌
* Reporting bugs & suggestions 🧠

---

# ⚠️ Disclaimer

This tool is **testnet-only** and comes with no warranty. Use at your own risk.
The developers are not liable for any misuse or consequences.

---

# 📄 License

[MIT License](LICENSE)

---
