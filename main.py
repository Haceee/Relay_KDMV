import os
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


# --- STARTUP ---
async def on_startup(app):
    try:
        await app.bot.send_message(
            chat_id=SOURCE_CHAT_ID,
            text="🟢 Relay Bot ONLINE (DEBUG)"
        )

        await app.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text="🟢 Relay Bot ONLINE (DEBUG)",
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


# --- RELAY (DEBUG MODE) ---
async def relay(update, context):
    msg = update.message
    if not msg:
        return

    print("\n===== DEBUG MESSAGE =====")
    print("CHAT ID:", msg.chat_id)
    print("THREAD ID:", msg.message_thread_id)
    print("TEXT:", msg.text)

    if msg.from_user:
        print("FROM_USER:", msg.from_user.id, msg.from_user.username)

    if msg.sender_chat:
        print("SENDER_CHAT:", msg.sender_chat.id, msg.sender_chat.title)

    print("=========================\n")

    # --- ONLY SOURCE GROUP ---
    if msg.chat_id != SOURCE_CHAT_ID:
        print("❌ Not source group")
        return

    if not msg.text:
        print("❌ No text")
        return

    # --- FORCE RELAY (no filters) ---
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text="DEBUG RELAY:\n" + msg.text,
        message_thread_id=TARGET_TOPIC_ID
    )

    print("✅ RELAY SENT")


# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, relay))
    app.add_error_handler(error_handler)

    app.post_init = on_startup

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
