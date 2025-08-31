
# 🚨 Pi Transaction Notifier

Get Telegram alerts whenever your Pi address has a new operation/payment visible on the Pi block explorer API (Horizon-style).

## 1) Create a Telegram Bot
- Open Telegram, talk to **@BotFather**
- `/newbot` → name it → copy the **Token**
- Start a chat with your bot (send any message once)

Find your numeric chat id:
- Talk to **@userinfobot** → it replies with your `id`

## 2) Configure Environment Variables
- `BOT_TOKEN` — Token from BotFather
- `CHAT_ID` — Your Telegram numeric ID
- `ADDRESS` — Your Pi public address (starts with G...)
- `API_BASE` — (optional) defaults to `https://api.mainnet.minepi.com`
- `POLL_INTERVAL` — (optional) seconds between checks, default 60
- `SEND_TEST` — (optional) "1" to send a startup test message

## 3) Run locally
```bash
pip install -r requirements.txt
export BOT_TOKEN=xxx
export CHAT_ID=123456789
export ADDRESS=GXXXXXXXXXXXX
python pi_notifier.py
```

## 4) Deploy on Railway (recommended, free tier)
1. Push this folder to a GitHub repo.
2. Go to **railway.app** → New Project → Deploy from GitHub → select the repo.
3. After first build, open the service → **Variables** and add:
   - `BOT_TOKEN`, `CHAT_ID`, `ADDRESS` (and optionally `API_BASE`, `POLL_INTERVAL`, `SEND_TEST`)
4. If Railway asks for a start command, set: `python pi_notifier.py`
5. Check **Logs**. You should see "Pi Notifier is live..." and get a Telegram test message.

## 5) Deploy on Heroku (alternative)
```bash
heroku login
heroku create pi-notifier
git push heroku main
heroku ps:scale worker=1
heroku config:set BOT_TOKEN=xxx CHAT_ID=123 ADDRESS=GXXXXX
```

### Notes
- This watcher **polls** the API every `POLL_INTERVAL` seconds.
- On the very first run it sets a baseline and avoids spamming old operations; you still receive a "bot live" test message.
- If the default API base ever changes, set `API_BASE` to the correct Horizon endpoint (check your explorer's network calls).
