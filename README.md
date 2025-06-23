# ⚙️ Pharos Automation BOT (Multi-Module)

A one-stop automation suite for the **Pharos Testnet** and its expanding ecosystem. Run everything — **Pharos, Gotchipus, OpenFi, and Brokex** — using just **one wallet, proxy, and config**.

> 🔑 Unified Wallet | 🌍 Proxy Rotation | 🧩 Multi-Module Scripts | 📁 All-in-One Repo

---

## 📦 Included Bots

| File Name | Bot Name      | Description                        |
| --------- | ------------- | ---------------------------------- |
| `bot1.py` | Pharos BOT    | DeFi automation for Pharos Testnet |
| `bot2.py` | Gotchipus BOT | NFT minting & wearable claiming    |
| `bot3.py` | OpenFi BOT    | Lending, borrowing & DeFi services |
| `bot4.py` | Brokex BOT    | Faucet claim and trade automation  |

---

## 🧠 Features

✅ Use one wallet + proxy across all bots  
✅ Modular system — run individually or in sequence  
✅ Covers check-ins, faucets, swaps, NFTs, lending, LPs, and more  
✅ Free & authenticated proxy support with rotation  
✅ Multi-account ready for testnet farming  

---

## 🔧 Requirements

* Python `3.9+`
* `pip` or `pip3` for dependency installs

---

## 🚀 Quick Start Guide

1. **Clone this Repo**

```bash
git clone https://github.com/cryptodai3/Pharos-Automation-Bot.git
```
```bash
cd Pharos-Automation-Bot
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

3. **Add Your Keys & Proxies**

Create `accounts.txt`:

```
your_private_key_1
your_private_key_2
```

Create `proxy.txt`:

```
127.0.0.1:8080
http://127.0.0.1:8080
http://user:pass@127.0.0.1:8080
```

4. **Run a Bot**

```bash
python bot1.py  # Pharos
python bot2.py  # Gotchipus
python bot3.py  # OpenFi
python bot4.py  # Brokex
```

---

## 🤖 Bot Breakdown

### `bot1.py` — **Pharos Testnet BOT**

🔗 [Pharos Testnet](https://testnet.pharosnetwork.xyz/experience?inviteCode=8G8MJ3zGE5B7tJgP)

Handles:

* Daily check-ins
* Faucet claims
* Token swap, LP add, wrap/unwrap
* Proxy rotation + multi-account

---

### `bot2.py` — **Gotchipus BOT**

🔗 [Gotchipus](https://gotchipus.com/)

Handles:

* NFT minting
* Wearable claims
* Same wallet support

---

### `bot3.py` — **OpenFi BOT**

🔗 [OpenFi](https://app.open-fi.xyz/)

Handles:

* Faucet mint
* Deposit/lend/borrow
* Fully automated DeFi tasks

---

### `bot4.py` — **Brokex BOT**

🔗 [Brokex](https://app.brokex.trade/)
🚰 [Brokex Faucet](https://brokex.trade/faucet)

Handles:

* USDT faucet claims
* Auto trades

---

## ⚙️ Dependency Notes

Ensure version compatibility for:
`web3`, `eth-account`, `eth-utils`, and `eth-abi`.

If you run into issues:

```bash
pip uninstall library_name
pip install library_name==exact_version
```

---

## 🌾 Happy Farming!

Crafted with ❤️ by [CryptoDai3](https://t.me/cryptodai3) × [YetiDAO](https://t.me/YetiDAO)

---

## ☕ Buy Me a Coffee

* **EVM:** `0x49bb35693e9631760d2f3519e7db1dd618580a6a`
* **TON:** `UQDDYNRWZI12zMfXYBoy300ydECC5uouMUFLd_yZa6ZO4Jsm`
* **SOL:** `2PhLDFnyX8whHDMBbfGSFoLnVEsei6TYxyiqpDzPGyT1`
* **SUI:** `0xf3b008f8aac4b92195176aad27a892c565c216fd5c07bc99c70edb8394e23b59`

---

## 🔒 Security & Disclaimer

⚠️ Use responsibly:

* **For Testnet Use Only**
* **No mainnet wallets** — use burners
* **Keep keys safe** — don’t share
* **DYOR** — review code before use
* **No liability** — you’re on your own, devs aren't responsible

---

## 🙌 Support the Mission

Help us grow this tool:

⭐ Star this repo
🔗 Share with fellow airdrop hunters
🧠 Contribute ideas, PRs, or guides
🧪 Suggest new module integrations

---

## 📄 License

Licensed under the **MIT License** — free to use, improve, and fork.
---
