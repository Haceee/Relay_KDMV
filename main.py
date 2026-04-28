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

    # 1) Only from source group
    if msg.chat_id != SOURCE_CHAT_ID:
        return

    # 2) Only General topic (no thread id)
    if msg.message_thread_id is not None:
        return

    # 3) Only forwarded from PayWay bot
    if not msg.forward_from or msg.forward_from.id != PAYWAY_BOT_ID:
        return

    # 4) Relay exact message
    await context.bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=msg.text,
        message_thread_id=TARGET_TOPIC_ID
    )

# --- MAIN ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, relay))
    app.run_polling()

if __name__ == "__main__":
    main()
