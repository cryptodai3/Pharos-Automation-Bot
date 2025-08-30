# ⚙️ Pharos Automation BOT (Multi-Module)

A one-stop automation suite for the **Pharos Testnet** ecosystem. Run everything - **Pharos, Gotchipus, OpenFi, Brokex, Faroswap, and AquaFlux** - using just **one wallet, proxy, and config**.

> 🔑 Unified Wallet | 🌍 Proxy Rotation | 🧩 Multi-Module Scripts | 📁 All-in-One Repo

---

## 📦 Included Bots

| File Name | Bot Name           | Description                        |
| --------- | ------------------ | ---------------------------------- |
| `bot1.py` | Pharos BOT         | DeFi automation for Pharos Testnet |
| `bot2.py` | Gotchipus BOT      | NFT minting & wearable claiming    |
| `bot3.py` | OpenFi BOT         | Lending, borrowing & DeFi services |
| `bot4.py` | Brokex BOT         | Faucet claim and trade automation  |
| `bot5.py` | FaroSwap BOT       | Swap and liquidity automation      |
| `bot6.py` | AquaFlux BOT   | Auto Mint Standard & Premium NFT (need bind twitter)  |
| `bot7.py` | Zenith Swap BOT      | Swap and liquidity automation    |
| `bot8.py` | Pharos Name Service BOT         | Auto Mint Random .phrs Domain |
| `bot9.py` | Grandline BOT         | Auto Claim All Available Badge  |
| `bot10.py` | R2 Pharos BOT       | Swap and liquidity automation      |

---

## 🧠 Features

✅ Use one wallet + proxy across all bots  
✅ Modular system - run individually or in sequence  
✅ Covers check-ins, faucets, swaps, NFTs, lending, tips, and more  
✅ Three proxy modes: Free public, Private, or No Proxy  
✅ Auto-rotation for invalid proxies  
✅ Multi-account ready for testnet farming  

---

## 🔧 Requirements

* Python `3.9+`
* `pip` or `pip3` for dependency installs
* Libraries: `web3`, `eth-account`, `requests`, `colorama`

---

## 🚀 Quick Start Guide

1. **Clone this Repo**
```bash
git clone https://github.com/cryptodai3/Pharos-Automation-Bot.git
cd Pharos-Automation-Bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Add Your Keys & Proxies**

`accounts.txt`:
```
your_private_key_1
your_private_key_2
```

`proxy.txt` (multiple formats supported):
```
127.0.0.1:8080
http://user:pass@127.0.0.1:8080
socks5://127.0.0.1:1080
```

4. **Special Configurations**
- For Faroswap BOT: Update `pools.json` with pool addresses
- For Primuslabs BOT: No additional config needed

5. **Run Bots**
```bash
python bot1.py  # Pharos
python bot2.py  # Gotchipus
python bot3.py  # OpenFi
python bot4.py  # Brokex
python bot5.py  # Faroswap
python bot6.py  # AquaFlux
python bot7.py  # Zenith Swap
python bot8.py  # Pharos Name Service
python bot9.py  # Grandline
python bot10.py  # R2 Pharos
```

---

## 🤖 Bot Breakdown

### `bot1.py` — **Pharos Testnet BOT**
🔗 [Pharos Testnet](https://testnet.pharosnetwork.xyz/experience?inviteCode=8G8MJ3zGE5B7tJgP)  
✅ Daily check-ins  
✅ Faucet claims  
✅ Token swaps  
✅ LP management  

### `bot2.py` — **Gotchipus BOT**
🔗 [Gotchipus](https://gotchipus.com/)  
✅ NFT minting   
✅ Wearable claims  
✅ Daily check-ins  

### `bot3.py` — **OpenFi BOT**
🔗 [OpenFi](https://app.open-fi.xyz/)  
✅ Lending/borrowing  
✅ Faucet mint  
✅ Auto repay       

### `bot4.py` — **Brokex BOT**
🔗 [Brokex](https://app.brokex.trade/)  
✅ USDT faucet   
✅ Auto trades   
✅ Liquidity management    

### `bot5.py` — **Faroswap BOT**
🔗 [Faroswap](https://faroswap.xyz/swap)  
✅ PHRS wrapping   
✅ Swaps   
✅ Liquidity pools    

### `bot6.py` — **AquaFlux BOT** (NEW)
🔗 [AquaFlux](https://playground.aquaflux.pro/)  
✅ Auto Mint Standard NFT    
✅ Auto Mint Premium NFT (need bind twitter)        
✅ Multi-account support  

### `bot7.py` — Zenith Swap BOT
🔗 [Zenith Swap](https://testnet.zenithswap.xyz/home)  
✅ Auto Wrap PHRS to WPHRS  
✅ Auto Unwrap WPHRS to PHRS  
✅ Random Swap TX  
✅ Add Liquidity  
✅ Multi-account support  

### `bot8.py` — Pharos Name Service BOT
🔗 [Pharos Name Service](https://test.pharosname.com/)  
✅ Auto Mint Random .phrs Domain  
✅ Multi-account support  

### `bot9.py` — Grandline BOT
🔗 [Grandline](https://app.grandline.world/)  
✅ Auto Claim All Available Badges  
✅ Multi-account support  

### `bot10.py` — R2 Pharos BOT
🔗 [R2 Pharos](https://www.r2.money/)  
✅ Auto Make R2 Swap TX  
✅ Auto Make R2 Earn TX  
✅ Multi-account support    

---

## ⚠️ Dependency Notes
Ensure version compatibility:
```bash
pip uninstall web3 eth-account
pip install web3==6.15.0 eth-account==0.11.0
```

---

## ☕ Support the Developers
**EVM:** `0x3b94Ff1611773171E06047C0041099CccCFC609F`   

---

## 🔒 Security & Disclaimer
> ⚠️ **For Testnet Use Only**  
> 🔥 Use burner wallets • 🔐 Never share private keys  
> 🛡️ Review code • ⚖️ No developer liability  

---

## 🙌 Grow With Us
⭐ Star repo • 💬 Share with hunters • 💡 Suggest features  
**Crafted with ❤️ by [CryptoDai3](https://t.me/cryptodai3) × [YetiDAO](https://t.me/YetiDAO)**  
**MIT Licensed • Free to use and modify**
nd the social tip feature is highlighted as a key capability of the new bot.
