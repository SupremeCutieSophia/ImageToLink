# Granny File-To-Link Bot

A Telegram bot that converts **any file** into a **direct download link**.  
Supports **Permanent (Catbox)** and **Temporary (Litterbox)** uploads.

👉 **Bot:** https://t.me/Images_To_Link_bot  
👉 **Updates:** https://t.me/Granny_Bots

---

## ✨ Features
- 📤 Upload any file (video, image, document, audio, etc.)
- 🔗 **Permanent uploads** — up to **200MB**
- ⏳ **Temporary uploads** — 1h, 12h, 24h, 72h (up to **1GB**)
- ⚡ Fast Pyrogram backend
- 🧹 Automatic cache cleaner
- 🐳 Ready for Docker deployment
- 🌐 Built-in health check server for hosting platforms

---

## 🚀 How to Use
1. Open the bot on Telegram  
2. Send any file  
3. Choose:
   - **Permanent (200MB limit)**
   - **Temporary (1h–72h expiry)**
4. Receive a **direct download URL**

---

# 🛠️ Installation & Setup

## 1️⃣ Clone the Repository
```bash
git clone https://github.com/SupremeCutieSophia/ImageToLink
cd ImageToLink
```

## 2️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

## 3️⃣ Configure Environment Variables
```bash
export API_ID=12345
export API_HASH=abcd1234
export BOT_TOKEN=123456:ABC-xyz
```

## 4️⃣ Run the Bot
```bash
python bot.py
```

---

# 🐳 Docker Deployment

## Build Docker Image
```bash
docker build -t granny-link .
```

## Run Container
```bash
docker run -d \
  -e API_ID=12345 \
  -e API_HASH=abcd1234 \
  -e BOT_TOKEN=123456:ABC \
  link-bot
```

Health-check endpoint:
```
http://localhost:8080/health
```

---

# 📂 Project Structure
```
├── bot.py                 # Telegram bot logic
├── litterbox_uploader.py  # Litterbox temporary uploader
├── Dockerfile             # Docker setup
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

---

# 🤝 Contributing
Contributions, issues, and feature requests are welcome!

---

# 📜 License
This project is licensed under the **MIT License**.
