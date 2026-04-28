import os
import re
import traceback
from telegram.ext import Application, MessageHandler, filters

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

# --- CONFIG ---
SOURCE_CHAT_ID = -1002813360979      # PCMKR Division
TARGET_CHAT_ID = -1002962986373      # KDMV ORDERS
TARGET_TOPIC_ID = 4491               # Website payment topic

# --- PAYMENT PATTERN ---
PAYMENT_PATTERN = re.compile(
    r"\$\d+(?:\.\d{2})?.*paid by.*ABA PAY.*Trx\. ID:.*APV:",
    re.IGNORECASE
)

# --- STARTUP MESSAGE ---
async def on_startup(app):
    try:
        # Source group
        await app.bot.send_message(
            chat_id=SOURCE_CHAT_ID,
            text="🟢 Relay Bot ONLINE"
        )

        # Target topic
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

# --- RELAY LOGIC ---
async def relay(update, context):
    msg = update.message
    if not msg:
        return

    # Only source group
    if msg.chat_id != SOURCE_CHAT_ID:
        return

    # Only General topic
    if msg.message_thread_id is not None:
        return

    # Must be text
    if not msg.text:
        return

    text = msg.text.strip()

    # Match payment structure
    if not PAYMENT_PATTERN.search(text):
        return

    # Relay to target topic
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=text,
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
