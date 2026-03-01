import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ola! Sou seu assistente de IA. Como posso te ajudar?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append(user_message)
    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id] = conversation_history[user_id][-10:]
    try:
        history_text = "\n".join(conversation_history[user_id][:-1])
        prompt = f"Voce e um assistente util. Responda em portugues brasileiro.\n\nHistorico:\n{history_text}\n\nUsuario: {user_message}\nAssistente:"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        assistant_message = response.text
        conversation_history[user_id].append(f"Assistente: {assistant_message}")
        await update.message.reply_text(assistant_message)
    except Exception as e:
        await update.message.reply_text("Desculpe, ocorreu um erro. Tente novamente.")
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
