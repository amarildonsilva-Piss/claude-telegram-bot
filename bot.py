import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ola! Sou o Claude. Como posso te ajudar?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": user_message})
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="Voce e um assistente util. Responda em portugues.",
            messages=conversation_history[user_id]
        )
        assistant_message = response.content[0].text
        conversation_history[user_id].append({"role": "assistant", "content": assistant_message})
        await update.message.reply_text(assistant_message)
    except Exception as e:
        await update.message.reply_text("Erro. Tente novamente.")
        print(f"Erro: {e}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversation_history[update.effective_user.id] = []
    await update.message.reply_text("Historico limpo!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot iniciado!")
    app.run_polling()
