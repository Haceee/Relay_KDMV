import os
import re
import traceback
from telegram.ext import Application, MessageHandler, filters

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

# --- CONFIG ---
SOURCE_CHAT_ID = -1002813360979
TARGET_CHAT_ID = -1002962986373
TARGET_TOPIC_ID = 4491


# --- STARTUP MESSAGE ---
async def on_startup(app):
    try:
        await app.bot.send_message(
            chat_id=SOURCE_CHAT_ID,
            text="🟢 Relay Bot ONLINE"
        )

        await app.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="🟢 Relay Bot ONLINE",
            message_thread_id=TARGET_TOPIC_ID
        )
    except Exception as e:
        print("Startup notify failed:", e)


# --- ERROR HANDLER ---
async def error_handler(update, context):
    print("\n=== ERROR ===")
    print("Update:", update)
    print("Error:", context.error)

    traceback.print_exception(
        type(context.error),
        context.error,
        context.error.__traceback__
    )
    print("=============\n")


# --- PARSER ---
def parse_payment(text: str):
    amount = re.search(r"\$(\d+(?:\.\d{2})?)", text)
    name = re.search(r"paid by (.*?) \(", text, re.IGNORECASE)
    trx = re.search(r"trx\. id:\s*([a-zA-Z0-9]+)", text, re.IGNORECASE)
    apv = re.search(r"apv:\s*(\d+)", text, re.IGNORECASE)

    return {
        "amount": amount.group(1) if amount else "N/A",
        "name": name.group(1) if name else "N/A",
        "trx": trx.group(1) if trx else "N/A",
        "apv": apv.group(1) if apv else "N/A",
    }


# --- RELAY ---
async def relay(update, context):
    msg = update.message
    if not msg:
        return

    # Only source group
    if msg.chat_id != SOURCE_CHAT_ID:
        return

    if not msg.text:
        return

    text = msg.text.strip()
    text_lower = text.lower()

    # =========================
    # TEST MODE (no real payment needed)
    # =========================
    if text.startswith("TESTPAY"):
        sample = text.replace("TESTPAY", "").strip()

        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=f"TEST MODE\n{sample}",
            message_thread_id=TARGET_TOPIC_ID
        )
        return

    # =========================
    # REAL PAYMENT DETECTION
    # =========================
    if (
        "$" not in text or
        "trx. id" not in text_lower or
        "apv" not in text_lower
    ):
        return

    # =========================
    # PARSE + FORMAT
    # =========================
    data = parse_payment(text)

    formatted = (
        f"AMOUNT: ${data['amount']}\n"
        f"PAID BY: {data['name']}\n"
        f"TRX ID: {data['trx']}\n"
        f"APV: {data['apv']}"
    )

    # =========================
    # SEND
    # =========================
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=formatted,
        message_thread_id=TARGET_TOPIC_ID
    )


# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, relay))
    app.add_error_handler(error_handler)

    app.post_init = on_startup

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
