from telegram.ext import Application, MessageHandler, filters

TOKEN = "8780536402:AAGjzORxNIQKdgV0lpR9E155Jhetein74-U"

async def debug(update, context):

    msg = update.message

    print("CHAT ID:", msg.chat_id)

    print("THREAD ID:", msg.message_thread_id)

    print("IS TOPIC:", msg.is_topic_message)

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, debug))

app.run_polling()
