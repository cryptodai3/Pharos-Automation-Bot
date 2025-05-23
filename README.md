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
---
# 📋 Prerequisites

- Node.js v18+  
- npm or yarn  
- One or more Pharos **testnet private keys**  
- (Optional) A list of proxies in `proxies.txt`
---
# Installation

````markdown
git clone https://github.com/cryptodai3/Pharos-Testnet-Multi-Bot.git
````
````
cd Pharos-Testnet-Multi-Bot
````
````
npm install
````
# Setup Instructions ⚙️

# 1. Create a `.env` file:
```env
PRIVATE_KEY_1=your_first_private_key_here
PRIVATE_KEY_2=your_second_private_key_here
# Add more if needed
````
# 2. (Optional) Create `proxies.txt`:

Each proxy must be on a new line:

```
http://user:pass@ip:port
socks5://user:pass@ip:port
```

# ⚙️ Configuration

The bot comes with default settings for the Pharos Testnet, but you can modify::
- RPC endpoint  
- Token contract addresses  
- Swap amounts  
- Transfer behavior  

All inside `index.js` or a config file if provided.

# 🚀 Usage
Run the bot:
```bash
node index.js
````

The bot will:

1. Show a welcome banner
2. Load all wallets and proxies
3. For each wallet:

   * Claim faucet (if available)
   * Perform daily check-in
   * Transfer PHRS (10x)
   * Perform token swaps (10x)
4. Repeat automatically every 30 minutes

---
# 📝 Logging

You'll see:
- ✅ Success logs in green  
- ⚠️ Warnings in yellow  
- ❌ Errors in red  
- 🔄 Process info in cyan  
- ➤ Step logs in white
---
### ⚠️ Important Notes

- ONLY use testnet wallets  
- NEVER paste mainnet private keys  
- This bot runs indefinitely (use `Ctrl + C` to stop)  
- Testnet = Zero gas cost  
- Randomized delays between operations for safety

### 💬 Support

Need help? Open an issue in the [GitHub repo](https://github.com/cryptodai3/Pharos-Testnet-Multi-Bot/issues)

## 🧑‍💻 Contributors

- Developed by [cryptodai3](https://t.me/cryptodai3)
- Supported by the Web3 farming community 💚

---

## 🙌 Support the Project

If this helps you, show love by:
- Using our referral link 💰
- Sharing the repo 🙌
- Reporting bugs & ideas 🧠
---

### ⚠️ Disclaimer

This tool is **testnet-only** and comes with no warranty. Use it at your own risk. The developers are not liable for any misuse or consequences.
---
### 📄 License

[MIT License](LICENSE)
---
