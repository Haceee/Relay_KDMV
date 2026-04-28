import os
from telegram.ext import Application, MessageHandler, filters

# --- ENV TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

# --- CONFIG ---
SOURCE_CHAT_ID = -1002813360979      # PCMKR Division
TARGET_CHAT_ID = -1002962986373      # KDMV ORDERS
TARGET_TOPIC_ID = 4491               # Website payment topic

PAYWAY_BOT_ID = 1148497258           # PayWayByABA_bot


# --- RELAY LOGIC ---
async def relay(update, context):
    msg = update.message
    if not msg:
        return

    # ===== DEBUG LOG =====
    print("\n===== NEW MESSAGE =====")
    print("CHAT ID:", msg.chat_id)
    print("THREAD ID:", msg.message_thread_id)
    print("TEXT:", msg.text)

    if msg.forward_origin:
        print("FORWARD_ORIGIN:", msg.forward_origin)
        if hasattr(msg.forward_origin, "sender_user"):
            print("FORWARD_ORIGIN USER ID:", msg.forward_origin.sender_user.id)

    if msg.forward_from:
        print("FORWARD_FROM:", msg.forward_from)
        print("FORWARD_FROM ID:", msg.forward_from.id)

    # ===== FILTERS =====

    # 1. Source group only
    if msg.chat_id != SOURCE_CHAT_ID:
        print("❌ Not source group")
        return

    # 2. Only General topic
    if msg.message_thread_id is not None:
        print("❌ Not General topic")
        return

    # 3. Must be text
    if not msg.text:
        print("❌ No text")
        return

    # 4. Detect PayWay source
    is_payway = False

    # New Telegram format
    if msg.forward_origin:
        if hasattr(msg.forward_origin, "sender_user"):
            if msg.forward_origin.sender_user.id == PAYWAY_BOT_ID:
                is_payway = True

    # Old fallback
    if msg.forward_from:
        if msg.forward_from.id == PAYWAY_BOT_ID:
            is_payway = True

    print("IS PAYWAY:", is_payway)

    if not is_payway:
        print("❌ Filtered out (not PayWay)")
        return

    # ===== RELAY =====
    print("✅ RELAYING MESSAGE")

    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=msg.text,
        message_thread_id=TARGET_TOPIC_ID
    )


# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, relay))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
