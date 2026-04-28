import os
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
PAYWAY_BOT_ID = 1148497258           # PayWay bot


# --- STARTUP STATUS ---
async def on_startup(app):
    try:
        # Send to SOURCE (general chat)
        await app.bot.send_message(
            chat_id=SOURCE_CHAT_ID,
            text="🟢 Relay Bot ONLINE"
        )

        # Send to TARGET (specific topic)
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


# --- RELAY ---
async def relay(update, context):
    msg = update.message
    if not msg:
        return

    # Source group only
    if msg.chat_id != SOURCE_CHAT_ID:
        return

    # Only General topic
    if msg.message_thread_id is not None:
        return

    # Must be text
    if not msg.text:
        return

    # Detect PayWay forwarded message
    is_payway = False

    if msg.forward_origin and hasattr(msg.forward_origin, "sender_user"):
        if msg.forward_origin.sender_user.id == PAYWAY_BOT_ID:
            is_payway = True

    if msg.forward_from and msg.forward_from.id == PAYWAY_BOT_ID:
        is_payway = True

    if not is_payway:
        return

    # Relay to target topic
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=msg.text,
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
