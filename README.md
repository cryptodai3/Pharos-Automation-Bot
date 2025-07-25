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
| `bot5.py` | FaroSwap BOT  | Swap and liquidity automation      |

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

4. Configuration only for Faroswap BOT

### Screenshots
<img width="1919" height="887" alt="image1" src="https://github.com/user-attachments/assets/f32173f0-6dbb-4bfe-b9bd-963f2e992f1d" />

<img width="1919" height="891" alt="image2" src="https://github.com/user-attachments/assets/e65d4da6-bb11-4890-9b1d-89f81299e846" />

<img width="1919" height="883" alt="image3" src="https://github.com/user-attachments/assets/b88a4dd6-a3ff-489a-9e02-aa047474b86b" />

<img width="1919" height="896" alt="image4" src="https://github.com/user-attachments/assets/b7d4e074-f05b-4908-baf4-1787f03b94fb" />

<img width="1918" height="889" alt="image5" src="https://github.com/user-attachments/assets/f5f74d67-92c9-4655-927f-aec3997141ef" />

<img width="1594" height="503" alt="image6" src="https://github.com/user-attachments/assets/556b095e-02f0-4101-8bf8-4601afedf55b" />

<img width="681" height="402" alt="image7" src="https://github.com/user-attachments/assets/3de642d3-61fb-4b9f-937b-715603042be6" />

- **pools.json:** You will find the file `pools.json` inside the project directory. Make sure `pools.json` contains data that matches the format expected by the script. Here are examples of file formats:
  ```json
    [    
        {
            "USDC_USDT": "Your USDC_USDT PMM Pool Address",
            "USDT_USDC": "Your USDT_USDC PMM Pool Address"
        }
    ]
  ```

5. **Run a Bot**

```bash
python bot1.py  # Pharos
python bot2.py  # Gotchipus
python bot3.py  # OpenFi
python bot4.py  # Brokex
python bot5.py  # Faroswap
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
* Auto Claim Daily Check-In

---

### `bot3.py` — **OpenFi BOT**

🔗 [OpenFi](https://app.open-fi.xyz/)

Handles:

* Faucet mint
* Deposit/lend/borrow
* Auto Repay
* Fully automated DeFi tasks

---

### `bot4.py` — **Brokex BOT**

🔗 [Brokex](https://app.brokex.trade/)
🚰 [Brokex Faucet](https://brokex.trade/faucet)

Handles:

* USDT faucet claims
* Auto trades
* Auto Add & Withdraw Liquidity Pool
* Auto Make Random Open & Close Potition

---

### `bot5.py` — **Faroswap BOT**

🔗 [Faroswap Swap](https://faroswap.xyz/swap)
🚰 [Faroswap Pool](https://faroswap.xyz/pool)

Handles:

* Auto Deposit PHRS to WPHRS
* Auto Withdraw WPHRS to PHRS
* Auto Swap With Random Pairs
* Auto Add Liquidity Pool
* Multi Accounts

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
