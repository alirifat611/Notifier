
import os
import time
import requests

# === Config via Environment Variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
ADDRESS = os.getenv("ADDRESS", "").strip()  # Your Pi Wallet public address
API_BASE = os.getenv("API_BASE", "https://api.mainnet.minepi.com").strip()
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))  # seconds
SEND_TEST = os.getenv("SEND_TEST", "1").strip()  # send a test message on startup

last_seen = None

def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not set.")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=15,
        )
    except Exception as e:
        print("Telegram send error:", e)

def fetch_latest_record():
    """Try Pi Horizon-style endpoints to fetch the latest operation.
    Returns a dict for the latest record, or None if nothing found.
    """
    headers = {"Accept": "application/json"}
    endpoints = [
        f"{API_BASE}/accounts/{ADDRESS}/operations",
        f"{API_BASE}/accounts/{ADDRESS}/payments",
        f"{API_BASE}/accounts/{ADDRESS}/transactions",
    ]
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                continue
            data = r.json()
            # Stellar/Horizon-like structure
            records = (
                data.get("_embedded", {}).get("records") or
                data.get("records")  # in case of a plain records list
            )
            if records and len(records) > 0:
                return records[0]
        except Exception as e:
            print("Fetch error:", e)
            continue
    return None

def format_message(rec: dict) -> str:
    if not rec:
        return "No recent records found."
    op_type = rec.get("type") or rec.get("memo_type") or "unknown"
    amount = rec.get("amount") or rec.get("amount_in") or ""
    from_addr = rec.get("from") or rec.get("source_account") or ""
    to_addr = rec.get("to") or ""
    tx_id = rec.get("id") or rec.get("paging_token") or rec.get("hash") or "n/a"
    created_at = rec.get("created_at", "")

    msg = (
        "🚨 New Pi Operation Detected\n"
        f"Type: {op_type}\n"
        f"Amount: {amount}\n"
        f"From: {from_addr}\n"
        f"To: {to_addr}\n"
        f"ID: {tx_id}\n"
        f"Time: {created_at}"
    )
    return msg

def main():
    global last_seen
    # Startup test message (optional)
    if SEND_TEST == "1":
        send_telegram("✅ Pi Notifier is live. I'll alert on new operations.")

    while True:
        try:
            rec = fetch_latest_record()
            if rec is not None:
                tx_id = rec.get("id") or rec.get("paging_token") or rec.get("hash")
                if tx_id and tx_id != last_seen:
                    # Only notify if we have seen at least one before (avoid sending
                    # old record on very first run). You can change this by setting
                    # SEND_TEST to 1 which already confirms the bot is running.
                    if last_seen is not None:
                        send_telegram(format_message(rec))
                    last_seen = tx_id
        except Exception as e:
            print("Loop error:", e)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if not ADDRESS:
        print("Please set ADDRESS environment variable.")
    else:
        main()
